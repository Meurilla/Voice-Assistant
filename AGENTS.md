# Project Agent Instructions

## Project State

This project is in Phase 2 scope/evaluation, following the approved Phase 1 exit. The runtime still implements the Phase 1 text assistant until Phase 2 changes are delivered and verified.

The current objective is controlled English voice input on Windows with a portable core, initially evaluating one free cloud STT service. Voice output is reserved for Phase 3. See `PHASE_2.md` and `PHASE_2_EXIT_CRITERIA.md`.

## Required Reading

Before making any code, configuration, dependency, or documentation change, read:

1. `PHASE_1.md`
2. `PHASE_1_EXIT_CRITERIA.md`
3. `AGENTS.md`
4. `PHASE_2.md`
5. `PHASE_2_EXIT_CRITERIA.md`

Treat `PHASE_1.md` as the source of truth for Phase 1 scope.

Treat `PHASE_1_EXIT_CRITERIA.md` as the source of truth for Phase 1 completion.

Treat `PHASE_2.md` as the active scope contract and `PHASE_2_EXIT_CRITERIA.md` as its completion gate. The Phase 1 sections below preserve the baseline rules. Only the explicit Phase 2 additions supersede their prohibitions on speech input, audio dependencies, and a separate STT service. All other safeguards and exclusions remain in force.

## Phase 2 Rules

- Keep Gemini as the sole conversation provider; one STT service may convert audio to text.
- Start with the free cloud evaluation in `PHASE_2.md`; do not enable paid usage.
- Keep recording deliberate, bounded and separate from transcript review and assistant requests.
- Require transcript acceptance before Gemini submission; rejected or failed transcription must not update history.
- Keep text mode usable without speech credentials, audio packages, or hardware.
- Isolate platform-specific capture details; do not claim other platforms are supported before testing them.
- Permit only narrowly justified optional speech dependencies documented before installation.
- Keep secrets environment-based, redact both service keys, and retain no raw audio by default.
- Do not implement voice output or other later-phase capabilities.

## Core Rule

Do not build "Jarvis" in Phase 1.

Build only the reliable foundation that a future Jarvis-like assistant can safely grow from.

Phase 1 must stay boring, limited, testable, and maintainable.

## Phase 1 Scope Boundary

Allowed Phase 1 work:

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
- Graceful shutdown, including cleanup-failure behavior.
- Clear error messages.
- Unit tests.
- Integration-style tests using fakes or mocks.
- Manual verification checklist.
- Documentation for setup, configuration, use, and limitations.

Do not add these in Phase 1:

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

If a requested change falls outside Phase 1, do not implement it directly. Explain that it is out of scope, suggest recording it for a later phase, and only proceed if the user explicitly revises the Phase 1 contract.

## Phase 1 Defaults

Use these defaults unless `PHASE_1.md` is deliberately updated:

- Session history limit: last 10 conversation messages, excluding the system prompt; configured limits must be positive even integers.
- Maximum user input length: 8,000 characters.
- Log format: JSONL, one interaction per line.
- Log location: local filesystem only.
- Exit commands: `/exit` and `/quit`.
- Provider timeout: 30 seconds.
- Provider maximum retries: 2, configurable from 0 through 2.
- Provider retry base delay: 3 seconds, configurable from 0 through 10 seconds.

## Architecture Rules

Keep responsibilities separated:

- `interfaces/`: user-facing input and output.
- `core/`: assistant orchestration, session handling, validation, and errors.
- `providers/`: external LLM provider adapters.
- `config/`: local configuration and prompt files.
- `tests/`: automated verification.
- `logs/`: local runtime logs.

The CLI must not contain provider-specific logic.

The provider implementation must not contain CLI behavior.

The assistant core must be testable without live network calls.

Do not add new directories or architectural layers unless they clearly support the active phase contract.

## Dependency Rules

Prefer the Python standard library.

Allowed runtime dependency:

- One official LLM client package, if required by the selected provider.

Allowed development dependencies:

- `pytest`
- `pytest-cov`
- `ruff`
- `mypy`, only if type checking is enforced from the start

