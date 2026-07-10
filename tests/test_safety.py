"""Tests for exit command detection and user input validation."""

import unittest

from core.errors import InputValidationError
from core.safety import is_exit_command, validate_user_input


class SafetyTests(unittest.TestCase):
    """Coverage for Phase 1 input safety helpers."""

    def test_exit_commands(self) -> None:
        self.assertTrue(is_exit_command("/exit"))
        self.assertTrue(is_exit_command(" /quit "))
        self.assertFalse(is_exit_command("hello"))

    def test_validate_user_input_accepts_text(self) -> None:
        self.assertEqual(validate_user_input(" hello ", 8000), "hello")

    def test_validate_user_input_rejects_empty_text(self) -> None:
        with self.assertRaises(InputValidationError):
            validate_user_input("   ", 8000)

    def test_validate_user_input_rejects_too_long_text(self) -> None:
        with self.assertRaises(InputValidationError):
            validate_user_input("x" * 8001, 8000)


if __name__ == "__main__":
    unittest.main()
