from abc import ABC, abstractmethod
from typing import Callable

from pydantic import BaseModel, TypeAdapter, ValidationError

from aiteamwork.llm_context import EmptyRuntimeContext
from aiteamwork.llm_provider import LLMProviderContext


class ProviderPolicy[ValueType](ABC):
    @abstractmethod
    async def __call__(self, context: LLMProviderContext) -> ValueType:
        raise NotImplementedError("This method must be overridden by subclasses")

    def get_runtime_context_schema(self) -> type[BaseModel]:
        return EmptyRuntimeContext

    @staticmethod
    async def value_with_model[
        ValidationModel: BaseModel
    ](
        value: "ValueOrProviderPolicy[ValueType]",
        context: LLMProviderContext,
        check_schema: type[ValidationModel],
        error_wrapper: Callable[[ValidationError], Exception],
    ) -> ValidationModel:
        try:
            if isinstance(value, ProviderPolicy):
                return check_schema.model_validate(await value(context.model_copy()))
            return check_schema.model_validate(value)
        except ValidationError as exc:
            raise error_wrapper(exc)

    @staticmethod
    async def value_with_adapter[
        TypeAdapterType
    ](
        value: "ValueOrProviderPolicy[ValueType]",
        context: LLMProviderContext,
        check_schema: TypeAdapter[TypeAdapterType],
        error_wrapper: Callable[[ValidationError], Exception],
    ) -> TypeAdapterType:
        try:
            if isinstance(value, ProviderPolicy):
                return check_schema.validate_python(await value(context.model_copy()))
            return check_schema.validate_python(value)
        except ValidationError as exc:
            raise error_wrapper(exc)


type ValueOrProviderPolicy[ValueType] = ValueType | ProviderPolicy[ValueType]
