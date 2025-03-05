from typing import Any, Callable, Coroutine

from pydantic import TypeAdapter, BaseModel

from aiteamwork.llm_provider import LLMProviderContext
from aiteamwork.policies.provider_policy import ProviderPolicy
from aiteamwork.util.validators import SyncOrAsyncCallback, get_function_context_types, validated_sync_async_callback

type CustomProviderPolicyFactorySync[ValueType] = Callable[[LLMProviderContext], ValueType]
type CustomProviderPolicyFactoryAsync[ValueType] = Callable[[LLMProviderContext], Coroutine[None, None, ValueType]]


class CustomProviderPolicy[ValueType](ProviderPolicy):

    _factory: Callable[[LLMProviderContext], Coroutine[None, None, ValueType]]
    _runtime_context_type: type[BaseModel]

    def __init__(self, factory: SyncOrAsyncCallback[[LLMProviderContext], ValueType]) -> None:
        super().__init__()

        _context_type, runtime_context_type = get_function_context_types(
            LLMProviderContext,
            LLMProviderContext,
            factory,
        )

        self._runtime_context_type = runtime_context_type
        self._factory = validated_sync_async_callback(
            TypeAdapter[Any](Any),
            ["context"],
            "factory",
            factory,
        )

    async def __call__(self, context: LLMProviderContext) -> ValueType:
        return await self._factory(context)

    def get_runtime_context_schema(self) -> type[BaseModel]:
        return self._runtime_context_type
