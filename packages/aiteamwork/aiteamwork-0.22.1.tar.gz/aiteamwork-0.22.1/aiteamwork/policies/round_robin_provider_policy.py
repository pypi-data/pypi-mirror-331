from aiteamwork.llm_provider import LLMProviderContext
from aiteamwork.policies.provider_policy import ProviderPolicy
from aiteamwork.providers.openai import ValueOrProviderPolicy


class RoundRobinProviderPolicy[ValueType](ProviderPolicy[ValueType]):
    _values: list[ValueOrProviderPolicy[ValueType]]
    _counter: int

    def __init__(self, values: list[ValueOrProviderPolicy[ValueType]]) -> None:
        super().__init__()
        self._values = values
        self._counter = 0

    async def __call__(self, context: LLMProviderContext) -> ValueType:
        value = self._values[self._counter]
        self._counter = (self._counter + 1) % len(self._values)
        if isinstance(value, ProviderPolicy):
            return await value(context)
        return value
