"""Tests for bounded in-memory session history."""

import unittest

from core.session import Session


class SessionTests(unittest.TestCase):
    """Coverage for session storage and truncation behavior."""

    def test_add_stores_messages(self) -> None:
        session = Session(max_messages=10)
        session.add("user", "hello")
        session.add("assistant", "hi")

        self.assertEqual(len(session.messages), 2)
        self.assertEqual(session.messages[0].role, "user")
        self.assertEqual(session.messages[1].content, "hi")

    def test_session_truncates_to_last_10_messages(self) -> None:
        session = Session(max_messages=10)

        for index in range(12):
            session.add("user", f"message {index}")

        self.assertEqual(len(session.messages), 10)
        self.assertEqual(session.messages[0].content, "message 2")
        self.assertEqual(session.messages[-1].content, "message 11")

    def test_session_rejects_invalid_max_messages(self) -> None:
        for value in (True, 0, -2):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    Session(max_messages=value)

    def test_session_rejects_odd_max_messages(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be even"):
            Session(max_messages=9)

    def test_session_rejects_invalid_role(self) -> None:
        session = Session(max_messages=10)

        with self.assertRaisesRegex(ValueError, "role must be"):
            session.add("model", "hello")

    def test_session_rejects_empty_content(self) -> None:
        session = Session(max_messages=10)

        with self.assertRaisesRegex(ValueError, "content must not be empty"):
            session.add("user", "")


if __name__ == "__main__":
    unittest.main()
