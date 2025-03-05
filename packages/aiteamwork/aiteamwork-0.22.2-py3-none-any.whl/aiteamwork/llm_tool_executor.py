import asyncio
import json
from logging import Logger
from typing import Any, Tuple, cast

from pydantic import BaseModel, Field

from aiteamwork.callbacks.human_in_the_loop import (
    LLMHumanInTheLoopArtifacts,
    LLMHumanInTheLoopContext,
    LLMHumanInTheLoopHumanInputs,
)
from aiteamwork.exceptions.llm_tool_call_failed_exception import ToolCallFailedException
from aiteamwork.llm_agent_usage import LLMAgentUsage
from aiteamwork.llm_context import LLMContext
from aiteamwork.llm_message import LLMMessage
from aiteamwork.llm_provider import LLMProvider, LLMProviderContext
from aiteamwork.llm_role import LLMRole
from aiteamwork.llm_tool_call_request import LLMToolCallRequest
from aiteamwork.llm_tool_call_result import LLMToolCallResult
from aiteamwork.llm_tool_flow_control import LLMToolFlowControl
from aiteamwork.llm_tool_function import LLMToolFunctionDefinition
from aiteamwork.util.date import get_current_time
from aiteamwork.util.validators import validate_and_raise_model, validate_not_none

TOOL_REQUEST_GENERATION_RETRIES = 2


class ErrorReplyException(Exception):
    messages: list[LLMMessage]

    def __init__(self, messages: list[LLMMessage], *args):
        super().__init__(*args)
        self.messages = messages


class LLMToolExecutorResult(BaseModel):
    executed_requests: list[LLMToolCallRequest] = Field()
    new_messages: list[LLMMessage] = Field()
    has_next_round: bool = Field()
    prompt_usage: LLMAgentUsage = Field()
    state_updates: dict = Field()

    @property
    def is_awaiting_human_confirmation(self) -> bool:
        return any(msg.role == LLMRole.AWAITING_HUMAN_ACTION for msg in self.new_messages)


