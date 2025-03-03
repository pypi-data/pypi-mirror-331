import os
from typing import Any, Dict

from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages.base import BaseMessage
from langchain_core.runnables import Runnable
from langchain_fireworks import ChatFireworks
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from pydantic import BaseModel

import kiln_ai.datamodel as datamodel
from kiln_ai.adapters.ml_model_list import (
    KilnModelProvider,
    ModelProviderName,
    StructuredOutputMode,
)
from kiln_ai.adapters.model_adapters.base_adapter import (
    COT_FINAL_ANSWER_PROMPT,
    AdapterConfig,
    BaseAdapter,
    RunOutput,
)
from kiln_ai.adapters.ollama_tools import (
    get_ollama_connection,
    ollama_base_url,
    ollama_model_installed,
)
from kiln_ai.datamodel import PromptId
from kiln_ai.datamodel.task import RunConfig
from kiln_ai.utils.config import Config
from kiln_ai.utils.exhaustive_error import raise_exhaustive_enum_error

LangChainModelType = BaseChatModel | Runnable[LanguageModelInput, Dict | BaseModel]


class LangchainAdapter(BaseAdapter):
    _model: LangChainModelType | None = None

    def __init__(
        self,
        kiln_task: datamodel.Task,
        custom_model: BaseChatModel | None = None,
        model_name: str | None = None,
        provider: str | None = None,
        prompt_id: PromptId | None = None,
        base_adapter_config: AdapterConfig | None = None,
    ):
        if custom_model is not None:
            self._model = custom_model

            # Attempt to infer model provider and name from custom model
            if provider is None:
                provider = "custom.langchain:" + custom_model.__class__.__name__

            if model_name is None:
                model_name = "custom.langchain:unknown_model"
                if hasattr(custom_model, "model_name") and isinstance(
                    getattr(custom_model, "model_name"), str
                ):
                    model_name = "custom.langchain:" + getattr(
                        custom_model, "model_name"
                    )
                if hasattr(custom_model, "model") and isinstance(
                    getattr(custom_model, "model"), str
                ):
                    model_name = "custom.langchain:" + getattr(custom_model, "model")
        elif model_name is not None:
            # default provider name if not provided
            provider = provider or "custom.langchain.default_provider"
        else:
            raise ValueError(
                "model_name and provider must be provided if custom_model is not provided"
            )

        if model_name is None:
            raise ValueError("model_name must be provided")

        run_config = RunConfig(
            task=kiln_task,
            model_name=model_name,
            model_provider_name=provider,
            prompt_id=prompt_id or datamodel.PromptGenerators.SIMPLE,
        )

        super().__init__(
            run_config=run_config,
            config=base_adapter_config,
        )

    async def model(self) -> LangChainModelType:
        # cached model
        if self._model:
            return self._model

        self._model = await self.langchain_model_from()

        # Decide if we want to use Langchain's structured output:
        # 1. Only for structured tasks
        # 2. Only if the provider's mode isn't json_instructions (only mode that doesn't use an API option for structured output capabilities)
        provider = self.model_provider()
        use_lc_structured_output = (
            self.has_structured_output()
            and provider.structured_output_mode
            != StructuredOutputMode.json_instructions
        )

        if use_lc_structured_output:
            if not hasattr(self._model, "with_structured_output") or not callable(
                getattr(self._model, "with_structured_output")
            ):
                raise ValueError(
                    f"model {self._model} does not support structured output, cannot use output_json_schema"
                )
            # Langchain expects title/description to be at top level, on top of json schema
            output_schema = self.task().output_schema()
            if output_schema is None:
                raise ValueError(
                    f"output_json_schema is not valid json: {self.task().output_json_schema}"
                )
            output_schema["title"] = "task_response"
            output_schema["description"] = "A response from the task"
            with_structured_output_options = self.get_structured_output_options(
                self.run_config.model_name, self.run_config.model_provider_name
            )
            self._model = self._model.with_structured_output(
                output_schema,
                include_raw=True,
                **with_structured_output_options,
            )
        return self._model

    async def _run(self, input: Dict | str) -> RunOutput:
        if self.base_adapter_config.top_logprobs is not None:
            raise ValueError(
                "Kiln's Langchain adapter does not support logprobs/top_logprobs. Select a model from an OpenAI compatible provider (openai, openrouter, etc) instead."
            )

        provider = self.model_provider()
        model = await self.model()
        chain = model
        intermediate_outputs = {}

        prompt = self.build_prompt()
        user_msg = self.prompt_builder.build_user_message(input)
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=user_msg),
        ]

        run_strategy, cot_prompt = self.run_strategy()

        if run_strategy == "cot_as_message":
            if not cot_prompt:
                raise ValueError("cot_prompt is required for cot_as_message strategy")
            messages.append(SystemMessage(content=cot_prompt))
        elif run_strategy == "cot_two_call":
            if not cot_prompt:
                raise ValueError("cot_prompt is required for cot_two_call strategy")
            messages.append(
                SystemMessage(content=cot_prompt),
            )

            # Base model (without structured output) used for COT message
            base_model = await self.langchain_model_from()

            cot_messages = [*messages]
            cot_response = await base_model.ainvoke(cot_messages)
            intermediate_outputs["chain_of_thought"] = cot_response.content
            messages.append(AIMessage(content=cot_response.content))
            messages.append(HumanMessage(content=COT_FINAL_ANSWER_PROMPT))

        response = await chain.ainvoke(messages)

        # Langchain may have already parsed the response into structured output, so use that if available.
        # However, a plain string may still be fixed at the parsing layer, so not being structured isn't a critical failure (yet)
        if (
            self.has_structured_output()
            and isinstance(response, dict)
            and "parsed" in response
            and isinstance(response["parsed"], dict)
        ):
            structured_response = response["parsed"]
            return RunOutput(
                output=self._munge_response(structured_response),
                intermediate_outputs=intermediate_outputs,
            )

        if not isinstance(response, BaseMessage):
            raise RuntimeError(f"response is not a BaseMessage: {response}")

        text_content = response.content
        if not isinstance(text_content, str):
            raise RuntimeError(f"response is not a string: {text_content}")

        return RunOutput(
            output=text_content,
            intermediate_outputs=intermediate_outputs,
        )

    def adapter_name(self) -> str:
        return "kiln_langchain_adapter"

    def _munge_response(self, response: Dict) -> Dict:
        # Mistral Large tool calling format is a bit different. Convert to standard format.
        if (
            "name" in response
            and response["name"] == "task_response"
            and "arguments" in response
        ):
            return response["arguments"]
        return response

    def get_structured_output_options(
        self, model_name: str, model_provider_name: str
    ) -> Dict[str, Any]:
        provider = self.model_provider()
        if not provider:
            return {}

        options = {}
        # We may need to add some provider specific logic here if providers use different names for the same mode, but everyone is copying openai for now
        match provider.structured_output_mode:
            case StructuredOutputMode.function_calling_weak:
                # Langchaing doesn't handle weak/strict separately
                options["method"] = "function_calling"
            case StructuredOutputMode.function_calling:
                options["method"] = "function_calling"
            case StructuredOutputMode.json_mode:
                options["method"] = "json_mode"
            case StructuredOutputMode.json_instruction_and_object:
                # We also pass instructions
                options["method"] = "json_mode"
            case StructuredOutputMode.json_schema:
                options["method"] = "json_schema"
            case StructuredOutputMode.json_instructions:
                # JSON done via instructions in prompt, not via API
                pass
            case StructuredOutputMode.default:
                if provider.name == ModelProviderName.ollama:
                    # Ollama has great json_schema support, so use that: https://ollama.com/blog/structured-outputs
                    options["method"] = "json_schema"
                else:
                    # Let langchain decide the default
                    pass
            case _:
                raise_exhaustive_enum_error(provider.structured_output_mode)

        return options

    async def langchain_model_from(self) -> BaseChatModel:
        provider = self.model_provider()
        return await langchain_model_from_provider(provider, self.run_config.model_name)


