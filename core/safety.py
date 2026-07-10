"""Input validation helpers for the Phase 1 CLI."""

from core.errors import InputValidationError

EXIT_COMMANDS = frozenset({"/exit", "/quit"})


def is_exit_command(value: str) -> bool:
    """Return whether the supplied input is a configured exit command."""

    return value.strip().lower() in EXIT_COMMANDS


def validate_user_input(value: str, max_chars: int) -> str:
    """Normalize and validate user text against Phase 1 input rules."""

    text = value.strip()
    if not text:
        raise InputValidationError("Please enter a non-empty message.")
    if len(text) > max_chars:
        raise InputValidationError(f"Input is too long. Maximum length is {max_chars} characters.")
    return text
