"""Configuration loading and validation for the Phase 1 runtime."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.errors import ConfigurationError, MissingConfigError, MissingSecretError

DEFAULT_CONFIG_PATH = Path("config/settings.toml")


@dataclass(frozen=True)
class RuntimeConfig:
    """Validated non-secret runtime settings loaded from the local config file."""

    provider_name: str
    provider_model: str
    provider_timeout_seconds: int
    provider_thinking_level: str
    provider_max_retries: int
    session_history_max_messages: int
    max_user_input_chars: int
    api_key_env_var: str
    system_prompt_path: Path
    log_file: Path


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> RuntimeConfig:
    """Load and validate the local TOML config file."""

    config_path = Path(path)
    if not config_path.exists():
        raise MissingConfigError(f"Missing config file: {config_path}")

    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigurationError(f"Invalid TOML in {config_path}: {exc}") from exc
    except OSError as exc:
        raise ConfigurationError(f"Could not read config file {config_path}: {exc}") from exc

    base_dir = _project_root_for(config_path)
    config = RuntimeConfig(
        provider_name=_require_str(data, "provider_name"),
        provider_model=_require_str(data, "provider_model"),
        provider_timeout_seconds=_require_positive_int(data, "provider_timeout_seconds"),
        provider_thinking_level=_require_thinking_level(data, "provider_thinking_level"),
        provider_max_retries=_require_non_negative_int(data, "provider_max_retries"),
        session_history_max_messages=_require_positive_int(data, "session_history_max_messages"),
        max_user_input_chars=_require_positive_int(data, "max_user_input_chars"),
        api_key_env_var=_require_str(data, "api_key_env_var"),
        system_prompt_path=_resolve_path(_require_str(data, "system_prompt_path"), base_dir),
        log_file=_resolve_path(_require_str(data, "log_file"), base_dir),
    )

    if config.provider_name != "gemini":
        raise ConfigurationError("Phase 1 supports only provider_name = 'gemini'.")

    return config


def load_system_prompt(path: Path) -> str:
    """Load the editable system prompt from disk."""

    if not path.exists():
        raise ConfigurationError(f"Missing system prompt file: {path}")
    try:
        prompt = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ConfigurationError(f"Could not read system prompt file {path}: {exc}") from exc
    if not prompt:
        raise ConfigurationError("System prompt file must not be empty.")
    return prompt


def load_api_key(env_var: str) -> str:
    """Read a required API key from an environment variable."""

    value = os.environ.get(env_var, "").strip()
    if not value:
        raise MissingSecretError(f"Missing required environment variable: {env_var}")
    return value


def _project_root_for(config_path: Path) -> Path:
    resolved = config_path.resolve()
    if resolved.parent.name == "config":
        return resolved.parent.parent
    return resolved.parent


def _resolve_path(value: str, base_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return base_dir / path


def _require_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"Config value '{key}' must be a non-empty string.")
    return value.strip()


def _require_positive_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or value <= 0:
        raise ConfigurationError(f"Config value '{key}' must be a positive integer.")
    return value


def _require_non_negative_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or value < 0:
        raise ConfigurationError(f"Config value '{key}' must be a non-negative integer.")
    return value


def _require_thinking_level(data: dict[str, Any], key: str) -> str:
    value = _require_str(data, key).lower()
    if value not in {"minimal", "high"}:
        raise ConfigurationError("Config value 'provider_thinking_level' must be minimal or high.")
    return value
