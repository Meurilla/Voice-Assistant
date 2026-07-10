"""Tests for JSONL interaction logging and secret redaction behavior."""

import json
import tempfile
import unittest
from pathlib import Path

from core.errors import LogWriteError
from core.logging import InteractionLogger


class LoggingTests(unittest.TestCase):
    """Coverage for local interaction logging success and failure paths."""

    def test_log_interaction_writes_jsonl_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "interactions.jsonl"
            logger = InteractionLogger(log_file)

            logger.log_interaction(
                session_id="session-1",
                user_input="hello",
                assistant_response="hi",
                provider_name="gemini",
                success=True,
            )

            lines = log_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["session_id"], "session-1")
            self.assertEqual(record["user_input"], "hello")
            self.assertEqual(record["assistant_response"], "hi")
            self.assertEqual(record["provider_name"], "gemini")
            self.assertTrue(record["success"])
            self.assertIsNone(record["error_type"])

    def test_log_interaction_redacts_configured_secret_from_conversation_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "interactions.jsonl"
            secret = "configured-secret-value-1234567890"
            logger = InteractionLogger(log_file, secrets=(secret,))

            logger.log_interaction(
                session_id="session-1",
                user_input=f"my key is {secret}",
                assistant_response=f"you pasted {secret}",
                provider_name="gemini",
                success=True,
            )

            log_text = log_file.read_text(encoding="utf-8")
            self.assertNotIn(secret, log_text)
            record = json.loads(log_text)
            self.assertEqual(record["user_input"], "my key is [REDACTED_API_KEY]")
            self.assertEqual(record["assistant_response"], "you pasted [REDACTED_API_KEY]")

    def test_log_interaction_redacts_google_api_key_shaped_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "interactions.jsonl"
            pasted_key = "AIza" + "A" * 32
            logger = InteractionLogger(log_file)

            logger.log_interaction(
                session_id="session-1",
                user_input=f"accidental paste {pasted_key}",
                assistant_response=f"echoed {pasted_key}",
                provider_name="gemini",
                success=True,
            )

            log_text = log_file.read_text(encoding="utf-8")
            self.assertNotIn(pasted_key, log_text)
            record = json.loads(log_text)
            self.assertEqual(record["user_input"], "accidental paste [REDACTED_API_KEY]")
            self.assertEqual(record["assistant_response"], "echoed [REDACTED_API_KEY]")

    def test_log_interaction_reports_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = InteractionLogger(Path(temp_dir))

            with self.assertRaises(LogWriteError):
                logger.log_interaction(
                    session_id="session-1",
                    user_input="hello",
                    assistant_response=None,
                    provider_name="gemini",
                    success=False,
                    error_type="ProviderUnavailableError",
                )


if __name__ == "__main__":
    unittest.main()
