from pydantic import BaseModel

from aiteamwork.llm_context import LLMContext


class LLMInstructionsContext[RuntimeContextType: BaseModel](LLMContext[RuntimeContextType]):
    """Context for the instructions callback in LLMAgent."""

    pass


class LLMInstructionsResult(BaseModel):
    """Result of the instructions callback in LLMAgent."""

    instructions: str
    """Instructions for the LLM agent."""
