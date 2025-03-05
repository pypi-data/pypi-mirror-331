import json
from traceback import format_exc
from typing import Callable, Coroutine, Self, cast
from pydantic import BaseModel, TypeAdapter, model_validator
import yaml
import urllib.parse
from aiteamwork.agents.llm_agent import Any, Field
from aiteamwork.llm_context import EmptyRuntimeContext
from aiteamwork.llm_tool_function import LLMToolContext, LLMToolFunctionDefinition
from aiteamwork.util.validators import SyncOrAsyncCallback, validated_sync_async_callback
import aiohttp


class OpenAPIServer(BaseModel):
    url: str = Field()
    description: str | None = Field()


class OpenAPIServersList(BaseModel):
    servers: list[OpenAPIServer] = Field(default_factory=list)

    @property
    def first_server(self) -> str | None:
        if self.servers:
            return self.servers[0].url
        return None


class OpenAPIParameter(BaseModel):
    name: str = Field()
    description: str = Field(default="")
    in_: str = Field(alias="in")
    required: bool = Field(default=False)
    schema_: dict[str, Any] = Field(default_factory=dict, alias="schema")


class OpenAPIRequestContentDescription(BaseModel):
    schema_: dict[str, object] | None = Field(default=None, alias="schema")


class OpenAPIRequestBody(BaseModel):
    content: dict[str, OpenAPIRequestContentDescription] = Field(default_factory=dict)


class OpenAPIOperation(BaseModel):
    operationId: str | None = Field(default=None)
    summary: str | None = Field(default=None)
    description: str | None = Field(default=None)
    requestBody: OpenAPIRequestBody | None = Field(default=None)
    parameters: list[OpenAPIParameter] = Field(default_factory=list)

    @property
    def operation_name(self) -> str | None:
        summary = self.summary
        description = self.description
        operationId = self.operationId

        if summary and len(summary) < 8:
            summary = ""
        if description and len(description) < 8:
            description = ""

        name = summary or operationId or description

        if name:
            without_spaces = name.lower().strip().replace(" ", "_").replace("-", "_")
            without_non_alphanumeric = "".join(c for c in without_spaces if c.isalnum() or c == "_")
            without_repeated_underscores = without_non_alphanumeric.replace("__", "_")
            cropped = without_repeated_underscores[:64]
            remove_trainling_underscore = cropped.rstrip("_")
            return remove_trainling_underscore

        return None

    @model_validator(mode="after")
    def validate_props(self) -> Self:
        if self.description and len(self.description) > 255:
            self.description = self.description[:252] + "..."
        if self.summary and len(self.summary) > 255:
            self.summary = self.summary[:252] + "..."

        return self


class OpenAPIPath(BaseModel):
    get: OpenAPIOperation | None = Field(default=None)
    post: OpenAPIOperation | None = Field(default=None)
    put: OpenAPIOperation | None = Field(default=None)
    delete: OpenAPIOperation | None = Field(default=None)
    options: OpenAPIOperation | None = Field(default=None)
    head: OpenAPIOperation | None = Field(default=None)
    patch: OpenAPIOperation | None = Field(default=None)
    trace: OpenAPIOperation | None = Field(default=None)
    parameters: list[OpenAPIParameter] = Field(default_factory=list)


class OpenAPIPathsList(BaseModel):
    paths: dict[str, OpenAPIPath] = Field(default_factory=dict)


class SwaggerAPIHost(BaseModel):
    host: str | None = Field(default=None)
    basePath: str | None = Field(default=None)

    @property
    def server(self) -> str | None:
        if not self.host:
            return None
        return self.host + (self.basePath or "")


class OpenAPIComponent(BaseModel):
    schemas: dict[str, dict[str, Any]] = Field(default_factory=dict)


class OpenAPIComponentsList(BaseModel):
    components: OpenAPIComponent = Field(default_factory=OpenAPIComponent)


class SwaggerAPIDefinitionsList(BaseModel):
    definitions: dict[str, dict[str, Any]] = Field(default_factory=dict)


class OpenAPIConverterOptions(BaseModel):
    server: str | None = Field(
        description=(
            "Server URL to use for the OpenAPI spec. "
            "If not provided, the server URL will be extracted from the spec."
        ),
        examples=["https://api.example.com"],
        default=None,
    )
    resolve_type_refs: bool = Field(
        description="Whether to resolve type references in the OpenAPI spec.",
        default=True,
    )
    extra_headers: dict[str, str] = Field(
        description="Extra headers to send with the OpenAPI request.",
        default_factory=dict,
    )
    prefered_content_types: list[str] = Field(
        description="Preferred content type for the request.",
        default=["application/json"],
    )
    name_adjustment: SyncOrAsyncCallback[[str], str] = Field(
        description="Function to adjust the operation name.",
        default=lambda x: x,
    )
    filter_operations: SyncOrAsyncCallback[["OpenAPIOperationFilterContext"], bool] = Field(
        description="Function to filter operations included in the toolset.",
        default=lambda x: True,
    )
    add_method_data_warnings_to_description: bool = Field(
        description="Add warnings about wether an operation is destructive or not to the description.",
        default=True,
    )
    post_method_is_destructive: bool = Field(
        description="Whether POST method is considered destructive.",
        default=False,
    )


