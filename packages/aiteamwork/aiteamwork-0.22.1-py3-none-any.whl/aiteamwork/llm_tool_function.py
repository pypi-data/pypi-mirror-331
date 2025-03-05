import inspect
from functools import cached_property, wraps
from inspect import Parameter, signature
from typing import Any, Callable, Coroutine, Literal, Self, Tuple, cast

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, create_model, model_validator

from aiteamwork.callbacks.human_in_the_loop import LLMHumanInTheLoopContext, LLMHumanInTheLoopResult
from aiteamwork.exceptions.llm_tool_call_failed_exception import ToolCallFailedException
from aiteamwork.llm_context import EmptyRuntimeContext, LLMContext  # noqa F401
from aiteamwork.llm_message import LLMMessage
from aiteamwork.llm_role import LLMRole
from aiteamwork.llm_tool_flow_control import LLMToolFlowControl
from aiteamwork.util.callable import SyncOrAsyncCallback
from aiteamwork.util.validators import (
    get_function_context_types,
    get_parameter_type_hint_from_function,
    validate_and_raise_adapter,
    validate_and_raise_model,
    validate_not_none,
    validated_sync_async_callback,
)


class ToolInputWithHumanInteraction[HumanInputType](BaseModel):
    human_input: HumanInputType = Field()


class LLMToolContext[InputType: BaseModel | ToolInputWithHumanInteraction | None, RuntimeContextType: BaseModel](
    LLMContext[RuntimeContextType]
):
    """Context of the LLM Tool. Passed down to tools."""

    messages: list[LLMMessage]
    """List of new messages in the conversation."""
    flow_control: LLMToolFlowControl
    """Flow control object for the tool. Used to control the flow of the conversation.
    Use this to append new messages, skip reprompt or require reprompt after the tool is called."""
    input: InputType
    """Input arguments for the tool."""
    input_raw: dict
    """Raw input arguments for the tool, as a dict."""


class LLMToolFunctionDefinitionSchema(BaseModel):
    input_argument: type[BaseModel] | None = Field(description="Schema for the input.", default=None)
    return_type_annotation: Any = Field(description="Schema for the output.")
    context_argument: type[LLMToolContext] | None = Field(description="Schema for the tool context.", default=None)
    name: str = Field(description="Name of the tool function.", min_length=6, max_length=64)
    method_docstring: str = Field(description="Description of the tool function.", min_length=8, max_length=256)

    class Config:
        arbitrary_types_allowed = True


class LLMToolRetryPolicy(BaseModel):
    retries: list[int] = Field(
        description="List of retry intervals in milliseconds.", default_factory=lambda: [100, 200, 500]
    )
    on_failure: Callable[[ToolCallFailedException], None] = Field(
        description="Callback on failure.",
        default=lambda _: None,
    )
    reply_on_failure: str | Callable[[ToolCallFailedException], list[LLMMessage]] | None = Field(
        description="Reply to send when the .", default=None
    )

    @cached_property
    def run_on_failure(self) -> Callable[[ToolCallFailedException], Coroutine[None, None, None]]:
        return validated_sync_async_callback(
            TypeAdapter[None](None),
            ["exception"],
            "on_failure",
            self.on_failure,
        )

    @cached_property
    def run_reply_on_failure(
        self,
    ) -> Callable[[ToolCallFailedException], Coroutine[None, None, list[LLMMessage]]] | None:
        if not self.reply_on_failure:
            return None

        if isinstance(self.reply_on_failure, str):
            return validated_sync_async_callback(
                TypeAdapter[list[LLMMessage]](list[LLMMessage]),
                ["exception"],
                "reply_on_failure",
                lambda e: [
                    LLMMessage(
                        role=LLMRole.AGENT, content=cast(str, self.reply_on_failure), authors=e.messages[-1].authors
                    )
                ],
            )

        return validated_sync_async_callback(
            TypeAdapter[list[LLMMessage]](list[LLMMessage]),
            ["exception"],
            "reply_on_failure",
            cast(Callable[[ToolCallFailedException], list[LLMMessage]], self.reply_on_failure),
        )


def with_llm_tool_retry_policy(retry_policy: LLMToolRetryPolicy):
    if retry_policy is None or not isinstance(retry_policy, LLMToolRetryPolicy):
        raise ValueError("retry_policy must be an instance of LLMToolRetryPolicy")

    def decorator(tool: SyncOrAsyncCallback):
        if not callable(tool):
            raise ValueError("tool must be a callable")

        @wraps(tool)
        def wrapper(*args, **kwds):
            return tool(*args, **kwds)

        wrapper.__annotations__.update({"retry_policy": retry_policy})
        return wrapper

    return decorator


