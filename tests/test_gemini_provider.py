"""Tests for Gemini request mapping, retry behavior, and error handling."""

import unittest
from collections.abc import Sequence
from typing import Any

from google.genai import errors as genai_errors

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

    def __init__(self, status_code: int, message: str = "provider error") -> None:
        super().__init__(message)
        self.status_code = status_code


class GeminiProviderTests(unittest.TestCase):
    """Coverage for Gemini provider success, retries, and status mapping."""

    def test_init_rejects_retry_values_outside_phase_one_limits(self) -> None:
        cases = [
            ({"max_retries": 3}, "max retries"),
            ({"retry_delay_seconds": 11}, "retry delay"),
        ]

        for overrides, expected_message in cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(ProviderUnavailableError) as context:
                    GeminiProvider(
                        api_key="secret",
                        model="gemma-4-31b-it",
                        thinking_level="minimal",
                        client=FakeClient(FakeModels(response=FakeResponse("ok"))),
                        **overrides,
                    )

                self.assertIn(expected_message, context.exception.user_message)

    def test_generate_response_sends_text_history_and_config(self) -> None:
        models = FakeModels(response=FakeResponse(" assistant text "))
        clock_values = iter([10.0, 10.125])
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            client=FakeClient(models),
            clock_func=clock_values.__next__,
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
        self.assertEqual(provider.last_request_metadata.attempt_count, 1)
        self.assertEqual(provider.last_request_metadata.retry_count, 0)
        self.assertIsNone(provider.last_request_metadata.final_status_code)
        self.assertIsNone(provider.last_request_metadata.error_message)
        self.assertEqual(provider.last_request_metadata.elapsed_ms, 125)

    def test_generate_response_rejects_empty_response(self) -> None:
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            client=FakeClient(FakeModels(response=FakeResponse("   "))),
        )

        with self.assertRaises(ProviderUnavailableError) as context:
            provider.generate_response(
                system_prompt="system prompt",
                messages=[ConversationMessage(role="user", content="hello")],
                timeout_seconds=30,
            )

        self.assertEqual(context.exception.user_message, "I've encountered an error. Please retry.")
        self.assertEqual(provider.last_request_metadata.attempt_count, 1)
        self.assertEqual(
            provider.last_request_metadata.error_message,
            "Gemini returned an empty response.",
        )

    def test_generate_response_maps_provider_error_statuses(self) -> None:
        cases = [
            (
                StatusError(401),
                ProviderAuthenticationError,
                "Authentication failed. Check the configured API key.",
            ),
            (
                StatusError(403),
                ProviderAuthenticationError,
                "Authentication failed. Check the configured API key.",
            ),
            (
                StatusError(408),
                ProviderTimeoutError,
                "The request timed out. Please try again.",
            ),
            (
                StatusError(429),
                ProviderRateLimitError,
                "The service is temporarily rate-limited. Please try again later.",
            ),
            (
                StatusError(400),
                ProviderUnavailableError,
                "The request was rejected. Check the model configuration and try again.",
            ),
            (
                StatusError(500),
                ProviderUnavailableError,
                "I've encountered an error. Please retry.",
            ),
            (
                StatusError(504),
                ProviderTimeoutError,
                "The request timed out. Please try again.",
            ),
        ]

        for error, expected_error, expected_message in cases:
            with self.subTest(status=error.status_code):
                provider = GeminiProvider(
                    api_key="secret",
                    model="gemma-4-31b-it",
                    thinking_level="minimal",
                    max_retries=0,
                    client=FakeClient(FakeModels(error=error)),
                )

                with self.assertRaises(expected_error) as context:
                    provider.generate_response(
                        system_prompt="system prompt",
                        messages=[ConversationMessage(role="user", content="hello")],
                        timeout_seconds=30,
                    )

                self.assertEqual(context.exception.user_message, expected_message)
                self.assertEqual(
                    provider.last_request_metadata.final_status_code,
                    error.status_code,
                )
                self.assertEqual(provider.last_request_metadata.error_message, "provider error")

    def test_generate_response_maps_official_sdk_client_error_code(self) -> None:
        error = genai_errors.ClientError(
            401,
            {
                "error": {
                    "code": 401,
                    "message": "API key rejected",
                    "status": "UNAUTHENTICATED",
                }
            },
        )
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            max_retries=0,
            client=FakeClient(FakeModels(error=error)),
        )

        with self.assertRaises(ProviderAuthenticationError):
            provider.generate_response(
                system_prompt="system prompt",
                messages=[ConversationMessage(role="user", content="hello")],
                timeout_seconds=30,
            )

        self.assertEqual(provider.last_request_metadata.final_status_code, error.code)

    def test_generate_response_retries_official_sdk_server_error_code(self) -> None:
        error = genai_errors.ServerError(
            500,
            {
                "error": {
                    "code": 500,
                    "message": "Internal error encountered.",
                    "status": "INTERNAL",
                }
            },
        )
        models = SequencedModels([error, FakeResponse("recovered")])
        sleep_calls: list[float] = []
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            max_retries=1,
            retry_delay_seconds=3,
            client=FakeClient(models),
            sleep_func=sleep_calls.append,
        )

        response = provider.generate_response(
            system_prompt="system prompt",
            messages=[ConversationMessage(role="user", content="hello")],
            timeout_seconds=30,
        )

        self.assertEqual(response, "recovered")
        self.assertEqual(len(models.calls), 2)
        self.assertEqual(sleep_calls, [3])
        self.assertEqual(provider.last_request_metadata.retry_count, 1)

    def test_generate_response_retries_transient_server_error_once(self) -> None:
        models = SequencedModels([StatusError(500), FakeResponse("recovered")])
        sleep_calls: list[float] = []
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            max_retries=1,
            retry_delay_seconds=3,
            client=FakeClient(models),
            sleep_func=sleep_calls.append,
        )

        response = provider.generate_response(
            system_prompt="system prompt",
            messages=[ConversationMessage(role="user", content="hello")],
            timeout_seconds=30,
        )

        self.assertEqual(response, "recovered")
        self.assertEqual(len(models.calls), 2)
        self.assertEqual(provider.last_retry_count, 1)
        self.assertEqual(sleep_calls, [3])
        self.assertEqual(provider.last_request_metadata.attempt_count, 2)
        self.assertEqual(provider.last_request_metadata.retry_count, 1)
        self.assertIsNone(provider.last_request_metadata.final_status_code)
        self.assertIsNone(provider.last_request_metadata.error_message)

    def test_generate_response_keeps_transient_retries_bounded(self) -> None:
        models = SequencedModels([StatusError(500), StatusError(503), StatusError(500)])
        sleep_calls: list[float] = []
        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            max_retries=2,
            retry_delay_seconds=3,
            client=FakeClient(models),
            sleep_func=sleep_calls.append,
        )

        with self.assertRaises(ProviderUnavailableError) as context:
            provider.generate_response(
                system_prompt="system prompt",
                messages=[ConversationMessage(role="user", content="hello")],
                timeout_seconds=30,
            )

        self.assertEqual(context.exception.user_message, "I've encountered an error. Please retry.")
        self.assertEqual(len(models.calls), 3)
        self.assertEqual(provider.last_retry_count, 2)
        self.assertEqual(sleep_calls, [3, 6])
        self.assertEqual(provider.last_request_metadata.attempt_count, 3)
        self.assertEqual(provider.last_request_metadata.retry_count, 2)
        self.assertEqual(provider.last_request_metadata.final_status_code, 500)
        self.assertEqual(provider.last_request_metadata.error_message, "provider error")

    def test_generate_response_propagates_keyboard_interrupt_during_retry_delay(self) -> None:
        models = SequencedModels([StatusError(500), FakeResponse("unused")])

        def interrupt_sleep(delay: float) -> None:
            self.assertEqual(delay, 3)
            raise KeyboardInterrupt

        provider = GeminiProvider(
            api_key="secret",
            model="gemma-4-31b-it",
            thinking_level="minimal",
            max_retries=1,
            retry_delay_seconds=3,
            client=FakeClient(models),
            sleep_func=interrupt_sleep,
        )

        with self.assertRaises(KeyboardInterrupt):
            provider.generate_response(
                system_prompt="system prompt",
                messages=[ConversationMessage(role="user", content="hello")],
                timeout_seconds=30,
            )

        self.assertEqual(len(models.calls), 1)
        self.assertEqual(provider.last_request_metadata.attempt_count, 1)
        self.assertEqual(provider.last_request_metadata.retry_count, 1)

    def test_generate_response_redacts_api_key_from_diagnostics(self) -> None:
        api_key = "configured-secret-value-1234567890"
        error_message = f"request exposed {api_key} " + "x" * 600
        provider = GeminiProvider(
            api_key=api_key,
            model="gemma-4-31b-it",
            thinking_level="minimal",
            max_retries=0,
            client=FakeClient(FakeModels(error=StatusError(500, error_message))),
        )

        with self.assertRaises(ProviderUnavailableError):
            provider.generate_response(
                system_prompt="system prompt",
                messages=[ConversationMessage(role="user", content="hello")],
                timeout_seconds=30,
            )

        diagnostic = provider.last_request_metadata.error_message or ""
        self.assertNotIn(api_key, diagnostic)
        self.assertTrue(diagnostic.startswith("request exposed [REDACTED_API_KEY]"))
        self.assertEqual(len(diagnostic), 500)
        self.assertTrue(diagnostic.endswith("..."))

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
