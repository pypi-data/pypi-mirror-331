from abc import ABC, abstractmethod
from typing import Self, Union
from aiteamwork.llm_context import LLMContext
from pydantic import BaseModel, ConfigDict, TypeAdapter


class SerializableProducer(ABC):

    @abstractmethod
    def get_dependents(self) -> list[Union["SerializableProducer", type[BaseModel], TypeAdapter]]:
        """
        Get the dependents of the current agent.

        This method must be overridden by subclasses.
        """
        raise NotImplementedError("This method must be overridden by subclasses")

    @abstractmethod
    def set_dependents(self, dependents: list[Union["SerializableProducer", type[BaseModel], TypeAdapter]]) -> None:
        """
        Get the dependents of the current agent.

        This method must be overridden by subclasses.
        """
        raise NotImplementedError("This method must be overridden by subclasses")

    async def get_serialization_models(self, context: LLMContext) -> list[type[BaseModel] | TypeAdapter]:
        result: list[type[BaseModel] | TypeAdapter] = []
        for dependent in self.get_dependents():
            if isinstance(dependent, SerializableProducer):
                result.extend(await dependent.get_serialization_models(context))
            else:
                result.append(dependent)
        return result

    def add_dependents(
        self,
        agent: (
            Union["SerializableProducer", type[BaseModel], TypeAdapter]
            | list[Union["SerializableProducer", type[BaseModel], TypeAdapter]]
        ),
    ) -> Self:
        """
        Add a dependent agent to the current agent. Makes sure all agents are properly validated during prompt runtime.

        This method must be overridden by subclasses.
        """

        dep_list = TypeAdapter[list[Union[SerializableProducer, type[BaseModel], TypeAdapter]]](
            list[Union[SerializableProducer, type[BaseModel], TypeAdapter]],
            config=ConfigDict(arbitrary_types_allowed=True),
        ).validate_python(
            agent if isinstance(agent, list) else [agent],
        )
        for dep in dep_list:
            if dep == self:
                raise ValueError("An agent cannot be dependent on itself.")

            deps = [*self.get_dependents()]
            if dep not in deps:
                deps.append(dep)
                self.set_dependents(deps)
        return self
