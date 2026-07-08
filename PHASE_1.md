# Phase 1 Contract

## Purpose

Phase 1 exists to build a small, reliable assistant core that can be trusted before any advanced "Jarvis" features are added.

The goal is not to build the full assistant. The goal is to build the smallest useful foundation that can survive repeated use, failure cases, refactoring, and future expansion.

## Phase 1 Goal

Build a text-first command-line assistant that can:

1. Accept user text input.
2. Send that input to one configured LLM provider.
3. Return a clear text response.
4. Maintain a short in-memory session during the current run.
5. Log each interaction in a reviewable local format.
6. Handle common failures without crashing.
7. Be tested and manually verified before any Phase 2 work begins.

## Guiding Principle

Phase 1 must be boring, robust, and limited.

Any feature that does not directly support the core text assistant loop is out of scope unless this document is explicitly updated.

## Core User Flow

```text
Start assistant
  -> load config
  -> load system prompt
  -> wait for user input
  -> exit cleanly if input is /exit or /quit
  -> validate input
  -> send request to LLM provider
  -> receive response
  -> print response
  -> log interaction
  -> wait for next input
```

## Phase 1 Defaults

Phase 1 must use these concrete defaults unless this contract is deliberately updated:

- Session history limit: last 10 conversation messages, excluding the system prompt.
- Maximum user input length: 8,000 characters.
- Log format: JSONL, one interaction per line.
- Log location: local filesystem only.
- Exit commands: `/exit` and `/quit`.
- Provider timeout: 30 seconds.

## In Scope

Phase 1 includes only the following:

- Command-line interface.
- Text input.
- Text output.
- One LLM provider.
- One editable system prompt.
- One local config file.
- Basic runtime settings.
- Environment-variable secret loading.
- Bounded session history for the current process.
- Local JSONL interaction logging.
- Graceful shutdown.
- Clear error messages.
- Unit tests.
- Integration-style tests using fakes or mocks.
- Manual verification checklist.
- Documentation for setup, configuration, use, and limitations.

## Out Of Scope

The following are not allowed in Phase 1:

- Wake word detection.
- Always-listening microphone behavior.
- Speech-to-text.
- Text-to-speech.
- GUI.
- Web UI.
- Mobile app.
- Browser automation.
- Computer control.
- Home Assistant integration.
- Smart home control.
- Tool calling.
- Autonomous agents.
- Background tasks.
- Scheduling.
- Long-term memory.
- Vector databases.
- Embeddings.
- Retrieval-augmented generation.
- Multi-provider routing.
- Provider fallback logic.
- Plugin systems.
- Self-modifying code.
- Self-improvement loops.
- Complex personality systems.
- External databases.
- Cloud storage.
- User accounts.

If one of these becomes necessary, it belongs in a later phase unless this contract is deliberately revised.

## Proposed Project Shape

```text
voice-assistant/
  main.py
  config/
    settings.toml
    system_prompt.txt
  core/
    assistant.py
    config.py
    errors.py
    logging.py
    session.py
    safety.py
  providers/
    base.py
    gemini_provider.py
  interfaces/
    cli.py
  tests/
    test_assistant.py
    test_config.py
    test_logging.py
    test_session.py
    test_safety.py
  logs/
    .gitkeep
  AGENTS.md
  PHASE_1.md
  PHASE_1_EXIT_CRITERIA.md
  README.md
  pyproject.toml
```

This shape is a starting point, not a license to add extra systems. Any directory added during Phase 1 must have a clear Phase 1 purpose.

## Architecture Boundaries

The project must keep these responsibilities separate:

- `interfaces/`: user-facing input and output.
- `core/`: assistant orchestration, session handling, validation, and errors.
- `providers/`: external LLM provider adapters.
- `config/`: local configuration and prompt files.
- `tests/`: automated verification.
- `logs/`: local runtime logs.

The command-line interface must not contain provider-specific logic.

The provider implementation must not contain command-line behavior.

The assistant core must be testable without making network calls.

## Dependency Rules

Phase 1 should use the Python standard library wherever practical.

Allowed runtime dependency:

- One official LLM client package, if needed for the selected provider.

Allowed development dependencies:

- `pytest`
- `pytest-cov`
- `ruff`
- `mypy`, only if type checking is enforced from the start

Not allowed without explicit approval:

- Agent frameworks.
- Workflow orchestration frameworks.
- Vector database clients.
- Web frameworks.
- GUI frameworks.
- Speech libraries.
- Home Assistant libraries.
- Database ORMs.
- Plugin frameworks.

