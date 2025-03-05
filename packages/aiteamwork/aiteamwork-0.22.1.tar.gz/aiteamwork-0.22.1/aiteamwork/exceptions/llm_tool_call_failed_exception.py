from pydantic import BaseModel

from aiteamwork.llm_context import LLMContext
from aiteamwork.llm_message import LLMMessage
from aiteamwork.llm_tool_call_request import LLMToolCallRequest


class ToolCallFailedException[RuntimeContextType: BaseModel](Exception):
    round: int
    retry_count: int
    messages: list[LLMMessage]
    last_agent_id: str
    agent_context: LLMContext[RuntimeContextType]
    ai_tool_call_request: LLMToolCallRequest
    exception: Exception

    def __init__(
        self,
        exception: Exception,
        round: int,
        retry_count: int,
        last_agent_id: str,
        agent_context: LLMContext[RuntimeContextType],
        ai_tool_call_request: LLMToolCallRequest,
        messages: list[LLMMessage],
        *args,
    ):
        super().__init__(*args)
        self.exception = exception
        self.round = round
        self.retry_count = retry_count
        self.last_agent_id = last_agent_id
        self.agent_context = agent_context
        self.ai_tool_call_request = ai_tool_call_request
        self.messages = messages
