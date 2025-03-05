from typing import Callable

from pydantic import BaseModel

from aiteamwork.llm_provider import LLMProviderContext
from aiteamwork.policies.provider_policy import ProviderPolicy
from aiteamwork.providers.openai import ValueOrProviderPolicy


class TokenCountCondition[ValueType](BaseModel):
    when: Callable[[int], bool]
    value: ValueOrProviderPolicy[ValueType]

    class Config:
        arbitrary_types_allowed = True


class SwitchWhenTokenCountProviderPolicy[ValueType](ProviderPolicy[ValueType]):

    _conditions: list[TokenCountCondition[ValueType]]
    _default: ValueOrProviderPolicy[ValueType]

    def __init__(
        self,
        conditions: list[TokenCountCondition[ValueType]],
        default: ValueOrProviderPolicy[ValueType],
    ) -> None:
        super().__init__()
        self._conditions = conditions
        self._default = default

    async def __call__(self, context: LLMProviderContext) -> ValueType:
        token_count = context.total_usage.total_tokens
        for condition in self._conditions:
            if condition.when(token_count):
                value = condition.value
                if isinstance(value, ProviderPolicy):
                    return await value(context)
                return value
        if isinstance(self._default, ProviderPolicy):
            return await self._default(context)
        return self._default
