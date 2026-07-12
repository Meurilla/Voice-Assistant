"""Local JSONL interaction logging with Phase 1 secret redaction safeguards."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from core.errors import LogWriteError

_GOOGLE_API_KEY_PATTERN = re.compile(r"AIza[0-9A-Za-z_\-]{20,}")
_API_KEY_REDACTION = "[REDACTED_API_KEY]"


class InteractionLogger:
    """Append one redacted interaction record per line to a local JSONL file."""

    def __init__(self, log_file: Path, secrets: Iterable[str] = ()) -> None:
        self.log_file = log_file
        self._secrets = tuple(
            sorted({secret for secret in secrets if secret}, key=len, reverse=True)
        )

    def log_interaction(
        self,
        *,
        session_id: str,
        user_input: str,
        assistant_response: str | None,
        provider_name: str,
        success: bool,
        error_type: str | None = None,
        provider_attempt_count: int = 0,
        provider_retry_count: int = 0,
        provider_final_status_code: int | None = None,
        provider_error_message: str | None = None,
        provider_elapsed_ms: int | None = None,
    ) -> None:
        """Write one interaction record, raising a user-facing error on failure."""

        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": session_id,
            "user_input": self._redact_secrets(user_input),
            "assistant_response": self._redact_secrets(assistant_response),
            "provider_name": provider_name,
            "success": success,
            "error_type": error_type,
            "provider_attempt_count": provider_attempt_count,
            "provider_retry_count": provider_retry_count,
            "provider_final_status_code": provider_final_status_code,
            "provider_error_message": self._redact_secrets(provider_error_message),
            "provider_elapsed_ms": provider_elapsed_ms,
        }

        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with self.log_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as exc:
            raise LogWriteError(f"Could not write interaction log: {exc}") from exc

    def _redact_secrets(self, value: str | None) -> str | None:
        if value is None:
            return None

        redacted = value
        for secret in self._secrets:
            redacted = redacted.replace(secret, _API_KEY_REDACTION)
        return _GOOGLE_API_KEY_PATTERN.sub(_API_KEY_REDACTION, redacted)