async def langchain_model_from_provider(
    provider: KilnModelProvider, model_name: str
) -> BaseChatModel:
    if provider.name == ModelProviderName.openai:
        # We use the OpenAICompatibleAdapter for OpenAI
        raise ValueError("OpenAI is not supported in Langchain adapter")
    elif provider.name == ModelProviderName.openai_compatible:
        # We use the OpenAICompatibleAdapter for OpenAI compatible
        raise ValueError("OpenAI compatible is not supported in Langchain adapter")
    elif provider.name == ModelProviderName.groq:
        api_key = Config.shared().groq_api_key
        if api_key is None:
            raise ValueError(
                "Attempted to use Groq without an API key set. "
                "Get your API key from https://console.groq.com/keys"
            )
        return ChatGroq(**provider.provider_options, groq_api_key=api_key)  # type: ignore[arg-type]
    elif provider.name == ModelProviderName.amazon_bedrock:
        api_key = Config.shared().bedrock_access_key
        secret_key = Config.shared().bedrock_secret_key
        # langchain doesn't allow passing these, so ugly hack to set env vars
        os.environ["AWS_ACCESS_KEY_ID"] = api_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
        return ChatBedrockConverse(
            **provider.provider_options,
        )
    elif provider.name == ModelProviderName.fireworks_ai:
        api_key = Config.shared().fireworks_api_key
        return ChatFireworks(**provider.provider_options, api_key=api_key)
    elif provider.name == ModelProviderName.ollama:
        # Ollama model naming is pretty flexible. We try a few versions of the model name
        potential_model_names = []
        if "model" in provider.provider_options:
            potential_model_names.append(provider.provider_options["model"])
        if "model_aliases" in provider.provider_options:
            potential_model_names.extend(provider.provider_options["model_aliases"])

        # Get the list of models Ollama supports
        ollama_connection = await get_ollama_connection()
        if ollama_connection is None:
            raise ValueError("Failed to connect to Ollama. Ensure Ollama is running.")

        for model_name in potential_model_names:
            if ollama_model_installed(ollama_connection, model_name):
                return ChatOllama(model=model_name, base_url=ollama_base_url())

        raise ValueError(f"Model {model_name} not installed on Ollama")
    elif provider.name == ModelProviderName.openrouter:
        raise ValueError("OpenRouter is not supported in Langchain adapter")
    else:
        raise ValueError(f"Invalid model or provider: {model_name} - {provider.name}")
