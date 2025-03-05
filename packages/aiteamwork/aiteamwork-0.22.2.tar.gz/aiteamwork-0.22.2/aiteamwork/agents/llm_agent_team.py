import asyncio
import logging
from math import floor
from typing import Any, Coroutine, Self, Callable, cast
from logging import Logger
from pydantic import BaseModel, Field, PrivateAttr, model_validator, TypeAdapter
from aiteamwork.agents.llm_agent import LLMMessage
from aiteamwork.contextvar import get_agent_usage, get_llm_context, set_agent_usage, set_llm_context
from aiteamwork.llm_agent_like import LLMAgentLike
from aiteamwork.llm_agent_usage import LLMAgentUsage
from aiteamwork.llm_file_converter import LLMFileConverter
from aiteamwork.llm_pipeable import LLMPipeable
from aiteamwork.llm_prompt_round_result import LLMPromptRoundResult
from aiteamwork.llm_tool_function import LLMToolFunctionDefinition
from aiteamwork.serializable_producer import SerializableProducer
from aiteamwork.tools.agent_team.switch_agent import get_switch_agent_tool
from aiteamwork.util.date import get_current_time
from aiteamwork.util.validators import SyncOrAsyncCallback, validate_not_none, validated_sync_async_callback
from aiteamwork.llm_context import EmptyRuntimeContext, LLMInitialContext, LLMContext, combine_runtime_context_schemas
from aiteamwork.llm_prompt_result import LLMPromptResult
from aiteamwork.llm_pipe import LLMPipe
from aiteamwork.llm_role import LLMRole


