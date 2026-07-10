"""Provider protocol shared by the assistant core and provider adapters."""

from collections.abc import Sequence
from typing import Protocol

from core.session import ConversationMessage


class LLMProvider(Protocol):
    """Protocol implemented by Phase 1 text-only LLM providers."""

    name: str

    def generate_response(
        self,
        *,
        system_prompt: str,
        messages: Sequence[ConversationMessage],
        timeout_seconds: int,
    ) -> str:
        """Return a provider response for the supplied conversation."""
