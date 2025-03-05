import re
from enum import Enum
from typing import Any, Self, cast

from pydantic import BaseModel, Field, model_validator

from aiteamwork.callbacks.human_in_the_loop import LLMHumanInTheLoopArtifacts, LLMHumanInTheLoopHumanInputs
from aiteamwork.llm_file import LLMFile
from aiteamwork.llm_role import LLMRole
from aiteamwork.llm_tool_call_request import LLMToolCallRequest
from aiteamwork.llm_tool_call_result import LLMToolCallResult
from aiteamwork.util.date import get_current_time
from aiteamwork.util.model import get_model_name_from_value
from aiteamwork.util.service_version import get_current_service_version


class LLMMessagePriority(str, Enum):
    HIGH = "high"
    DEFAULT = "default"


class LLMMessage(BaseModel):
    """
    Model representing a message with metadata.

    Attributes:
        role (LLMRole): The role of the message.
        content (str): The content of the message.
        content_metadata (dict): Metadata associated with the content.
        purpose (str | None): The purpose of the message.
        service_version (str): The version of the service that generated the message.
        authors (list[str]): A set containing the agent IDs or user ID that generated the message.
        artifact (Any | None): The artifact that the message is associated with.
        id (str | None): The unique identifier of the message.
        provider_role (str | None): The role of the provider that generated the message.
        provider_platform (str | None): The platform that generated the message.
        tool_call_requests (list[LLMToolCallRequest]): The tool call requests that generated the message.
        tool_call_resuls (LLMToolCallResult | None): The tool call results that generated the message.
        files (list[LLMFile]): The files associated with the message.
        timestamp (str): The timestamp of the message.
        hidden (bool): Whether the message is hidden.
        priority (LLMMessagePriority): Priority of the message, it helps the provider decide how the message internal \
            role should be determined.
    """

    role: LLMRole = Field(
        default=LLMRole.USER,
        description="The role of the message.",
        examples=["LLMRole.USER", "LLMRole.AGENT", "LLMRole.SYSTEM"],
    )
    """The role of the message."""

    content: str = Field(description="The content of the message.", default="")
    """The content of the message."""

    content_metadata: dict = Field(
        description="Metadata associated with the content.",
        examples=[{"key": "value"}],
        default_factory=dict,
    )
    """Metadata associated with the content."""

    purpose: str | None = Field(
        description="The purpose of the message.",
        examples=["completion", "prompt", "system"],
        default=None,
    )
    """The purpose of the message."""

    service_version: str | None = Field(
        description="The version of the service that generated the message.",
        examples=["1.0.0"],
        default_factory=get_current_service_version,
    )
    """The version of the service that generated the message."""

    authors: list[str] = Field(
        description="A list containing the agent IDs or user ID that generated the message, in order of action.",
        examples=[["composed_agent_1", "augmentation_agent_1", "dumb_agent_1"], ["user_1"]],
        default_factory=list,
    )
    """A set containing the agent IDs or user ID that generated the message."""

    artifact: Any = Field(
        description="The artifact that the message is associated with.",
        examples=["conversation", "tool_call"],
        default=None,
    )
    """The artifact that the message is associated with."""

    artifact_type: str | None = Field(
        description=(
            "The type of the artifact that the message is associated with. "
            "This is used to serialize the artifact back into the correct Python type."
        ),
        examples=["MyCustomClass", "Recommendation"],
        default=None,
    )
    """The type of the artifact that the message is associated with.
    This is used to serialize the artifact back into the correct Python type."""

    id: str | None = Field(
        description="The unique identifier of the message.",
        examples=["1234-5678-9012-3456"],
        default=None,
    )
    """The unique identifier of the message."""

    provider_role: str | None = Field(
        description="The role of the provider that generated the message.", examples=["llm", "tool"], default=None
    )
    """The role of the provider that generated the message."""

    provider_platform: str | None = Field(
        description="The platform that generated the message.",
        examples=["openai", "gpt-3"],
        default=None,
    )
    """The platform that generated the message."""

    tool_call_requests: list[LLMToolCallRequest] = Field(
        description="The tool call requests that generated the message.",
        examples=[{"key": "value"}],
        default_factory=list,
    )
    """The tool call requests that generated the message."""

    tool_call_result: LLMToolCallResult | None = Field(
        description="The tool call results that generated the message.",
        default=None,
    )
    """The tool call results that generated the message."""

    files: list[LLMFile] = Field(
        description="The files associated with the message.",
        examples=["file1.txt", "file2.txt"],
        default_factory=list,
    )
    """The files associated with the message."""

    timestamp: float = Field(
        description="The timestamp of the message.",
        examples=["2022-01-01T00:00:00Z"],
        default_factory=lambda: get_current_time().timestamp(),
    )
    """The timestamp of the message."""

    hidden: bool = Field(
        description="Whether the message is hidden.",
        examples=[True, False],
        default=False,
    )
    """Whether the message is hidden."""

    priority: LLMMessagePriority = Field(
        description=(
            "Priority of the message, "
            "it helps the provider decide how the message internal role should be determined."
        ),
        examples=["LLMMessagePriority.HIGH", "LLMMessagePriority.DEFAULT"],
        default=LLMMessagePriority.DEFAULT,
    )
    """Priority of the message, it helps the provider decide how the message internal role should be determined."""

    @staticmethod
    def from_string(message: str) -> "LLMMessage":
        """
        Create an LLMMessage from a string.
        """

        regex_with_username = r"^(?P<role>[A-Z]+)(?: \((?P<username>.+)\)):(?P<content>.+)$"
        regex_with_role = r"^(?P<role>[A-Z]+):(?P<content>.+)$"

        match = re.match(regex_with_username, message, re.IGNORECASE)
        if match:
            role = match.group("role")
            username = match.group("username")
            content = match.group("content").strip()
            authors = ["unknown"]
            if username:
                authors = username.strip().split(",")
            return LLMMessage.model_validate(
                {
                    "role": role,
                    "content": content,
                    "authors": authors,
                }
            )
        match = re.match(regex_with_role, message, re.IGNORECASE)
        if match:
            role = match.group("role")
            content = match.group("content").strip()
            return LLMMessage.model_validate(
                {
                    "role": role,
                    "content": content,
                }
            )

        return LLMMessage.model_validate(
            {
                "role": LLMRole.USER,
                "content": message,
            }
        )

    def is_user_message_for_agent(self, agent_id: str) -> bool:
        return (self.role == LLMRole.USER) or (self.role == LLMRole.AGENT and agent_id not in self.authors)

    def is_agent_message_for_agent(self, agent_id: str) -> bool:
        return self.role == LLMRole.AGENT and (len(self.authors) == 0 or agent_id in self.authors)

    def get_human_action_requests(self) -> list[tuple[LLMToolCallRequest, BaseModel | None]]:
        if self.role != LLMRole.AWAITING_HUMAN_ACTION:
            return []

        return [
            (tool_call_request, cast(LLMHumanInTheLoopArtifacts, self.artifact).artifacts[index])
            for index, tool_call_request in enumerate(self.tool_call_requests)
        ]

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        if self.artifact:
            expected_artifact_type = get_model_name_from_value(self.artifact)
            if self.artifact_type != expected_artifact_type:
                self.artifact_type = expected_artifact_type

        if self.role == LLMRole.AWAITING_HUMAN_ACTION:
            if self.artifact is None:
                raise ValueError(
                    "Artifact must be provided for messages of role AWAITING_HUMAN_ACTION. "
                    "Must be of type LLMHumanInTheLoopArtifacts"
                )
            if not isinstance(self.artifact, LLMHumanInTheLoopArtifacts):
                raise ValueError(
                    f"Artifact must be of type LLMHumanInTheLoopArtifacts, got {type(self.artifact).__name__}."
                )
            if len(self.tool_call_requests) != len(self.artifact.artifacts):
                raise ValueError(
                    "Number of tool call requests must match number of artifacts in LLMHumanInTheLoopArtifacts."
                )

        if self.role == LLMRole.HUMAN_CONFIRMATION:
            if self.artifact is None:
                raise ValueError(
                    "Artifact must be provided for messages of role HUMAN_CONFIRMATION. "
                    "Must be of type LLMHumanInTheLoopHumanInputs"
                )
            if not isinstance(self.artifact, LLMHumanInTheLoopHumanInputs):
                raise ValueError(
                    f"Artifact must be of type LLMHumanInTheLoopHumanInputs, got {type(self.artifact).__name__}."
                )

        return self

    @staticmethod
    def validate_message_history(messages: list["LLMMessage"]):
        if messages and messages[-1].role == LLMRole.AWAITING_HUMAN_ACTION:
            raise ValueError(
                "Cannot prompt with a message of role LLMRole.AWAITING_HUMAN_ACTION, "
                "add a message of role LLMRole.HUMAN_CONFIRMATION first."
            )

        last_non_info_debug_message: LLMMessage | None = None
        for index, message in enumerate(messages[1:]):
            prior_message = messages[index]
            if prior_message.role not in {LLMRole.INFO, LLMRole.DEBUG}:
                last_non_info_debug_message = prior_message

            if message.role == LLMRole.AWAITING_HUMAN_ACTION:
                if not last_non_info_debug_message or last_non_info_debug_message.role != LLMRole.AGENT:
                    raise ValueError(
                        "Cannot prompt with a message of role LLMRole.AWAITING_HUMAN_ACTION "
                        "without a prior message of role LLMRole.AGENT."
                    )

            if message.role == LLMRole.HUMAN_CONFIRMATION and prior_message.role != LLMRole.AWAITING_HUMAN_ACTION:
                raise ValueError(
                    "Cannot prompt with a message of role LLMRole.HUMAN_CONFIRMATION "
                    "without a prior message of role LLMRole.AWAITING_HUMAN_ACTION."
                )

    class Config:
        validate_assignment = True


__all__ = ["LLMMessage"]
