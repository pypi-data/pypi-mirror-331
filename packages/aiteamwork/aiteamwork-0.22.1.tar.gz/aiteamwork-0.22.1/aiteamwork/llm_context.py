from logging import Logger
from typing import cast, final

from pydantic import BaseModel, Field, TypeAdapter, create_model


@final
class EmptyRuntimeContext(BaseModel):
    pass


class LLMInitialContext[RuntimeContextType: BaseModel](BaseModel):
    """Initial context data for the LLM."""

    user_id: str | None = Field(default=None)
    """ID of the user that owns the conversation with the assistant.
    Not used by all the framework, helper property"""
    conversation_id: str | None = Field(default=None)
    """Conversation ID. Not used by all the framework, helper property"""
    assistant_name: str | None = Field(default=None)
    """Name of the assistant. Used for logging and """
    runtime_context: RuntimeContextType = Field()
    """Runtime context of the assistant. Used to pass tools and efemeral data or objects to tools or agent callbacks."""
    agent_state: dict = Field(default_factory=dict)
    """State of the agent. Used to store the state of the agent between tools, agents and callbacks."""

    class Config:
        arbitrary_types_allowed = True


class LLMContext[RuntimeContextType: BaseModel](LLMInitialContext[RuntimeContextType]):
    current_agent: str | None = Field(default=None)
    """ID of the current agent that is processing the message."""

    logger: Logger = Field()
    """Logger for the current agent."""


def combine_runtime_contexts[
    RuntimeContextType: BaseModel
](agent_runtime_context: RuntimeContextType, *other_contexts: BaseModel) -> RuntimeContextType:
    validated_contexts = TypeAdapter[list[BaseModel]](list[BaseModel]).validate_python(
        [agent_runtime_context, *other_contexts]
    )

    validated_contexts.reverse()

    runtime_schemas: set[type[BaseModel]] = set()

    for context in validated_contexts:
        runtime_schemas.add(context.__class__)

    combined_model = combine_runtime_context_schemas(list(runtime_schemas))

    input_dict: dict = {}
    for context in validated_contexts:
        input_dict = {**input_dict, **context.model_dump(mode="python")}

    return cast(RuntimeContextType, combined_model.model_validate(input_dict))


def combine_runtime_context_schemas(
    schemas: list[type[BaseModel]],
) -> type[BaseModel]:
    all_schemas_are_empty = all(issubclass(schema, EmptyRuntimeContext) for schema in schemas)
    if all_schemas_are_empty:
        return EmptyRuntimeContext
    as_tuple = tuple(schemas)
    return create_model("CombinedRuntimeContextModel", __base__=as_tuple)


__all__ = [
    "EmptyRuntimeContext",
    "LLMInitialContext",
    "LLMContext",
    "combine_runtime_contexts",
    "combine_runtime_context_schemas",
]
