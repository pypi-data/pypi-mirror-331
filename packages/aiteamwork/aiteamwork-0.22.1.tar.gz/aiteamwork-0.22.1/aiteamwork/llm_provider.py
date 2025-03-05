from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, final

from pydantic import BaseModel, Field

from aiteamwork.llm_agent_usage import LLMAgentUsage
from aiteamwork.llm_file import LLMFile, LLMSupportedFileType, LLMSupportedFileTypeContentType
from aiteamwork.llm_file_converter import LLMFileConverter
from aiteamwork.llm_message import LLMMessage
from aiteamwork.llm_provider_result import LLMProviderResult
from aiteamwork.llm_tool_function import LLMToolFunctionDefinition
from aiteamwork.llm_context import LLMContext


class LLMProviderContext[RuntimeContextType: BaseModel](LLMContext[RuntimeContextType]):
    system_instructions: str = Field()
    messages: list[LLMMessage] = Field()
    artifact_schema: type[BaseModel] | None = Field()
    tools: list[LLMToolFunctionDefinition] = Field()
    total_usage: LLMAgentUsage = Field()
    prompt_usage: LLMAgentUsage = Field(default_factory=LLMAgentUsage)
    attempt: int = Field(default=1)
    streaming_callback: Callable[[str, str, bool], Coroutine[None, None, None]] | None = Field(default=None)
    file_converters: list[LLMFileConverter] = Field(default_factory=list)


class LLMProvider[ValidationModel: BaseModel](ABC):
    @abstractmethod
    async def prompt(self, context: LLMProviderContext) -> LLMProviderResult:
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    def get_runtime_context_schema(self) -> type[ValidationModel]:
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    def get_supported_file_types(self) -> list[LLMSupportedFileType]:
        raise NotImplementedError("This method must be overridden by subclasses")

    @final
    def validate_configuration(self, runtime_context: Any, tools: list[LLMToolFunctionDefinition]) -> None:
        schema = self.get_runtime_context_schema()
        if schema is None or not issubclass(schema, BaseModel) or schema == BaseModel:
            raise ValueError("get_runtime_context_schema must return a subclass of pydantic.BaseModel")
        schema.model_validate({**runtime_context})
        self.validate_runtime_context(runtime_context)
        self.validate_tools(tools)

    def validate_runtime_context(self, runtime_context: Any):
        pass

    def validate_tools(self, tools: list[LLMToolFunctionDefinition]):
        pass

    async def get_supported_llm_file(
        self, file: LLMFile, context: LLMProviderContext
    ) -> tuple[LLMFile, LLMSupportedFileTypeContentType]:
        if not file.is_binary:
            return file, LLMSupportedFileTypeContentType.PLAIN_TEXT

        return await file.get_as_supported_llm_file(
            self.get_supported_file_types(),
            self.get_name(),
            context.file_converters,
        )


__all__ = ["LLMProvider", "LLMProviderContext"]
