from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, HttpUrl

from aiteamwork.llm_file import LLMFile


class LLMFileUploadResult(BaseModel):
    url: HttpUrl
    expires_at: int = Field(default=-1)
    external_id: str | None = Field(default=None)


class LLMFileUploader(ABC):

    @abstractmethod
    async def upload_file(self, file: LLMFile) -> LLMFileUploadResult:
        raise NotImplementedError("This method must be overridden by subclasses")
