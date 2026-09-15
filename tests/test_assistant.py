"""Tests for assistant turn orchestration, session updates, and log records."""

import json
import tempfile
import unittest
from collections.abc import Sequence
from pathlib import Path

from core.assistant import Assistant
from core.config import RuntimeConfig
from core.errors import ProviderUnavailableError
from core.logging import InteractionLogger
from core.session import ConversationMessage, Session
from providers.base import ProviderRequestMetadata


class FakeProvider:
    """Provider fake that records calls and returns a configured response."""

    name = "gemini"

    def __init__(
        self,
        response: str = "assistant response",
        metadata: ProviderRequestMetadata | None = None,
    ) -> None:
        self.response = response
        self.closed = False
        self.last_request_metadata = metadata or ProviderRequestMetadata(
            attempt_count=1,
            elapsed_ms=25,
        )
        self.calls: list[tuple[str, tuple[ConversationMessage, ...], int]] = []

    def generate_response(
        self,
        *,
        system_prompt: str,
        messages: Sequence[ConversationMessage],
        timeout_seconds: int,
    ) -> str:
        self.calls.append((system_prompt, tuple(messages), timeout_seconds))
        return self.response

    def close(self) -> None:
        self.closed = True


class FailingProvider:
    """Provider fake that raises a deterministic provider error."""

    name = "gemini"
    last_request_metadata = ProviderRequestMetadata(
        attempt_count=3,
        retry_count=2,
        final_status_code=500,
        error_message="500 INTERNAL",
        elapsed_ms=9000,
    )

    def generate_response(
        self,
        *,
        system_prompt: str,
        messages: Sequence[ConversationMessage],
        timeout_seconds: int,
    ) -> str:
        raise ProviderUnavailableError("Provider unavailable for test.")

    def close(self) -> None:
        pass


