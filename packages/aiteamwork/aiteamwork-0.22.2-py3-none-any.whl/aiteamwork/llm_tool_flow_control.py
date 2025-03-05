from typing import final

from aiteamwork.llm_message import LLMMessage


@final
class LLMToolFlowControl:
    _new_messages: list[LLMMessage]
    _state_changes: dict
    _requires_reprompt: bool

    def __init__(self) -> None:
        self._new_messages = []
        self._state_changes = {}
        self._requires_reprompt = True

    @property
    def new_messages(self) -> list[LLMMessage]:
        return self._new_messages.copy()

    @property
    def should_reprompt(self) -> bool:
        return self._requires_reprompt

    def append_message(self, message: LLMMessage) -> "LLMToolFlowControl":
        self._new_messages.append(message)
        return self

    def skip_reprompt(self) -> "LLMToolFlowControl":
        self._requires_reprompt = False
        return self

    def request_reprompt(self) -> "LLMToolFlowControl":
        self._requires_reprompt = True
        return self

    def update_state(self, state_changes: dict) -> "LLMToolFlowControl":
        self._state_changes.update(state_changes)
        return self

    @property
    def state_changes(self) -> dict:
        return self._state_changes.copy()

    @property
    def has_state_changes(self) -> bool:
        return len(self._state_changes) > 0
