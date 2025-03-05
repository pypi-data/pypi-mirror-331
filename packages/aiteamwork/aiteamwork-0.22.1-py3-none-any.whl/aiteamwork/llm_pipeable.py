from abc import ABC, abstractmethod
from typing import Callable, Self, cast

from pydantic import BaseModel, ConfigDict, TypeAdapter

from aiteamwork.callbacks.pipe import LLMPipeContext, LLMPipeResult
from aiteamwork.llm_manifold_pipe import LLMManifoldPipe
from aiteamwork.llm_pipe import LLMPipe
from aiteamwork.serializable_producer import SerializableProducer
from aiteamwork.util.validators import SyncOrAsyncCallback


class LLMPipeable(ABC):

    def pipe(
        self,
        callable_or_pipe: (
            SyncOrAsyncCallback[[LLMPipeContext], LLMPipeResult]
            | list[SyncOrAsyncCallback[[LLMPipeContext], None]]  # noqa: W503
            | LLMPipe  # noqa: W503
        ),
        pipe_name: str | None = None,
        dependents: list[SerializableProducer | type[BaseModel] | TypeAdapter] | None = None,
    ) -> Self:
        """
        Pipe the output of one process to another. Transoforming the output.

        This method must be overridden by subclasses.
        """

        callable_or_pipe = TypeAdapter[Callable | list[Callable] | LLMPipe](
            Callable | list[Callable] | LLMPipe, config=ConfigDict(arbitrary_types_allowed=True)
        ).validate_python(callable_or_pipe)

        current_pipe = self.get_pipe()

        if isinstance(callable_or_pipe, LLMPipe):
            if current_pipe:
                current_pipe.pipe(cast(LLMPipe, callable_or_pipe))
            else:
                self.set_pipe(callable_or_pipe)
        elif isinstance(callable_or_pipe, list):
            if current_pipe:
                current_pipe.pipe(LLMManifoldPipe(callable_or_pipe, pipe_name, dependents or []))
            else:
                self.set_pipe(LLMManifoldPipe(callable_or_pipe, pipe_name, dependents or []))
        elif callable(callable_or_pipe):
            if current_pipe:
                current_pipe.pipe(LLMPipe(callable_or_pipe, pipe_name, dependents or []))
            else:
                self.set_pipe(LLMPipe(callable_or_pipe, pipe_name, dependents or []))
        else:
            raise ValueError("Invalid pipe or callable.")

        return self

    @abstractmethod
    def get_pipe(self) -> LLMPipe | None:
        """
        Get the pipe of the current agent.

        This method must be overridden by subclasses.
        """
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    def set_pipe(self, pipe: LLMPipe) -> None:
        """
        Get the pipe of the current agent.

        This method must be overridden by subclasses.
        """
        raise NotImplementedError("This method must be overridden by subclasses")
