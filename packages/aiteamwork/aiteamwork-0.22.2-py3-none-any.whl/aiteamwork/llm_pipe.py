from logging import Logger
from typing import Any, Callable, Coroutine, Optional

from pydantic import BaseModel, TypeAdapter, ConfigDict

from aiteamwork.callbacks.pipe import LLMPipeContext, LLMPipeResult
from aiteamwork.llm_context import EmptyRuntimeContext, LLMContext
from aiteamwork.llm_prompt_result import LLMPromptResult
from aiteamwork.serializable_producer import SerializableProducer
from aiteamwork.util.callable import SyncOrAsyncCallback
from aiteamwork.util.validators import get_function_context_types, validated_sync_async_callback


class LLMPipe(SerializableProducer):
    _pipe_name: str
    _next_pipe: Optional["LLMPipe"]
    _context_schema: type[LLMPipeContext]
    _runtime_context_schema: type[BaseModel]
    _validated_pipe_fn: Callable[[LLMPipeContext], Coroutine[None, None, LLMPipeResult]]
    _dependents: list[SerializableProducer | type[BaseModel] | TypeAdapter]

    def __init__(
        self,
        pipe_fn: SyncOrAsyncCallback[[LLMPipeContext], LLMPipeResult],
        pipe_name: str | None = None,
        dependents: list[SerializableProducer | type[BaseModel] | TypeAdapter] | None = None,
    ) -> None:
        if pipe_name:
            self._pipe_name = pipe_name
        else:
            if pipe_fn.__name__:
                self._pipe_name = f"function {pipe_fn.__name__}"
            else:
                self._pipe_name = "unnamed pipe"

        self._next_pipe = None
        self._setup_schemas(pipe_fn)
        self._validated_pipe_fn = validated_sync_async_callback(LLMPipeResult, ["context"], "pipe_fn", pipe_fn)
        self._dependents = TypeAdapter(
            list[SerializableProducer | type[BaseModel] | TypeAdapter], config=ConfigDict(arbitrary_types_allowed=True)
        ).validate_python(dependents or [])

    def _setup_schemas(self, pipe_fn: SyncOrAsyncCallback[[LLMPipeContext], Any]) -> None:
        context_schema, runtime_context_schema = self._extract_schemas_from_function(pipe_fn)

        self._context_schema = context_schema
        self._runtime_context_schema = runtime_context_schema

    def _extract_schemas_from_function(
        self, pipe_fn: SyncOrAsyncCallback[[LLMPipeContext], Any]
    ) -> tuple[type[LLMPipeContext], type[BaseModel]]:
        return get_function_context_types(LLMPipeContext, LLMPipeContext[EmptyRuntimeContext], pipe_fn)

    def get_pipe_type(self) -> str:
        return "Simple Pipe"

    def pipe(self, pipe_fn: "LLMPipe") -> "LLMPipe":
        if self._next_pipe:
            self._next_pipe.pipe(pipe_fn)
        else:
            self._next_pipe = pipe_fn

        return self

    async def __call__(self, result: LLMPromptResult, context: LLMContext, logger: Logger) -> LLMPromptResult:
        pipe_context = self._context_schema.model_validate(
            {
                **context.model_dump(mode="python"),
                "prompt_result": result,
            }
        )
        agent_name = f"[LLM Agent {pipe_context.current_agent or "unknown agent"}]"
        logger.info(f"{agent_name} Running through pipe '{self._pipe_name}' ({self.get_pipe_type()})")
        r = await self._validated_pipe_fn(pipe_context)
        logger.info(f"{agent_name} Pipe '{self._pipe_name}' finished")
        if self._next_pipe:
            return await self._next_pipe(r.prompt_result, context, logger)
        return r.prompt_result

    def validate_configuration(self, runtime_context: Any) -> None:
        self._runtime_context_schema.model_validate(runtime_context)

    async def get_serialization_models(self, context: LLMContext) -> list[type[BaseModel] | TypeAdapter]:
        models: list[type[BaseModel] | TypeAdapter] = []
        serialization_models = [dep for dep in self._dependents if isinstance(dep, SerializableProducer)]
        explicit_dependents = [dep for dep in self._dependents if not isinstance(dep, SerializableProducer)]
        for serialization_prod in serialization_models:
            models.extend(await serialization_prod.get_serialization_models(context))
        for dep in explicit_dependents:
            models.append(dep)

        if self._next_pipe:
            models.extend(await self._next_pipe.get_serialization_models(context))

        return models

    def get_dependents(self) -> list[SerializableProducer | type[BaseModel] | TypeAdapter]:
        return self._dependents

    def set_dependents(self, dependents: list[SerializableProducer | type[BaseModel] | TypeAdapter]) -> None:
        self._dependents = dependents
