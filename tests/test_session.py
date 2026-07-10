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


if __name__ == "__main__":
    unittest.main()
