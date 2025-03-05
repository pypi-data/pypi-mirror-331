import asyncio
import json
from typing import Any, cast

from openai import NOT_GIVEN, APIStatusError, AsyncOpenAI, InternalServerError, RateLimitError
from openai.types import CompletionUsage
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionContentPartParam,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
    ParsedChatCompletionMessage,
)
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall, ChoiceDeltaToolCallFunction
from pydantic import BaseModel, Field, HttpUrl, TypeAdapter

from aiteamwork.llm_context import combine_runtime_context_schemas
from aiteamwork.llm_file import LLMFile
from aiteamwork.llm_file_uploader import LLMFileUploader, LLMFileUploadResult
from aiteamwork.llm_message import LLMMessage, LLMMessagePriority
from aiteamwork.llm_provider import (
    LLMProvider,
    LLMProviderContext,
    LLMSupportedFileType,
    LLMSupportedFileTypeContentType,
)
from aiteamwork.llm_provider_result import LLMAgentUsage, LLMProviderResult
from aiteamwork.llm_role import LLMRole
from aiteamwork.llm_tool_call_request import LLMToolCallRequest
from aiteamwork.llm_tool_function import LLMToolFunctionDefinition
from aiteamwork.policies.provider_policy import ProviderPolicy, ValueOrProviderPolicy
from aiteamwork.util.callable import with_retrying
from aiteamwork.util.validators import validate_not_none


class OpenAITeamworkClient(AsyncOpenAI):
    async def __aenter__(self) -> "OpenAITeamworkClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()


