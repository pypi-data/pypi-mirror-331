from pydantic import BaseModel, Field, field_validator

from aiteamwork.llm_context import LLMContext
from aiteamwork.llm_message import LLMMessage
from aiteamwork.llm_role import LLMRole


class LLMMemoryContext[RuntimeContextType: BaseModel](LLMContext[RuntimeContextType]):
    """Context of the LLM Memory callback. Use to add RAG and dynamic memories to the LLM."""

    last_user_message: LLMMessage = Field(description="The last user message in the conversation.")
    """The last user message in the conversation."""

    messages: list[LLMMessage] = Field(
        description="The complete list of messages in the conversation.", default_factory=list
    )
    """The complete list of messages in the conversation."""


class LLMMemoryResult(BaseModel):
    """Result of the LLM Memory callback."""

    memories: list[LLMMessage] = Field(
        description="List of memories to be added to the LLM. Must have role of LLMRole.MEMORY.", default_factory=list
    )
    """List of memories to be added to the LLM. Must have role of LLMRole.MEMORY."""

    @field_validator("memories", mode="after")
    @classmethod
    def validate_memories(cls, memories: list[LLMMessage]) -> list[LLMMessage]:
        allowed_roles = {LLMRole.MEMORY, LLMRole.INFO, LLMRole.DEBUG}
        for message in memories:
            if message.role not in allowed_roles:
                raise ValueError("Memory messages must have a role of MEMORY, INFO, or DEBUG.")

        return memories
