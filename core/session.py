"""Bounded in-memory conversation history for the current process."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationMessage:
    """A single normalized conversation message passed between core and providers."""

    role: str
    content: str


class Session:
    """In-memory bounded session history for the current process."""

    def __init__(self, max_messages: int) -> None:
        if max_messages <= 0:
            raise ValueError("max_messages must be greater than zero")
        self.max_messages = max_messages
        self._messages: list[ConversationMessage] = []

    @property
    def messages(self) -> tuple[ConversationMessage, ...]:
        """Return an immutable snapshot of the current session history."""

        return tuple(self._messages)

    def add(self, role: str, content: str) -> None:
        """Append a message and trim history to the configured maximum."""

        if role not in {"user", "assistant"}:
            raise ValueError("role must be 'user' or 'assistant'")
        if not content:
            raise ValueError("content must not be empty")

        self._messages.append(ConversationMessage(role=role, content=content))
        overflow = len(self._messages) - self.max_messages
        if overflow > 0:
            del self._messages[:overflow]