class OpenAICompletionsLLMProvider(BaseModel, LLMProvider[BaseModel]):
    base_url: ValueOrProviderPolicy[str | None] = Field(default=None)
    api_key: ValueOrProviderPolicy[str] = Field()
    model: ValueOrProviderPolicy[str] = Field(default="gpt-4o-mini")
    max_tokens: ValueOrProviderPolicy[int | None] = Field(default=None)
    temperature: ValueOrProviderPolicy[float | None] = Field(default=None)
    top_p: ValueOrProviderPolicy[float | None] = Field(default=None)
    presence_penalty: ValueOrProviderPolicy[float | None] = Field(default=None)
    seed: ValueOrProviderPolicy[int | None] = Field(default=None)
    stop: ValueOrProviderPolicy[str | list[str] | None] = Field(default=None)
    logit_bias: ValueOrProviderPolicy[dict[str, float] | None] = Field(default=None)
    retry_policy: ValueOrProviderPolicy[list[int] | None] = Field(default=None)
    parallel_tool_calls: ValueOrProviderPolicy[bool | None] | None = Field(default=None)
    file_uploader: LLMFileUploader | None = Field(default=None)

    class Config:
        arbitrary_types_allowed: bool = True

    def get_name(self) -> str:
        return "OpenAICompletions"

    def get_runtime_context_schema(self) -> type[BaseModel]:
        props = list(self.model_fields.keys())
        values = [p for p in [getattr(self, prop) for prop in props] if isinstance(p, ProviderPolicy)]
        runtime_schemas = [value.get_runtime_context_schema() for value in values]
        return combine_runtime_context_schemas(runtime_schemas)

    def get_supported_file_types(self) -> list[LLMSupportedFileType]:
        return [
            LLMSupportedFileType(
                extensions=["jpg", "jpeg"],
                mime_type="image/jpeg",
                max_size=5 * 1024 * 1024,
                support_content_type=LLMSupportedFileTypeContentType.IMAGE,
            ),
            LLMSupportedFileType(
                extensions=["png"],
                mime_type="image/png",
                max_size=5 * 1024 * 1024,
                support_content_type=LLMSupportedFileTypeContentType.IMAGE,
            ),
            LLMSupportedFileType(
                extensions=["webp"],
                mime_type="image/webp",
                max_size=5 * 1024 * 1024,
                support_content_type=LLMSupportedFileTypeContentType.IMAGE,
            ),
            LLMSupportedFileType(
                extensions=["gif"],
                mime_type="image/gif",
                max_size=5 * 1024 * 1024,
                support_content_type=LLMSupportedFileTypeContentType.IMAGE,
            ),
            LLMSupportedFileType(
                extensions=["wav"],
                mime_type="audio/wav",
                max_size=5 * 1024 * 1024,
                support_content_type=LLMSupportedFileTypeContentType.AUDIO,
            ),
            LLMSupportedFileType(
                extensions=["mp3"],
                mime_type="audio/mpeg",
                max_size=5 * 1024 * 1024,
                support_content_type=LLMSupportedFileTypeContentType.AUDIO,
            ),
        ]

    def _convert_schema_to_openai_jsonschema(self, schema: dict[str, object]) -> dict:
        stack: list[object] = [schema]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                if ("description" in node or "title" in node) and node.get("$ref"):
                    raise ValueError(
                        f"OpenAI does not support title/description fields in $ref, found in {node},"
                        "Don't use title/description with complex types in pydantic Field(), "
                        "if you need it, add to the type definition using model_config and json_schema_extra."
                    )
                for value in node.values():
                    stack.append(value)
                if "properties" in node:
                    node["additionalProperties"] = False

                    if "required" not in node:
                        node["required"] = list(node["properties"].keys())

        return schema

    def _map_tool_definition_to_openai_tool(
        self, tool: LLMToolFunctionDefinition, context: LLMProviderContext
    ) -> ChatCompletionToolParam:
        parameters = self._convert_schema_to_openai_jsonschema(tool.get_input_json_schema())

        return {
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": parameters,
                "strict": True,
            },
            "type": "function",
        }

    @with_retrying(retries=[200, 500, 1000])
    async def _upload_file(
        self,
        file: LLMFile,
    ) -> LLMFileUploadResult:
        if not self.file_uploader:
            raise ValueError("No file uploader is provided")

        return await self.file_uploader.upload_file(file)

    async def get_openai_file(
        self, file: LLMFile, context: LLMProviderContext
    ) -> ChatCompletionContentPartParam | None:
        if not file.is_binary:
            return {"type": "text", "text": f"File: {file.filename}\n```${await file.get_text_file_contexts()}```"}

        supported_file, content_type = await self.get_supported_llm_file(file, context)
        openai_url = supported_file.urls.get("openai")

        if not openai_url or not isinstance(openai_url, HttpUrl):
            http_url = supported_file.urls.get("http")
            if not http_url:
                upload_result = await self._upload_file(supported_file)
                supported_file.urls["openai"] = upload_result.url
                supported_file.expires_timestamp["openai"] = upload_result.expires_at
            else:
                supported_file.urls["openai"] = http_url
                supported_file.expires_timestamp["openai"] = validate_not_none(
                    supported_file.expires_timestamp.get("http")
                )

        if content_type == LLMSupportedFileTypeContentType.IMAGE:
            return {
                "type": "image_url",
                "image_url": {
                    "detail": "auto",
                    "url": str(cast(HttpUrl, supported_file.urls["openai"])),
                },
            }

        if content_type == LLMSupportedFileTypeContentType.AUDIO:
            data = await supported_file.get_binary_file_contents()
            data_as_base64 = data.decode("base64")
            return {
                "type": "input_audio",
                "input_audio": {
                    "data": data_as_base64,
                    "format": "mp3",
                },
            }

        return None

    async def _map_message_to_openai_message(
        self, client: AsyncOpenAI, message: LLMMessage, context: LLMProviderContext
    ) -> ChatCompletionMessageParam | None:
        agent_used = validate_not_none(context.current_agent)

        if message.role == LLMRole.INFO:
            return None

        if message.role == LLMRole.MEMORY:
            if message.priority == LLMMessagePriority.HIGH:
                return {
                    "role": "user",
                    "name": "Memory",
                    "content": message.content,
                }
            else:
                return {
                    "role": "system",
                    "name": "Memory",
                    "content": message.content,
                }

        if message.role == LLMRole.SYSTEM:
            return {
                "role": "system",
                "content": [{"type": "text", "text": message.content}],
                "name": "System",
            }

        if message.role == LLMRole.TOOL:
            call_result = validate_not_none(message.tool_call_result)
            return {
                "role": "tool",
                "content": (
                    call_result.result.model_dump_json()
                    if isinstance(call_result.result, BaseModel)
                    else json.dumps(call_result.result)
                ),
                "tool_call_id": call_result.call_id,
            }

        if message.is_user_message_for_agent(agent_used):
            files = [
                file
                for file in await asyncio.gather(*[self.get_openai_file(file, context) for file in message.files])
                if file
            ]

            return {
                "role": "user",
                "content": [{"type": "text", "text": message.content}, *files],
            }

        if message.is_agent_message_for_agent(agent_used):
            msg: ChatCompletionAssistantMessageParam = {
                "role": "assistant",
                "content": message.content,
            }

            if not message.content and message.artifact:
                if hasattr(message.artifact, "to_content_string"):
                    if not callable(getattr(message.artifact, "to_content_string")):
                        raise ValueError("to_content_string is not callable")

                    msg["content"] = message.artifact.to_content_string()
                elif isinstance(message.artifact, BaseModel):
                    msg["content"] = message.artifact.model_dump_json()
                else:
                    try:
                        msg["content"] = json.dumps(message.artifact)
                    except Exception:
                        raise ValueError("Artifact is not serializable")

            if message.tool_call_requests:
                msg["tool_calls"] = [
                    {
                        "function": {"name": req.tool_name, "arguments": json.dumps(req.tool_args_raw)},
                        "id": req.call_id,
                        "type": "function",
                    }
                    for req in message.tool_call_requests
                ]

            return msg

        return None

    async def _map_openai_completion_to_message(
        self, completion: ParsedChatCompletionMessage, context: LLMProviderContext
    ) -> LLMMessage:
        content = ""
        artifact: Any | None = None

        if context.artifact_schema and (completion.content or completion.parsed):
            artifact = validate_not_none(cast(Any, completion.parsed))
            if artifact and hasattr(artifact, "content") and isinstance(artifact.content, str):
                content = artifact.content
        else:
            content = completion.content or ""

        return LLMMessage(
            role=LLMRole.AGENT,
            content=content,
            artifact=artifact,
            provider_platform="openai",
            provider_role=completion.role,
            hidden=not bool(content) and not bool(artifact),
            authors=[validate_not_none(context.current_agent)],
            tool_call_requests=[
                LLMToolCallRequest(
                    tool_name=tool_call.function.name,
                    tool_args_raw=json.loads(tool_call.function.arguments),
                    call_id=tool_call.id,
                )
                for tool_call in (completion.tool_calls or [])
            ],
        )

    async def prompt(self, context: LLMProviderContext) -> LLMProviderResult:
        base_url = await ProviderPolicy.value_with_adapter(
            self.base_url, context, TypeAdapter[str | None](HttpUrl | None), ValueError
        )

        api_key = await ProviderPolicy.value_with_adapter(self.api_key, context, TypeAdapter[str](str), ValueError)

        model = await ProviderPolicy.value_with_adapter(self.model, context, TypeAdapter[str](str), ValueError)

        temperature = await ProviderPolicy.value_with_adapter(
            self.temperature, context, TypeAdapter[float | None](float | None), ValueError
        )

        max_tokens = await ProviderPolicy.value_with_adapter(
            self.max_tokens, context, TypeAdapter[int | None](int | None), ValueError
        )

        top_p = await ProviderPolicy.value_with_adapter(
            self.top_p, context, TypeAdapter[float | None](float | None), ValueError
        )

        presence_penalty = await ProviderPolicy.value_with_adapter(
            self.presence_penalty, context, TypeAdapter[float | None](float | None), ValueError
        )

        seed = await ProviderPolicy.value_with_adapter(
            self.seed, context, TypeAdapter[int | None](int | None), ValueError
        )

        stop = await ProviderPolicy.value_with_adapter(
            self.stop, context, TypeAdapter[str | list[str] | None](str | list[str] | None), ValueError
        )

        logit_bias = await ProviderPolicy.value_with_adapter(
            self.logit_bias, context, TypeAdapter[dict[str, int] | None](dict[str, int] | None), ValueError
        )

        parallel_tool_calls = await ProviderPolicy.value_with_adapter(
            self.parallel_tool_calls, context, TypeAdapter[bool | None](bool | None), ValueError
        )

        retry_policy = (
            await ProviderPolicy.value_with_adapter(
                self.retry_policy, context, TypeAdapter[list[int] | None](list[int] | None), ValueError
            )
        ) or [200, 500, 1000, 2000]

        messages: list[ChatCompletionMessageParam] = []

        if context.system_instructions:
            messages.append({"role": "system", "content": context.system_instructions, "name": "System"})

        async with AsyncOpenAI(api_key=api_key, base_url=str(base_url) if base_url else None) as client:
            messages.extend(
                [
                    msg
                    for msg in await asyncio.gather(
                        *[self._map_message_to_openai_message(client, message, context) for message in context.messages]
                    )
                    if msg
                ]
            )

            tools: list[ChatCompletionToolParam] = [
                self._map_tool_definition_to_openai_tool(tool, context) for tool in context.tools
            ]

            try:
                if context.streaming_callback:
                    openai_result_stream = await client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature if temperature else NOT_GIVEN,
                        max_tokens=max_tokens if max_tokens else NOT_GIVEN,
                        top_p=top_p if top_p else NOT_GIVEN,
                        presence_penalty=presence_penalty if presence_penalty else NOT_GIVEN,
                        seed=seed if seed else NOT_GIVEN,
                        stop=stop if stop else NOT_GIVEN,
                        logit_bias=logit_bias if logit_bias else NOT_GIVEN,
                        tools=tools if tools else NOT_GIVEN,
                        parallel_tool_calls=parallel_tool_calls if parallel_tool_calls is not None else NOT_GIVEN,
                        stream_options={
                            "include_usage": True,
                        },
                        stream=True,
                    )

                    usage: CompletionUsage | None = None
                    message_content = ""
                    tool_calls: list[ChoiceDeltaToolCall] = []
                    provider_role: str | None = ""

                    async for chunk in openai_result_stream:
                        if chunk.choices:
                            choice = chunk.choices[0]
                            provider_role = provider_role or choice.delta.role
                            if choice.delta.content:
                                piece = choice.delta.content
                                message_content += piece
                                await context.streaming_callback(piece, message_content, False)
                            for tool_call in choice.delta.tool_calls or []:
                                if tool_call.id:
                                    tool_calls.append(tool_call)
                                else:
                                    last_tool_call_fn_added = cast(ChoiceDeltaToolCallFunction, tool_calls[-1].function)
                                    last_tool_call_fn_added.arguments = last_tool_call_fn_added.arguments or ""
                                    if tool_call.function:
                                        last_tool_call_fn_added.arguments += tool_call.function.arguments or ""

                        if chunk.usage:
                            usage = chunk.usage
                            await context.streaming_callback("", message_content, True)

                    new_message = LLMMessage(
                        role=LLMRole.AGENT,
                        content=message_content,
                        provider_platform="openai",
                        provider_role=provider_role,
                        hidden=not bool(message_content),
                        authors=[validate_not_none(context.current_agent)],
                        tool_call_requests=[
                            LLMToolCallRequest(
                                tool_name=validate_not_none(tool_call.function.name),
                                tool_args_raw=json.loads(validate_not_none(tool_call.function.arguments)),
                                call_id=validate_not_none(tool_call.id),
                            )
                            for tool_call in (tool_calls or [])
                            if tool_call.function
                        ],
                    )

                    usage = validate_not_none(usage)

                else:
                    openai_result = await client.beta.chat.completions.parse(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        presence_penalty=presence_penalty,
                        seed=seed,
                        stop=stop if stop else NOT_GIVEN,
                        logit_bias=logit_bias,
                        response_format=(context.artifact_schema if context.artifact_schema else NOT_GIVEN),
                        tools=tools if tools else NOT_GIVEN,
                        parallel_tool_calls=parallel_tool_calls if parallel_tool_calls is not None else NOT_GIVEN,
                    )

                    new_message = await self._map_openai_completion_to_message(
                        openai_result.choices[0].message, context
                    )

                    usage = validate_not_none(openai_result.usage)

                context.prompt_usage = context.prompt_usage + LLMAgentUsage(
                    completion_tokens=usage.completion_tokens,
                    prompt_tokens=usage.prompt_tokens,
                )

                return LLMProviderResult(
                    new_messages=[new_message],
                    usage=context.prompt_usage,
                )
            except Exception as e:
                can_retry = (
                    isinstance(e, RateLimitError)
                    or isinstance(e, InternalServerError)
                    or not isinstance(e, APIStatusError)
                )
                if can_retry and context.attempt < (len(retry_policy) + 1):
                    await asyncio.sleep(retry_policy[context.attempt - 1] / 1000)
                    context.attempt += 1
                    return await self.prompt(context)
                raise e

    def validate_tools(self, tools: list[LLMToolFunctionDefinition]):
        if len(tools) > 125:
            raise ValueError("The OpenAI Provider supports a maximum of 125 tools.")
