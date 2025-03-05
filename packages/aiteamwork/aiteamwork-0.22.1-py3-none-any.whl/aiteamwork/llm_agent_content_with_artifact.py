from pydantic import BaseModel


class LLMAgentContentWithArtifact[Artifact: BaseModel](BaseModel):
    content: str
    artifact: Artifact


__all__ = ["LLMAgentContentWithArtifact"]
