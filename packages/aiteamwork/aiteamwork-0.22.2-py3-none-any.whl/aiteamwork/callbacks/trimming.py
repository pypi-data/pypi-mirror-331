from pydantic import BaseModel, Field

from aiteamwork.llm_context import LLMContext
from aiteamwork.llm_message import LLMMessage


class LLMTrimmingContext[RuntimeContextType: BaseModel](LLMContext[RuntimeContextType]):
    """Context of the LLM Conversation Trimmer."""

    messages: list[LLMMessage] = Field(
        description="The complete list of messages in the conversation.", default_factory=list
    )
    """The complete list of messages in the conversation."""


class LLMTrimmingResult(BaseModel):
    """Result of the LLM Conversation Trimmer."""

    messages: list[LLMMessage] = Field(
        description="List of messages to be kept in the conversation.", default_factory=list
    )
    """List of messages to be kept in the conversation."""
