"""Tests for Gemini request mapping, retry behavior, and error handling."""

import unittest
from collections.abc import Sequence
from typing import Any

from core.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from core.session import ConversationMessage
from providers.gemini_provider import GeminiProvider


class FakeResponse:
    """Minimal response object shaped like the SDK response used by the adapter."""

    def __init__(self, text: str | None) -> None:
        self.text = text


class FakeModels:
    """Gemini models fake that records calls and returns or raises one effect."""

    def __init__(
        self,
        response: FakeResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def generate_content(
        self,
        *,
        model: str,
        contents: Sequence[dict[str, Any]],
        config: dict[str, Any],
    ) -> FakeResponse:
        self.calls.append(
            {
                "model": model,
                "contents": contents,
                "config": config,
            }
        )
        if self.error is not None:
            raise self.error
        if self.response is None:
            raise AssertionError("fake response was not configured")
        return self.response


class SequencedModels:
    """Gemini models fake that returns or raises a configured sequence of effects."""

    def __init__(self, effects: list[FakeResponse | Exception]) -> None:
        self.effects = effects
        self.calls: list[dict[str, Any]] = []

    def generate_content(
        self,
        *,
        model: str,
        contents: Sequence[dict[str, Any]],
        config: dict[str, Any],
    ) -> FakeResponse:
        self.calls.append(
            {
                "model": model,
                "contents": contents,
                "config": config,
            }
        )
        effect = self.effects.pop(0)
        if isinstance(effect, Exception):
            raise effect
        return effect


class FakeClient:
    """Minimal Gemini client fake exposing a models client and close state."""

    def __init__(self, models: FakeModels | SequencedModels) -> None:
        self.models = models
        self.closed = False

    def close(self) -> None:
        self.closed = True


class StatusError(Exception):
    """Provider exception fake carrying an HTTP-like status code."""

    def __init__(self, status_code: int) -> None:
        super().__init__("provider error")
        self.status_code = status_code


class GeminiProviderTests(unittest.TestCase):
    """Coverage for Gemini provider success, retries, and status mapping."""

    def test_generate_response_sends_text_history_and_config(self) -> None:
        models = FakeModels(response=FakeResponse(" assistant text "))
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            client=FakeClient(models),
        )

        response = provider.generate_response(
            system_prompt="system prompt",
            messages=[
                ConversationMessage(role="user", content="hello"),
                ConversationMessage(role="assistant", content="hi"),
                ConversationMessage(role="user", content="next"),
            ],
            timeout_seconds=30,
        )

        self.assertEqual(response, "assistant text")
        self.assertEqual(len(models.calls), 1)
        call = models.calls[0]
        self.assertEqual(call["model"], "gemma-4-31b-it")
        self.assertEqual(
            call["contents"],
            [
                {"role": "user", "parts": [{"text": "hello"}]},
                {"role": "model", "parts": [{"text": "hi"}]},
                {"role": "user", "parts": [{"text": "next"}]},
            ],
        )
        self.assertEqual(call["config"]["system_instruction"], "system prompt")
        self.assertEqual(call["config"]["thinking_config"]["thinking_level"], "minimal")
        self.assertEqual(call["config"]["http_options"]["timeout"], 30000)

    def test_generate_response_rejects_empty_response(self) -> None:
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            client=FakeClient(FakeModels(response=FakeResponse("   "))),
        )

        with self.assertRaises(ProviderUnavailableError):
            provider.generate_response(
                system_prompt="system prompt",
                messages=[ConversationMessage(role="user", content="hello")],
                timeout_seconds=30,
            )

    def test_generate_response_maps_provider_error_statuses(self) -> None:
        cases = [
            (StatusError(401), ProviderAuthenticationError),
            (StatusError(403), ProviderAuthenticationError),
            (StatusError(408), ProviderTimeoutError),
            (StatusError(429), ProviderRateLimitError),
            (StatusError(500), ProviderUnavailableError),
            (StatusError(504), ProviderTimeoutError),
        ]

        for error, expected_error in cases:
            with self.subTest(status=error.status_code):
                provider = GeminiProvider(
                    api_key="secret",
                    model="gemma-4-31b-it",
                    thinking_level="minimal",
                    client=FakeClient(FakeModels(error=error)),
                )

                with self.assertRaises(expected_error):
                    provider.generate_response(
                        system_prompt="system prompt",
                        messages=[ConversationMessage(role="user", content="hello")],
                        timeout_seconds=30,
                    )

    def test_generate_response_retries_transient_server_error_once(self) -> None:
        models = SequencedModels([StatusError(500), FakeResponse("recovered")])
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            max_retries=1,
            client=FakeClient(models),
        )

        response = provider.generate_response(
            system_prompt="system prompt",
            messages=[ConversationMessage(role="user", content="hello")],
            timeout_seconds=30,
        )

        self.assertEqual(response, "recovered")
        self.assertEqual(len(models.calls), 2)

    def test_generate_response_keeps_transient_retries_bounded(self) -> None:
        models = SequencedModels([StatusError(500), StatusError(500)])
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            max_retries=1,
            client=FakeClient(models),
        )

        with self.assertRaises(ProviderUnavailableError):
            provider.generate_response(
                system_prompt="system prompt",
                messages=[ConversationMessage(role="user", content="hello")],
                timeout_seconds=30,
            )

        self.assertEqual(len(models.calls), 2)

    def test_generate_response_maps_socket_timeout(self) -> None:
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            client=FakeClient(FakeModels(error=TimeoutError("timed out"))),
        )

        with self.assertRaises(ProviderTimeoutError):
            provider.generate_response(
                system_prompt="system prompt",
                messages=[ConversationMessage(role="user", content="hello")],
                timeout_seconds=30,
            )

    def test_close_closes_underlying_client_when_available(self) -> None:
        client = FakeClient(FakeModels(response=FakeResponse("ok")))
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            client=client,
        )

        provider.close()

        self.assertTrue(client.closed)


if __name__ == "__main__":
    unittest.main()
