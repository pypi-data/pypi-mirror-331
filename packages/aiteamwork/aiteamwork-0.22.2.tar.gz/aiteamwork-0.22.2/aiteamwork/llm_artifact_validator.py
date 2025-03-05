from functools import cached_property
from logging import Logger
from typing import Any, Callable, Coroutine

from pydantic import BaseModel

from aiteamwork.callbacks.artifact_verification import LLMArtifactVerificationContext, LLMArtifactVerificationResult
from aiteamwork.exceptions.invalid_artifact_exception import InvalidArtifactException
from aiteamwork.llm_agent_usage import LLMAgentUsage
from aiteamwork.llm_context import EmptyRuntimeContext, LLMContext, cast
from aiteamwork.llm_message import LLMMessage
from aiteamwork.llm_provider import LLMProvider, LLMProviderContext
from aiteamwork.llm_role import LLMRole
from aiteamwork.llm_tool_function import LLMToolFunctionDefinition
from aiteamwork.util.validators import (
    SyncOrAsyncCallback,
    get_model_generic_type_hint,
    get_parameter_type_hint_from_function,
    validate_and_raise_model,
    validate_not_none,
    validated_sync_async_callback,
)


class LLMArtifactValidatorResult(BaseModel):
    artifact: Any
    usage: LLMAgentUsage

    class Config:
        arbitrary_types_allowed = True


