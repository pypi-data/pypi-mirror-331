from pydantic import BaseModel, Field

from aiteamwork.contextvar import LLMContext


class LLMArtifactVerificationContext[ArtifactType: BaseModel, RuntimeContextType: BaseModel](
    LLMContext[RuntimeContextType]
):
    """Context for the artifact_verification callback in LLMAgent."""

    artifact: ArtifactType = Field(description="The artifact to be verified.")
    """The artifact to be verified."""


class LLMArtifactVerificationResult(BaseModel):
    """Result of the artifact_verification callback in LLMAgent."""

    issues: list[str] = Field(
        description="Error messages from the artifact verification process. Leave empty if no errors.",
        default_factory=list,
    )
    """Error messages from the artifact verification process. Leave empty if no errors."""
