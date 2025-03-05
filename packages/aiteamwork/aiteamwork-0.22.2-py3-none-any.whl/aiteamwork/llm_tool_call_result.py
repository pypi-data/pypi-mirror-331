from typing import Any, Self

from pydantic import BaseModel, Field, model_validator

from aiteamwork.llm_tool_call_request import LLMToolCallRequest
from aiteamwork.util.model import get_model_name_from_value


class LLMToolCallResult[ResultType: Any, LLMToolArgsType: BaseModel](BaseModel):
    call_id: str = Field()
    """ID of the call, used to match the request with the result. Automatically filled by the agent."""
    result: ResultType = Field()
    """Result of the tool call, can be any type, must be serializable to JSON."""
    result_type: str | None = Field(
        description="Type of the result. Used to serialize result back into the correct Python type.",
        examples=["MyClass", "Recommendation"],
        default=None,
    )
    """Type of the result. Used to serialize result back into the correct Python type."""
    request: LLMToolCallRequest[LLMToolArgsType] = Field()
    """Request that generated this result."""
    time_taken_ms: int = Field()
    """Time taken to generate the result in milliseconds."""

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        if self.result:
            expected_type = get_model_name_from_value(self.result)
            if expected_type != self.result_type:
                self.result_type = expected_type
        return self

    class Config:
        validate_assignment = True


__all__ = ["LLMToolCallResult"]
