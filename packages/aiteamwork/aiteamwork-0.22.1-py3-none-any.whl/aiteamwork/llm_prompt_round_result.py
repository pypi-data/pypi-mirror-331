from pydantic import BaseModel

from aiteamwork.llm_prompt_result import LLMPromptResult


class LLMPromptRoundResult(BaseModel):
    result: LLMPromptResult
    should_continue: bool
