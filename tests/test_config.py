"""Tests for local config, prompt, and environment-secret loading."""

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from core.config import load_api_key, load_config, load_system_prompt
from core.errors import ConfigurationError, MissingConfigError, MissingSecretError


class ConfigTests(unittest.TestCase):
    """Coverage for runtime config validation and required secret loading."""

    def test_load_config_reads_required_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "config"
            config_dir.mkdir()
            settings = config_dir / "settings.toml"
            settings.write_text(_valid_settings(), encoding="utf-8")

            config = load_config(settings)

            self.assertEqual(config.provider_name, "gemini")
            self.assertEqual(config.provider_model, "gemma-4-31b-it")
            self.assertEqual(config.provider_timeout_seconds, 30)
            self.assertEqual(config.provider_thinking_level, "minimal")
            self.assertEqual(config.provider_max_retries, 1)
            self.assertEqual(config.session_history_max_messages, 10)
            self.assertEqual(config.max_user_input_chars, 8000)
            self.assertEqual(config.system_prompt_path, root / "config/system_prompt.txt")
            self.assertEqual(config.log_file, root / "logs/interactions.jsonl")

    def test_load_config_rejects_missing_file(self) -> None:
        with self.assertRaises(MissingConfigError):
            load_config(Path("does-not-exist.toml"))

    def test_load_config_rejects_invalid_integer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "config"
            config_dir.mkdir()
            settings = config_dir / "settings.toml"
            settings.write_text(
                _valid_settings().replace(
                    "provider_timeout_seconds = 30",
                    "provider_timeout_seconds = 0",
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ConfigurationError):
                load_config(settings)

    def test_load_config_rejects_invalid_values(self) -> None:
        cases = [
            (
                "unsupported provider",
                'provider_name = "gemini"',
                'provider_name = "openai"',
                "Phase 1 supports only provider_name",
            ),
            (
                "empty model",
                'provider_model = "gemma-4-31b-it"',
                'provider_model = ""',
                "provider_model",
            ),
            (
                "invalid timeout type",
                "provider_timeout_seconds = 30",
                'provider_timeout_seconds = "30"',
                "provider_timeout_seconds",
            ),
            (
                "invalid thinking level",
                'provider_thinking_level = "minimal"',
                'provider_thinking_level = "medium"',
                "provider_thinking_level",
            ),
            (
                "negative retry count",
                "provider_max_retries = 1",
                "provider_max_retries = -1",
                "provider_max_retries",
            ),
            (
                "zero history limit",
                "session_history_max_messages = 10",
                "session_history_max_messages = 0",
                "session_history_max_messages",
            ),
            (
                "zero input limit",
                "max_user_input_chars = 8000",
                "max_user_input_chars = 0",
                "max_user_input_chars",
            ),
        ]

        for name, original, replacement, expected_message in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    config_dir = root / "config"
                    config_dir.mkdir()
                    settings = config_dir / "settings.toml"
                    settings.write_text(
                        _valid_settings().replace(original, replacement),
                        encoding="utf-8",
                    )

                    with self.assertRaises(ConfigurationError) as context:
                        load_config(settings)

                    self.assertIn(expected_message, str(context.exception))

    def test_load_system_prompt_reads_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompt = Path(temp_dir) / "system_prompt.txt"
            prompt.write_text("  hello  ", encoding="utf-8")

            self.assertEqual(load_system_prompt(prompt), "hello")

    def test_load_system_prompt_rejects_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompt = Path(temp_dir) / "missing_prompt.txt"

            with self.assertRaises(ConfigurationError) as context:
                load_system_prompt(prompt)

            self.assertIn("Missing system prompt file", str(context.exception))

    def test_load_api_key_reads_environment_variable(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": "secret"}, clear=True):
            self.assertEqual(load_api_key("GEMINI_API_KEY"), "secret")

    def test_load_api_key_rejects_missing_environment_variable(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(MissingSecretError):
                load_api_key("GEMINI_API_KEY")


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