class LLMArtifactValidator[RuntimeContextType: BaseModel, ArtifactType: BaseModel]:
    _messages: list[LLMMessage]
    _provider: LLMProvider
    _agent_id: str
    _agent_description: str
    _retries: int
    _round: int
    _context: LLMContext[RuntimeContextType]
    _tools: list[LLMToolFunctionDefinition]
    _tool_map: dict[str, LLMToolFunctionDefinition]
    _system_instructions: str
    _current_usage: LLMAgentUsage
    _new_usage: LLMAgentUsage
    _artifact_schema: type[BaseModel]
    _artifact_verification: (
        SyncOrAsyncCallback[
            [LLMArtifactVerificationContext[ArtifactType, RuntimeContextType]], LLMArtifactVerificationResult
        ]
        | None
    )
    _logger: Logger
    _artifact_verification_runtime_context: type[BaseModel]

    def __init__(
        self,
        agent_id: str,
        agent_description: str,
        system_instructions: str,
        tools: list[LLMToolFunctionDefinition],
        provider: LLMProvider,
        messages: list[LLMMessage],
        current_usage: LLMAgentUsage,
        context: LLMContext[RuntimeContextType],
        artifact_verification: (
            SyncOrAsyncCallback[
                [LLMArtifactVerificationContext[ArtifactType, RuntimeContextType]], LLMArtifactVerificationResult
            ]
            | None
        ),
        artifact_schema: type[BaseModel],
        round: int,
        logger: Logger,
        retries: int = 5,
    ) -> None:
        self._agent_id = agent_id
        self._agent_description = agent_description
        self._system_instructions = system_instructions
        self._provider = provider
        self._messages = messages.copy()
        self._context = context
        self._round = round
        self._retries = retries
        self._tools = tools
        self._tool_map = {tool.name: tool for tool in tools}
        self._current_usage = current_usage
        self._new_usage = LLMAgentUsage()
        self._artifact_verification = artifact_verification
        self._artifact_schema = artifact_schema
        self._logger = logger
        self._artifact_verification_runtime_context = self._extract_verification_runtime_schema(artifact_verification)

    @cached_property
    def _verify_artifact(
        self,
    ) -> Callable[
        [LLMArtifactVerificationContext[ArtifactType, RuntimeContextType]],
        Coroutine[None, None, LLMArtifactVerificationResult],
    ]:
        return validated_sync_async_callback(
            LLMArtifactVerificationResult,
            ["context"],
            "artifact_verification",
            self._artifact_verification or (lambda context: LLMArtifactVerificationResult(issues=[])),
        )

    @staticmethod
    def _extract_verification_runtime_schema(
        artifact_verification_fn: (
            SyncOrAsyncCallback[
                [LLMArtifactVerificationContext[ArtifactType, RuntimeContextType]], LLMArtifactVerificationResult
            ]
            | None
        ),
    ) -> type[BaseModel]:
        if artifact_verification_fn is None:
            return EmptyRuntimeContext

        context_schema: type[BaseModel] = get_parameter_type_hint_from_function(
            artifact_verification_fn, "context", LLMArtifactVerificationContext
        )

        if not issubclass(context_schema, LLMArtifactVerificationContext):
            raise ValueError("The context parameter must have a type annotation of LLMArtifactVerificationContext")

        runtime_context_schema = get_model_generic_type_hint(context_schema, "runtime_context", EmptyRuntimeContext)

        if not issubclass(runtime_context_schema, BaseModel):
            raise ValueError(
                "The runtime_context parameter must have a type annotation of pydantic.BaseModel or no annotation"
            )

        return runtime_context_schema

    async def _generate_new_artifact(
        self,
        exception: InvalidArtifactException,
        messages: list[LLMMessage],
    ) -> list[LLMMessage]:
        new_messages = messages.copy()

        issues_str = "\n".join([f"- {issue}" for issue in exception.issues])

        new_messages.append(
            LLMMessage(
                content=(
                    f"The last message contains errors. Please review it and try again.\n"
                    "Do not inform the user about this issue.\n\n"
                    "Issues: \n"
                    f"{issues_str}"
                ),
                role=LLMRole.SYSTEM,
                authors=[self._agent_id],
                hidden=True,
            )
        )

        runtime_context = validate_and_raise_model(
            self._provider.get_runtime_context_schema(),
            self._context.runtime_context.model_dump(mode="python"),
            lambda: ValueError("Invalid output schema."),
            lambda e: ValueError(f"Invalid output data: {e}"),
        )

        provider_result = await self._provider.prompt(
            context=LLMProviderContext(
                logger=self._logger,
                system_instructions=self._system_instructions,
                messages=new_messages,
                artifact_schema=self._artifact_schema,
                tools=self._tools,
                total_usage=self._new_usage + self._current_usage,
                attempt=self._round,
                runtime_context=runtime_context,
                current_agent=self._agent_id,
                user_id=self._context.user_id,
                conversation_id=self._context.conversation_id,
                assistant_name=self._context.assistant_name,
                agent_state=self._context.agent_state,
            ),
        )

        self._new_usage += provider_result.usage
        new_messages = new_messages + provider_result.new_messages
        return new_messages

    async def _handle_validation(
        self,
        messages: list[LLMMessage],
        retry: int = 0,
    ) -> LLMArtifactValidatorResult:
        try:
            last_message = validate_not_none(messages[-1])
            artifact: Any = validate_not_none(last_message.artifact)

            runtime_context = self._artifact_verification_runtime_context.model_validate(
                self._context.runtime_context.model_dump(mode="python")
            )

            context = LLMArtifactVerificationContext[
                self._artifact_schema, self._artifact_verification_runtime_context
            ].model_validate(
                {
                    **self._context.model_dump(mode="python"),
                    "runtime_context": runtime_context,
                    "artifact": artifact,
                }
            )

            result = await self._verify_artifact(
                cast(LLMArtifactVerificationContext, context),
            )
            issues = result.issues
            if not issues:
                return LLMArtifactValidatorResult(
                    artifact=artifact,
                    usage=self._new_usage,
                )
            else:
                issues_str = "\n".join([f"- {issue}" for issue in issues])
                self._logger.info(f"[LLM Agent {self._agent_id}] Validation failed. Issues found:\n{issues_str}")
                raise InvalidArtifactException(issues, f"Artifact validation failed: {issues}")
        except InvalidArtifactException as e:
            if retry < self._retries:
                self._logger.info(
                    f"[LLM Agent {self._agent_id}] Generating a new artifact and retrying... "
                    f"(attempt {retry + 1} of {self._retries})"
                )
                messages = await self._generate_new_artifact(
                    e,
                    messages,
                )
                return await self._handle_validation(
                    messages,
                    retry + 1,
                )
            raise e

    async def validate_artifact(
        self,
        messages: list[LLMMessage],
    ) -> LLMArtifactValidatorResult:
        """
        Validate the artifact using the provided tools.

        Args:
            artifact (ArtifactType): The artifact to validate.
        """

        self._logger.info(f"[LLM Agent {self._agent_id}] Validating produced artifact...")

        r = await self._handle_validation(messages)

        self._logger.info(f"[LLM Agent {self._agent_id}] Validation completed with success.")

        return r

    @classmethod
    def validate_configuration(
        cls,
        artifact_verification: (
            SyncOrAsyncCallback[[LLMArtifactVerificationContext], LLMArtifactVerificationResult] | None
        ),
        runtime_context: Any,
    ) -> None:
        if artifact_verification is None:
            return

        runtime_schema = cls._extract_verification_runtime_schema(artifact_verification)
        runtime_schema.model_validate(runtime_context)
