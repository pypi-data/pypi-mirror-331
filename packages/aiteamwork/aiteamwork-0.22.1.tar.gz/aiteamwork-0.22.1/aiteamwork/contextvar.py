import contextvars

from aiteamwork.llm_agent_usage import LLMAgentUsage
from aiteamwork.llm_context import LLMContext

AGENT_USAGE_CONTEXT_VAR = contextvars.ContextVar[LLMAgentUsage | None]("AGENT_USAGE_CONTEXT_VAR", default=None)
LLM_CONTEXT_CONTEXT_VAR = contextvars.ContextVar[LLMContext | None]("LLM_CONTEXT_CONTEXT_VAR", default=None)


def get_agent_usage() -> LLMAgentUsage | None:
    """
    Get the current agent usage.
    """
    return AGENT_USAGE_CONTEXT_VAR.get()


def set_agent_usage(usage: LLMAgentUsage | None) -> None:
    """
    Set the current agent usage.
    """
    AGENT_USAGE_CONTEXT_VAR.set(usage)


def get_llm_context() -> LLMContext | None:
    """
    Get the current agent usage.
    """
    return LLM_CONTEXT_CONTEXT_VAR.get()


def set_llm_context(context: LLMContext | None) -> None:
    """
    Set the current agent usage.
    """
    LLM_CONTEXT_CONTEXT_VAR.set(context)
