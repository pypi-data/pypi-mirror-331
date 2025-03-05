from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class LLMFileConverterConvertTarget(BaseModel):
    extension: str = Field()
    mime_type: str = Field()


class LLMFileConverterFile(BaseModel):
    data: bytes = Field()
    filename: str = Field()
    mime_type: str = Field()
    is_binary: bool = Field(default=True)


class LLMFileConverter(ABC):

    @abstractmethod
    def get_supported_file_sources(self) -> list[LLMFileConverterConvertTarget]:
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    def get_supported_file_targets(self) -> LLMFileConverterConvertTarget:
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    async def convert_file(self, file: LLMFileConverterFile) -> LLMFileConverterFile:
        raise NotImplementedError("This method must be overridden by subclasses")