Every dependency must have a clear reason, and the standard library must be considered first.

## Configuration Rules

Phase 1 configuration must be simple and local.

Required:

- Config file for non-secret settings.
- Environment variable for API keys.
- Separate system prompt file.
- Clear startup error if required configuration is missing.
- Explicit `session_history_max_messages` value, defaulting to 10.
- Explicit `max_user_input_chars` value, defaulting to 8,000.
- Explicit `provider_timeout_seconds` value, defaulting to 30.

Not allowed:

- Hardcoded secrets.
- Multiple config formats.
- Hidden global state.
- Silent fallback to unsafe defaults.

## Logging Rules

The assistant must log enough information to debug behavior without exposing secrets.

Logs must be local only.

Logs must use JSONL, with one complete interaction per line.

Logs may include user and assistant conversation text in Phase 1, but this must be documented clearly in the README.

Future phases may add configurable redaction or logging levels. Phase 1 should not build that system early.

Required log fields:

- Timestamp.
- Session ID.
- User input.
- Assistant response.
- Provider name.
- Success or failure state.
- Error type when applicable.

Logs must not include:

- API keys.
- Raw environment variable dumps.
- Unnecessary system information.

Logs must not be sent to any external logging service in Phase 1.

## Error Handling Requirements

The assistant must handle these cases cleanly:

- Missing config file.
- Invalid config value.
- Missing API key.
- Empty user input.
- User input longer than 8,000 characters.
- Provider timeout after the configured timeout, defaulting to 30 seconds.
- Provider authentication failure.
- Provider rate limit.
- Provider unavailable.
- Keyboard interrupt.
- Log write failure.

Handling cleanly means the assistant gives a useful message, preserves control of the process when appropriate, and does not print secrets.

## Testing Requirements

Automated tests are required but not sufficient.

Phase 1 must include tests for:

- Assistant request flow.
- Session history behavior.
- Session history truncation at 10 conversation messages.
- Input validation.
- User input length validation.
- Config loading.
- Missing config behavior.
- Missing API key behavior.
- Exit commands `/exit` and `/quit`.
- Provider success.
- Provider failure.
- Provider timeout configuration.
- Logging success.
- Logging failure.
- JSONL log formatting.
- Graceful shutdown paths where practical.

Network calls must be mocked or faked in automated tests.

No test should require a real API key unless it is explicitly marked as a manual or optional live-provider test.

## Manual Verification Requirements

Before Phase 1 can be considered complete, the following must be manually verified:

- Fresh setup from documented instructions.
- Assistant starts successfully with valid config.
- Assistant fails clearly with missing config.
- Assistant fails clearly with missing API key.
- Normal prompt and response works.
- Empty input is handled cleanly.
- Input longer than 8,000 characters is handled cleanly.
- Multi-turn session behaves as expected.
- Session history is bounded to the last 10 conversation messages.
- `/exit` exits cleanly.
- `/quit` exits cleanly.
- Logs are written as local JSONL and are reviewable.
- Logs do not contain secrets.
- Logs may contain conversation text, and this is clearly documented.
- Ctrl+C exits cleanly.
- Provider failure produces a useful error.
- Provider timeout behavior uses the configured timeout, defaulting to 30 seconds.
- README instructions are accurate.

## Phase 1 Exit Rule

Phase 1 is not complete just because tests pass.

Phase 1 is complete only when:

1. All automated tests pass.
2. Linting passes.
3. Type checks pass if type checking is enabled.
4. Manual verification is completed.
5. Logs have been inspected.
6. Failure modes have been tested.
7. Documentation matches actual behavior.
8. `PHASE_1_EXIT_CRITERIA.md` is fully checked off.
9. No out-of-scope features were added.
10. The project can be explained simply from the README and code structure.

## Change Control

This file controls Phase 1 scope.

If a proposed change is not clearly in scope, it must not be implemented until one of the following happens:

1. The change is moved to a later-phase backlog.
2. This document is deliberately updated.
3. The reason for the exception is documented.

Scope changes should be rare.

## Later-Phase Parking Lot

Ideas that are intentionally deferred:

- Voice input.
- Voice output.
- Wake word.
- Home Assistant control.
- Tool calling.
- Local memory.
- Long-term memory.
- GUI.
- Web dashboard.
- Mobile companion.
- Background automation.
- Multi-provider support.
- Offline/local model support.
- Permissions system.
- User profiles.
- Configurable log redaction.
- Configurable logging levels.

This parking lot exists so good ideas are not lost, but they must not leak into Phase 1.
