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


class FakeProvider:
    """Provider fake that records calls and returns a configured response."""

    name = "gemini"

    def __init__(self, response: str = "assistant response") -> None:
        self.response = response
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


class FailingProvider:
    """Provider fake that raises a deterministic provider error."""

    name = "gemini"

    def generate_response(
        self,
        *,
        system_prompt: str,
        messages: Sequence[ConversationMessage],
        timeout_seconds: int,
    ) -> str:
        raise ProviderUnavailableError("Provider unavailable for test.")


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

    def test_assistant_attaches_log_failure_to_provider_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = _assistant(Path(temp_dir), FailingProvider())

            with self.assertRaises(ProviderUnavailableError) as context:
                assistant.handle_user_input("hello")

            self.assertIn("Could not write interaction log", context.exception.log_error)
            self.assertEqual(len(assistant.session.messages), 0)

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
        provider_max_retries=1,
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
