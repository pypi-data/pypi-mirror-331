import json
from logging import Logger, getLogger
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, TypeAdapter

from aiteamwork.llm_agent_like import LLMAgentLike
from aiteamwork.llm_context import EmptyRuntimeContext, LLMContext, LLMInitialContext
from aiteamwork.llm_message import LLMMessage
from aiteamwork.llm_tool_function import LLMToolFunctionDefinition
from aiteamwork.util.model import get_model_name


class LLMSerializer:
    _agents: dict[str, LLMAgentLike]
    _tools: set[Callable | LLMToolFunctionDefinition]
    _extra_models: dict[str, type[BaseModel] | TypeAdapter]
    _logger: Logger
    _empty_context: LLMContext

    def __init__(
        self,
        agents: list[LLMAgentLike] | None = None,
        tools: set[Callable | LLMToolFunctionDefinition] | None = None,
        logger: Logger | None = None,
    ) -> None:
        self._logger = TypeAdapter[Logger | None](
            Logger | None, config=ConfigDict(arbitrary_types_allowed=True)
        ).validate_python(logger) or getLogger("aiteamwork")
        self._extra_models = {}
        self._agents = {}
        for agent in (
            TypeAdapter[list[LLMAgentLike] | None](
                list[LLMAgentLike] | None, config=ConfigDict(arbitrary_types_allowed=True)
            ).validate_python(agents)
            or []
        ):
            self._agents[agent.get_id()] = agent

        self._tools = (
            TypeAdapter[set[Callable | LLMToolFunctionDefinition] | None](
                set[Callable | LLMToolFunctionDefinition] | None, config=ConfigDict(arbitrary_types_allowed=True)
            ).validate_python(tools)
            or set()
        )
        self._empty_context = LLMContext[EmptyRuntimeContext](
            runtime_context=EmptyRuntimeContext(),
            logger=self._logger,
        )

    def add_model(self, model: type[BaseModel] | TypeAdapter, alias: str | list[str] | None = None) -> None:
        alias = TypeAdapter[str | list[str] | None](str | list[str] | None).validate_python(alias)
        alias_list = alias if isinstance(alias, list) else [alias] if alias else []
        self._extra_models[get_model_name(model)] = model
        for alias_name in alias_list:
            self._extra_models[alias_name] = model

    def add_models_from_agent(self, agent: LLMAgentLike) -> None:
        agent = TypeAdapter[LLMAgentLike](
            LLMAgentLike, config=ConfigDict(arbitrary_types_allowed=True)
        ).validate_python(agent)
        self._agents[agent.get_id()] = agent

    def add_models_from_tool(self, tool: Callable | LLMToolFunctionDefinition) -> None:
        tool = TypeAdapter[Callable | LLMToolFunctionDefinition](
            Callable | LLMToolFunctionDefinition, config=ConfigDict(arbitrary_types_allowed=True)
        ).validate_python(tool)
        self._tools.add(tool)

    def _get_context(self, context: LLMContext | LLMInitialContext | None) -> LLMContext:
        if context is None:
            return self._empty_context

        if isinstance(context, LLMContext):
            return context

        if isinstance(context, LLMInitialContext):
            return LLMContext[Any].model_validate(
                {
                    **context.model_dump(mode="python"),
                    "runtime_context": context.runtime_context,
                    "logger": self._logger,
                }
            )

        raise ValueError("context must be an instance of LLMContext or LLMInitialContext or None")

    async def _get_model_map(self, context: LLMContext) -> dict[str, type[BaseModel] | TypeAdapter]:
        model_map: dict[str, type[BaseModel] | TypeAdapter] = {}
        for agent in self._agents.values():
            agent_models = await agent.get_serialization_models(context)
            for model in agent_models:
                model_map[get_model_name(model)] = model

        for tool in self._tools:
            as_def: LLMToolFunctionDefinition = (
                tool if isinstance(tool, LLMToolFunctionDefinition) else LLMToolFunctionDefinition(tool)
            )
            if as_def.input_schema:
                model_map[get_model_name(as_def.input_schema)] = as_def.input_schema
            if as_def.output_schema:
                model_map[get_model_name(as_def.output_schema)] = as_def.output_schema

        model_map.update(self._extra_models)

        return model_map

    def serialize_message(self, message: LLMMessage) -> str:
        return message.model_dump_json()

    def serialize_messages(self, messages: list[LLMMessage]) -> str:
        return json.dumps([message.model_dump(mode="json") for message in messages])

    def _parse_message_models(self, message: dict, model_map: dict[str, type[BaseModel] | TypeAdapter]) -> dict:
        message = TypeAdapter[dict](dict).validate_python(message)

        requests: list[dict] = []

        artifact = message.get("artifact")
        artifact_type_name = TypeAdapter[str | None](str | None).validate_python(message.get("artifact_type"))

        if artifact and artifact_type_name:
            artifact_type = model_map.get(artifact_type_name)
            if artifact_type:
                if callable(artifact_type) and issubclass(artifact_type, BaseModel):
                    message["artifact"] = artifact_type.model_validate(artifact)
                elif isinstance(artifact_type, TypeAdapter):
                    message["artifact"] = artifact_type.validate_python(artifact)

        tool_call_result = TypeAdapter[dict | None](dict | None).validate_python(message.get("tool_call_result"))

        tool_call_result_type_name = (
            TypeAdapter[str | None](str | None).validate_python(tool_call_result.get("result_type"))
            if tool_call_result
            else None
        )
        tool_call_result_data = tool_call_result.get("result") if tool_call_result else None

        message["tool_call_result"] = tool_call_result

        if tool_call_result and tool_call_result_data and tool_call_result_type_name:
            result_type = model_map.get(tool_call_result_type_name)
            if result_type:
                if callable(result_type) and issubclass(result_type, BaseModel):
                    tool_call_result["result"] = result_type.model_validate(tool_call_result_data)
                elif isinstance(result_type, TypeAdapter):
                    tool_call_result["result"] = result_type.validate_python(tool_call_result_data)

        if tool_call_result:
            request = TypeAdapter[dict](dict).validate_python(tool_call_result.get("request"))
            tool_call_result["request"] = request
            requests.append(request)

        tool_call_requests = TypeAdapter[list[dict]](list[dict]).validate_python(message.get("tool_call_requests", []))
        message["tool_call_requests"] = tool_call_requests

        requests.extend(tool_call_requests)

        for request in requests:
            tool_args_type_name = TypeAdapter[str | None](str | None).validate_python(request.get("tool_args_type"))
            if not tool_args_type_name:
                continue

            tool_args_type = model_map.get(tool_args_type_name)

            if tool_args_type:
                tool_args = TypeAdapter[dict](dict).validate_python(request.get("tool_args"))
                if callable(tool_args_type) and issubclass(tool_args_type, BaseModel):
                    request["tool_args"] = tool_args_type.model_validate(tool_args)
                elif isinstance(tool_args_type, TypeAdapter):
                    request["tool_args"] = tool_args_type.validate_python(tool_args)
        return message

    async def parse_message_json(
        self, message: str, context: LLMContext | LLMInitialContext | None = None
    ) -> LLMMessage:
        context = self._get_context(context)
        model_map = await self._get_model_map(context)
        as_dict = TypeAdapter[dict](dict).validate_json(message)
        as_dict = self._parse_message_models(as_dict, model_map)
        return LLMMessage.model_validate(as_dict)

    async def parse_message_dict(
        self, message: dict, context: LLMContext | LLMInitialContext | None = None
    ) -> LLMMessage:
        context = self._get_context(context)
        model_map = await self._get_model_map(context)
        as_dict = TypeAdapter[dict](dict).validate_python(message)
        as_dict = self._parse_message_models(as_dict, model_map)
        return LLMMessage.model_validate(as_dict)

    async def parse_message_list_json(
        self, messages: str, context: LLMContext | LLMInitialContext | None = None
    ) -> list[LLMMessage]:
        context = self._get_context(context)
        model_map = await self._get_model_map(context)
        parsed = TypeAdapter[list[dict]](list[dict]).validate_json(messages)
        parsed = [self._parse_message_models(message, model_map) for message in parsed]
        return TypeAdapter[list[LLMMessage]](list[LLMMessage]).validate_python(parsed)

    async def parse_message_list_dict(
        self, messages: list[dict], context: LLMContext | LLMInitialContext | None = None
    ) -> list[LLMMessage]:
        context = self._get_context(context)
        model_map = await self._get_model_map(context)
        parsed = TypeAdapter[list[dict]](list[dict]).validate_python(messages)
        parsed = [self._parse_message_models(message, model_map) for message in parsed]
        return TypeAdapter[list[LLMMessage]](list[LLMMessage]).validate_python(parsed)
