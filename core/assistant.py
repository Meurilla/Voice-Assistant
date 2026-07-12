"""Assistant turn orchestration for Phase 1 text interactions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from core.config import RuntimeConfig
from core.errors import LogWriteError, ProviderError, ProviderUnavailableError
from core.logging import InteractionLogger
from core.safety import validate_user_input
from core.session import ConversationMessage, Session
from providers.base import LLMProvider, ProviderRequestMetadata


@dataclass(frozen=True)
class AssistantReply:
    """Text returned to the caller plus any non-fatal logging failure."""

    text: str
    log_error: str | None = None


class Assistant:
    """Coordinate validation, provider calls, session updates, and interaction logging."""

    def __init__(
        self,
        *,
        config: RuntimeConfig,
        system_prompt: str,
        provider: LLMProvider,
        session: Session,
        interaction_logger: InteractionLogger,
        session_id: str | None = None,
    ) -> None:
        self.config = config
        self.system_prompt = system_prompt
        self.provider = provider
        self.session = session
        self.interaction_logger = interaction_logger
        self.session_id = session_id or str(uuid4())

    def handle_user_input(self, raw_input: str) -> AssistantReply:
        """Process one user input through validation, provider response, session, and logs."""

        user_input = validate_user_input(raw_input, self.config.max_user_input_chars)
        provider_messages = self.session.messages + (
            ConversationMessage(role="user", content=user_input),
        )

        try:
            response = self.provider.generate_response(
                system_prompt=self.system_prompt,
                messages=provider_messages,
                timeout_seconds=self.config.provider_timeout_seconds,
            )
        except ProviderError as exc:
            log_error = self._try_log(
                user_input=user_input,
                assistant_response=None,
                success=False,
                error_type=type(exc).__name__,
            )
            if log_error:
                exc.log_error = log_error
            raise
        except Exception as exc:
            provider_error = ProviderUnavailableError()
            log_error = self._try_log(
                user_input=user_input,
                assistant_response=None,
                success=False,
                error_type=type(provider_error).__name__,
            )
            if log_error:
                provider_error.log_error = log_error
            raise provider_error from exc

        # Commit only complete turns so a failed request is not replayed without a response.
        self.session.add("user", user_input)
        self.session.add("assistant", response)
        log_error = self._try_log(
            user_input=user_input,
            assistant_response=response,
            success=True,
            error_type=None,
        )
        return AssistantReply(text=response, log_error=log_error)

    def close(self) -> None:
        """Release resources owned by the configured provider."""

        self.provider.close()

    def _try_log(
        self,
        *,
        user_input: str,
        assistant_response: str | None,
        success: bool,
        error_type: str | None,
    ) -> str | None:
        provider_metadata = self._provider_request_metadata()
        try:
            self.interaction_logger.log_interaction(
                session_id=self.session_id,
                user_input=user_input,
                assistant_response=assistant_response,
                provider_name=self.provider.name,
                success=success,
                error_type=error_type,
                provider_attempt_count=provider_metadata.attempt_count,
                provider_retry_count=provider_metadata.retry_count,
                provider_final_status_code=provider_metadata.final_status_code,
                provider_error_message=provider_metadata.error_message,
                provider_elapsed_ms=provider_metadata.elapsed_ms,
            )
        except LogWriteError as exc:
            return exc.user_message
        return None

    def _provider_request_metadata(self) -> ProviderRequestMetadata:
        value = getattr(self.provider, "last_request_metadata", None)
        if isinstance(value, ProviderRequestMetadata):
            return value

        retry_count = getattr(self.provider, "last_retry_count", 0)
        if not isinstance(retry_count, int) or retry_count < 0:
            retry_count = 0
        return ProviderRequestMetadata(attempt_count=1, retry_count=retry_count)
