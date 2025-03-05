import asyncio
import logging
from functools import cached_property
from logging import Logger
from math import floor
from typing import Any, Callable, Coroutine, Union, cast

from pydantic import BaseModel, Field, PrivateAttr, TypeAdapter

from aiteamwork.callbacks.artifact_verification import LLMArtifactVerificationContext, LLMArtifactVerificationResult
from aiteamwork.callbacks.instructions import LLMInstructionsContext, LLMInstructionsResult
from aiteamwork.callbacks.memory import LLMMemoryContext, LLMMemoryResult
from aiteamwork.callbacks.stop_when import LLMStopWhenContext, LLMStopWhenResult
from aiteamwork.callbacks.tools_factory import LLMToolsFactoryContext, LLMToolsFactoryResult
from aiteamwork.callbacks.trigger_when import LLMTriggerWhenContext, LLMTriggerWhenResult
from aiteamwork.callbacks.trimming import LLMTrimmingContext, LLMTrimmingResult
from aiteamwork.contextvar import get_agent_usage, get_llm_context, set_agent_usage, set_llm_context
from aiteamwork.llm_agent_like import LLMAgentLike
from aiteamwork.llm_agent_usage import LLMAgentUsage
from aiteamwork.llm_artifact_validator import LLMArtifactValidator
from aiteamwork.llm_context import EmptyRuntimeContext, LLMContext, LLMInitialContext
from aiteamwork.llm_file_converter import LLMFileConverter
from aiteamwork.llm_message import LLMMessage
from aiteamwork.llm_pipe import LLMPipe
from aiteamwork.llm_pipeable import LLMPipeable
from aiteamwork.llm_prompt_result import LLMPromptResult
from aiteamwork.llm_prompt_round_result import LLMPromptRoundResult
from aiteamwork.llm_provider import LLMProvider, LLMProviderContext
from aiteamwork.llm_provider_result import LLMProviderResult
from aiteamwork.llm_role import LLMRole
from aiteamwork.llm_tool_executor import LLMToolExecutor
from aiteamwork.llm_tool_function import LLMToolFunctionDefinition
from aiteamwork.serializable_producer import SerializableProducer
from aiteamwork.util.callable import SyncOrAsyncCallback
from aiteamwork.util.date import get_current_time
from aiteamwork.util.validators import validate_and_raise_model, validate_not_none, validated_sync_async_callback


def stop_when_tools_are_called_or_agent_message_exists(context: LLMStopWhenContext) -> LLMStopWhenResult:
    old_messages = context.prompt_start_messages
    result = context.prompt_result

    non_info_debug_messages = [msg for msg in result.messages if msg.role not in {LLMRole.INFO, LLMRole.DEBUG}]

    old_tool_calls = set(
        [validate_not_none(msg.tool_call_result).call_id for msg in old_messages if msg.role == LLMRole.TOOL]
    )

    new_tool_calls = set(
        [validate_not_none(msg.tool_call_result).call_id for msg in result.messages if msg.role == LLMRole.TOOL]
    )

    executed_tools = len(new_tool_calls.difference(old_tool_calls)) > 0

    has_new_human_awaiting_actions = (
        non_info_debug_messages and non_info_debug_messages[-1].role == LLMRole.AWAITING_HUMAN_ACTION
    )

    if executed_tools or has_new_human_awaiting_actions:
        return LLMStopWhenResult(stop=True)

    if not executed_tools and len(non_info_debug_messages) > len(old_messages):
        last_message = non_info_debug_messages[-1]
        if last_message.role == LLMRole.AGENT:
            return LLMStopWhenResult(stop=True)

    return LLMStopWhenResult(stop=False)


