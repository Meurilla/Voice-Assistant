"""Gemini provider adapter for Phase 1 text-only assistant requests."""

from __future__ import annotations

import re
import socket
import time
from collections.abc import Callable, Sequence
from dataclasses import replace
from typing import Any, Protocol, cast

from core.config import (
    PROVIDER_MAX_RETRIES_MAX,
    PROVIDER_MAX_RETRIES_MIN,
    PROVIDER_RETRY_DELAY_SECONDS_MAX,
    PROVIDER_RETRY_DELAY_SECONDS_MIN,
)
from core.errors import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from core.session import ConversationMessage
from providers.base import ProviderRequestMetadata


class GeminiModelsClient(Protocol):
    """Subset of the Gemini SDK models client used by this adapter."""

    def generate_content(
        self,
        *,
        model: str,
        contents: Sequence[dict[str, Any]],
        config: dict[str, Any],
    ) -> Any:
        """Generate text from a Gemini-compatible model."""


class GeminiClient(Protocol):
    """Subset of the Gemini SDK client required by the provider."""

    @property
    def models(self) -> GeminiModelsClient:
        """Return the models API used by this adapter."""

        ...


ClientFactory = Callable[[str], GeminiClient]
SleepFunc = Callable[[float], None]
ClockFunc = Callable[[], float]


class GeminiProvider:
    """Gemini provider adapter for Phase 1 text-only requests."""

    name = "gemini"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        thinking_level: str,
        max_retries: int = PROVIDER_MAX_RETRIES_MAX,
        retry_delay_seconds: int = 3,
        client: GeminiClient | None = None,
        client_factory: ClientFactory | None = None,
        sleep_func: SleepFunc = time.sleep,
        clock_func: ClockFunc = time.perf_counter,
    ) -> None:
        # Validate at the adapter boundary because callers can bypass config loading.
        if not api_key.strip():
            raise ProviderAuthenticationError("Provider API key is empty.")
        if not model.strip():
            raise ProviderUnavailableError("Provider model must not be empty.")
        if thinking_level not in {"minimal", "high"}:
            raise ProviderUnavailableError("Provider thinking level must be minimal or high.")
        if (
            isinstance(max_retries, bool)
            or not isinstance(max_retries, int)
            or not PROVIDER_MAX_RETRIES_MIN <= max_retries <= PROVIDER_MAX_RETRIES_MAX
        ):
            raise ProviderUnavailableError(
                "Provider max retries must be an integer from "
                f"{PROVIDER_MAX_RETRIES_MIN} to {PROVIDER_MAX_RETRIES_MAX}."
            )
        if (
            isinstance(retry_delay_seconds, bool)
            or not isinstance(retry_delay_seconds, int)
            or not PROVIDER_RETRY_DELAY_SECONDS_MIN
            <= retry_delay_seconds
            <= PROVIDER_RETRY_DELAY_SECONDS_MAX
        ):
            raise ProviderUnavailableError(
                "Provider retry delay must be an integer from "
                f"{PROVIDER_RETRY_DELAY_SECONDS_MIN} "
                f"to {PROVIDER_RETRY_DELAY_SECONDS_MAX}."
            )

        self._api_key = api_key
        self.model = model.strip()
        self.thinking_level = thinking_level
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.last_request_metadata = ProviderRequestMetadata()
        self._client = client
        self._client_factory = client_factory or _default_client_factory
        self._sleep_func = sleep_func
        self._clock_func = clock_func

    def generate_response(
        self,
        *,
        system_prompt: str,
        messages: Sequence[ConversationMessage],
        timeout_seconds: int,
    ) -> str:
        """Generate a text response from Gemini for the supplied conversation."""

        started_at = self._clock_func()
        self.last_request_metadata = ProviderRequestMetadata()
        try:
            response = self._generate_with_retries(
                system_prompt=system_prompt,
                messages=messages,
                timeout_seconds=timeout_seconds,
            )
            text = _extract_response_text(response)
            if not text:
                self._record_failure(
                    status_code=None,
                    error_message="Gemini returned an empty response.",
                )
                raise ProviderUnavailableError()
            return text
        except ProviderError:
            raise
        except Exception as exc:
            self._record_failure(
                status_code=_status_code_from_exception(exc),
                error_message=_safe_exception_message(exc, self._api_key),
            )
            raise ProviderUnavailableError from exc
        finally:
            elapsed_seconds = max(0.0, self._clock_func() - started_at)
            self.last_request_metadata = replace(
                self.last_request_metadata,
                elapsed_ms=int(elapsed_seconds * 1000),
            )

    def _generate_with_retries(
        self,
        *,
        system_prompt: str,
        messages: Sequence[ConversationMessage],
        timeout_seconds: int,
    ) -> Any:
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            self.last_request_metadata = replace(
                self.last_request_metadata,
                attempt_count=attempt + 1,
            )
            try:
                response = self._get_client().models.generate_content(
                    model=self.model,
                    contents=_to_gemini_contents(messages),
                    config={
                        "system_instruction": system_prompt,
                        "thinking_config": {"thinking_level": self.thinking_level},
                        "http_options": {"timeout": timeout_seconds * 1000},
                    },
                )
            except Exception as exc:
                self._record_failure(
                    status_code=_status_code_from_exception(exc),
                    error_message=_safe_exception_message(exc, self._api_key),
                )
                if attempt < self.max_retries and _is_retryable_provider_exception(exc):
                    retry_count = self.last_request_metadata.retry_count + 1
                    self.last_request_metadata = replace(
                        self.last_request_metadata,
                        retry_count=retry_count,
                    )
                    retry_delay = self.retry_delay_seconds * (2 ** (retry_count - 1))
                    if retry_delay:
                        self._sleep_func(retry_delay)
                    continue
                raise _map_provider_exception(exc) from exc
            else:
                self.last_request_metadata = replace(
                    self.last_request_metadata,
                    final_status_code=None,
                    error_message=None,
                )
                return response

    @property
    def last_retry_count(self) -> int:
        """Return the retry count retained for backwards-compatible diagnostics."""

        return self.last_request_metadata.retry_count

    def close(self) -> None:
        """Close the underlying SDK client when it exposes a close method."""

        close_client = getattr(self._client, "close", None)
        if callable(close_client):
            close_client()

    def _get_client(self) -> GeminiClient:
        if self._client is None:
            self._client = self._client_factory(self._api_key)
        return self._client

    def _record_failure(
        self,
        *,
        status_code: int | None,
        error_message: str,
    ) -> None:
        self.last_request_metadata = replace(
            self.last_request_metadata,
            final_status_code=status_code,
            error_message=error_message,
        )


