"""Provider protocol shared by the assistant core and provider adapters."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from core.session import ConversationMessage


@dataclass(frozen=True)
class ProviderRequestMetadata:
    """Sanitized diagnostics captured for the most recent provider request."""

    attempt_count: int = 0
    retry_count: int = 0
    final_status_code: int | None = None
    error_message: str | None = None
    elapsed_ms: int | None = None


class LLMProvider(Protocol):
    """Protocol implemented by Phase 1 text-only LLM providers."""

    name: str
    last_request_metadata: ProviderRequestMetadata

    def generate_response(
        self,
        *,
        system_prompt: str,
        messages: Sequence[ConversationMessage],
        timeout_seconds: int,
    ) -> str:
        """Return a provider response for the supplied conversation."""
