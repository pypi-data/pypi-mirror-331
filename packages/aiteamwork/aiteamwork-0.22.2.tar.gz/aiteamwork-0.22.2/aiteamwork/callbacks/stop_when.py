from pydantic import BaseModel, Field

from aiteamwork.llm_agent_like import LLMPromptResult
from aiteamwork.llm_context import LLMContext
from aiteamwork.llm_message import LLMMessage


class LLMStopWhenContext[RuntimeContextType: BaseModel](LLMContext[RuntimeContextType]):
    """Context for the LLMAgent stop_when callback.
    Use this data to define when the LLM should stop doing prompt rounds."""

    prompt_result: LLMPromptResult[RuntimeContextType] = Field(description="The result of the prompt round.")
    """The result of the prompt round. Use this to define if the LLM should trigger a prompt round or not"""

    prompt_start_messages: list[LLMMessage] = Field(
        description=(
            "The messages that were passed at the start of the conversation. "
            "You can use this to check for differences between the conversation start and result."
        ),
    )
    """The messages that were passed at the start of the conversation.
    You can use this to check for differences between the conversation start and result."""


class LLMStopWhenResult(BaseModel):
    """Result of the LLMAgent stop_when callback."""

    stop: bool = Field(description="Whether the LLM should stop prompting or not.")
    """Whether the LLM should stop prompting or not."""