def _default_client_factory(api_key: str) -> GeminiClient:
    try:
        from google import genai
    except ImportError as exc:
        raise ProviderUnavailableError(
            "google-genai is not installed. Run python -m pip install -e .[dev]."
        ) from exc

    return cast(GeminiClient, genai.Client(api_key=api_key))


def _to_gemini_contents(
    messages: Sequence[ConversationMessage],
) -> list[dict[str, Any]]:
    contents: list[dict[str, Any]] = []
    for message in messages:
        if message.role == "user":
            role = "user"
        elif message.role == "assistant":
            role = "model"
        else:
            raise ProviderUnavailableError(f"Unsupported conversation role: {message.role}")

        contents.append(
            {
                "role": role,
                "parts": [{"text": message.content}],
            }
        )
    return contents


def _extract_response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str):
        return text.strip()
    return ""


def _map_provider_exception(exc: Exception) -> ProviderError:
    if isinstance(exc, ProviderError):
        return exc

    status_code = _status_code_from_exception(exc)
    if isinstance(exc, (TimeoutError, socket.timeout)) or status_code in {408, 504}:
        return ProviderTimeoutError()
    if status_code in {401, 403}:
        return ProviderAuthenticationError()
    if status_code == 429:
        return ProviderRateLimitError()
    if status_code == 400:
        return ProviderUnavailableError(
            "The request was rejected. Check the model configuration and try again."
        )
    if status_code is not None:
        return ProviderUnavailableError()
    if "timeout" in type(exc).__name__.lower():
        return ProviderTimeoutError()
    return ProviderUnavailableError()


def _status_code_from_exception(exc: Exception) -> int | None:
    for attribute in ("status_code", "code"):
        value = getattr(exc, attribute, None)
        if isinstance(value, int):
            return value

    response = getattr(exc, "response", None)
    value = getattr(response, "status_code", None)
    if isinstance(value, int):
        return value

    return None


def _is_retryable_provider_exception(exc: Exception) -> bool:
    return _status_code_from_exception(exc) in {500, 503}


def _safe_exception_message(exc: Exception, api_key: str) -> str:
    message = str(exc).strip() or type(exc).__name__
    message = message.replace(api_key, "[REDACTED_API_KEY]")
    message = re.sub(r"AIza[0-9A-Za-z_\-]{20,}", "[REDACTED_API_KEY]", message)
    message = " ".join(message.split())
    if len(message) > 500:
        return message[:497] + "..."
    return message
