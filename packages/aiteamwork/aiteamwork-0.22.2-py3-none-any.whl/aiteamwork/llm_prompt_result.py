from pydantic import BaseModel, Field, TypeAdapter

from aiteamwork.llm_agent_usage import LLMAgentUsage
from aiteamwork.llm_message import LLMMessage
from aiteamwork.llm_tool_call_request import LLMToolCallRequest


class LLMPromptResult[RuntimeContextType](BaseModel):
    messages: list[LLMMessage] = Field()
    usage: LLMAgentUsage = Field()
    agent_state: dict = Field()
    runtime_context: RuntimeContextType = Field()
    user_id: str | None = Field(default=None)
    conversation_id: str | None = Field(default=None)
    time_taken_ms: int = Field(default=0)

    class Config:
        arbitrary_types_allowed = True

    def last_message(self) -> LLMMessage:
        if len(self.messages) == 0:
            raise ValueError("No messages in prompt result.")
        return self.messages[-1]

    def last_message_content(self) -> str:
        last_msg = self.last_message()
        return last_msg.content

    def last_artifact[
        ExpectedType: BaseModel,
    ](self, expected_type: type[ExpectedType]) -> ExpectedType:
        msg = self.last_message()
        if msg is None:
            raise ValueError("No messages in prompt result.")
        artifact = msg.artifact
        if artifact is None:
            raise ValueError("No artifact in last message.")
        return TypeAdapter(expected_type).validate_python(artifact)

    def human_action_requests(self) -> list[tuple[LLMToolCallRequest, BaseModel | None]]:
        msg = self.last_message()
        if msg is None:
            return []
        return msg.get_human_action_requests()


__all__ = ["LLMPromptResult"]