class LLMToolExecutor[RuntimeContextType: BaseModel]:

    _provider: LLMProvider
    _agent_id: str
    _agent_description: str
    _round: int
    _context: LLMContext[RuntimeContextType]
    _tools: list[LLMToolFunctionDefinition]
    _tool_map: dict[str, LLMToolFunctionDefinition]
    _system_instructions: str
    _new_usage: LLMAgentUsage
    _current_usage: LLMAgentUsage
    _logger: Logger

    def __init__(
        self,
        agent_id: str,
        agent_description: str,
        system_instructions: str,
        tools: list[LLMToolFunctionDefinition],
        provider: LLMProvider,
        context: LLMContext[RuntimeContextType],
        round: int,
        current_usage: LLMAgentUsage,
        logger: Logger,
    ) -> None:
        self._agent_id = agent_id
        self._agent_description = agent_description
        self._system_instructions = system_instructions
        self._provider = provider
        self._context = context
        self._round = round
        self._tools = tools
        self._tool_map = {tool.name: tool for tool in tools}
        self._current_usage = current_usage
        self._new_usage = LLMAgentUsage()
        self._logger = logger

    async def _generate_new_tool_request(
        self,
        req: LLMToolCallRequest,
        err: Exception,
        messages: list[LLMMessage],
        retries: int,
    ) -> tuple[LLMToolCallRequest, LLMToolFunctionDefinition, list[LLMMessage]]:
        new_messages = messages.copy()
        altered_last_msg = new_messages[-1].model_copy()
        altered_last_msg.tool_call_requests = []
        new_messages[-1] = altered_last_msg

        if retries == TOOL_REQUEST_GENERATION_RETRIES:
            new_messages.append(
                LLMMessage(
                    content=(
                        f"The requested function {req.tool_name} "
                        f"generated an error, adjust your arguments and try again: \n\n{str(err)}"
                        "\n\n---\nPlease review the arguments, apply the necessary changes and try again, "
                        "do not inform the user about this issue, repeat the last reply you gave it to the user.\n"
                        "Do not call other tools or generate more than 1 tool call request.\n"
                        "Here is the last input you provided to the tool:"
                        f"\n\n{json.dumps(req.tool_args_raw)}"
                    ),
                    role=LLMRole.SYSTEM,
                    authors=[self._agent_id],
                    hidden=True,
                )
            )

        runtime_context = validate_and_raise_model(
            self._provider.get_runtime_context_schema(),
            self._context.runtime_context.model_dump(mode="python"),
            lambda: ValueError("Invalid output schema."),
            lambda e: ValueError(f"Invalid output data: {e}"),
        )

        provider_result = await self._provider.prompt(
            context=LLMProviderContext(
                logger=self._logger,
                system_instructions=self._system_instructions,
                messages=new_messages,
                artifact_schema=None,
                tools=self._tools,
                total_usage=self._new_usage + self._current_usage,
                attempt=self._round,
                runtime_context=runtime_context,
                current_agent=self._agent_id,
                user_id=self._context.user_id,
                conversation_id=self._context.conversation_id,
                assistant_name=self._context.assistant_name,
                agent_state=self._context.agent_state,
            ),
        )

        self._new_usage += provider_result.usage

        new_messages = new_messages + provider_result.new_messages
        last_message = new_messages[-1]

        if (not last_message.tool_call_requests or len(last_message.tool_call_requests) > 1) and retries > 0:
            if len(last_message.tool_call_requests) > 1:
                last_message.tool_call_requests = []
                new_messages.append(
                    LLMMessage(
                        content=("Do not generate more than 1 tool call, please adjust your response and try again."),
                        role=LLMRole.SYSTEM,
                        authors=[self._agent_id],
                        hidden=True,
                    )
                )
            else:
                retries -= 1
                new_messages.append(
                    LLMMessage(
                        content=(
                            "You did not call the tool, let's try again, "
                            "generate another tool call with adjusted arguments. "
                            f"(We will try for more {retries} times)"
                            if retries > 0
                            else ""
                        ),
                        role=LLMRole.SYSTEM,
                        authors=[self._agent_id],
                        hidden=True,
                    )
                )
            return await self._generate_new_tool_request(
                req,
                err,
                new_messages,
                retries,
            )

        last_message.content = ""

        if len(last_message.tool_call_requests) != 1:
            raise err

        tool_call = last_message.tool_call_requests[0]

        return (
            tool_call,
            validate_not_none(
                self._tool_map.get(tool_call.tool_name),
                f"Tool {tool_call.tool_name} does not exist inside the tool list.",
            ),
            new_messages,
        )

    async def execute(
        self,
        call: LLMToolCallRequest,
        human_input: Any | None,
        tool: LLMToolFunctionDefinition,
        messages: list[LLMMessage],
        retry_count: int,
    ) -> Tuple[LLMToolCallResult, LLMToolFlowControl]:
        try:
            self._logger.info(
                f'[LLM Agent {self._agent_id}] Running request tool request for "{call.tool_name}", '
                f"arguments: \n{call.tool_args_raw}"
            )
            self._logger.info(f'[LLM Agent {self._agent_id}] Running request tool request for "{call.tool_name}"...')
            start_time = int(get_current_time().timestamp() * 1000)
            result_data, flow_control, parsed_input = await tool(
                input=call.tool_args_raw, human_input=human_input, context=self._context, messages=messages
            )
            taken_time = int(get_current_time().timestamp() * 1000) - start_time
            call.tool_args = parsed_input

            self._logger.info(
                f'[LLM Agent {self._agent_id}] Tool request for "{call.tool_name}" finished '
                f"successfully in {taken_time} ms. Result: \n{result_data}"
            )

            input_schema = tool.input_schema or BaseModel

            return (
                LLMToolCallResult[tool.output_annotation, input_schema](
                    call_id=call.call_id,
                    result=result_data,
                    request=call,
                    time_taken_ms=taken_time,
                ),
                flow_control,
            )
        except Exception as e:
            raise ToolCallFailedException(
                exception=e,
                round=self._round,
                retry_count=retry_count,
                messages=messages,
                last_agent_id=self._agent_id,
                agent_context=self._context,
                ai_tool_call_request=call,
            ) from e

    async def execute_with_retry_policy(
        self,
        call: LLMToolCallRequest,
        human_input: Any | None,
        tool: LLMToolFunctionDefinition,
        messages: list[LLMMessage],
        retry_count: int = 0,
    ) -> Tuple[LLMToolCallResult, LLMToolFlowControl]:
        try:
            return await self.execute(call, human_input, tool, messages, retry_count)
        except ToolCallFailedException as e:
            self._logger.info(
                f'[LLM Agent {self._agent_id}] Tool request for "{call.tool_name}" failed: '
                f"({len(tool.retry_policy.retries) - retry_count + 1} retries left).\n"
                "Error: \n"
                f"{e.exception}"
            )
            if retry_count < len(tool.retry_policy.retries):
                self._logger.info(
                    f'[LLM Agent {self._agent_id}] Retrying tool request for "{call.tool_name}" '
                    f"after {tool.retry_policy.retries[retry_count]} ms..."
                )
                await asyncio.sleep(tool.retry_policy.retries[retry_count] / 1000)
                await tool.retry_policy.run_on_failure(e)

                retry_count += 1

                try:
                    call, tool, new_messages = await self._generate_new_tool_request(
                        e.ai_tool_call_request,
                        e.exception,
                        e.messages,
                        TOOL_REQUEST_GENERATION_RETRIES,
                    )

                    return await self.execute_with_retry_policy(
                        e.ai_tool_call_request,
                        human_input,
                        tool,
                        new_messages,
                        retry_count + 1,
                    )
                except ToolCallFailedException:
                    # failed to generate new tool call or execute, re-raise the original exception
                    pass

            if tool.retry_policy.run_reply_on_failure:
                self._logger.info(
                    f'[LLM Agent {self._agent_id}] Out of retries for "{call.tool_name}".\n'
                    f"Replying back with failure messages to the user."
                )
                raise ErrorReplyException(messages=await tool.retry_policy.run_reply_on_failure(e))

            self._logger.info(
                f'[LLM Agent {self._agent_id}] Out of retries for "{call.tool_name}".\n'
                f"No reply policy defined, erroring out."
            )

            raise e

    async def _handle_tool_calls(
        self,
        calls: list[tuple[LLMToolCallRequest, LLMToolFunctionDefinition]],
        messages: list[LLMMessage],
    ) -> LLMToolExecutorResult:
        try:
            last_message = validate_not_none(messages[-1])
            msg_with_calls = last_message
            is_human_confirmation = last_message.role == LLMRole.HUMAN_CONFIRMATION
            human_input = None

            if is_human_confirmation:
                msg_with_calls = validate_not_none(messages[-2])
                human_input = last_message.artifact

            new_messages: list[LLMMessage] = []
            state_changes: dict = {}
            has_next_round = False
            call_results = await asyncio.gather(
                *[
                    self.execute_with_retry_policy(
                        call,
                        None if not human_input else cast(LLMHumanInTheLoopHumanInputs, human_input).inputs[index],
                        tool,
                        messages,
                    )
                    for index, (call, tool) in enumerate(calls)
                ]
            )
            for tool_result, _ in call_results:
                new_messages.append(
                    LLMMessage(
                        content="",
                        role=LLMRole.TOOL,
                        authors=[self._agent_id],
                        provider_platform=msg_with_calls.provider_platform,
                        tool_call_result=tool_result,
                        hidden=True,
                        timestamp=msg_with_calls.timestamp + 0.001,
                    )
                )
            for _, flow_control in call_results:
                state_changes.update(flow_control.state_changes)
                new_messages.extend(flow_control.new_messages)
                has_next_round = has_next_round or flow_control.should_reprompt

            # Make sure all tool messages are at the beginning of the list
            # Most providers error out when there tool requests followed by non-tool messages
            new_messages = [msg for msg in new_messages if msg.role == LLMRole.TOOL] + [
                msg for msg in new_messages if msg.role != LLMRole.TOOL
            ]

            return LLMToolExecutorResult(
                new_messages=new_messages,
                has_next_round=has_next_round,
                executed_requests=[result.request for result, _ in call_results],
                prompt_usage=self._new_usage,
                state_updates=state_changes,
            )
        except ErrorReplyException as e:
            return LLMToolExecutorResult(
                new_messages=e.messages,
                has_next_round=False,
                executed_requests=[],
                prompt_usage=self._new_usage,
                state_updates={},
            )

    async def run_tools(
        self,
        messages: list[LLMMessage],
    ) -> LLMToolExecutorResult:
        last_message = validate_not_none(messages[-1])
        msg_with_calls = last_message
        is_human_confirmation = last_message.role == LLMRole.HUMAN_CONFIRMATION

        if is_human_confirmation:
            msg_with_calls = validate_not_none(messages[-2])

        calls = msg_with_calls.tool_call_requests

        self._logger.info(f"[LLM Agent {self._agent_id}] Got {len(calls)} tool requests...")

        calls_with_tools: list[tuple[LLMToolCallRequest, LLMToolFunctionDefinition]] = [
            (
                call,
                validate_not_none(
                    self._tool_map.get(call.tool_name),
                    f"Tool {call.tool_name} does not exist inside the tool list.",
                ),
            )  # todo: add custom error
            for call in calls
        ]

        human_in_the_loop_calls = (
            [] if is_human_confirmation else [(call, tool) for call, tool in calls_with_tools if tool.human_in_the_loop]
        )

        if human_in_the_loop_calls:
            artifacts: list = []
            for call, tool in human_in_the_loop_calls:
                call.tool_args = tool.get_parsed_input(call.tool_args_raw)
                human_in_the_loop = validate_not_none(tool.human_in_the_loop)

                runtime_context_type = human_in_the_loop.runtime_schema

                runtime_context = validate_and_raise_model(
                    runtime_context_type,
                    self._context.runtime_context.model_dump(mode="python"),
                    lambda: ValueError("Invalid output schema."),
                    lambda e: ValueError(f"Invalid output data: {e}"),
                )

                context = validate_and_raise_model(
                    LLMHumanInTheLoopContext[BaseModel, runtime_context_type],
                    {
                        **self._context.model_dump(mode="python"),
                        "runtime_context": runtime_context,
                        "tool_args": call.tool_args,
                        "tool_args_raw": call.tool_args_raw,
                    },
                    lambda: ValueError("Invalid output schema."),
                    lambda e: ValueError(f"Invalid output data: {e}"),
                )

                artifact_result = await human_in_the_loop.get_confirmation_artifact(context)
                artifacts.append(artifact_result.artifact or None)

            return LLMToolExecutorResult(
                new_messages=[
                    LLMMessage(
                        role=LLMRole.AWAITING_HUMAN_ACTION,
                        authors=[self._agent_id],
                        tool_call_requests=calls,
                        artifact=LLMHumanInTheLoopArtifacts(artifacts=artifacts),
                    )
                ],
                has_next_round=False,
                executed_requests=[],
                prompt_usage=self._new_usage,
                state_updates={},
            )

        r = await self._handle_tool_calls(
            calls_with_tools,
            messages,
        )

        self._logger.info(f"[LLM Agent {self._agent_id}] Finished all tool requests ({len(calls)} calls)...")

        return r
