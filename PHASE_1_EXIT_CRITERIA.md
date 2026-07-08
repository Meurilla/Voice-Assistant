# Phase 1 Exit Criteria

## Purpose

This document is the release gate for Phase 1.

Phase 1 is not complete when the code "basically works." Phase 1 is complete only when every required item in this file has been checked, verified, and reviewed against `PHASE_1.md`.

No Phase 2 feature work may begin until this document is complete.

## Completion Rule

Every required checklist item must be marked complete before Phase 1 is considered finished.

Use this format when completing an item:

```text
- [x] Requirement name
  - Evidence: What was run, inspected, or verified.
  - Date:
  - Notes:
```

If an item is intentionally skipped, it must be documented under `Deferred Or Waived Items` with a clear reason and explicit approval.

## 1. Scope Control

- [ ] `PHASE_1.md` has been reviewed before exit.
- [ ] No out-of-scope Phase 1 features were added.
- [ ] No wake word behavior exists.
- [ ] No speech-to-text behavior exists.
- [ ] No text-to-speech behavior exists.
- [ ] No GUI or web UI exists.
- [ ] No Home Assistant or smart home control exists.
- [ ] No autonomous agent behavior exists.
- [ ] No tool-calling system exists.
- [ ] No long-term memory system exists.
- [ ] No vector database, embeddings, or retrieval system exists.
- [ ] No multi-provider routing or fallback system exists.
- [ ] Any deferred ideas were recorded outside the implementation path.

## 2. Project Structure

- [ ] Project structure matches the approved Phase 1 shape or has documented deviations.
- [ ] CLI code is isolated under the interface layer.
- [ ] Assistant orchestration is isolated under the core layer.
- [ ] LLM provider code is isolated under the provider layer.
- [ ] Configuration files are isolated under the config area.
- [ ] Tests are isolated under the tests area.
- [ ] Runtime logs are isolated under the logs area.
- [ ] No module has mixed unrelated responsibilities.
- [ ] The assistant core can be tested without live network calls.

## 3. Configuration

- [ ] Non-secret settings load from a local config file.
- [ ] The system prompt loads from a separate editable prompt file.
- [ ] API keys are loaded from environment variables.
- [ ] No secrets are hardcoded in source files.
- [ ] `session_history_max_messages` is explicit and defaults to 10.
- [ ] `max_user_input_chars` is explicit and defaults to 8,000.
- [ ] `provider_timeout_seconds` is explicit and defaults to 30.
- [ ] Missing config produces a clear startup error.
- [ ] Invalid config produces a clear startup error.
- [ ] Missing prompt file produces a clear startup error.
- [ ] Missing API key produces a clear startup error.
- [ ] Config defaults are explicit and documented.
- [ ] No silent fallback hides unsafe or invalid configuration.

## 4. Core Assistant Behavior

- [ ] Assistant starts from the documented command.
- [ ] Assistant accepts normal text input.
- [ ] Assistant rejects or ignores empty input cleanly.
- [ ] Assistant rejects or handles input over 8,000 characters cleanly.
- [ ] Assistant sends valid input to the configured provider.
- [ ] Assistant prints a clear text response.
- [ ] Assistant keeps bounded session history during the current run.
- [ ] Assistant retains no more than the last 10 conversation messages, excluding the system prompt.
- [ ] Session history is passed consistently to the provider when expected.
- [ ] Assistant handles multiple prompts in one run.
- [ ] Assistant exits cleanly on `/exit`.
- [ ] Assistant exits cleanly on `/quit`.
- [ ] Assistant exits cleanly on keyboard interrupt.
- [ ] Assistant does not expose internal stack traces during normal user-facing failures.

## 5. Provider Behavior

- [ ] Exactly one LLM provider is configured for Phase 1.
- [ ] Provider interface is abstracted enough to fake in tests.
- [ ] Provider implementation has no CLI behavior.
- [ ] Provider success path is tested.
- [ ] Provider timeout is configured explicitly and defaults to 30 seconds.
- [ ] Provider timeout path is tested or manually simulated.
- [ ] Provider authentication failure path is tested or manually simulated.
- [ ] Provider rate-limit path is tested or manually simulated.
- [ ] Provider unavailable path is tested or manually simulated.
- [ ] Provider errors become clear user-facing messages.
- [ ] Provider errors are logged without leaking secrets.
- [ ] No automated test requires a live API key.