class LLMToolHumanInTheLoop[ToolArgsType: BaseModel, ArtifactType: BaseModel | None, RuntimeContextType: BaseModel](
    BaseModel
):
    confirmation_artifact: (
        SyncOrAsyncCallback[
            [LLMHumanInTheLoopContext[ToolArgsType, RuntimeContextType]], LLMHumanInTheLoopResult[ArtifactType]
        ]
        | ArtifactType
        | None
    ) = Field(default=None)
    """Content shown to the user."""

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode="after")
    def _validate(self) -> Self:
        validate_not_none(self.runtime_schema)
        validate_not_none(self.get_confirmation_artifact)
        return self

    @cached_property
    def runtime_schema(self) -> type[BaseModel]:
        if not self.confirmation_artifact or not callable(self.confirmation_artifact):
            return EmptyRuntimeContext

        _context, runtime_context_type = get_function_context_types(
            LLMHumanInTheLoopContext,
            LLMHumanInTheLoopContext[BaseModel, EmptyRuntimeContext],
            self.confirmation_artifact,
        )
        return runtime_context_type

    @cached_property
    def get_confirmation_artifact(
        self,
    ) -> Callable[
        [LLMHumanInTheLoopContext[ToolArgsType, RuntimeContextType]],
        Coroutine[None, None, LLMHumanInTheLoopResult[ArtifactType]],
    ]:
        if not callable(self.confirmation_artifact):
            value = cast(ArtifactType, self.confirmation_artifact)

            async def factory(
                context: LLMHumanInTheLoopContext[ToolArgsType, RuntimeContextType]
            ) -> LLMHumanInTheLoopResult[ArtifactType]:
                return LLMHumanInTheLoopResult[ArtifactType](artifact=value)

            return factory

        return validated_sync_async_callback(
            LLMHumanInTheLoopResult,
            ["context"],
            "confirmation_artifact",
            self.confirmation_artifact,
        )

    def validate_configuration(self, runtime_context: Any) -> None:
        self.runtime_schema.model_validate(runtime_context)


def with_llm_tool_human_in_the_loop(human_in_the_loop_config: LLMToolHumanInTheLoop):
    if human_in_the_loop_config is None or not isinstance(human_in_the_loop_config, LLMToolHumanInTheLoop):
        raise ValueError("human_in_the_loop_config must be an instance of LLMToolHumanInTheLoop")

    def decorator(tool: SyncOrAsyncCallback):
        if not callable(tool):
            raise ValueError("tool must be a callable")

        @wraps(tool)
        def wrapper(*args, **kwds):
            return tool(*args, **kwds)

        wrapper.__annotations__.update({"human_in_the_loop": human_in_the_loop_config})
        return wrapper

    return decorator


def wrap_into_tool_function[
    Args, ReturnType
](
    fn: Callable[[Args], ReturnType],
    fallback_param_types: dict[str, type] | None = None,
    fallback_description: str | None = None,
) -> Callable:
    fallback_param_types = fallback_param_types or {}
    signature = inspect.signature(fn)
    ContextType = LLMToolContext
    if signature.parameters:
        params: list[tuple[Literal["prop"], Parameter]] = []

        for param_name, param in signature.parameters.items():
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                raise ValueError("Tool function arguments cannot be positional-only.")
            if param_name.startswith("__"):
                raise ValueError("Tool function arguments cannot start with '__'.")
            param_type = fallback_param_types.get(param_name) or param.annotation
            if param_type == inspect.Parameter.empty or not param_type:
                raise ValueError(
                    "All tool function arguments must have type annotations or be provided in fallback_param_types."
                )

            params.append((cast(Literal["prop"], param_name), param.replace(annotation=param_type)))

        prop_map = cast(
            dict[Literal["prop"], tuple[type, Any]], {name: (param.annotation, Field()) for name, param in params}
        )

        input_type = create_model("InputType", **prop_map, __config__=ConfigDict(arbitrary_types_allowed=True))

        ContextType = LLMToolContext[input_type, EmptyRuntimeContext]

    def tool_function(context: ContextType) -> Any:
        input = cast(BaseModel, cast(LLMToolContext, context).input).model_dump(mode="python")
        return cast(Callable, fn)(**input)

    tool_function.__name__ = fn.__name__
    tool_function.__doc__ = fallback_description or fn.__doc__

    return tool_function


