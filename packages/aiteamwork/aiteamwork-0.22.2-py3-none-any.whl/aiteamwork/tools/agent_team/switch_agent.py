from typing import TypedDict
from pydantic import BaseModel, Field
from aiteamwork.llm_agent_like import Callable, LLMAgentLike
from aiteamwork.llm_context import EmptyRuntimeContext
from aiteamwork.llm_file import validate_not_none
from aiteamwork.llm_role import LLMRole
from aiteamwork.llm_tool_function import LLMToolContext


class AgentSwitchRequest(TypedDict):
    new_agent: str
    old_agent: str


class AgentSwitchFailedError(Exception):
    current_agent: str
    new_agent: str

    def __init__(self, reason: str, current_agent: str, new_agent: str):
        super().__init__(reason)
        self.current_agent = current_agent
        self.new_agent = new_agent


class AgentSwitchInput(BaseModel):
    agent_to_pass_name: str = Field(
        description=("The name of the agent to transfer the conversation as " "passed in the agent list")
    )


def get_switch_agent_tool(get_agents: Callable[[], dict[str, LLMAgentLike]]) -> Callable:

    async def switch_agent(
        context: LLMToolContext[AgentSwitchInput, EmptyRuntimeContext],
    ) -> AgentSwitchRequest:
        """Pass the conversation to another agent"""
        agents = get_agents()
        agent_to_pass_name = context.input.agent_to_pass_name
        current_agent = validate_not_none(context.current_agent)
        new_agent_impl = agents.get(agent_to_pass_name)

        context.logger.info(f'[LLM Agent {context.current_agent}] Requested an agent switch to "{agent_to_pass_name}"')

        if context.messages:
            last_message = context.messages[-1]
            if last_message.role == LLMRole.SYSTEM and last_message.purpose == "agent_switch":
                raise AgentSwitchFailedError(
                    (
                        "You are not allowed to switch right after an the conversation was passed, "
                        "answer the user with existing knowledge."
                    ),
                    current_agent=current_agent,
                    new_agent=agent_to_pass_name,
                )

        if not new_agent_impl:
            raise AgentSwitchFailedError(
                (f"Failed, there is no agent called: {agent_to_pass_name}, " "cant pass the conversation, try again."),
                current_agent=current_agent,
                new_agent=agent_to_pass_name,
            )

        agent_impl = agents.get(current_agent)

        if not agent_impl:
            raise AgentSwitchFailedError(
                (f"Failed, there is no agent called: {agent_to_pass_name}, " "incorrect current agent passed"),
                current_agent=current_agent,
                new_agent=agent_to_pass_name,
            )

        return {
            "new_agent": agent_to_pass_name,
            "old_agent": current_agent,
        }

    return switch_agent
