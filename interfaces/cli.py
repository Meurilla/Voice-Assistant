"""Command-line interface wiring and run loop for the Phase 1 assistant."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

from core.assistant import Assistant
from core.config import DEFAULT_CONFIG_PATH, load_api_key, load_config, load_system_prompt
from core.errors import AssistantError, InputValidationError, ProviderError
from core.logging import InteractionLogger
from core.safety import is_exit_command
from core.session import Session
from providers.gemini_provider import GeminiProvider

OutputFunc = Callable[[str], None]
InputFunc = Callable[[str], str]


def _default_error_output(message: str) -> None:
    print(message, file=sys.stderr)


def _close_assistant(assistant: Assistant) -> bool:
    """Close assistant resources and report an ordinary cleanup failure safely."""

    try:
        assistant.close()
    except Exception:
        _default_error_output("Shutdown error: Could not close provider resources.")
        return False
    return True


def build_assistant(config_path: Path = DEFAULT_CONFIG_PATH) -> Assistant:
    """Build the assistant from local config, environment secrets, and provider wiring."""

    config = load_config(config_path)
    system_prompt = load_system_prompt(config.system_prompt_path)
    api_key = load_api_key(config.api_key_env_var)
    provider = GeminiProvider(
        api_key=api_key,
        model=config.provider_model,
        thinking_level=config.provider_thinking_level,
        max_retries=config.provider_max_retries,
        retry_delay_seconds=config.provider_retry_delay_seconds,
    )
    session = Session(max_messages=config.session_history_max_messages)
    interaction_logger = InteractionLogger(config.log_file, secrets=(api_key,))
    return Assistant(
        config=config,
        system_prompt=system_prompt,
        provider=provider,
        session=session,
        interaction_logger=interaction_logger,
    )


def run(config_path: Path = DEFAULT_CONFIG_PATH) -> int:
    """Start the CLI application and return a process exit code."""

    try:
        assistant = build_assistant(config_path)
    except AssistantError as exc:
        print(f"Startup error: {exc.user_message}", file=sys.stderr)
        return 1

    try:
        exit_code = run_loop(assistant)
    except BaseException:
        _close_assistant(assistant)
        raise

    if not _close_assistant(assistant):
        return 1
    return exit_code


def run_loop(
    assistant: Assistant,
    *,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
    error_func: OutputFunc | None = None,
) -> int:
    """Run the interactive text loop until shutdown or end-of-input."""

    if error_func is None:
        error_func = _default_error_output

    while True:
        try:
            try:
                raw_input = input_func("> ")
            except EOFError:
                output_func("")
                output_func("Goodbye.")
                return 0

            if is_exit_command(raw_input):
                output_func("Goodbye.")
                return 0

            try:
                reply = assistant.handle_user_input(raw_input)
            except InputValidationError as exc:
                error_func(exc.user_message)
                continue
            except ProviderError as exc:
                error_func(exc.user_message)
                if exc.log_error:
                    error_func(exc.log_error)
                continue

            output_func(reply.text)
            if reply.log_error:
                error_func(reply.log_error)
        except KeyboardInterrupt:
            output_func("")
            output_func("Goodbye.")
            return 0
