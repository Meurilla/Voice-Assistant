# Project Agent Instructions

## Current State And Required Reading

The active phase is Phase 2: controlled English voice input on Windows with a portable core. The runtime remains the completed text assistant until voice input is implemented and verified. Voice output belongs to Phase 3.

Before code, configuration, dependency, or documentation changes, read:

1. `AGENTS.md`.
2. [PHASE_2.md](PHASE_2.md), the active scope and CLI/audio contract.
3. [PHASE_2_EXIT_CRITERIA.md](PHASE_2_EXIT_CRITERIA.md), the completion gate.

For compatibility decisions, consult the completed [Phase 1 contract](phases/phase_1/PHASE_1.md) and [exit evidence](phases/phase_1/PHASE_1_EXIT_CRITERIA.md). These record the historical baseline, not current feature prohibitions.

## Phase Documents And History

Keep the current phase contract and exit criteria, `AGENTS.md`, and README at the repository root. Archive completed phase documents under `phases/phase_<number>/` when the next phase is approved and documented.

Archived documents are immutable history. Preserve their contents, dates, evidence, and historical path references. Update active documents to link to the archive; record new decisions and compatibility amendments in the active contract instead of rewriting completed phases.

## Scope Boundaries

- Implement only the controlled recording, transcription evaluation, transcript review, and text handoff defined in `PHASE_2.md`.
- Use Gemini as the sole conversation provider and one selected cloud STT service for audio-to-text conversion. Keep the trial on the Free tier.
- Keep typed input usable without speech credentials, audio dependencies, or a microphone.
- Follow the exact CLI state/command table and frozen audio format. Verify the real Windows capture path before collecting the 25-sample evaluation.
- Do not claim support for other platforms without testing; isolate platform-specific behavior.
- No voice output, wake words, always-listening behavior, streaming conversations, global keyboard hooks, GUI, web UI, mobile app, Home Assistant, computer control, tool calling, agents, background automation, scheduling, long-term memory, retrieval, multi-provider routing/fallback, plugins, self-modification, external databases/storage, or application user accounts.
- No expanded personality system, logging levels, or configurable redaction system without an explicit scope revision.
- Park out-of-scope ideas for later. Do not implement them until the user revises the active contract.

## Compatibility Baseline

Preserve existing text behavior unless an active-contract change explicitly requires otherwise:

- One local TOML config, separate editable system prompt, environment-variable secrets.
- Default history: 10 conversation messages excluding the system prompt; positive even limits, complete turns only, failed provider turns excluded.
- Default maximum input length: 8,000 characters.
- Gemini timeout: 30 seconds; retries: 2, configurable 0-2; base delay: 3 seconds, configurable 0-10. Retry only transient 500/503 responses with bounded exponential backoff.
- Local JSONL interaction logging, secret redaction, and successful replies surviving log-write failure.
- `/exit`, `/quit`, Ctrl+C and EOF shutdown, deterministic resource cleanup, and cleanup failures reported without replacing an active exception.

STT timeout/retry settings are separate from Gemini settings. Rejected or failed speech input must not invoke Gemini or change conversation history.

## Architecture And Dependencies

- `interfaces/`: terminal interaction and isolated microphone/device boundary.
- `core/`: validation, assistant orchestration, session handling, errors, and local logging.
- `providers/`: separate conversation and transcription adapters; no CLI behavior.
- `config/`: local non-secret settings and system prompt.
- `tests/`: offline verification with fakes/mocks.
- `logs/`: local runtime logs.

Keep the core independent of audio transport and operating-system APIs. Do not introduce new layers unless they directly support the active scope. Internal capture callbacks/workers may support a foreground recording, but must stop with that operation; they are not background automation.

Prefer the standard library and existing tooling. Runtime dependencies may include the existing official Gemini client plus narrowly justified optional voice capture/STT dependencies. Text mode must not import or initialize optional speech components unconditionally.

Before adding a dependency, document its purpose, why existing tools/the standard library are insufficient, runtime versus development status, maintenance/security implications, platform support, and setup/verification impact. Use existing `unittest` and Ruff tooling. The allowed development tools remain pytest, pytest-cov and Ruff; add mypy only with an explicit decision to enforce type checking consistently. Do not add frameworks outside the phase scope.

## Secrets And Privacy

- Never hardcode, print, or log keys or raw environment variables. Examples contain placeholders only.
- Redact both loaded service keys from diagnostics and logs.
- Keep logs local JSONL; document conversation-text logging. Do not log raw audio, raw provider payloads, or rejected transcript text.
- Send audio only through the explicit transcription action and send only accepted text to Gemini.
- Retain no raw audio by default; follow the contract for temporary-file cleanup and intentional evaluation recordings.
- Document cloud processing and provider retention separately from local cleanup. Do not imply that deleting local audio deletes cloud data.

## Workflow And Verification

Before editing, inspect relevant files, related tests and docs, check git status, and give a short plan for non-trivial work. Make small focused changes, preserve unrelated work and safeguards, and update documentation with behavior changes.

After editing, re-read the change and run the narrowest meaningful checks. For implementation changes, use unit/integration tests for affected behavior, broader regression tests for shared behavior, configured lint/format/type checks, and a user-facing smoke test where practical.

Automated tests must not require real API keys, microphones, or live network calls by default. Use fake audio devices and STT/Gemini responses. Complete the hardware, failure, privacy, and setup checks in the exit criteria; mark items complete only with evidence and limitations.

Do not delete data, revert user changes, commit, push, or rewrite git history unless explicitly asked. Keep changes reversible and reviewable.

## Phase Progression And Reporting

Before Phase 3 starts, complete Phase 2 exit criteria or obtain explicit item-by-item waivers, obtain the user's approval to proceed, and document the new scope. Roadmap placement alone does not authorize Phase 3 implementation.

Report files changed, what changed and why, validation performed, validation not performed, and remaining risks or next steps. Distinguish planned behavior from working and verified behavior.
