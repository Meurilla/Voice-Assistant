"""Gemini provider adapter for Phase 1 text-only assistant requests."""

from __future__ import annotations

import re
import socket
from collections.abc import Callable, Sequence
from typing import Any, Protocol

from core.errors import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from core.session import ConversationMessage


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

    models: GeminiModelsClient


ClientFactory = Callable[[str], GeminiClient]


class GeminiProvider:
    """Gemini provider adapter for Phase 1 text-only requests."""

    name = "gemini"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        thinking_level: str,
        max_retries: int = 1,
        client: GeminiClient | None = None,
        client_factory: ClientFactory | None = None,
    ) -> None:
        if not api_key.strip():
            raise ProviderAuthenticationError("Gemini API key is empty.")
        if not model.strip():
            raise ProviderUnavailableError("Gemini model must not be empty.")
        if thinking_level not in {"minimal", "high"}:
            raise ProviderUnavailableError("Gemini thinking level must be minimal or high.")
        if max_retries < 0:
            raise ProviderUnavailableError("Gemini max retries must not be negative.")

        self._api_key = api_key
        self.model = model.strip()
        self.thinking_level = thinking_level
        self.max_retries = max_retries
        self._client = client
        self._client_factory = client_factory or _default_client_factory

    def generate_response(
        self,
        *,
        system_prompt: str,
        messages: Sequence[ConversationMessage],
        timeout_seconds: int,
    ) -> str:
        """Generate a text response from Gemini for the supplied conversation."""

        response = self._generate_with_retries(
            system_prompt=system_prompt,
            messages=messages,
            timeout_seconds=timeout_seconds,
        )

        text = _extract_response_text(response)
        if not text:
            raise ProviderUnavailableError("Gemini returned an empty response.")
        return text

    def _generate_with_retries(
        self,
        *,
        system_prompt: str,
        messages: Sequence[ConversationMessage],
        timeout_seconds: int,
    ) -> Any:
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            try:
                return self._get_client().models.generate_content(
                    model=self.model,
                    contents=_to_gemini_contents(messages),
                    config={
                        "system_instruction": system_prompt,
                        "thinking_config": {"thinking_level": self.thinking_level},
                        "http_options": {"timeout": timeout_seconds * 1000},
                    },
                )
            except Exception as exc:
                if attempt < self.max_retries and _is_retryable_provider_exception(exc):
                    continue
                raise _map_provider_exception(exc, self._api_key) from exc

        raise ProviderUnavailableError("Gemini provider request failed.")

    def close(self) -> None:
        """Close the underlying SDK client when it exposes a close method."""

        close_client = getattr(self._client, "close", None)
        if callable(close_client):
            close_client()

    def _get_client(self) -> GeminiClient:
        if self._client is None:
            self._client = self._client_factory(self._api_key)
        return self._client


def _default_client_factory(api_key: str) -> GeminiClient:
    try:
        from google import genai
    except ImportError as exc:
        raise ProviderUnavailableError(
            "google-genai is not installed. Run python -m pip install -e .[dev]."
        ) from exc

    return genai.Client(api_key=api_key)


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


def _map_provider_exception(exc: Exception, api_key: str) -> ProviderError:
    status_code = _status_code_from_exception(exc)
    details = _safe_exception_message(exc, api_key)
    if isinstance(exc, (TimeoutError, socket.timeout)) or status_code in {408, 504}:
        return ProviderTimeoutError("Gemini provider request timed out.")
    if status_code in {401, 403}:
        return ProviderAuthenticationError(
            "Gemini authentication failed. Check the configured API key."
        )
    if status_code == 429:
        return ProviderRateLimitError("Gemini rate limit reached. Try again later.")
    if status_code == 400:
        return ProviderUnavailableError(
            f"Gemini provider rejected the request as invalid: {details}"
        )
    if status_code is not None:
        return ProviderUnavailableError(
            f"Gemini provider request failed with status {status_code}: {details}"
        )
    if "timeout" in type(exc).__name__.lower():
        return ProviderTimeoutError("Gemini provider request timed out.")
    return ProviderUnavailableError(f"Gemini provider request failed: {details}")


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
