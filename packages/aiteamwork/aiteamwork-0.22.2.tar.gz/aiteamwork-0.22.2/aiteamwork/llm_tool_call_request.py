from typing import Self

from pydantic import BaseModel, Field, model_validator

from aiteamwork.util.model import get_model_name_from_value


class LLMToolCallRequest[ToolArgs: BaseModel](BaseModel):
    call_id: str = Field()
    """ID of the call, used to match the request with the result. Filled automatically by the agent."""
    tool_name: str = Field()
    """Name of the tool to call. Must be inside the agent's tool list."""
    tool_args_raw: dict = Field()
    """Arguments to pass to the tool. Must be a single object and serializable to JSON."""
    tool_args: ToolArgs | None = Field(default=None)
    """Arguments parsed into a pydantic model."""
    tool_args_type: str | None = Field(
        description="Type of the tool arguments. Used to serialize tool_args back into the correct Python type.",
        examples=["MyClass", "Recommendation"],
        default=None,
    )
    """Type of the tool arguments. Used to serialize tool_args back into the correct Python type."""

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        if self.tool_args:
            expected_type = get_model_name_from_value(self.tool_args)
            if expected_type != self.tool_args_type:
                self.tool_args_type = expected_type
        return self

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True


__all__ = ["LLMToolCallRequest"]