Do not add agent frameworks, web frameworks, GUI frameworks, speech libraries, vector databases, plugin frameworks, or Home Assistant libraries during Phase 1.

Before adding any dependency, document:

- Why it is needed.
- Why the standard library is insufficient.
- Whether it is runtime or development-only.
- How it affects setup and verification.

## Secrets And Privacy

Never hardcode secrets.

API keys must come from environment variables.

Do not print or log API keys.

Do not dump raw environment variables.

Logs must be useful for debugging but must not expose secrets or unnecessary system information.

Logs must be local only.

Logs must use JSONL.

Logs may include user and assistant conversation text in Phase 1, but this must be documented clearly.

Do not add configurable log redaction or logging levels in Phase 1 unless the phase contract is explicitly revised.

Example config files must use placeholders only.

## Testing Rules

Automated tests are required but not sufficient.

Tests must not require a real API key by default.

Tests must not make live network calls by default.

Provider behavior should be tested with fakes or mocks.

Failure modes must be tested or manually simulated before Phase 1 exit.

When practical, test:

- Config loading.
- Prompt loading.
- Missing config.
- Invalid config.
- Missing API key.
- Input validation.
- Input length validation.
- Assistant request flow.
- Session history.
- Session history truncation at 10 conversation messages.
- Exit commands `/exit` and `/quit`.
- Provider success.
- Provider failure.
- Provider timeout configuration.
- Logging success.
- Logging failure.
- JSONL log formatting.
- Graceful shutdown and cleanup-failure behavior.

## Verification Standard

A change is not complete merely because code was edited.

For every implementation change, verify with the narrowest meaningful commands available:

- Unit tests for touched behavior.
- Broader tests when shared behavior changes.
- Linting when configured.
- Type checking when configured.
- Manual smoke test when behavior is user-facing.

If validation cannot be run, say so clearly and explain what should be run.

Before Phase 2 starts, `PHASE_1_EXIT_CRITERIA.md` must be completed or explicitly waived item by item.

## Development Workflow

Before editing:

1. Inspect the relevant files.
2. Understand existing structure and naming.
3. Check related tests and documentation.
4. Make a short plan for non-trivial changes.

While editing:

1. Make small, focused changes.
2. Preserve existing behavior unless the task requires changing it.
3. Avoid unrelated refactors.
4. Keep code readable and explicit.
5. Add comments only for non-obvious intent or edge cases.

After editing:

1. Re-read the modified area.
2. Run relevant validation.
3. Summarize changed files.
4. Report validation performed and not performed.
5. Call out remaining risk or follow-up work.

## Git Rules

Do not commit unless explicitly asked.

Do not push unless explicitly asked.

Do not rewrite history unless explicitly asked and the consequences are clear.

Do not revert user changes unless explicitly asked.

Keep diffs focused and reviewable.

## Documentation Rules

Documentation must match actual behavior.

If behavior, commands, configuration, dependencies, or limitations change, update the relevant documentation in the same task.

The README must eventually explain:

- What the assistant does.
- What it does not do.
- Setup.
- Configuration.
- Default session history limit.
- Default maximum user input length.
- Default provider timeout.
- Exit commands.
- Required environment variables.
- Run command.
- Test command.
- Local JSONL logging.
- Phase 1 conversation-text logging behavior.
- Troubleshooting.
- Phase 1 limitations.

## Phase Progression

The Phase 2 entry requirements are:

1. `PHASE_1_EXIT_CRITERIA.md` is complete or explicitly waived item by item.
2. The user approves moving beyond Phase 1.
3. The new phase scope is documented.

Phase 1 exit and the user's Phase 2 direction are recorded in the phase documents. Before Phase 3 begins, complete or explicitly waive Phase 2 exit items, obtain approval to start Phase 3, and document its scope. Voice output is a roadmap direction only until then.

## Response Expectations

When reporting completed work, include:

- Files changed.
- What changed.
- Why it changed.
- Validation performed.
- Validation not performed, if any.
- Remaining risks or recommended next step.
