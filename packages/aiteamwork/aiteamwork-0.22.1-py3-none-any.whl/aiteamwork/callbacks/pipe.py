from pydantic import BaseModel, Field

from aiteamwork.llm_context import LLMContext
from aiteamwork.llm_prompt_result import LLMPromptResult


class LLMPipeContext[RuntimeContextType: BaseModel](LLMContext[RuntimeContextType]):
    prompt_result: LLMPromptResult[RuntimeContextType]
    """Prompt result of the current agent."""


class LLMPipeResult(BaseModel):
    prompt_result: LLMPromptResult = Field(description="New prompt result of the current agent.")
    """New prompt result of the current agent."""

    class Config:
        arbitrary_types_allowed = True
