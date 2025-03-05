from pydantic import BaseModel, Field

from aiteamwork.llm_agent_usage import LLMAgentUsage
from aiteamwork.llm_message import LLMMessage


class LLMProviderResult(BaseModel):
    """
    Represents the result from an LLM provider.

    Attributes:
      new_messages (list[LLMMessage]): A list of new messages from the LLM provider.
      usage (LLMAgentUsage): Usage information from the LLM provider.
    See Also:
      LLMProvider: The provider that generates these results.
    """

    new_messages: list[LLMMessage] = Field(description="Usage information")
    usage: LLMAgentUsage = Field(description="Usage information")


__all__ = ["LLMProviderResult"]