class AssistantTests(unittest.TestCase):
    """Coverage for assistant request flow and logging behavior."""

    def test_assistant_request_flow_updates_session_and_logs_success(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "interactions.jsonl"
            provider = FakeProvider(response="hello back")
            assistant = _assistant(log_file, provider)

            reply = assistant.handle_user_input("hello")

            self.assertEqual(reply.text, "hello back")
            self.assertIsNone(reply.log_error)
            self.assertEqual(len(provider.calls), 1)
            system_prompt, messages, timeout_seconds = provider.calls[0]
            self.assertEqual(system_prompt, "system prompt")
            self.assertEqual(messages[-1].content, "hello")
            self.assertEqual(timeout_seconds, 30)
            self.assertEqual(
                [message.role for message in assistant.session.messages],
                ["user", "assistant"],
            )

            record = json.loads(log_file.read_text(encoding="utf-8").splitlines()[0])
            self.assertTrue(record["success"])
            self.assertEqual(record["assistant_response"], "hello back")
            self.assertEqual(record["provider_attempt_count"], 1)
            self.assertEqual(record["provider_retry_count"], 0)
            self.assertIsNone(record["provider_final_status_code"])
            self.assertIsNone(record["provider_error_message"])
            self.assertEqual(record["provider_elapsed_ms"], 25)

    def test_assistant_passes_current_bounded_history_to_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            provider = FakeProvider(response="latest response")
            assistant = _assistant(
                Path(temp_dir) / "interactions.jsonl",
                provider,
            )
            for index in range(12):
                role = "user" if index % 2 == 0 else "assistant"
                assistant.session.add(role, f"history-{index}")

            assistant.handle_user_input("latest request")

            _, messages, _ = provider.calls[0]
            expected_messages = tuple(
                ConversationMessage(
                    role="user" if index % 2 == 0 else "assistant",
                    content=f"history-{index}",
                )
                for index in range(2, 12)
            ) + (ConversationMessage(role="user", content="latest request"),)
            self.assertEqual(messages, expected_messages)

    def test_close_releases_provider_resources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            provider = FakeProvider(response="hello back")
            assistant = _assistant(Path(temp_dir) / "interactions.jsonl", provider)

            assistant.close()

            self.assertTrue(provider.closed)

    def test_assistant_logs_provider_failure_without_updating_session(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "interactions.jsonl"
            assistant = _assistant(log_file, FailingProvider())

            with self.assertRaises(ProviderUnavailableError):
                assistant.handle_user_input("hello")

            self.assertEqual(len(assistant.session.messages), 0)
            record = json.loads(log_file.read_text(encoding="utf-8").splitlines()[0])
            self.assertFalse(record["success"])
            self.assertEqual(record["error_type"], "ProviderUnavailableError")
            self.assertEqual(record["provider_attempt_count"], 3)
            self.assertEqual(record["provider_retry_count"], 2)
            self.assertEqual(record["provider_final_status_code"], 500)
            self.assertEqual(record["provider_error_message"], "500 INTERNAL")
            self.assertEqual(record["provider_elapsed_ms"], 9000)

    def test_assistant_logs_provider_retry_count(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "interactions.jsonl"
            provider = FakeProvider(
                response="hello back",
                metadata=ProviderRequestMetadata(
                    attempt_count=2,
                    retry_count=1,
                    elapsed_ms=3025,
                ),
            )
            assistant = _assistant(log_file, provider)

            assistant.handle_user_input("hello")

            record = json.loads(log_file.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(record["provider_attempt_count"], 2)
            self.assertEqual(record["provider_retry_count"], 1)
            self.assertEqual(record["provider_elapsed_ms"], 3025)

    def test_assistant_attaches_log_failure_to_provider_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = _assistant(Path(temp_dir), FailingProvider())

            with self.assertRaises(ProviderUnavailableError) as context:
                assistant.handle_user_input("hello")

            self.assertIn("Could not write interaction log", context.exception.log_error)
            self.assertEqual(len(assistant.session.messages), 0)

    def test_assistant_preserves_successful_reply_when_logging_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            provider = FakeProvider(response="hello back")
            assistant = _assistant(Path(temp_dir), provider)

            reply = assistant.handle_user_input("hello")

            self.assertEqual(reply.text, "hello back")
            self.assertIn("Could not write interaction log", reply.log_error or "")
            self.assertEqual(
                assistant.session.messages,
                (
                    ConversationMessage(role="user", content="hello"),
                    ConversationMessage(role="assistant", content="hello back"),
                ),
            )

    def test_assistant_redacts_secret_from_logged_conversation_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "interactions.jsonl"
            api_key = "configured-secret-value-1234567890"
            provider = FakeProvider(response=f"assistant echoed {api_key}")
            assistant = _assistant(log_file, provider, logger_secrets=(api_key,))

            reply = assistant.handle_user_input(f"user pasted {api_key}")

            self.assertIn(api_key, reply.text)
            log_text = log_file.read_text(encoding="utf-8")
            self.assertNotIn(api_key, log_text)
            record = json.loads(log_text)
            self.assertEqual(record["user_input"], "user pasted [REDACTED_API_KEY]")
            self.assertEqual(
                record["assistant_response"],
                "assistant echoed [REDACTED_API_KEY]",
            )


def _assistant(
    log_file: Path,
    provider: FakeProvider | FailingProvider,
    logger_secrets: Sequence[str] = (),
) -> Assistant:
    config = RuntimeConfig(
        provider_name="gemini",
        provider_model="gemma-4-31b-it",
        provider_timeout_seconds=30,
        provider_thinking_level="minimal",
        provider_max_retries=2,
        provider_retry_delay_seconds=3,
        session_history_max_messages=10,
        max_user_input_chars=8000,
        api_key_env_var="GEMINI_API_KEY",
        system_prompt_path=Path("config/system_prompt.txt"),
        log_file=log_file,
    )
    return Assistant(
        config=config,
        system_prompt="system prompt",
        provider=provider,
        session=Session(max_messages=10),
        interaction_logger=InteractionLogger(log_file, secrets=logger_secrets),
        session_id="session-1",
    )


if __name__ == "__main__":
    unittest.main()
