from pydantic import BaseModel, Field

from aiteamwork.llm_context import LLMContext
from aiteamwork.llm_message import LLMMessage


class LLMTriggerWhenContext[RuntimeContextType: BaseModel](LLMContext[RuntimeContextType]):
    """Context for the LLMAgent trigger_when callback.
    Use this data to define when the LLM should trigger a prompt round."""

    messages: list[LLMMessage] = Field(
        description=(
            "The complete list of messages in the conversation. "
            "Use this to define if the LLM should trigger a prompt round or not."
        ),
    )
    """The complete list of messages in the conversation.
    Use this to define if the LLM should trigger a prompt round or not."""


class LLMTriggerWhenResult(BaseModel):
    """Result of the LLMAgent trigger_when callback."""

    trigger: bool = Field(description="Whether the LLM should be trigger a prompt round or not.")
    """Whether the LLM should be trigger a prompt round or not."""
