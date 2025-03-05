import asyncio
from abc import ABC, abstractmethod
from logging import Logger
from typing import Callable, Coroutine
from pydantic import BaseModel
from aiteamwork.llm_agent_usage import LLMAgentUsage
from aiteamwork.llm_context import LLMContext, LLMInitialContext
from aiteamwork.llm_file_converter import LLMFileConverter
from aiteamwork.llm_message import LLMMessage
from aiteamwork.llm_pipeable import LLMPipeable
from aiteamwork.llm_prompt_result import LLMPromptResult
from aiteamwork.llm_prompt_round_result import LLMPromptRoundResult
from aiteamwork.llm_tool_function import LLMToolFunctionDefinition
from aiteamwork.serializable_producer import SerializableProducer
from aiteamwork.util.callable import SyncOrAsyncCallback


class LLMAgentLike[
    RuntimeContextType: BaseModel,
](SerializableProducer, LLMPipeable, ABC):
    @abstractmethod
    def get_id(self) -> str:
        """
        Get the ID of the LLM agent.
        """
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    def get_description(self) -> str:
        """
        Get the description of the LLM agent.
        """
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    def get_runtime_context_schema(self) -> type[BaseModel]:
        """
        Get the runtime context schema of the LLM agent.
        """
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    async def execute_prompt_round(
        self,
        messages: list[LLMMessage],
        context: LLMContext[RuntimeContextType],
        logger: Logger,
        extra_instructions_before: str,
        extra_instructions_after: str,
        extra_tools: list[LLMToolFunctionDefinition],
        streaming_callback: Callable[[str, str, bool], Coroutine[None, None, None]] | None,
        usage: LLMAgentUsage,
        round: int,
    ) -> LLMPromptRoundResult:
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    async def prompt(
        self,
        messages: list[LLMMessage | str] | list[LLMMessage] | list[str] | LLMMessage | str,
        context: LLMInitialContext[RuntimeContextType] | None = None,
        logger: Logger | None = None,
        max_rounds: int | None = None,
        extra_instructions_before: str | None = None,
        extra_instructions_after: str | None = None,
        extra_tools: list[Callable | LLMToolFunctionDefinition] | None = None,
        previous_usage: LLMAgentUsage | None = None,
        streaming_callback: SyncOrAsyncCallback[[str, str, bool], None] | None = None,
        file_converters: list[LLMFileConverter] = [],
    ) -> LLMPromptResult:
        """
        Generate a response based on the provided messages and context.

        Args:
            messages (list[LLMMessage]): List of messages to process.
            max_rounds (int | None): Maximum amount of message creating rounds the LLM is allowed to run.
            extra_instructions_before (str | None): Additional instructions before processing.
            extra_instructions_after (str | None): Additional instructions after processing.
            extra_tools (list[LLMToolFunctionDefinition] | None): Additional tools for processing.
            context (LLMContext): Context for the LLM agent.
            previous_usage: (LLMAgentUsage): Previous LLM Agent token usage for filtering and pipe information.
            streaming_callback (Callable | None): Callback for streaming responses.

        Returns:
            list[str]: List of generated responses.
        """
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    def prompt_sync(
        self,
        messages: list[LLMMessage | str] | list[LLMMessage] | list[str] | LLMMessage | str,
        context: LLMInitialContext[RuntimeContextType] | None = None,
        logger: Logger | None = None,
        max_rounds: int | None = None,
        extra_instructions_before: str | None = None,
        extra_instructions_after: str | None = None,
        extra_tools: list[Callable | LLMToolFunctionDefinition] | None = None,
        previous_usage: LLMAgentUsage | None = None,
        streaming_callback: SyncOrAsyncCallback[[str, str, bool], None] | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
        file_converters: list[LLMFileConverter] = [],
    ) -> LLMPromptResult:
        """
        Generate a response based on the provided messages and context.

        Args:
            messages (list[LLMMessage]): List of messages to process.
            max_rounds (int | None): Maximum amount of message creating rounds the LLM is allowed to run.
            extra_instructions_before (str | None): Additional instructions before processing.
            extra_instructions_after (str | None): Additional instructions after processing.
            extra_tools (list[LLMToolFunctionDefinition] | None): Additional tools for processing.
            context (LLMContext): Context for the LLM agent.
            previous_usage: (LLMAgentUsage): Previous LLM Agent token usage for filtering and pipe information.
            streaming_callback (Callable | None): Callback for streaming responses.

        Returns:
            list[str]: List of generated responses.
        """
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    async def validate_configuration(
        self,
        context: LLMInitialContext[RuntimeContextType],
        extra_tools: list[LLMToolFunctionDefinition],
    ) -> None:
        """
        Validate the configuration or state of the LLM agent.

        This method must be overridden by subclasses.
        """
        raise NotImplementedError("This method must be overridden by subclasses")


__all__ = ["LLMAgentLike"]
