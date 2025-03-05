import asyncio
import base64
import enum
import mimetypes
import urllib.parse
from pathlib import Path
from re import Pattern
from typing import Callable, Coroutine

import aiohttp
from pydantic import BaseModel, Field, FileUrl, HttpUrl, TypeAdapter

from aiteamwork.llm_file_converter import LLMFileConverter, LLMFileConverterFile
from aiteamwork.util.callable import with_retrying
from aiteamwork.util.validators import validate_not_none

COMMON_BINARY_FORMAT_MIME_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/ogg",
    "audio/flac",
    "audio/aac",
    "audio/x-ms-wma",
    "audio/x-wav",
    "audio/x-aiff",
    "audio/x-m4a",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/webp",
    "image/tiff",
    "image/x-icon",
    "image/svg+xml",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/rtf",
    "application/epub+zip",
    "application/x-mobipocket-ebook",
    "application/vnd.amazon.ebook",
    "application/x-cbr",
    "application/x-cbz",
}

COMMON_TEXT_FORMAT_MIME_TYPES = {
    "text/plain",
    "text/html",
    "text/css",
    "text/csv",
    "text/xml",
    "text/markdown",
    "application/json",
    "application/javascript",
    "application/xml",
    "application/x-www-form-urlencoded",
    "application/xhtml+xml",
}


class LLMSupportedFileTypeContentType(enum.Enum):
    PLAIN_TEXT = "plain_text"
    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"


class LLMSupportedFileType(BaseModel):
    extensions: list[str | Pattern] = Field()
    mime_type: str | Pattern = Field()
    max_size: int = Field(default=-1)
    support_content_type: LLMSupportedFileTypeContentType = Field()
    other_constraints: list[Callable[["LLMFile"], Coroutine[None, None, list[str]]]] = Field(default_factory=list)

    def matches(self, mime_type: str, extension: str) -> bool:
        return (
            (
                extension in self.extensions
                or any(pattern.match(extension) for pattern in self.extensions if isinstance(pattern, Pattern))
            )
            and (isinstance(self.mime_type, Pattern) and bool(self.mime_type.match(mime_type)))
            or (isinstance(self.mime_type, str) and self.mime_type == mime_type)
        )

    async def check_file(self, file: "LLMFile") -> list[str]:
        all_files = [file] + file.converted_files
        files_with_issues: list[tuple[LLMFile, list[str]]] = []
        early_exit = False

        async def check_variant_file(file_to_check: LLMFile) -> tuple[LLMFile, list[str]] | None:
            nonlocal early_exit
            if early_exit:
                return None

            issues = []
            if file.filename:
                extension = file_to_check.filename.split(".")[-1].lower().strip()
                is_in_extension_list = extension in self.extensions
                is_in_pattern_list = any(
                    pattern.match(extension) for pattern in self.extensions if isinstance(pattern, Pattern)
                )
                if not is_in_extension_list and not is_in_pattern_list:
                    issues.append(f"Unsupported file extension: {extension}")
            if isinstance(self.mime_type, Pattern) and not self.mime_type.match(file_to_check.mime_type):
                issues.append(f"MIME type {file_to_check.mime_type} is not supported")
            if isinstance(self.mime_type, str) and file_to_check.mime_type != self.mime_type:
                issues.append(f"MIME type {self.mime_type} is not supported")
            if self.max_size > 0 and file_to_check.file_size > self.max_size:
                issues.append(f"File size exceeds the maximum size of {self.max_size} bytes")

            if not issues:
                for constraint in self.other_constraints:
                    if early_exit:
                        return None
                    issues.extend(await constraint(file_to_check))

            if not issues:
                early_exit = True

            return (file_to_check, issues)

        files_with_issues = [
            item
            for item in (await asyncio.gather(*[check_variant_file(file_to_check) for file_to_check in all_files]))
            if item
        ]
        has_files_without_issues = any(file for file, issues in files_with_issues if not issues)

        if has_files_without_issues:
            return []

        compiled_issue_list: list[str] = []

        for file, issues in files_with_issues:
            for issue in issues:
                compiled_issue_list.append(f"File: {file.filename}: {issue}")

        return compiled_issue_list