## 6. Logging

- [ ] Each interaction logs a timestamp.
- [ ] Each interaction logs a session ID.
- [ ] Each interaction logs the user input.
- [ ] Each interaction logs the assistant response when available.
- [ ] Each interaction logs the provider name.
- [ ] Each interaction logs success or failure state.
- [ ] Failures log an error type.
- [ ] Logs are local only.
- [ ] Logs use JSONL.
- [ ] Logs contain one complete interaction per line.
- [ ] Each generated JSONL line is parseable as JSON.
- [ ] Logs are written in a reviewable local format.
- [ ] Log write failure is handled cleanly.
- [ ] Logs do not include API keys.
- [ ] Logs do not include raw environment dumps.
- [ ] Logs do not include unnecessary system information.
- [ ] Logs are not sent to an external logging service.
- [ ] Logs may include conversation text in Phase 1, and this is documented clearly.
- [ ] A generated log file has been manually inspected.

## 7. Error Handling

- [ ] Missing config file handled cleanly.
- [ ] Invalid config value handled cleanly.
- [ ] Missing API key handled cleanly.
- [ ] Empty input handled cleanly.
- [ ] Input over 8,000 characters handled cleanly.
- [ ] Provider timeout handled cleanly.
- [ ] Provider authentication failure handled cleanly.
- [ ] Provider rate limit handled cleanly.
- [ ] Provider unavailable handled cleanly.
- [ ] Keyboard interrupt handled cleanly.
- [ ] Log write failure handled cleanly.
- [ ] User-facing error messages are specific enough to act on.
- [ ] User-facing error messages do not expose secrets.

## 8. Automated Tests

- [ ] Test suite runs from the documented command.
- [ ] Assistant request flow is tested.
- [ ] Session history behavior is tested.
- [ ] Session history truncation at 10 conversation messages is tested.
- [ ] Input validation is tested.
- [ ] Input length validation is tested.
- [ ] Config loading is tested.
- [ ] Missing config behavior is tested.
- [ ] Invalid config behavior is tested.
- [ ] Missing API key behavior is tested.
- [ ] Prompt loading is tested.
- [ ] `/exit` command behavior is tested.
- [ ] `/quit` command behavior is tested.
- [ ] Provider success is tested with a fake or mock.
- [ ] Provider failure is tested with a fake or mock.
- [ ] Provider timeout configuration is tested.
- [ ] Logging success is tested.
- [ ] Logging failure is tested.
- [ ] JSONL log formatting is tested.
- [ ] Graceful shutdown paths are tested where practical.
- [ ] Tests do not depend on execution order.
- [ ] Tests do not depend on a real API key.
- [ ] Tests do not make live network calls by default.
- [ ] All tests pass.

## 9. Static Validation

- [ ] Formatting command has been run, if configured.
- [ ] Linting command has been run.
- [ ] Linting passes.
- [ ] Type checking has been run if configured.
- [ ] Type checking passes if configured.
- [ ] Dependency list has been reviewed.
- [ ] No unapproved runtime dependency was added.
- [ ] No unapproved development dependency was added.
- [ ] Import structure has been reviewed for obvious circular dependencies.

## 10. Manual Verification

- [ ] Fresh setup was performed from the README instructions.
- [ ] Virtual environment creation works as documented.
- [ ] Dependency installation works as documented.
- [ ] Valid config starts the assistant successfully.
- [ ] Missing config fails clearly.
- [ ] Invalid config fails clearly.
- [ ] Missing API key fails clearly.
- [ ] Normal prompt and response works.
- [ ] Empty input is handled cleanly.
- [ ] Input over 8,000 characters is handled cleanly.
- [ ] Multi-turn session behaves as expected.
- [ ] Session history remains bounded to the last 10 conversation messages.
- [ ] `/exit` exits cleanly.
- [ ] `/quit` exits cleanly.
- [ ] Logs are created.
- [ ] Logs are JSONL.
- [ ] Logs are local only.
- [ ] Logs are reviewable.
- [ ] Logs do not contain secrets.
- [ ] Logs may contain conversation text, and this is documented clearly.
- [ ] Keyboard interrupt exits cleanly.
- [ ] Provider failure produces a useful error.
- [ ] Provider timeout uses the configured timeout, defaulting to 30 seconds.
- [ ] README commands match actual commands.
- [ ] README limitations match actual Phase 1 limits.

