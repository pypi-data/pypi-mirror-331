import inspect
from typing import Any, Callable, Coroutine, TypeVar, cast

from pydantic import BaseModel, TypeAdapter, ValidationError

from aiteamwork.llm_context import EmptyRuntimeContext, LLMContext
from aiteamwork.util.callable import SyncOrAsyncCallback, SyncOrAsyncReturn


def validate_not_none[DataType](data: DataType | None, error: str | Exception | None = None) -> DataType:
    if data is None:
        if error:
            if isinstance(error, str):
                raise ValueError(error)
            else:
                raise error
        raise ValueError("Unexpected None value")

    return data


def validate_and_raise_model[
    ValidationModel: BaseModel
](
    model: type[ValidationModel],
    data: Any,
    bad_schema_wrapper: Callable[[], Exception],
    validation_wrapper: Callable[[ValidationError], Exception],
) -> ValidationModel:
    """
    Validate the data against the model and raise an exception if it is invalid.
    """

    if not issubclass(model, BaseModel) or model == BaseModel:
        raise bad_schema_wrapper()

    if inspect.isabstract(model):
        raise bad_schema_wrapper()

    try:
        return model.model_validate(data)
    except ValidationError as e:
        raise validation_wrapper(e) from e


def validate_and_raise_adapter[
    TypeAdapterType,
](
    model: TypeAdapter[TypeAdapterType],
    data: Any,
    bad_schema_wrapper: Callable[[], Exception],
    validation_wrapper: Callable[[ValidationError], Exception],
) -> TypeAdapterType:
    """
    Validate the data against the model and raise an exception if it is invalid.
    """

    if not isinstance(model, TypeAdapter):
        raise bad_schema_wrapper()

    try:
        return model.validate_python(data)
    except ValidationError as e:
        raise validation_wrapper(e) from e


def validated_sync_async_callback[
    **ContextArgs, ReturnType
](
    return_type: type[BaseModel] | TypeAdapter,
    parameters: list[str],
    callback_name: str,
    callback: SyncOrAsyncCallback[ContextArgs, ReturnType],  # noqa F821
) -> Callable[
    ContextArgs, Coroutine[None, None, ReturnType]  # noqa F821
]:
    # TODO: Wrap validation errors in proper custom exceptions

    # if callback is not a function, raise an error
    if not callable(callback):
        raise ValueError(f"Callback ({callback_name}) must be a function or callable")

    if inspect.isgeneratorfunction(callback):
        raise ValueError(f"Callback ({callback_name}) (function {callback.__name__}) must not be a generator function")

    callback_parameters = inspect.signature(callback).parameters

    if len(callback_parameters) != len(parameters):
        has_variadic_param = any([len(str(param).split("*")) == 2 for param in callback_parameters.values()])
        if not has_variadic_param:
            params_str = ", ".join(parameters)
            raise ValueError(
                f"Callback ({callback_name}) (function {callback.__name__}) must have the following parameters "
                f"(in this exact order): {params_str}"
            )

    async def new_callback(*args) -> ReturnType:
        result_or_coroutine = cast(SyncOrAsyncReturn[ReturnType], cast(Callable, callback)(*args))
        result: ReturnType
        if inspect.isawaitable(result_or_coroutine):
            result = await result_or_coroutine
        else:
            result = result_or_coroutine

        if isinstance(return_type, TypeAdapter):
            return cast(ReturnType, return_type.validate_python(result))
        elif issubclass(return_type, BaseModel):
            return cast(ReturnType, return_type.model_validate(result))
        else:
            raise ValueError(
                f"Callback ({callback_name}) (function {callback.__name__}) return type must be a subclass of "
                "pydantic.BaseModel or a pydantic.TypeAdapter"
            )

    return cast(
        Callable[ContextArgs, Coroutine[None, None, ReturnType]],  # noqa F821
        new_callback,
    )


def get_model_generic_type_hint(cls: type[BaseModel], property_name: str, default_type: type) -> type:
    if not inspect.isclass(cls):
        raise ValueError(f"{cls} is not a class")

    if issubclass(cls, BaseModel) is False:
        raise ValueError(f"{cls} is not a subclass of pyndatic.BaseModel")

    constructor_signature = inspect.signature(cls)
    property = validate_not_none(
        constructor_signature.parameters.get(property_name), f"Property {property_name} does not exist in {cls}"
    )
    property_type = property.annotation

    final_type: type = property_type

    while hasattr(final_type, "__origin__"):
        final_type = final_type.__origin__

    if isinstance(final_type, TypeVar):
        return default_type

    return final_type


def get_parameter_type_hint_from_function(fn: Callable, parameter_name: str, default_type: type) -> type:
    if callable(fn) is False:
        raise ValueError(f"{fn} is not a callable")

    signature = inspect.signature(fn)
    parameter = validate_not_none(
        signature.parameters.get(parameter_name), f"Parameter {parameter_name} does not exist in {fn}"
    )

    final_type: type = parameter.annotation

    if final_type is inspect.Parameter.empty or final_type is None:
        return default_type

    while hasattr(final_type, "__origin__"):
        final_type = final_type.__origin__

    if isinstance(final_type, TypeVar):
        return default_type

    return final_type


def get_function_context_types[
    ContextType: LLMContext,
    DefaultContextType: LLMContext,
](parent_context_type: type[ContextType], default_context_type: type[DefaultContextType], fn: Callable) -> tuple[
    type[ContextType], type[BaseModel]
]:
    if not issubclass(parent_context_type, LLMContext):
        raise ValueError("The parent_context_type parameter must be a subclass of LLMContext")
    if not issubclass(default_context_type, LLMContext):
        raise ValueError("The default_context_type parameter must be a subclass of LLMContext")
    if not issubclass(default_context_type, parent_context_type):
        raise ValueError("The default_context_type parameter must be a subclass of parent_context_type")

    context_schema: type[ContextType] = get_parameter_type_hint_from_function(fn, "context", default_context_type)

    if not issubclass(context_schema, parent_context_type):
        raise ValueError(f"The context parameter must have a type annotation of {parent_context_type.__name__}")

    runtime_context_schema = get_model_generic_type_hint(context_schema, "runtime_context", EmptyRuntimeContext)

    if not issubclass(runtime_context_schema, BaseModel):
        raise ValueError(
            "The runtime_context parameter must have a type annotation of pydantic.BaseModel or no annotation"
        )

    return context_schema, runtime_context_schema