class LLMAgentTeam[
    RuntimeContextType: BaseModel,
](LLMAgentLike[RuntimeContextType], BaseModel, LLMPipeable):
    id: str = Field(default="unknown_agent")

    description: str = Field(min_length=8, max_length=256, default="Unknown agent.")

    agents: list[LLMAgentLike] = Field(min_length=1)

    default_agent: str = Field()

    class Config:
        arbitrary_types_allowed = True

    _switch_tool: LLMToolFunctionDefinition = PrivateAttr()
    _pipe: LLMPipe | None = PrivateAttr(default=None)
    _dependents: list[LLMAgentLike | SerializableProducer | type[BaseModel] | TypeAdapter] = PrivateAttr()
    _combined_runtime_schema: type[BaseModel] | None = PrivateAttr(default=None)

    def get_id(self) -> str:
        return self.id

    def get_description(self) -> str:
        return self.description

    def get_agent_map(self) -> dict[str, LLMAgentLike]:
        return {agent.get_id(): agent for agent in self.agents}

    @model_validator(mode="after")
    def _validate_agents(self) -> Self:
        agent_ids = [agent.get_id() for agent in self.agents]
        repeated_ids = [id for id in agent_ids if agent_ids.count(id) > 1]
        if repeated_ids:
            raise ValueError(f"agent ids must be unique, but {repeated_ids} are repeated")
        if self.default_agent not in agent_ids:
            raise ValueError("default_agent must be one of the agent ids")
        if None in agent_ids:
            raise ValueError("agent ids must not be None")

        self._switch_tool = LLMToolFunctionDefinition(tool=get_switch_agent_tool(lambda: self.get_agent_map()))

        combined_runtime_schema = combine_runtime_context_schemas(
            [agent.get_runtime_context_schema() for agent in self.agents]
        )
        if combined_runtime_schema != EmptyRuntimeContext:
            self._combined_runtime_schema = combined_runtime_schema

        return self

    def _get_agent_team_instructions(
        self,
        agent: LLMAgentLike,
        other_agents: list[LLMAgentLike],
        llm_assistant_name: str,
    ) -> str:
        other_agents_str = "\n".join(
            [
                (f'- Name: "{agent.get_id()}"\n' f'  Description: "{agent.get_description()}"\n')
                for agent in other_agents
            ]
        )

        return (
            f'You are part of a collaborative team of agents, and your name is: "{agent.get_id()}".\n'
            f'If the user asks for your name, please respond with "{llm_assistant_name}" to maintain consistency.\n'
            f'Your role is: "{agent.get_description()}".\n'
            f"It is important that you answer queries specifically related to your role.\n"
            "If the user's request answer is already in the conversation, you are encouraged to provide it.\n"
            "If the user's request answer is in an article or reference mentioned in the coversation, "
            "you are also encouraged to provide it.\n"
            "If the user's request falls outside your area of expertise and you don't have an answer, "
            "feel free to ask follow-up questions to clarify what they are looking for. "
            "If you're still unable to assist, you may switch the conversation to another agent "
            f'by using the "{self._switch_tool.name}" tool.\n'
            "Do NOT attempt to answer questions meant for other agents. Here is a list of your teammates:\n\n"
            f"{other_agents_str}\n"
            "If the conversation was just passed to you from another agent, do not pass it before answering the user, "
            "answer first. "
            "Pretend the whole team is a single entity and you are the one talking to the user. "
            "Do not mention the other agents or the fact that the conversation was passed to you."
        )

    def _get_current_agent(self, messages: list[LLMMessage]) -> LLMAgentLike[RuntimeContextType]:
        non_user_messages = [message for message in messages if message.role != LLMRole.USER]

        agent_map = self.get_agent_map()

        if not non_user_messages:
            return agent_map[self.default_agent]

        message_index = len(non_user_messages) - 1
        last_agent_id = ""
        while message_index >= 0:
            message = non_user_messages[message_index]
            authors = [author for author in message.authors if author in agent_map]
            if authors:
                last_agent_id = authors[0]
                break
            message_index -= 1
        if not last_agent_id:
            return agent_map[self.default_agent]

        if not agent_map.get(last_agent_id):
            raise ValueError(f"Agent not found: {last_agent_id}")

        return agent_map[last_agent_id]

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
        last_agent = self._get_current_agent(messages)

        team_instructions = self._get_agent_team_instructions(
            last_agent, self.agents, context.assistant_name or "Assistant"
        )

        extra_instructions_before = (team_instructions + "\n\n\n" + (extra_instructions_before or "")).strip()

        context.current_agent = last_agent.get_id()

        round_result = await last_agent.execute_prompt_round(
            messages=messages,
            context=context,
            logger=logger,
            round=round,
            extra_instructions_after=extra_instructions_after or "",
            extra_instructions_before=extra_instructions_before,
            extra_tools=[self._switch_tool, *extra_tools],
            streaming_callback=streaming_callback,
            usage=usage,
        )

        result = round_result.result
        non_info_msgs = [msg for msg in result.messages if msg.role not in {LLMRole.INFO, LLMRole.DEBUG}]
        last_message = non_info_msgs[-1]

        if last_message.tool_call_result and last_message.tool_call_result.request.tool_name == self._switch_tool.name:
            originating_message = non_info_msgs[-2]
            time_string = get_current_time().strftime("%Y-%m-%d, %I:%M %p")
            new_agent = self.get_agent_map()[last_message.tool_call_result.result["new_agent"]]
            authors = [
                new_agent.get_id(),
                last_agent.get_id(),
                self.id,
            ]

            result.messages.append(
                LLMMessage(
                    content=(
                        f"It's {time_string}, " f'the conversation has been passed from agent "{last_agent.get_id()}"'
                    ),
                    role=LLMRole.SYSTEM,
                    authors=authors,
                    hidden=True,
                    purpose="agent_switch",
                    timestamp=last_message.timestamp + 1,
                )
            )

            last_message.content = f'Conversation passed from agent "{last_agent.get_id()}"'

            last_message.authors = authors
            originating_message.authors = authors

            logger.info(f'[LLM Agent {last_agent.get_id()}] Passed conversation to agent "{new_agent.get_id()}"')

        pipe = self.get_pipe()
        if pipe:
            result = await pipe(result, context, logger)
            round_result.result = result

        return round_result

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

        if self._combined_runtime_schema and not context:
            raise ValueError("Context is required for this agent.")
        elif not self._combined_runtime_schema and not context:
            context = cast(
                LLMInitialContext[RuntimeContextType],
                LLMInitialContext[EmptyRuntimeContext](
                    runtime_context=EmptyRuntimeContext(),
                ),
            )

        if not isinstance(validate_not_none(context), LLMInitialContext):
            raise ValueError("Invalid context.")

        actual_context: LLMContext

        if self._combined_runtime_schema:
            if (
                context
                and isinstance(context.runtime_context, self._combined_runtime_schema)
                and context.runtime_context.__class__ != self._combined_runtime_schema
            ):
                LLMContext[self._combined_runtime_schema].model_validate(
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
                    LLMContext[self._combined_runtime_schema].model_validate(
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

        extra_tool_defs.append(self._switch_tool)

        actual_context.current_agent = self.id
        set_llm_context(actual_context)

        await self.validate_configuration(
            actual_context,
            extra_tool_defs,
        )

        round = 1
        should_continue = True
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
        await asyncio.gather(*[agent.validate_configuration(context, extra_tools) for agent in self.agents])

        if self._pipe:
            self._pipe.validate_configuration(context.runtime_context.model_dump(mode="python"))

    async def get_serialization_models(self, context: LLMContext) -> list[type[BaseModel] | TypeAdapter]:
        result: list[type[BaseModel] | TypeAdapter] = []

        for dependent in self._dependents:
            if isinstance(dependent, SerializableProducer):
                result.extend(await dependent.get_serialization_models(context))
            else:
                result.append(dependent)

        if self._pipe:
            result.extend(await self._pipe.get_serialization_models(context))

        return result

    def get_dependents(self) -> list[SerializableProducer | type[BaseModel] | TypeAdapter]:
        return self._dependents

    def set_dependents(self, dependents: list[SerializableProducer | type[BaseModel] | TypeAdapter]) -> None:
        self._dependents = dependents

    def get_pipe(self) -> LLMPipe | None:
        return self._pipe

    def set_pipe(self, pipe: LLMPipe) -> None:
        self._pipe = pipe

    def get_runtime_context_schema(self) -> type[BaseModel]:
        return self._combined_runtime_schema or EmptyRuntimeContext