class LLMToolFunctionDefinition:
    """
    Represents a tool function definition.
    """

    argument: type[BaseModel] | None
    input_schema: type[BaseModel] | None
    output_schema: TypeAdapter
    output_annotation: type
    tool_context_schema: type[BaseModel] | None
    name: str
    description: str
    tool_function: SyncOrAsyncCallback
    retry_policy: LLMToolRetryPolicy
    human_in_the_loop: LLMToolHumanInTheLoop | None
    parameters_json_schema: dict[str, object] | None
    metadata: dict[str, Any] = {}
    bound_parameters: dict[str, Any] = {}

    def __init__(
        self,
        tool: SyncOrAsyncCallback,
        retry_policy: LLMToolRetryPolicy | None = None,
        human_in_the_loop: LLMToolHumanInTheLoop | None = None,
        name: str | None = None,
        parameters_json_schema: dict[str, Any] | None = None,
        description: str | None = None,
        metadata: dict[str, Any] = {},
        bound_parameters: dict[str, Any] = {},
    ) -> None:
        tool_signature = signature(tool)
        parameters = tool_signature.parameters
        return_arg = tool_signature.return_annotation
        tool_name = name or tool.__name__
        docstring = description or tool.__doc__
        context_arg = parameters.get("context")
        input_arg: None | type[BaseModel] = None

        if return_arg == inspect.Parameter.empty or return_arg is None:
            raise ValueError("A non None return type annotation is required")

        if context_arg:
            if not issubclass(context_arg.annotation, LLMToolContext):
                raise ValueError('An argument named "context" with a subtype of LLMToolContext is required.')

            tool_context_type = get_function_context_types(LLMToolContext, LLMToolContext, tool)[0]
            input_type = get_parameter_type_hint_from_function(tool_context_type, "input", dict)

            if input_type:
                if not issubclass(input_type, BaseModel) and input_type != dict:
                    raise ValueError(
                        'The LLMToolContext "InputType" generic first parameter must be a '
                        "subtype of pydantic.BaseModel, "
                        "a subtype of ToolInputWithHumanInteraction, "
                        "equal to dict or equal to None."
                    )
                if input_type != dict:
                    input_arg = input_type

        data = {
            "input_argument": input_arg,
            "return_type_annotation": return_arg,
            "context_argument": context_arg.annotation if context_arg else None,
            "name": tool_name,
            "method_docstring": docstring,
        }

        validated = validate_and_raise_model(
            LLMToolFunctionDefinitionSchema,
            data,
            lambda: ValueError("Invalid tool function schema."),
            lambda e: ValueError(f"Invalid tool function data: {e}"),
        )

        self.input_schema = validated.input_argument
        self.output_schema = TypeAdapter(validated.return_type_annotation)
        self.output_annotation = validated.return_type_annotation
        self.tool_context_schema = validated.context_argument
        self.name = validated.name
        self.description = validated.method_docstring
        self.tool_function = tool
        self.parameters_json_schema = TypeAdapter(dict[str, object] | None).validate_python(parameters_json_schema)
        self.metadata = {
            **TypeAdapter[dict](dict).validate_python(metadata),
        }
        self.bound_parameters = {
            **TypeAdapter[dict](dict).validate_python(bound_parameters),
        }

        retry_policy_from_annotation = tool.__annotations__.get("retry_policy")
        if retry_policy_from_annotation and not isinstance(retry_policy_from_annotation, LLMToolRetryPolicy):
            raise ValueError("Invalid retry policy annotation, must be an instance of LLMToolRetryPolicy.")

        self.retry_policy = retry_policy or retry_policy_from_annotation or LLMToolRetryPolicy()

        human_in_the_loop_from_annotation = tool.__annotations__.get("human_in_the_loop")
        if human_in_the_loop_from_annotation and not isinstance(
            human_in_the_loop_from_annotation, LLMToolHumanInTheLoop
        ):
            raise ValueError("Invalid human in the loop annotation, must be an instance of LLMToolHumanInTheLoop.")

        self.human_in_the_loop = human_in_the_loop or human_in_the_loop_from_annotation

        if (
            self.human_in_the_loop
            and self.input_schema
            and not issubclass(self.input_schema, ToolInputWithHumanInteraction)
        ):
            raise ValueError(
                "Tools with Human in the loop must have an input schema that is a subclass "
                "of ToolInputWithHumanInteraction."
            )

    def validate_configuration(self, runtime_context: Any) -> None:
        """
        Validate the configuration of the tool function.
        """
        if self.tool_context_schema:
            runtime_context_type = validate_not_none(
                inspect.signature(self.tool_context_schema).parameters.get("runtime_context")
            ).annotation

            if inspect.isclass(runtime_context_type):
                validate_and_raise_model(
                    runtime_context_type,
                    runtime_context,
                    lambda: ValueError("Invalid runtime context schema."),
                    lambda e: ValueError(f"Invalid runtime context data: {e}"),
                )
        if self.human_in_the_loop:
            self.human_in_the_loop.validate_configuration(runtime_context)

    def get_parsed_input(self, raw_input: Any, human_input: Any | None = None) -> BaseModel | None:
        parsed_input: BaseModel | None = None

        if self.tool_context_schema:
            if self.input_schema:
                data = {
                    **raw_input,
                }
                if human_input:
                    data["human_input"] = human_input

                parsed_input = validate_and_raise_model(
                    self.input_schema,
                    data,
                    lambda: ValueError("Invalid input schema."),
                    lambda e: ValueError(f"Invalid input data: {e}"),
                )

        return parsed_input

    async def __call__(
        self, input: Any, human_input: Any | None, context: LLMContext, messages: list[LLMMessage]
    ) -> Tuple[Any, LLMToolFlowControl, BaseModel | dict | None]:
        args_dict: dict = {}
        input = {
            **input,
            **self.bound_parameters,
        }
        flow_control = LLMToolFlowControl()
        parsed_input = self.get_parsed_input(input, human_input)

        if self.tool_context_schema:
            args_dict["context"] = validate_and_raise_model(
                self.tool_context_schema,
                {
                    **context.model_dump(),
                    "messages": messages,
                    "flow_control": flow_control,
                    "input": parsed_input,
                    "input_raw": input,
                },
                lambda: ValueError("Invalid input schema."),
                lambda e: ValueError(f"Invalid input data: {e}"),
            )

        result_or_coroutine = self.tool_function(**args_dict)

        if inspect.isawaitable(result_or_coroutine):
            result = await result_or_coroutine
        else:
            result = result_or_coroutine

        if self.output_schema:
            output = validate_and_raise_adapter(
                self.output_schema,
                result,
                lambda: ValueError("Invalid output schema."),
                lambda e: ValueError(f"Invalid output data: {e}"),
            )

            try:
                self.output_schema.dump_json(output)
            except Exception as e:
                raise ValueError(f"Result data is not serializable: {e}")

            return (output, flow_control, parsed_input)

        raise ValueError("Output schema is not defined.")

    def get_input_json_schema(self) -> dict[str, object]:
        schema = {"additionalProperties": False, "type": "object", "properties": {}, "required": []}

        if self.parameters_json_schema:
            schema = self.parameters_json_schema
        elif self.input_schema:
            schema = self.input_schema.model_json_schema()

        schema["required"] = list(cast(dict, schema.get("properties", {})).keys())

        for param in self.bound_parameters:
            cast(dict, schema["properties"]).pop(param, None)
            if param in schema["required"]:
                schema["required"].remove(param)

        return schema

    def set_tool_retry_policy(self, retry_policy: LLMToolRetryPolicy) -> None:
        if retry_policy is None or not isinstance(retry_policy, LLMToolRetryPolicy):
            raise ValueError("retry_policy must be an instance of LLMToolRetryPolicy")

        self.retry_policy = retry_policy

    def copy(self) -> "LLMToolFunctionDefinition":
        return LLMToolFunctionDefinition(
            self.tool_function,
            self.retry_policy,
            (
                LLMToolHumanInTheLoop(
                    confirmation_artifact=self.human_in_the_loop.confirmation_artifact,
                )
                if self.human_in_the_loop
                else None
            ),
            self.name,
            self.parameters_json_schema,
            self.description,
            self.metadata,
        )

    def set_metadata(self, field: str, value: Any) -> None:
        self.metadata[field] = value

    def get_metadata(self, field: str) -> Any:
        return self.metadata.get(field)

    def bind_parameter(self, parameter_name: str, parameter_value: Any) -> None:
        self.bound_parameters[parameter_name] = parameter_value

    def unbind_parameter(self, parameter_name: str) -> None:
        self.bound_parameters.pop(parameter_name, None)


__all__ = ["LLMToolFunctionDefinition", "LLMToolContext"]
