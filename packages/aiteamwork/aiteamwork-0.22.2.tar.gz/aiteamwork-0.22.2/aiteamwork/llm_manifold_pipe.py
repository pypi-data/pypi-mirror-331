import asyncio
from typing import Any

from pydantic import BaseModel, TypeAdapter, create_model

from aiteamwork.callbacks.pipe import LLMPipeContext, LLMPipeResult
from aiteamwork.llm_pipe import LLMPipe
from aiteamwork.serializable_producer import SerializableProducer
from aiteamwork.util.callable import SyncOrAsyncCallback
from aiteamwork.util.validators import validated_sync_async_callback


class LLMManifoldPipe(LLMPipe):

    runtime_schemas: list[tuple[type[BaseModel], SyncOrAsyncCallback[[LLMPipeContext], None]]]

    def __init__(
        self,
        pipe_functions: list[SyncOrAsyncCallback[[LLMPipeContext], None]],
        pipe_name: str | None = None,
        dependents: list[SerializableProducer | type[BaseModel] | TypeAdapter] | None = None,
    ) -> None:
        self.runtime_schemas = []
        validated_functions = [
            validated_sync_async_callback(TypeAdapter[None](None), ["context"], "pipe_function", pipe_fn)
            for pipe_fn in pipe_functions
        ]

        self.runtime_schemas = [
            (self._extract_schemas_from_function(pipe_fn)[1], pipe_fn) for pipe_fn in pipe_functions
        ]

        self._combined_runtime_schema = create_model(
            "ManifoldCombinedRuntimeContext", __base__=tuple(set([schema[0] for schema in self.runtime_schemas]))
        )

        async def combined_fn(context: LLMPipeContext) -> LLMPipeResult:
            messages_to_check_consistency = context.prompt_result.messages.copy()

            await asyncio.gather(*[fn(context) for fn in validated_functions])

            for message in context.prompt_result.messages:
                if message not in messages_to_check_consistency:
                    raise ValueError(
                        "Manifold pipe functions must not add or remove messages in the result object (editing is OK)"
                    )

            return LLMPipeResult(prompt_result=context.prompt_result)

        super().__init__(combined_fn, pipe_name or "unnamed manifold pipe", dependents)

    def _setup_schemas(self, pipe_fn: SyncOrAsyncCallback[[LLMPipeContext], None]) -> None:
        self._context_schema = LLMPipeContext
        self._runtime_context_schema = self._combined_runtime_schema

    def get_pipe_type(self) -> str:
        return "Manifold Pipe"

    def validate_configuration(self, runtime_context: Any) -> None:
        for schema, _pipe_fn in self.runtime_schemas:
            schema.model_validate(runtime_context)
