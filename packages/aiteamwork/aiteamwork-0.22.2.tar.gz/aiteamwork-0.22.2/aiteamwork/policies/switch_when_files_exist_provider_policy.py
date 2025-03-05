from aiteamwork.llm_provider import LLMProviderContext
from aiteamwork.policies.provider_policy import ProviderPolicy
from aiteamwork.providers.openai import ValueOrProviderPolicy


class SwitchWhenFilesExistProviderPolicy[ValueType](ProviderPolicy[ValueType]):
    _with_files: ValueOrProviderPolicy[ValueType]
    _without_files: ValueOrProviderPolicy[ValueType]

    def __init__(
        self, with_files: ValueOrProviderPolicy[ValueType], without_files: ValueOrProviderPolicy[ValueType]
    ) -> None:
        super().__init__()
        self._with_files = with_files
        self._without_files = without_files

    async def __call__(self, context: LLMProviderContext) -> ValueType:
        has_files = bool([msg for msg in context.messages if msg.files])
        if has_files:
            if isinstance(self._with_files, ProviderPolicy):
                return await self._with_files(context)
            else:
                return self._with_files
        if isinstance(self._without_files, ProviderPolicy):
            return await self._without_files(context)
        else:
            return self._without_files
