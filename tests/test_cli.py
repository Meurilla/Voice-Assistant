"""Tests for CLI startup failure and graceful shutdown paths."""

import contextlib
import io
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from core.errors import ProviderUnavailableError
from interfaces.cli import run, run_loop
from providers.gemini_provider import GeminiModelsClient, GeminiProvider


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

    def test_run_closes_assistant_after_loop_exit(self) -> None:
        assistant = _ClosableAssistant()

        with (
            patch("interfaces.cli.build_assistant", return_value=assistant),
            patch("interfaces.cli.run_loop", return_value=0),
        ):
            exit_code = run()

        self.assertEqual(exit_code, 0)
        self.assertEqual(assistant.close_calls, 1)

    def test_run_closes_assistant_when_loop_raises(self) -> None:
        assistant = _ClosableAssistant()

        with (
            patch("interfaces.cli.build_assistant", return_value=assistant),
            patch("interfaces.cli.run_loop", side_effect=RuntimeError("loop failed")),
            self.assertRaisesRegex(RuntimeError, "loop failed"),
        ):
            run()

        self.assertEqual(assistant.close_calls, 1)

    def test_run_returns_failure_when_assistant_close_fails(self) -> None:
        assistant = _CloseFailingAssistant()
        stderr = io.StringIO()

        with (
            patch("interfaces.cli.build_assistant", return_value=assistant),
            patch("interfaces.cli.run_loop", return_value=0),
            contextlib.redirect_stderr(stderr),
        ):
            exit_code = run()

        self.assertEqual(exit_code, 1)
        self.assertEqual(assistant.close_calls, 1)
        self.assertEqual(
            stderr.getvalue().strip(),
            "Shutdown error: Could not close provider resources.",
        )
        self.assertNotIn("sensitive cleanup detail", stderr.getvalue())

    def test_run_preserves_loop_error_when_assistant_close_fails(self) -> None:
        assistant = _CloseFailingAssistant()
        loop_error = RuntimeError("loop failed")
        stderr = io.StringIO()

        with (
            patch("interfaces.cli.build_assistant", return_value=assistant),
            patch("interfaces.cli.run_loop", side_effect=loop_error),
            contextlib.redirect_stderr(stderr),
            self.assertRaises(RuntimeError) as context,
        ):
            run()

        self.assertIs(context.exception, loop_error)
        self.assertEqual(assistant.close_calls, 1)
        self.assertEqual(
            stderr.getvalue().strip(),
            "Shutdown error: Could not close provider resources.",
        )
        self.assertNotIn("sensitive cleanup detail", stderr.getvalue())

    def test_run_closes_gemini_provider_client_after_shutdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "config"
            config_dir.mkdir()
            settings = config_dir / "settings.toml"
            settings.write_text(_valid_settings(), encoding="utf-8")
            (config_dir / "system_prompt.txt").write_text(
                "system prompt",
                encoding="utf-8",
            )
            client = _ClosableGeminiClient()
            provider = GeminiProvider(
                api_key="fake-api-key",
                model="gemma-4-31b-it",
                thinking_level="minimal",
                client=client,
            )

            with (
                patch.dict("os.environ", {"GEMINI_API_KEY": "fake-api-key"}, clear=True),
                patch("interfaces.cli.GeminiProvider", return_value=provider),
                patch("interfaces.cli.run_loop", return_value=0),
            ):
                exit_code = run(settings)

            self.assertEqual(exit_code, 0)
            self.assertTrue(client.closed)

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

    def test_run_loop_exits_cleanly_on_keyboard_interrupt_during_request(self) -> None:
        outputs: list[str] = []

        exit_code = run_loop(
            _RequestInterruptAssistant(),
            input_func=lambda prompt: "hello",
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
                "I've encountered an error. Please retry.",
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
            log_error="Could not write interaction log for CLI test.",
        )


class _RequestInterruptAssistant:
    """Assistant stand-in for interruption during provider request processing."""

    def handle_user_input(self, raw_input: str):
        raise KeyboardInterrupt


class _ClosableAssistant:
    """Assistant stand-in that records lifecycle cleanup calls."""

    def __init__(self) -> None:
        self.close_calls = 0

    def close(self) -> None:
        self.close_calls += 1


class _CloseFailingAssistant(_ClosableAssistant):
    """Assistant stand-in whose cleanup fails with non-user-safe detail."""

    def close(self) -> None:
        super().close()
        raise RuntimeError("sensitive cleanup detail")


class _ClosableGeminiClient:
    """SDK client stand-in used to verify the concrete shutdown chain."""

    def __init__(self) -> None:
        self.closed = False

    @property
    def models(self) -> GeminiModelsClient:
        raise AssertionError("models should not be used during shutdown")

    def close(self) -> None:
        self.closed = True


def _valid_settings() -> str:
    return textwrap.dedent(
        """
        provider_name = "gemini"
        provider_model = "gemma-4-31b-it"
        provider_timeout_seconds = 30
        provider_thinking_level = "minimal"
        provider_max_retries = 2
        provider_retry_delay_seconds = 3
        session_history_max_messages = 10
        max_user_input_chars = 8000
        api_key_env_var = "GEMINI_API_KEY"
        system_prompt_path = "config/system_prompt.txt"
        log_file = "logs/interactions.jsonl"
        """
    ).strip()


if __name__ == "__main__":
    unittest.main()