class OpenAPIOperationFilterContext(BaseModel):
    operation: OpenAPIOperation = Field()
    path: str
    path_data: OpenAPIPath
    method: str
    options: OpenAPIConverterOptions


async def __create_operation_function(
    operation: OpenAPIOperation,
    path: str,
    path_data: OpenAPIPath,
    method: str,
    server_url: str,
    schemas: dict[str, dict[str, Any]],
    options: OpenAPIConverterOptions,
    name_adjustment_fn: Callable[[str], Coroutine[None, None, str]],
) -> LLMToolFunctionDefinition | None:
    name = operation.operation_name

    if not name:
        return None

    name = await name_adjustment_fn(name)

    parameters = [*path_data.parameters, *operation.parameters]
    params_in_url = [param for param in parameters if param.in_ == "path"]
    params_in_query = [param for param in parameters if param.in_ == "query"]

    function_params_schema = {
        "additionalProperties": False,
        "type": "object",
        "properties": {},
        "required": [],
    }

    params_in_query_schema = {
        "additionalProperties": False,
        "type": "object",
        "properties": {},
        "required": [],
    }

    for param in params_in_url:
        if len(param.schema_) == 0:
            param.schema_ = {"type": "string"}
        function_params_schema["properties"][param.name] = param.schema_
        if param.required:
            function_params_schema["required"].append(param.name)

    for param in params_in_query:
        if len(param.schema_) == 0:
            param.schema_ = {"type": "string"}
        params_in_query_schema["properties"][param.name] = param.schema_
        params_in_query_schema["required"].append(param.name)
        if not param.required and "null" not in param.schema_["type"]:
            param.schema_["type"] = [param.schema_["type"], "null"]

    if params_in_query:
        function_params_schema["properties"]["query"] = params_in_query_schema
        function_params_schema["required"].append("query")

    if operation.requestBody:
        request_bodies_for_content_types = list(operation.requestBody.content.items())
        request_bodies_for_content_types.sort(
            key=lambda x: options.prefered_content_types.index(x[0]) if x[0] in options.prefered_content_types else 999
        )
        if request_bodies_for_content_types:
            operation_request_body = request_bodies_for_content_types[0]
            schema = operation_request_body[1].schema_
            if schema:
                function_params_schema["properties"]["request"] = schema
                function_params_schema["required"].append("request")

    if options.resolve_type_refs:
        function_params_schema = __resolve_type_refs(function_params_schema, schemas)
    else:
        function_params_schema["$defs"] = schemas

    async def tool(context: LLMToolContext[None, EmptyRuntimeContext]) -> Any:
        url = server_url + path
        input = context.input_raw
        query_params = input.get("query", {})
        query_params = {k: v for k, v in query_params.items() if v is not None}
        for param in params_in_url:
            url = url.replace(f"{{{param.name}}}", str(input[param.name]))

        json_input = input.get("request")
        logger = context.logger

        logger.info("[OpenAPI] Calling operation: %s (%s)", method.upper(), url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers={
                        **options.extra_headers,
                    },
                    params=query_params,
                    json=json_input,
                ) as response:
                    response.raise_for_status()
                    as_text = await response.text()

                    logger.info("[OpenAPI] Operation completed successfully: %s", method.upper())

                    content_type = response.headers.get("Content-Type", "")

                    if "application/json" in content_type:
                        return json.loads(as_text)
                    elif "application/yaml" in content_type or "application/x-yaml" in content_type:
                        return yaml.safe_load(as_text)
                    else:
                        return as_text
        except Exception as e:
            logger.error("[OpenAPI] Failed to run operation: %s (%s)", method.upper(), url)
            stacktrace = format_exc()
            logger.error(e)
            logger.error(stacktrace)
            raise e

    fn_description = operation.description or operation.summary or operation.operationId or ""

    if fn_description and options.add_method_data_warnings_to_description:
        if method in {"get", "head", "options"}:
            fn_description = f"[Fetches data] Get {fn_description}"
        elif method in {"put", "patch", "delete"} or (method == "post" and options.post_method_is_destructive):
            fn_description = f"[Modifies existing data] {fn_description}"

    fn_description = fn_description[:255]

    return LLMToolFunctionDefinition(
        tool=tool,
        name=name,
        description=operation.description or operation.summary or operation.operationId or "",
        parameters_json_schema=function_params_schema,
        metadata={
            "openapi_summary": operation.summary,
            "openapi_description": operation.description,
            "openapi_operationId": operation.operationId,
            "openapi_path": path,
            "openapi_method": method,
        },
    )


