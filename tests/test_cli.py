"""Tests for CLI startup failure and graceful shutdown paths."""

import contextlib
import io
import json
import tempfile
import textwrap
import unittest
from functools import partial
from pathlib import Path
from unittest.mock import Mock, patch

from core.errors import ProviderUnavailableError
from core.session import ConversationMessage
from interfaces.cli import run, run_loop
from providers.base import LLMProvider, ProviderRequestMetadata
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

    def test_run_reports_invalid_file_encoding_without_starting_provider(self) -> None:
        for filename, label in (
            ("settings.toml", "Config file"),
            ("system_prompt.txt", "System prompt file"),
        ):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp_dir:
                config_dir = Path(temp_dir) / "config"
                config_dir.mkdir()
                settings = config_dir / "settings.toml"
                settings.write_text(_valid_settings(), encoding="utf-8")
                (config_dir / "system_prompt.txt").write_text("prompt", encoding="utf-8")
                invalid_file = config_dir / filename
                invalid_file.write_bytes(b"\xffinvalid")
                stderr = io.StringIO()

                with (
                    patch("interfaces.cli.GeminiProvider") as provider_factory,
                    contextlib.redirect_stderr(stderr),
                ):
                    exit_code = run(settings)

                self.assertEqual(exit_code, 1)
                self.assertEqual(
                    stderr.getvalue().strip(),
                    f"Startup error: {label} must use UTF-8 encoding: {invalid_file}",
                )
                provider_factory.assert_not_called()

    def test_run_recovers_after_provider_failure_and_exits_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "config"
            config_dir.mkdir()
            settings = config_dir / "settings.toml"
            settings.write_text(_valid_settings(), encoding="utf-8")
            (config_dir / "system_prompt.txt").write_text("system prompt", encoding="utf-8")
            provider = Mock(spec=LLMProvider)
            provider.name = "gemini"
            provider.last_request_metadata = ProviderRequestMetadata(attempt_count=1)
            provider.generate_response.side_effect = [
                "first response",
                ProviderUnavailableError(),
                "recovered response",
            ]
            inputs = iter(["first request", "failed request", "next request", "/exit"])
            outputs: list[str] = []
            errors: list[str] = []

            with (
                patch.dict("os.environ", {"GEMINI_API_KEY": "fake-api-key"}, clear=True),
                patch("interfaces.cli.GeminiProvider", return_value=provider),
                patch(
                    "interfaces.cli.run_loop",
                    side_effect=partial(
                        run_loop,
                        input_func=lambda prompt: next(inputs),
                        output_func=outputs.append,
                        error_func=errors.append,
                    ),
                ),
            ):
                exit_code = run(settings)

            self.assertEqual(exit_code, 0)
            self.assertEqual(outputs, ["first response", "recovered response", "Goodbye."])
            self.assertEqual(errors, ["I've encountered an error. Please retry."])
            self.assertEqual(provider.generate_response.call_count, 3)
            provider.close.assert_called_once_with()
            self.assertEqual(
                provider.generate_response.call_args.kwargs["messages"],
                (
                    ConversationMessage(role="user", content="first request"),
                    ConversationMessage(role="assistant", content="first response"),
                    ConversationMessage(role="user", content="next request"),
                ),
            )
            log_text = (root / "logs/interactions.jsonl").read_text(encoding="utf-8")
            records = [json.loads(line) for line in log_text.splitlines()]
            self.assertEqual([record["success"] for record in records], [True, False, True])
            self.assertEqual(records[1]["error_type"], "ProviderUnavailableError")
            self.assertIsNone(records[1]["assistant_response"])
            self.assertEqual(len({record["session_id"] for record in records}), 1)

    def test_run_displays_successful_reply_and_log_warning_before_eof(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            settings = config_dir / "settings.toml"
            # An existing directory is a deterministic invalid log-file destination.
            settings.write_text(
                _valid_settings().replace("logs/interactions.jsonl", "config"),
                encoding="utf-8",
            )
            (config_dir / "system_prompt.txt").write_text("system prompt", encoding="utf-8")
            provider = Mock(spec=LLMProvider)
            provider.name = "gemini"
            provider.last_request_metadata = ProviderRequestMetadata(attempt_count=1)
            provider.generate_response.return_value = "successful reply"
            outputs: list[str] = []

            with (
                patch.dict("os.environ", {"GEMINI_API_KEY": "fake-api-key"}, clear=True),
                patch("interfaces.cli.GeminiProvider", return_value=provider),
                patch(
                    "interfaces.cli.run_loop",
                    side_effect=partial(
                        run_loop,
                        input_func=Mock(side_effect=["hello", EOFError()]),
                        output_func=outputs.append,
                        error_func=outputs.append,
                    ),
                ),
            ):
                exit_code = run(settings)

            self.assertEqual(exit_code, 0)
            self.assertEqual(len(outputs), 4)
            self.assertEqual(outputs[0], "successful reply")
            self.assertTrue(outputs[1].startswith("Could not write interaction log:"))
            self.assertEqual(outputs[2:], ["", "Goodbye."])
            provider.generate_response.assert_called_once()
            provider.close.assert_called_once_with()

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
