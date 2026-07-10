"""Tests for CLI startup failure and graceful shutdown paths."""

import contextlib
import io
import tempfile
import textwrap
import unittest
from pathlib import Path

from core.errors import ProviderUnavailableError
from interfaces.cli import run, run_loop


class CliTests(unittest.TestCase):
    """Coverage for CLI startup and run-loop behavior."""

    def test_run_reports_missing_prompt_file_startup_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "config"
            config_dir.mkdir()
            settings = config_dir / "settings.toml"
            settings.write_text(_valid_settings(), encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                exit_code = run(settings)

            self.assertEqual(exit_code, 1)
            self.assertIn("Startup error: Missing system prompt file", stderr.getvalue())

    def test_run_loop_exits_on_exit_command(self) -> None:
        outputs: list[str] = []
        exit_code = run_loop(
            _NoopAssistant(),
            input_func=lambda prompt: "/exit",
            output_func=outputs.append,
            error_func=outputs.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(outputs, ["Goodbye."])

    def test_run_loop_exits_on_quit_command(self) -> None:
        outputs: list[str] = []
        exit_code = run_loop(
            _NoopAssistant(),
            input_func=lambda prompt: "/quit",
            output_func=outputs.append,
            error_func=outputs.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(outputs, ["Goodbye."])

    def test_run_loop_exits_cleanly_on_keyboard_interrupt(self) -> None:
        outputs: list[str] = []

        def raise_keyboard_interrupt(prompt: str) -> str:
            raise KeyboardInterrupt

        exit_code = run_loop(
            _NoopAssistant(),
            input_func=raise_keyboard_interrupt,
            output_func=outputs.append,
            error_func=outputs.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(outputs, ["", "Goodbye."])

    def test_run_loop_prints_log_failure_after_provider_error(self) -> None:
        inputs = iter(["hello", "/exit"])
        outputs: list[str] = []

        exit_code = run_loop(
            _ProviderFailAssistant(),
            input_func=lambda prompt: next(inputs),
            output_func=outputs.append,
            error_func=outputs.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            outputs,
            [
                "Provider unavailable for CLI test.",
                "Could not write interaction log for CLI test.",
                "Goodbye.",
            ],
        )


class _NoopAssistant:
    """Assistant stand-in for shutdown paths where no provider call should occur."""

    def handle_user_input(self, raw_input: str):  # pragma: no cover
        raise AssertionError("assistant should not be called for exit commands")


class _ProviderFailAssistant:
    """Assistant stand-in that raises both provider and logging errors."""

    def handle_user_input(self, raw_input: str):  # pragma: no cover
        raise ProviderUnavailableError(
            "Provider unavailable for CLI test.",
            log_error="Could not write interaction log for CLI test.",
        )


def _valid_settings() -> str:
    return textwrap.dedent(
        """
        provider_name = "gemini"
        provider_model = "gemma-4-31b-it"
        provider_timeout_seconds = 30
        provider_thinking_level = "minimal"
        provider_max_retries = 1
        session_history_max_messages = 10
        max_user_input_chars = 8000
        api_key_env_var = "GEMINI_API_KEY"
        system_prompt_path = "config/system_prompt.txt"
        log_file = "logs/interactions.jsonl"
        """
    ).strip()


if __name__ == "__main__":
    unittest.main()