def __resolve_type_refs(
    json_schema: dict[str, object],
    definitions: dict[str, dict[str, object]] | None = None,
    parent: dict | None = None,
) -> dict:
    if not definitions:
        definitions = cast(dict, json_schema.get("$defs") or {})
        for property, property_value in definitions.items():
            definitions[property] = __resolve_type_refs(cast(dict, property_value), definitions)
        if "$defs" in json_schema:
            del json_schema["$defs"]

    schema_type = cast(str, json_schema.get("type"))

    if schema_type == "object" or "properties" in json_schema:
        properties = cast(dict, json_schema.get("properties"))
        if properties:
            for prop_name, prop_schema in properties.items():
                properties[prop_name] = __resolve_type_refs(prop_schema, definitions, json_schema)

    if schema_type == "array":
        items = cast(dict | None, json_schema.get("items"))
        if items is not None:
            if len(items) == 0:
                del json_schema["items"]
            elif items:
                json_schema["items"] = __resolve_type_refs(items, definitions, json_schema)

    if "$ref" in json_schema:
        ref_path: str = cast(str, json_schema["$ref"])
        ref_name = ref_path.split("/")[-1]
        definition = definitions[ref_name]

        for property, property_value in definition.items():
            json_schema[property] = property_value

        del json_schema["$ref"]
        __resolve_type_refs(json_schema, definitions, json_schema)

    return json_schema


async def convert_openapi_spec_to_tools(
    spec: dict[str, object],
    options: OpenAPIConverterOptions | None = None,
    spec_url: str | None = None,
) -> list[LLMToolFunctionDefinition]:
    options = TypeAdapter[OpenAPIConverterOptions](OpenAPIConverterOptions).validate_python(options or {})

    host_from_spec = ""
    if spec_url:
        host_from_spec = urllib.parse.urlparse(spec_url)
        host_from_spec = host_from_spec._replace(query="", path="")
        server_host = host_from_spec.geturl()

        if "host" in spec and not spec["host"]:
            spec["host"] = server_host

    server_url = (
        options.server
        or OpenAPIServersList.model_validate(spec).first_server
        or SwaggerAPIHost.model_validate(spec).server
    )

    if not server_url:
        raise ValueError("Server URL not found in OpenAPI spec. Pass one in the options.")

    schemas = {
        **OpenAPIComponentsList.model_validate(spec).components.schemas,
        **SwaggerAPIDefinitionsList.model_validate(spec).definitions,
    }

    if options.resolve_type_refs:
        for schema_name, schema in schemas.items():
            schemas[schema_name] = __resolve_type_refs(schema, schemas)

    paths = OpenAPIPathsList.model_validate(spec).paths
    tools: list[LLMToolFunctionDefinition] = []
    tool_names: set[str] = set()

    methods = [
        "get",
        "post",
        "put",
        "delete",
        "options",
        "head",
        "patch",
        "trace",
    ]

    filter_operations = validated_sync_async_callback(
        TypeAdapter[bool](bool),
        ["context"],
        "filter_operations",
        options.filter_operations,
    )

    name_adjustment_fn = validated_sync_async_callback(
        TypeAdapter[str](str),
        ["name"],
        "name_adjustment",
        options.name_adjustment,
    )

    for path, path_data in paths.items():

        methods_data = cast(
            list[tuple[str, OpenAPIOperation]],
            [d for d in [(method, getattr(path_data, method, None)) for method in methods] if d[1]],
        )

        for method, operation in methods_data:
            should_created_context = OpenAPIOperationFilterContext(
                operation=operation,
                path=path,
                path_data=path_data,
                method=method,
                options=options,
            )
            if await filter_operations(should_created_context):
                operation_function = await __create_operation_function(
                    operation,
                    path,
                    path_data,
                    method,
                    server_url,
                    schemas,
                    options,
                    name_adjustment_fn,
                )
                if operation_function and operation_function.name not in tool_names:
                    tools.append(operation_function)
                    tool_names.add(operation_function.name)

    return tools


async def convert_openapi_spec_url_to_tools(
    url: str,
    options: OpenAPIConverterOptions | None = None,
) -> list[LLMToolFunctionDefinition]:
    options = TypeAdapter(OpenAPIConverterOptions | None).validate_python(options)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            spec_str = await response.text()
            parsed_url = urllib.parse.urlparse(url.lower().strip())
            if parsed_url.path.endswith(".json"):
                spec = json.loads(spec_str)
            elif parsed_url.path.endswith(".yaml") or parsed_url.path.endswith(".yml"):
                spec = yaml.safe_load(spec_str)
            else:
                raise ValueError(f"Unsupported file format in URL (must be json or yaml/yml): {url}")

            return await convert_openapi_spec_to_tools(spec, options, url)