class LLMAgent[
    RuntimeContextType: BaseModel,
    ArtifactType: BaseModel,
](LLMAgentLike[RuntimeContextType], BaseModel, LLMPipeable):
    id: str = Field(default="unknown_agent")
    description: str = Field(min_length=8, max_length=256, default="Unknown agent.")
    provider: LLMProvider = Field()
    instructions: str | SyncOrAsyncCallback[[LLMInstructionsContext[RuntimeContextType]], LLMInstructionsResult] = (
        Field(default="")
    )
    cache_instructions: bool = Field(default=True)
    tools: (
        list[Callable | LLMToolFunctionDefinition]
        | SyncOrAsyncCallback[[LLMToolsFactoryContext[RuntimeContextType]], LLMToolsFactoryResult]
    ) = Field(default_factory=lambda: [])
    cache_tools: bool = Field(default=True)
    artifact_schema: type[ArtifactType] | None = Field(default=None)
    artifact_verification: (
        SyncOrAsyncCallback[
            [LLMArtifactVerificationContext[ArtifactType, RuntimeContextType]], LLMArtifactVerificationResult
        ]
        | None
    ) = Field(default=None)
    runtime_context_schema: type[RuntimeContextType] | None = Field(default=None)
    trimming: SyncOrAsyncCallback[[LLMTrimmingContext[RuntimeContextType]], LLMTrimmingResult] | None = Field(
        default=None
    )
    memory: SyncOrAsyncCallback[[LLMMemoryContext[RuntimeContextType]], LLMMemoryResult] | None = Field(default=None)
    stop_when: SyncOrAsyncCallback[[LLMStopWhenContext[RuntimeContextType]], LLMStopWhenResult] | None = Field(
        default=None
    )
    trigger_when: SyncOrAsyncCallback[[LLMTriggerWhenContext[RuntimeContextType]], LLMTriggerWhenResult] | None = Field(
        default=None
    )
    file_converters: list[LLMFileConverter] = Field(default_factory=list)

    _pipe: LLMPipe | None = PrivateAttr(default=None)
    _instructions_cache: str | None = PrivateAttr(default=None)
    _tools_cache: list[LLMToolFunctionDefinition] | None = PrivateAttr(default=None)
    _dependents: list[LLMAgentLike | SerializableProducer | type[BaseModel] | TypeAdapter] = PrivateAttr(
        default_factory=list
    )

    class Config:
        arbitrary_types_allowed = True

    def get_id(self) -> str:
        return self.id

    def get_description(self) -> str:
        return self.description

    @cached_property
    def _tools_as_factory(
        self,
    ) -> Callable[[LLMToolsFactoryContext[RuntimeContextType]], Coroutine[None, None, list[LLMToolFunctionDefinition]]]:
        if isinstance(self.tools, list):
            value = [
                tool if isinstance(tool, LLMToolFunctionDefinition) else LLMToolFunctionDefinition(tool)
                for tool in self.tools
            ]

            async def value_factory(
                context: LLMToolsFactoryContext[RuntimeContextType],
            ) -> list[LLMToolFunctionDefinition]:
                return value

            return value_factory

        fetch_callables = validated_sync_async_callback(
            LLMToolsFactoryResult,
            ["context"],
            "tools",
            self.tools,
        )

        async def factory(context: LLMToolsFactoryContext[RuntimeContextType]) -> list[LLMToolFunctionDefinition]:
            if self.cache_tools and self._tools_cache is not None:
                return self._tools_cache

            tools = (await fetch_callables(context)).tools
            result = [
                tool if isinstance(tool, LLMToolFunctionDefinition) else LLMToolFunctionDefinition(tool)
                for tool in tools
            ]

            if self.cache_tools:
                self._tools_cache = result

            return result

        return factory

    @cached_property
    def _instructions_as_factory(
        self,
    ) -> Callable[[LLMInstructionsContext[RuntimeContextType]], Coroutine[None, None, LLMInstructionsResult]]:
        if isinstance(self.instructions, str):
            value = self.instructions

            async def factory(context: LLMInstructionsContext[RuntimeContextType]) -> LLMInstructionsResult:
                return LLMInstructionsResult(instructions=value)

            return factory

        return validated_sync_async_callback(
            LLMInstructionsResult,
            ["context"],
            "instructions",
            self.instructions,
        )

    @cached_property
    def _trim_conversation(
        self,
    ) -> Callable[
        [LLMTrimmingContext[RuntimeContextType]],
        Coroutine[None, None, LLMTrimmingResult],
    ]:
        return validated_sync_async_callback(
            LLMTrimmingResult,
            ["context"],
            "trimming",
            self.trimming or (lambda context: LLMTrimmingResult(messages=context.messages)),
        )

    @cached_property
    def _fetch_memories(
        self,
    ) -> Callable[[LLMMemoryContext[RuntimeContextType]], Coroutine[None, None, LLMMemoryResult]]:
        return validated_sync_async_callback(
            LLMMemoryResult,
            ["context"],
            "memory",
            self.memory or (lambda context: LLMMemoryResult()),
        )

    @cached_property
    def _stop_when(
        self,
    ) -> Callable[[LLMStopWhenContext[RuntimeContextType]], Coroutine[None, None, LLMStopWhenResult]]:
        return validated_sync_async_callback(
            LLMStopWhenResult,
            ["context"],
            "stop_when",
            self.stop_when or stop_when_tools_are_called_or_agent_message_exists,
        )

    @cached_property
    def _trigger_when(
        self,
    ) -> Callable[[LLMTriggerWhenContext[RuntimeContextType]], Coroutine[None, None, LLMTriggerWhenResult]]:
        return validated_sync_async_callback(
            LLMTriggerWhenResult,
            ["context"],
            "trigger_when",
            self.trigger_when or (lambda context: LLMTriggerWhenResult(trigger=True)),
        )

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
        logger.info(f"[LLM Agent {self.id}] Starting round {round}")
        runtime_context_schema = self.runtime_context_schema or EmptyRuntimeContext

        has_next_round = False

        tools_context_type = LLMToolsFactoryContext[runtime_context_schema]
        tools_context: LLMToolsFactoryContext = tools_context_type.model_validate(
            {
                **context.model_dump(mode="python"),
                "messages": [msg.model_copy() for msg in messages],
            }
        )

        agent_tools = await self._tools_as_factory(tools_context)

        tool_list = [
            *agent_tools,
            *extra_tools,
        ]

        messages_buffer: list[LLMMessage] = (
            await self._trim_conversation(
                LLMTrimmingContext.model_validate(
                    {
                        **context.model_dump(mode="python"),
                        "messages": [msg.model_copy() for msg in messages],
                    }
                ),
            )
        ).messages

        LLMMessage.validate_message_history(messages_buffer)

        instructions_context_type = LLMInstructionsContext[runtime_context_schema]
        instructions_context: LLMInstructionsContext = instructions_context_type.model_validate(
            context.model_dump(mode="python"),
        )

        if self.cache_instructions:
            if not self._instructions_cache:
                self._instructions_cache = (await self._instructions_as_factory(instructions_context)).instructions
        else:
            self._instructions_cache = (await self._instructions_as_factory(instructions_context)).instructions

        instructions = self._instructions_cache

        if extra_instructions_before:
            instructions = f"{extra_instructions_before}\n\n---\n\n{instructions}"

        if extra_instructions_after:
            instructions += f"\n\n---\n\n{extra_instructions_after}"

        human_in_the_loop_confirmation_round = (
            messages_buffer and messages_buffer[-1].role == LLMRole.HUMAN_CONFIRMATION
        )

        if not human_in_the_loop_confirmation_round:
            if len(messages_buffer) > 0:
                last_user_message = messages_buffer[-1]
                if last_user_message.role == LLMRole.USER:
                    memory_context_type = LLMMemoryContext[runtime_context_schema]
                    memory_context: LLMMemoryContext = memory_context_type.model_validate(
                        {
                            **context.model_dump(mode="python"),
                            "last_user_message": messages_buffer[-1].model_copy(),
                            "messages": [msg.model_copy() for msg in messages_buffer],
                        }
                    )
                    memory_messages = (await self._fetch_memories(memory_context)).memories
                    messages_buffer.pop()
                    last_message_timestamp = last_user_message.timestamp or get_current_time().timestamp()
                    for i in range(0, len(memory_messages)):
                        msg = memory_messages[i]
                        msg.timestamp = last_message_timestamp + i
                        messages_buffer.append(msg)
                    last_user_message.timestamp = last_message_timestamp + len(memory_messages) + 1
                    messages_buffer.append(last_user_message)

            validated_context = validate_and_raise_model(
                self.provider.get_runtime_context_schema(),
                {**context.runtime_context.model_dump(mode="python")},
                lambda: ValueError("Invalid output schema."),
                lambda e: ValueError(f"Invalid output data: {e}"),
            )

            logger.info(
                f"[LLM Agent {self.id}] Prompting provider {self.provider.get_name()} "
                f"with {len(messages_buffer)} messages."
            )
            provider_result = await self.provider.prompt(
                context=LLMProviderContext(
                    logger=logger,
                    system_instructions=instructions,
                    messages=messages_buffer,
                    artifact_schema=self.artifact_schema,
                    tools=tool_list,
                    total_usage=usage.model_copy(),
                    attempt=round,
                    runtime_context=validated_context,
                    streaming_callback=streaming_callback,
                    current_agent=self.id,
                    user_id=context.user_id,
                    conversation_id=context.conversation_id,
                    assistant_name=context.assistant_name,
                    agent_state=context.agent_state,
                ),
            )

            provider_result = validate_and_raise_model(LLMProviderResult, provider_result, ValueError, ValueError)
            usage += provider_result.usage

            non_info_debug_msgs = [
                msg for msg in provider_result.new_messages if msg.role not in {LLMRole.INFO, LLMRole.DEBUG}
            ]

            if non_info_debug_msgs:
                messages_buffer.extend(provider_result.new_messages)
        else:
            non_info_debug_msgs = [msg for msg in messages_buffer if msg.role not in {LLMRole.INFO, LLMRole.DEBUG}]

        if non_info_debug_msgs or human_in_the_loop_confirmation_round:
            last_message = non_info_debug_msgs[-1]

            if last_message.artifact and self.artifact_schema and not human_in_the_loop_confirmation_round:

                artifact_validator = LLMArtifactValidator[RuntimeContextType, ArtifactType](
                    agent_id=self.id,
                    agent_description=self.description,
                    system_instructions=instructions,
                    artifact_verification=self.artifact_verification,
                    artifact_schema=self.artifact_schema,
                    tools=tool_list,
                    provider=self.provider,
                    messages=messages_buffer,
                    context=context,
                    round=round,
                    retries=3,
                    logger=logger,
                    current_usage=usage.model_copy(),
                )

                validator_result = await artifact_validator.validate_artifact(
                    messages_buffer,
                )
                usage += validator_result.usage
                last_message.artifact = validator_result.artifact

            if last_message.tool_call_requests or human_in_the_loop_confirmation_round:
                tool_executor = LLMToolExecutor(
                    agent_id=self.id,
                    agent_description=self.description,
                    system_instructions=instructions,
                    tools=tool_list,
                    provider=self.provider,
                    context=context,
                    round=round,
                    current_usage=usage.model_copy(),
                    logger=logger,
                )

                exec_result = await tool_executor.run_tools(messages_buffer)
                if human_in_the_loop_confirmation_round:
                    last_agent_msg = next(msg for msg in non_info_debug_msgs.copy()[:-1] if msg.role == LLMRole.AGENT)
                    non_info_debug_msgs[-2].tool_call_requests = exec_result.executed_requests
                    last_agent_msg.tool_call_requests = exec_result.executed_requests
                else:
                    if not exec_result.is_awaiting_human_confirmation:
                        last_message.tool_call_requests = exec_result.executed_requests

                has_next_round = exec_result.has_next_round
                new_messages = exec_result.new_messages
                usage += exec_result.prompt_usage
                messages_buffer.extend(new_messages)
                context.agent_state.update(exec_result.state_updates)

            for new_msg_index in range(1, len(messages_buffer)):
                last_message = messages_buffer[new_msg_index - 1]
                current_message = messages_buffer[new_msg_index]
                if current_message.timestamp <= last_message.timestamp:
                    current_message.timestamp = last_message.timestamp + 1

        result = LLMPromptResult(
            messages=messages_buffer,
            usage=usage,
            agent_state=context.agent_state,
            user_id=context.user_id,
            conversation_id=context.conversation_id,
            runtime_context=context.runtime_context,
        )

        pipe = self.get_pipe()
        if pipe:
            result = await pipe(result, context, logger)

        stop_context_type: type[LLMStopWhenContext] = LLMStopWhenContext[runtime_context_schema]
        if not has_next_round:
            stop_runtime_context = context.runtime_context.model_dump(mode="python")
            stop_result = result.model_copy(update={"runtime_context": stop_runtime_context})
            has_next_round = not (
                await self._stop_when(
                    stop_context_type.model_validate(
                        {
                            **context.model_dump(mode="python"),
                            "runtime_context": stop_runtime_context,
                            "prompt_result": stop_result,
                            "prompt_start_messages": messages,
                        }
                    )
                )
            ).stop

        return LLMPromptRoundResult(
            result=result,
            should_continue=has_next_round,
        )

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
            streaming_callback (Callable | None): Callback for streaming responses.

        Returns:
            list[str]: List of generated responses.
        """

        start_time = get_current_time()
        logger = logger or logging.getLogger("aiteamwork")
        previous_usage = previous_usage or get_agent_usage() or LLMAgentUsage()
        set_agent_usage(previous_usage)

        parsed_messages = [
            message if isinstance(message, LLMMessage) else LLMMessage.from_string(message)
            for message in (messages if isinstance(messages, list) else [messages])
        ]

        LLMMessage.validate_message_history(parsed_messages)

        max_rounds = max_rounds or 5
        context = context or get_llm_context()

        if streaming_callback:
            streaming_callback = validated_sync_async_callback(
                TypeAdapter[None](None),
                ["piece", "message_so_far", "done"],
                "streaming_callback",
                streaming_callback,
            )

        if self.runtime_context_schema and not context:
            raise ValueError("Context is required for this agent.")
        elif not self.runtime_context_schema and not context:
            context = cast(
                LLMInitialContext[RuntimeContextType],
                LLMInitialContext[EmptyRuntimeContext](
                    runtime_context=EmptyRuntimeContext(),
                ),
            )

        if not isinstance(validate_not_none(context), LLMInitialContext):
            raise ValueError("Invalid context.")

        actual_context: LLMContext

        if self.runtime_context_schema:
            if (
                context
                and isinstance(context.runtime_context, self.runtime_context_schema)
                and context.runtime_context.__class__ != self.runtime_context_schema
            ):
                LLMContext[self.runtime_context_schema].model_validate(
                    {
                        **validate_not_none(context).model_dump(),
                        "logger": logger,
                    }
                )
                actual_context = cast(
                    LLMContext[RuntimeContextType],
                    LLMContext[Any].model_validate(
                        {
                            **context.model_dump(),
                            "logger": logger,
                        }
                    ),
                )
                actual_context.runtime_context = context.runtime_context
            else:
                actual_context = cast(
                    LLMContext[RuntimeContextType],
                    LLMContext[self.runtime_context_schema].model_validate(
                        {
                            **validate_not_none(context).model_dump(),
                            "logger": logger,
                        }
                    ),
                )
        elif isinstance(context, LLMContext):
            actual_context = cast(LLMContext[RuntimeContextType], context)
        else:
            context_data = validate_not_none(context).model_dump(mode="python")
            if isinstance(context, LLMInitialContext) and not isinstance(context.runtime_context, EmptyRuntimeContext):
                logger.warning(
                    f"[LLM Agent {self.id}] context provided for prompt, "
                    "but no runtime_context_schema is defined in the agent instantiation, "
                    "this causes undefined behaviour and should be avoided."
                    "Add a runtime_context_schema parameter to the agent creation."
                )
            actual_context = cast(
                LLMContext[RuntimeContextType],
                LLMContext[EmptyRuntimeContext].model_validate(
                    {
                        **context_data,
                        "logger": logger,
                    }
                ),
            )

        extra_tool_defs = [
            tool if isinstance(tool, LLMToolFunctionDefinition) else LLMToolFunctionDefinition(tool)
            for tool in (extra_tools or [])
        ]

        actual_context.current_agent = self.id
        set_llm_context(actual_context)

        await self.validate_configuration(
            actual_context,
            extra_tool_defs,
        )

        round = 1

        trigger_context_type: type[LLMTriggerWhenContext] = LLMTriggerWhenContext[
            self.runtime_context_schema or EmptyRuntimeContext
        ]
        should_continue = (
            await self._trigger_when(
                trigger_context_type.model_validate(
                    {
                        **actual_context.model_dump(mode="python"),
                        "runtime_context": actual_context.runtime_context.model_dump(mode="python"),
                        "messages": parsed_messages,
                    }
                )
            )
        ).trigger
        result: LLMPromptResult | None = None

        while should_continue:
            if round > max_rounds:
                raise ValueError("Max round count reached.")

            round_result = await self.execute_prompt_round(
                messages=parsed_messages,
                context=actual_context,
                logger=logger,
                round=round,
                extra_instructions_after=extra_instructions_after or "",
                extra_instructions_before=extra_instructions_before or "",
                extra_tools=extra_tool_defs,
                streaming_callback=streaming_callback,
                usage=previous_usage,
            )

            if round_result.should_continue:
                logger.info(
                    f"[LLM Agent {self.id}] Finished round {round}, "
                    f"procceeding to next round ({max_rounds - round} rounds remain before max)."
                )
            else:
                logger.info(f"[LLM Agent {self.id}] Finished round {round} - no more rounds needed, done prompt.")

            should_continue = round_result.should_continue
            parsed_messages = round_result.result.messages
            result = round_result.result

            round += 1

        result = validate_not_none(result)
        result.time_taken_ms = floor((get_current_time() - start_time).total_seconds() * 1000)

        return result

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
        loop = loop or asyncio.new_event_loop()
        return loop.run_until_complete(
            self.prompt(
                messages,
                context,
                logger,
                max_rounds,
                extra_instructions_before,
                extra_instructions_after,
                extra_tools,
                previous_usage,
                streaming_callback,
                file_converters,
            )
        )

    async def validate_configuration(
        self,
        context: LLMInitialContext[RuntimeContextType],
        extra_tools: list[LLMToolFunctionDefinition],
    ) -> None:
        """
        Validate the configuration or state of the LLM agent.

        This method must be overridden by subclasses.
        """

        agent_tools_context_type = LLMToolsFactoryContext[self.runtime_context_schema or EmptyRuntimeContext]
        agent_tools_context: LLMToolsFactoryContext = agent_tools_context_type.model_validate(
            {
                **context.model_dump(mode="python"),
                "messages": [],
            }
        )

        agent_tools = await self._tools_as_factory(agent_tools_context)

        all_tools = [
            *agent_tools,
            *extra_tools,
        ]

        tool_names = set[str]()

        for tool in all_tools:
            if tool.name in tool_names:
                raise ValueError(f"Duplicate tool name: {tool.name}")
            tool.validate_configuration(context.runtime_context.model_dump(mode="python"))
            tool_names.add(tool.name)

        self.provider.validate_configuration(context.runtime_context.model_dump(mode="python"), all_tools)

        pipe = self.get_pipe()
        if pipe:
            pipe.validate_configuration(context.runtime_context.model_dump(mode="python"))

        deps = self.get_dependents()
        for dependent in deps:
            if isinstance(dependent, LLMAgentLike):
                await dependent.validate_configuration(cast(Any, context), [])

        LLMArtifactValidator.validate_configuration(
            self.artifact_verification, context.runtime_context.model_dump(mode="python")
        )

    async def get_serialization_models(self, context: LLMContext) -> list[type[BaseModel] | TypeAdapter]:
        result = await super().get_serialization_models(context)

        if self.artifact_schema:
            result.append(self.artifact_schema)

        tools_context_type = LLMToolsFactoryContext[self.runtime_context_schema or EmptyRuntimeContext]
        tools_context: LLMToolsFactoryContext = tools_context_type.model_validate(
            {
                **context.model_dump(mode="python"),
                "messages": [],
            }
        )

        tools = await self._tools_as_factory(
            tools_context.model_validate({**context.model_dump(mode="python"), "messages": []}),
        )

        for tool in tools:
            if tool.input_schema:
                result.append(tool.input_schema)
            if tool.output_schema:
                result.append(tool.output_schema)

        pipe = self.get_pipe()
        if pipe:
            result.extend(await pipe.get_serialization_models(context))

        return result

    def get_dependents(self) -> list[Union["SerializableProducer", type[BaseModel], TypeAdapter]]:
        return self._dependents

    def set_dependents(self, dependents: list[Union["SerializableProducer", type[BaseModel], TypeAdapter]]) -> None:
        self._dependents = dependents

    def get_pipe(self) -> LLMPipe | None:
        return self._pipe

    def set_pipe(self, pipe: LLMPipe) -> None:
        self._pipe = pipe

    def get_runtime_context_schema(self) -> type[BaseModel]:
        return self.runtime_context_schema or EmptyRuntimeContext


__all__ = ["LLMAgent"]