## 11. Documentation

- [ ] README explains what the assistant does.
- [ ] README explains what the assistant does not do.
- [ ] README includes setup instructions.
- [ ] README includes configuration instructions.
- [ ] README documents the default session history limit of 10 conversation messages.
- [ ] README documents the default maximum input length of 8,000 characters.
- [ ] README documents the default provider timeout of 30 seconds.
- [ ] README documents `/exit` and `/quit`.
- [ ] README explains required environment variables.
- [ ] README includes run instructions.
- [ ] README includes test instructions.
- [ ] README includes troubleshooting notes.
- [ ] README documents that logs are local JSONL files.
- [ ] README documents that Phase 1 logs may include conversation text.
- [ ] README documents that logs must never include secrets.
- [ ] README references `PHASE_1.md`.
- [ ] README references this exit criteria document.
- [ ] `AGENTS.md` exists and enforces Phase 1 boundaries.
- [ ] Documentation has been checked against current behavior.

## 12. Security And Privacy

- [ ] Secrets are never committed.
- [ ] Example config files contain placeholders only.
- [ ] `.gitignore` excludes local secrets and runtime logs where appropriate.
- [ ] Error messages do not print API keys.
- [ ] Logs do not print API keys.
- [ ] Logs are local only.
- [ ] Logs use JSONL.
- [ ] Phase 1 conversation-text logging is clearly documented.
- [ ] Tests do not require real secrets.
- [ ] No unnecessary personal data is collected.
- [ ] No external service is contacted except the configured LLM provider during normal live use.
- [ ] No external logging service is contacted during normal use.

## 13. Reliability Review

- [ ] The assistant can run more than one prompt in a single session.
- [ ] The assistant can recover from a provider error and continue when appropriate.
- [ ] The assistant can exit without corrupting logs.
- [ ] The assistant behaves predictably with whitespace-only input.
- [ ] The assistant behaves predictably with unusually long input within configured limits.
- [ ] The assistant rejects or handles input over 8,000 characters predictably.
- [ ] The assistant has a clear session history limit of 10 conversation messages.
- [ ] The assistant has a clear user input limit of 8,000 characters.
- [ ] Failure behavior has been reviewed manually.

## 14. Final Review

- [ ] `PHASE_1.md` and implementation agree.
- [ ] `PHASE_1_EXIT_CRITERIA.md` is fully checked or documented.
- [ ] `AGENTS.md` reflects the current Phase 1 rules.
- [ ] README accurately explains the current project.
- [ ] No obvious dead code remains.
- [ ] No temporary debug prints remain.
- [ ] No test-only shortcuts are present in production code.
- [ ] No local-only absolute paths are required for normal use.
- [ ] The full validation command set has been run.
- [ ] Final manual smoke test has been run.

## Required Evidence Summary

Complete this section before Phase 1 exit.

```text
Automated tests:
Command:
Result:
Date:

Lint:
Command:
Result:
Date:

Type check, if enabled:
Command:
Result:
Date:

Manual smoke test:
Command:
Result:
Date:

Log inspection:
File inspected:
Result:
Date:

Config failure test:
Result:
Date:

Provider failure test:
Result:
Date:
```

## Deferred Or Waived Items

Any incomplete item must be listed here before Phase 1 can exit.

```text
Item:
Reason:
Risk:
Approved by:
Date:
Follow-up:
```

## Phase 1 Exit Decision

Phase 1 exit is approved only when the following is true:

- [ ] Every required item is checked or explicitly documented as waived.
- [ ] Waived items do not undermine the Phase 1 contract.
- [ ] Evidence summary is complete.
- [ ] No Phase 2 feature work has started.
- [ ] Final reviewer agrees Phase 1 is stable enough to build on.

```text
Phase 1 exit approved: yes/no
Approved by:
Date:
Notes:
```
