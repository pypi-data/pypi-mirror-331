from pydantic import BaseModel, Field, computed_field


class LLMAgentUsage(BaseModel):
    """
    Represents the usage statistics of an LLM agent.

    Attributes:
        completion_tokens (int): Number of tokens used for completion.
        prompt_tokens (int): Number of tokens used for prompt.

    Example:
        usage = LLMAgentUsage(
            completion_tokens=150,
            prompt_tokens=100,
        )
    """

    completion_tokens: int = Field(default=0, ge=0, examples=[123])
    """
    Number of tokens used for completion.
    """
    prompt_tokens: int = Field(default=0, ge=0, examples=[123])
    """
    Number of tokens used for prompt.
    """

    @computed_field  # type: ignore[misc]
    @property
    def total_tokens(self) -> int:
        """
        Total number of tokens used.
        """
        return self.completion_tokens + self.prompt_tokens

    def __iadd__(self, other: "LLMAgentUsage") -> "LLMAgentUsage":
        if not isinstance(other, LLMAgentUsage):
            return NotImplemented
        self.completion_tokens += other.completion_tokens
        self.prompt_tokens += other.prompt_tokens
        return self

    def __add__(self, other: "LLMAgentUsage") -> "LLMAgentUsage":
        if not isinstance(other, LLMAgentUsage):
            return NotImplemented
        return LLMAgentUsage(
            completion_tokens=self.completion_tokens + other.completion_tokens,
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
        )


__all__ = ["LLMAgentUsage"]