class LLMFile(BaseModel):
    """
    Model representing a file with metadata.

    Attributes:
        urls (dict[str, str]): Dictionary of provider names to URLs to download the file.
        cached_data (bytes | None): Cached data of the file.
        file_size (int): Filesize in bytes.
        mime_type (str): MIME type of the file.
        filename (str): Name of the file.
        expires_timestamp (dict[str, int]): Dictionary of provider names to a  Unix timestamp when the file expires \
            (in the respective provider platform).
        is_binary (bool): Whether the file has binary or plain text content.
        external_ids (dict[str, str]): Dictionary of provider names to External IDs of the file.
        converted_files (list[LLMFile]): List of converted files that might be used in place of the parent file.
    """

    urls: dict[str, HttpUrl | FileUrl] = Field(
        description="Dictionary of provider names to URLs to download the file.",
        examples=[{"openai": "https://example.com/file.pdf", "google": "https://example.com/image.png"}],
    )
    """Dictionary of provider names to URLs to download the file."""

    cached_data: bytes | None = Field(default=None, description="Cached data of the file.")
    """Cached data of the file."""

    file_size: int = Field(description="Filesize in bytes.")
    """Filesize in bytes."""

    mime_type: str = Field(description="MIME type of the file.", examples=["application/pdf", "image/png"])
    """MIME type of the file."""

    filename: str = Field(description="Name of the file.", examples=["file.pdf", "image.png"])
    """Name of the file."""

    expires_timestamp: dict[str, int] = Field(
        description=(
            "Dictionary of provider names to a  Unix timestamp when the file expires"
            "(in the respective provider platform)."
        ),
        examples=[{"google": 100000000}],
        default_factory=dict,
    )
    """Dictionary of provider names to a  Unix timestamp when the file expires (in the respective provider platform)."""

    is_binary: bool = Field(description="Whether the file has binary or plain text content.", default=True)
    """Whether the file has binary or plain text content."""

    external_ids: dict[str, str] = Field(
        description="Dictionary of provider names to External IDs of the file.",
        examples=[{"google": "1234", "openai": "5678"}],
        default_factory=dict,
    )
    """Dictionary of provider names to External IDs of the file."""

    provider_verification: dict[str, LLMSupportedFileTypeContentType] = Field(
        default_factory=dict,
        description=(
            "Dict of providers names to their supported content types, "
            "this is added after the file is verified and is used to evade re-verification."
        ),
        examples=[
            {"google": LLMSupportedFileTypeContentType.DOCUMENT, "openai": LLMSupportedFileTypeContentType.IMAGE}
        ],
    )
    """Set of providers that have verified that the file is correct and supported."""

    converted_files: list["LLMFile"] = Field(default_factory=list)
    """List of converted files that might be used in place of the parent file."""

    @with_retrying(retries=[100, 200, 500])
    @staticmethod
    async def _fetch_from_file_url(url: FileUrl) -> bytes:
        file_path = validate_not_none(url.path)
        my_file = Path(file_path)

        if not my_file.is_file():
            raise FileNotFoundError(f"File {file_path} does not exist.")

        with open(file_path, "rb") as file:
            return file.read()

    @with_retrying(retries=[100, 200, 500])
    @staticmethod
    async def _fetch_from_http_url(url: HttpUrl) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(str(url)) as response:
                response.raise_for_status()
                return await response.read()

    @with_retrying(retries=[100, 200, 500])
    @staticmethod
    async def _fetch_length_from_http_url(url: HttpUrl) -> int | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(str(url)) as response:
                return response.content_length

    async def fetch_from_url(self) -> bytes:
        urls = self.urls.values()
        sorted_urls = [url for url in urls if isinstance(url, FileUrl)] + [
            url for url in urls if not isinstance(url, FileUrl)
        ]

        exceptions_while_fetching: list[Exception] = []

        for url in sorted_urls:
            try:
                self.cached_data = (
                    await LLMFile._fetch_from_file_url(url)
                    if isinstance(url, FileUrl)
                    else await LLMFile._fetch_from_http_url(url)
                )
                return self.cached_data
            except Exception as e:
                exceptions_while_fetching.append(e)
                continue

        raise Exception("Failed to fetch file from any of the URLs.")

    async def get_binary_file_contents(self) -> bytes:
        if self.cached_data:
            return self.cached_data

        self.cached_data = await self.fetch_from_url()
        return self.cached_data

    async def get_text_file_contexts(self) -> str:
        if self.cached_data:
            return self.cached_data.decode("utf-8")

        self.cached_data = await self.fetch_from_url()
        return self.cached_data.decode("utf-8")

    async def get_as_supported_llm_file(
        self, supported_types: list[LLMSupportedFileType], provider_name: str, file_converters: list[LLMFileConverter]
    ) -> tuple["LLMFile", LLMSupportedFileTypeContentType]:
        files: list[LLMFile] = [self, *self.converted_files]

        for file in files:
            verified_content_type = file.provider_verification.get(provider_name)
            if verified_content_type:
                return file, verified_content_type

        for supported_type in supported_types:
            for file in files:
                issues = await supported_type.check_file(self)
                if not issues:
                    return file, supported_type.support_content_type

        # todo: support multi-step conversion, using a graph and djiakstra's algorithm
        for file_converter in file_converters:
            for supported_type in supported_types:
                for source_type in file_converter.get_supported_file_sources():
                    if supported_type.matches(source_type.mime_type, source_type.extension):
                        converted_data = await file_converter.convert_file(
                            LLMFileConverterFile(
                                data=await self.get_binary_file_contents(),
                                filename=self.filename,
                                mime_type=self.mime_type,
                                is_binary=self.is_binary,
                            )
                        )
                        new_file = self.model_copy(
                            update={
                                "cached_data": converted_data.data,
                                "mime_type": converted_data.mime_type,
                                "filename": converted_data.filename,
                                "file_size": len(converted_data.data),
                                "is_binary": converted_data.is_binary,
                                "urls": {},
                                "converted_files": [],
                                "provider_verification": {},
                                "external_ids": {},
                            }
                        )
                        self.converted_files.append(new_file)
                        return new_file, supported_type.support_content_type

        raise Exception("Can't convert file to any of the supported types.")

    @staticmethod
    async def is_file_binary(file_path: str) -> bool:
        try:
            with open(file_path, "rb") as file:
                for byte in file.read(1024):
                    if byte == 0:
                        return True
            return False
        except Exception:
            return False

    @staticmethod
    async def from_local_file(
        path: str, mime_type_hint: str | None = None, is_binary_hint: bool | None = None
    ) -> "LLMFile":
        path_checker = TypeAdapter[FileUrl](FileUrl)
        path = Path(path).resolve().as_posix()
        path = f"file://{urllib.parse.quote_plus(path)}".replace("%2F", "/")
        url = path_checker.validate_python(path)
        content = await LLMFile._fetch_from_file_url(url)
        name = path.split("/")[-1]
        if not mime_type_hint and not mimetypes.inited:
            mimetypes.init()
        mime_type = mime_type_hint or mimetypes.guess_type(name)[0]
        is_binary = is_binary_hint if is_binary_hint is not None else await LLMFile.is_file_binary(path)

        if not mime_type:
            raise ValueError("Can't infer MIME type of the file.")

        return LLMFile(
            cached_data=content,
            expires_timestamp={"local": -1},
            urls={"local": url},
            file_size=len(content),
            filename=name,
            is_binary=is_binary,
            mime_type=mime_type,
        )

    @staticmethod
    async def from_http_url(
        path: str,
        mime_type_hint: str | None = None,
        is_binary_hint: bool | None = None,
        file_size_hint: int | None = None,
        fetch_data: bool = True,
        fetch_size: bool = True,
    ) -> "LLMFile":
        url_checker = TypeAdapter[HttpUrl](HttpUrl)
        url = url_checker.validate_python(path)
        content: bytes | None = None
        if fetch_data:
            content = await LLMFile._fetch_from_http_url(url)
        name = validate_not_none(url.path).split("/")[-1]
        if not mime_type_hint and not mimetypes.inited:
            mimetypes.init()
        mime_type = mime_type_hint or mimetypes.guess_type(name)[0]

        if not mime_type:
            raise ValueError("Can't infer MIME type of the file.")

        is_binary = False
        if is_binary_hint:
            is_binary = is_binary_hint
        else:
            if fetch_data and content:
                is_binary = b"\x00" in content
            elif mime_type in COMMON_BINARY_FORMAT_MIME_TYPES:
                is_binary = True
            elif mime_type in COMMON_TEXT_FORMAT_MIME_TYPES:
                is_binary = False
            else:
                raise ValueError("Can't infer if the file is binary or not.")

        file_size: int | None = 0

        if file_size_hint:
            file_size = file_size_hint
        elif content:
            file_size = len(content)
        elif fetch_size:
            file_size = await LLMFile._fetch_length_from_http_url(url)

        if not file_size:
            raise ValueError("Can't infer file size.")

        return LLMFile(
            cached_data=content,
            expires_timestamp={"http": -1},
            urls={"http": url},
            file_size=file_size,
            filename=name,
            is_binary=is_binary,
            mime_type=mime_type,
        )

    @staticmethod
    async def from_base64(
        data: str, filename: str, mime_type_hint: str | None = None, is_binary_hint: bool | None = None
    ) -> "LLMFile":
        content = base64.b64decode(data.encode())
        return await LLMFile.from_bytes(content, filename, mime_type_hint, is_binary_hint)

    @staticmethod
    async def from_bytes(
        data: bytes, filename: str, mime_type_hint: str | None = None, is_binary_hint: bool | None = None
    ) -> "LLMFile":
        filename = Path(filename).as_posix()
        if not mime_type_hint and not mimetypes.inited:
            mimetypes.init()
        mime_type = mime_type_hint or mimetypes.guess_type(filename)[0]
        is_binary = is_binary_hint if is_binary_hint is not None else b"\x00" in data

        if not mime_type:
            raise ValueError("Can't infer MIME type of the file.")

        return LLMFile(
            cached_data=data,
            expires_timestamp={},
            urls={},
            file_size=len(data),
            filename=filename,
            is_binary=is_binary,
            mime_type=mime_type,
        )


__all__ = [
    "LLMFile",
    "LLMSupportedFileType",
    "LLMSupportedFileTypeContentType",
]
