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

- [x] `PHASE_1.md` has been reviewed before exit.
  - Evidence: `PHASE_1.md` was re-read during this exit-criteria pass.
  - Date: 2026-07-08
  - Notes:
- [x] No out-of-scope Phase 1 features were added.
  - Evidence: Source review of `main.py`, `interfaces/`, `core/`, `providers/`, `config/`, tests, README, and `pyproject.toml`.
  - Date: 2026-07-08
  - Notes: Current implementation remains CLI-only, text-only, one-provider, local-config, local-log Phase 1 scope.
- [x] No wake word behavior exists.
  - Evidence: Source review of implemented modules and README limitations.
  - Date: 2026-07-08
  - Notes:
- [x] No speech-to-text behavior exists.
  - Evidence: Source review of implemented modules and dependency list in `pyproject.toml`.
  - Date: 2026-07-08
  - Notes: No speech library is present.
- [x] No text-to-speech behavior exists.
  - Evidence: Source review of implemented modules and dependency list in `pyproject.toml`.
  - Date: 2026-07-08
  - Notes: No speech library is present.
- [x] No GUI or web UI exists.
  - Evidence: Source review of `main.py`, `interfaces/cli.py`, README limitations, and dependency list.
  - Date: 2026-07-08
  - Notes: The only user interface is the CLI loop.
- [x] No Home Assistant or smart home control exists.
  - Evidence: Source review of implemented modules and dependency list in `pyproject.toml`.
  - Date: 2026-07-08
  - Notes:
- [x] No autonomous agent behavior exists.
  - Evidence: Source review of assistant/provider code and README limitations.
  - Date: 2026-07-08
  - Notes: The assistant only responds to direct CLI prompts.
- [x] No tool-calling system exists.
  - Evidence: Source review of provider and assistant interfaces.
  - Date: 2026-07-08
  - Notes: Provider returns plain text only.
- [x] No long-term memory system exists.
  - Evidence: Source review of `core/session.py` and README limitations.
  - Date: 2026-07-08
  - Notes: Session history is in-memory only for the current process.
- [x] No vector database, embeddings, or retrieval system exists.
  - Evidence: Source review of implemented modules and dependency list in `pyproject.toml`.
  - Date: 2026-07-08
  - Notes:
- [x] No multi-provider routing or fallback system exists.
  - Evidence: `config/settings.toml` sets `provider_name = "gemini"`; `core/config.py` rejects non-Gemini providers.
  - Date: 2026-07-08
  - Notes: Transient retry is provider-local, not provider fallback.
- [x] Any deferred ideas were recorded outside the implementation path.
  - Evidence: `PHASE_1.md` contains a later-phase parking lot; README lists out-of-scope capabilities.
  - Date: 2026-07-08
  - Notes:

## 2. Project Structure

- [x] Project structure matches the approved Phase 1 shape or has documented deviations.
  - Evidence: Source tree contains `main.py`, `config/`, `core/`, `interfaces/`, `providers/`, `tests/`, `logs/`, README, phase docs, and `pyproject.toml`.
  - Date: 2026-07-08
  - Notes: Additional Phase 1 support files include `.gitignore`, `test_cli.py`, and `test_gemini_provider.py`.
- [x] CLI code is isolated under the interface layer.
  - Evidence: CLI loop and startup wiring are in `interfaces/cli.py`; `main.py` only calls `run()`.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant orchestration is isolated under the core layer.
  - Evidence: `core/assistant.py` handles validation, provider call orchestration, session updates, and logging calls.
  - Date: 2026-07-08
  - Notes:
- [x] LLM provider code is isolated under the provider layer.
  - Evidence: Provider protocol is in `providers/base.py`; Gemini adapter is in `providers/gemini_provider.py`.
  - Date: 2026-07-08
  - Notes:
- [x] Configuration files are isolated under the config area.
  - Evidence: Non-secret runtime config is `config/settings.toml`; editable prompt is `config/system_prompt.txt`.
  - Date: 2026-07-08
  - Notes:
- [x] Tests are isolated under the tests area.
  - Evidence: Automated tests are under `tests/`.
  - Date: 2026-07-08
  - Notes:
- [x] Runtime logs are isolated under the logs area.
  - Evidence: `config/settings.toml` sets `log_file = "logs/interactions.jsonl"`; `logs/.gitkeep` preserves the directory.
  - Date: 2026-07-08
  - Notes:
- [x] No module has mixed unrelated responsibilities.
  - Evidence: Source review shows separated config, safety, session, assistant orchestration, logging, CLI, and provider responsibilities.
  - Date: 2026-07-08
  - Notes:
- [x] The assistant core can be tested without live network calls.
  - Evidence: `tests/test_assistant.py` injects fake providers; `tests/test_gemini_provider.py` injects fake clients.
  - Date: 2026-07-08
  - Notes:

## 3. Configuration

- [x] Non-secret settings load from a local config file.
  - Evidence: `core/config.py::load_config` reads TOML from `config/settings.toml`; `tests/test_config.py` verifies required values.
  - Date: 2026-07-08
  - Notes:
- [x] The system prompt loads from a separate editable prompt file.
  - Evidence: `core/config.py::load_system_prompt` reads `config/system_prompt.txt`; prompt loading is tested.
  - Date: 2026-07-08
  - Notes:
- [x] API keys are loaded from environment variables.
  - Evidence: `core/config.py::load_api_key` reads the configured environment variable; `interfaces/cli.py` passes it to the provider.
  - Date: 2026-07-08
  - Notes:
- [x] No secrets are hardcoded in source files.
  - Evidence: Source review shows only placeholder/fake test values; real API keys are loaded from `GEMINI_API_KEY`.
  - Date: 2026-07-08
  - Notes:
- [x] `session_history_max_messages` is explicit and defaults to 10.
  - Evidence: `config/settings.toml` sets `session_history_max_messages = 10`; config tests assert the default and reject zero or odd values; Session tests reject invalid direct limits.
  - Date: 2026-07-12
  - Notes: Configurable history limits must be positive even integers so normal assistant-managed history retains complete turns.
- [x] `max_user_input_chars` is explicit and defaults to 8,000.
  - Evidence: `config/settings.toml` sets `max_user_input_chars = 8000`; config loading test asserts this value.
  - Date: 2026-07-08
  - Notes:
- [x] `provider_timeout_seconds` is explicit and defaults to 30.
  - Evidence: `config/settings.toml` sets `provider_timeout_seconds = 30`; provider test asserts it is sent as 30000 milliseconds.
  - Date: 2026-07-08
  - Notes:
- [x] `provider_max_retries` is explicit, defaults to 2, and is bounded from 0 through 2.
  - Evidence: `config/settings.toml` sets `provider_max_retries = 2`; config and provider tests reject values above the Phase 1 limit.
  - Date: 2026-07-11
  - Notes: The setting permits disabling or reducing retries without allowing an unbounded retry loop.
- [x] `provider_retry_delay_seconds` is explicit, defaults to 3, and is bounded from 0 through 10.
  - Evidence: `config/settings.toml` sets `provider_retry_delay_seconds = 3`; config and provider tests reject values above the Phase 1 limit.
  - Date: 2026-07-11
  - Notes: With at most two retries, the upper bound limits intentional exponential-backoff sleeping to 30 seconds.
- [x] Missing config produces a clear startup error.
  - Evidence: Non-live startup check returned `Startup error: Missing config file: missing-settings-for-verification.toml`; unit test covers missing config.
  - Date: 2026-07-08
  - Notes:
- [x] Invalid config produces a clear startup error.
  - Evidence: Config tests verify invalid values and invalid UTF-8 raise `ConfigurationError`; `test_run_reports_invalid_file_encoding_without_starting_provider` verifies config and prompt decoding failures return code 1 with a specific startup error before provider construction.
  - Date: 2026-09-15
  - Notes: `interfaces/cli.py::run` catches `AssistantError` and prints startup errors. UTF-16 files are rejected with instructions to use UTF-8.
- [x] Missing prompt file produces a clear startup error.
  - Evidence: `tests/test_cli.py::test_run_reports_missing_prompt_file_startup_error`.
  - Date: 2026-07-08
  - Notes:
- [x] Missing API key produces a clear startup error.
  - Evidence: Non-live startup check returned `Startup error: Missing required environment variable: GEMINI_API_KEY`; unit test covers missing API key.
  - Date: 2026-07-08
  - Notes:
- [x] Config defaults are explicit and documented.
  - Evidence: Defaults are listed in `config/settings.toml` and README Configuration section.
  - Date: 2026-07-08
  - Notes:
- [x] No silent fallback hides unsafe or invalid configuration.
  - Evidence: `core/config.py` requires non-empty strings, non-boolean integers, positive even session limits, valid integer ranges, supported thinking levels, bounded retry settings, and `provider_name = "gemini"`.
  - Date: 2026-07-12
  - Notes:

## 4. Core Assistant Behavior

- [x] Assistant starts from the documented command.
  - Evidence: README documents `python main.py`; `main.py` calls `interfaces.cli.run`; user reported live `python main.py` runs.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant accepts normal text input.
  - Evidence: `tests/test_assistant.py::test_assistant_request_flow_updates_session_and_logs_success`; user reported live prompts and replies.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant rejects or ignores empty input cleanly.
  - Evidence: `tests/test_safety.py::test_validate_user_input_rejects_empty_text`; `interfaces/cli.py` catches `InputValidationError` and continues.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant rejects or handles input over 8,000 characters cleanly.
  - Evidence: `tests/test_safety.py::test_validate_user_input_rejects_too_long_text`; default limit is configured at 8,000.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant sends valid input to the configured provider.
  - Evidence: `core/assistant.py` calls `provider.generate_response`; assistant request-flow test verifies provider call content and timeout.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant prints a clear text response.
  - Evidence: `interfaces/cli.py` prints `reply.text`; user reported live text responses.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant keeps bounded session history during the current run.
  - Evidence: `core/session.py` maintains in-memory messages with a configured max; session tests cover storage and truncation.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant retains no more than the last 10 conversation messages, excluding the system prompt.
  - Evidence: `Session(max_messages=10)` is wired from config; `tests/test_session.py::test_session_truncates_to_last_10_messages`.
  - Date: 2026-07-08
  - Notes:
- [x] Session history is passed consistently to the provider when expected.
  - Evidence: `tests/test_gemini_provider.py::test_generate_response_sends_text_history_and_config` verifies user/model role conversion and message order; `tests/test_assistant.py::test_assistant_logs_provider_failure_without_updating_session` verifies failed turns are excluded.
  - Date: 2026-07-12
  - Notes: Only complete user/assistant turns are sent as subsequent history.
- [x] Assistant handles multiple prompts in one run.
  - Evidence: `interfaces/cli.py::run_loop` continues after successful responses and handled validation/provider errors; user reported a 4-message live run.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant exits cleanly on `/exit`.
  - Evidence: `tests/test_cli.py::test_run_loop_exits_on_exit_command`.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant exits cleanly on `/quit`.
  - Evidence: `tests/test_cli.py::test_run_loop_exits_on_quit_command`.
  - Date: 2026-07-08
  - Notes:
- [x] Assistant exits cleanly on keyboard interrupt.
  - Evidence: CLI tests cover keyboard interrupt at the input prompt and during `assistant.handle_user_input`; the provider test verifies interruption during retry sleep propagates to the CLI boundary. The user-reported prompt-level manual test also passed.
  - Date: 2026-07-12
  - Notes: Request-stage interruption now exits with code 0 and prints `Goodbye.` without a traceback.
- [x] Assistant does not expose internal stack traces during normal user-facing failures.
  - Evidence: `interfaces/cli.py` catches startup, input validation, and provider errors and prints user-facing messages; tests cover startup and shutdown paths.
  - Date: 2026-07-08
  - Notes:

## 5. Provider Behavior

- [x] Exactly one LLM provider is configured for Phase 1.
  - Evidence: `config/settings.toml` sets `provider_name = "gemini"`; `core/config.py` rejects any other provider.
  - Date: 2026-07-08
  - Notes:
- [x] Provider interface is abstracted enough to fake in tests.
  - Evidence: `providers/base.py` defines `LLMProvider`; assistant tests use `FakeProvider` and `FailingProvider`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider implementation has no CLI behavior.
  - Evidence: `providers/gemini_provider.py` exposes provider request/error mapping only; CLI behavior is isolated in `interfaces/cli.py`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider success path is tested.
  - Evidence: `tests/test_gemini_provider.py::test_generate_response_sends_text_history_and_config`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider timeout is configured explicitly and defaults to 30 seconds.
  - Evidence: `config/settings.toml` sets `provider_timeout_seconds = 30`; provider test asserts `http_options.timeout == 30000`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider timeout path is tested or manually simulated.
  - Evidence: `tests/test_gemini_provider.py::test_generate_response_maps_socket_timeout` and status `408`/`504` mapping tests.
  - Date: 2026-07-08
  - Notes:
- [x] Provider authentication failure path is tested or manually simulated.
  - Evidence: `tests/test_gemini_provider.py::test_generate_response_maps_provider_error_statuses` covers `401` and `403`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider rate-limit path is tested or manually simulated.
  - Evidence: `tests/test_gemini_provider.py::test_generate_response_maps_provider_error_statuses` covers `429`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider unavailable path is tested or manually simulated.
  - Evidence: Provider tests cover empty responses, bounded `500`/`503` retries, final status capture, generic user-facing failure, and real `google.genai.errors.ServerError.code` retry behavior; the user previously observed a live `500 INTERNAL` provider failure.
  - Date: 2026-07-12
  - Notes: The default permits two retries with 3-second and 6-second delays; official SDK source and tests confirm HTTP status is exposed as `.code`.
- [x] Provider errors become clear user-facing messages.
  - Evidence: `providers/gemini_provider.py::_map_provider_exception` maps failures to provider-neutral `ProviderError` messages; tests include a real `google.genai.errors.ClientError.code`; CLI tests verify exhausted unavailable errors print `I've encountered an error. Please retry.` without a raw provider payload.
  - Date: 2026-07-12
  - Notes: Authentication, rate-limit, timeout, invalid-request, and unavailable categories retain distinct actionable messages.
- [x] Provider errors are logged without leaking secrets.
  - Evidence: `core/assistant.py` logs error type plus request diagnostics; provider and logger tests verify configured API keys are redacted from diagnostic messages.
  - Date: 2026-07-11
  - Notes: Diagnostic detail is sanitized and limited to 500 characters before logging, with logger redaction applied again.
- [x] No automated test requires a live API key.
  - Evidence: Provider tests inject fake clients and fake API key strings; full test suite passed without a real API key.
  - Date: 2026-07-08
  - Notes:

## 6. Logging

- [x] Each interaction logs a timestamp.
  - Evidence: `core/logging.py` writes `timestamp`; logging test parses the record.
  - Date: 2026-07-08
  - Notes:
- [x] Each interaction logs a session ID.
  - Evidence: `core/logging.py` writes `session_id`; logging test asserts `session-1`.
  - Date: 2026-07-08
  - Notes:
- [x] Each interaction logs the user input.
  - Evidence: `core/logging.py` writes redacted `user_input`; logging test asserts the value.
  - Date: 2026-07-08
  - Notes:
- [x] Each interaction logs the assistant response when available.
  - Evidence: `core/logging.py` writes redacted `assistant_response`; logging test asserts the value.
  - Date: 2026-07-08
  - Notes:
- [x] Each interaction logs the provider name.
  - Evidence: `core/logging.py` writes `provider_name`; logging test asserts `gemini`.
  - Date: 2026-07-08
  - Notes:
- [x] Each interaction logs success or failure state.
  - Evidence: `core/logging.py` writes `success`; assistant tests cover success and provider failure records.
  - Date: 2026-07-08
  - Notes:
- [x] Failures log an error type.
  - Evidence: `core/assistant.py` logs `error_type`; provider failure test asserts `ProviderUnavailableError`.
  - Date: 2026-07-08
  - Notes:
- [x] Logs are local only.
  - Evidence: `InteractionLogger` writes to a local `Path`; README documents local JSONL logs.
  - Date: 2026-07-08
  - Notes:
- [x] Logs use JSONL.
  - Evidence: `core/logging.py` appends one JSON object plus newline; logging test parses the line.
  - Date: 2026-07-08
  - Notes:
- [x] Logs contain one complete interaction per line.
  - Evidence: `core/logging.py` writes one record per `log_interaction` call; logging test verifies one line for one interaction.
  - Date: 2026-07-08
  - Notes:
- [x] Each generated JSONL line is parseable as JSON.
  - Evidence: Logging tests parse generated records with `json.loads`; local log inspection parsed 12 records.
  - Date: 2026-07-08
  - Notes:
- [x] Logs are written in a reviewable local format.
  - Evidence: Local log inspection parsed `logs/interactions.jsonl` as JSONL.
  - Date: 2026-07-08
  - Notes:
- [x] Log write failure is handled cleanly.
  - Evidence: `test_assistant_preserves_successful_reply_when_logging_fails` verifies the reply and history survive a write failure; `test_run_displays_successful_reply_and_log_warning_before_eof` verifies reply output, warning, EOF exit, and provider cleanup. Existing tests cover direct logger and provider-error write failures.
  - Date: 2026-09-15
  - Notes: This pass added the previously missing successful-reply coverage claimed by the earlier evidence. Surrogate logging is covered by `test_log_interaction_preserves_unicode_and_escapes_unpaired_surrogates`.
- [x] Logs do not include API keys.
  - Evidence: Logger redacts configured secrets and Google API-key-shaped text; tests cover both paths; local log inspection found zero API-key-shaped leaks.
  - Date: 2026-07-08
  - Notes:
- [x] Logs do not include raw environment dumps.
  - Evidence: Log record fields are fixed in `core/logging.py` and do not include environment variables.
  - Date: 2026-07-08
  - Notes:
- [x] Logs do not include unnecessary system information.
  - Evidence: Log record fields are limited to interaction data and bounded provider diagnostics: attempt/retry counts, final status, sanitized error detail, and elapsed milliseconds.
  - Date: 2026-07-11
  - Notes:
- [x] Logs are not sent to an external logging service.
  - Evidence: `InteractionLogger` only writes to the local filesystem path.
  - Date: 2026-07-08
  - Notes:
- [x] Logs may include conversation text in Phase 1, and this is documented clearly.
  - Evidence: README Logging section documents conversation-text logging and API-key redaction limits.
  - Date: 2026-07-08
  - Notes:
- [x] A generated log file has been manually inspected.
  - Evidence: Original inspection found 12 parseable records and zero Google API-key-shaped leaks. A metadata-only follow-up inspection parsed the latest 11-record live session and verified all provider diagnostic fields were present.
  - Date: 2026-07-12
  - Notes: Conversation text was not printed during either inspection.

## 7. Error Handling

- [x] Missing config file handled cleanly.
  - Evidence: Non-live startup check returned exit code 1 and a clear missing-config startup error; unit test covers missing config.
  - Date: 2026-07-08
  - Notes:
- [x] Invalid config value handled cleanly.
  - Evidence: Config tests cover invalid provider, model, timeout, thinking level, retry count and delay below and above their bounds, history limit, and input limit.
  - Date: 2026-07-11
  - Notes:
- [x] Missing API key handled cleanly.
  - Evidence: Non-live startup check returned exit code 1 and a clear missing-API-key startup error; unit test covers missing key.
  - Date: 2026-07-08
  - Notes:
- [x] Empty input handled cleanly.
  - Evidence: `validate_user_input` raises a user-facing `InputValidationError`; CLI catches it and continues.
  - Date: 2026-07-08
  - Notes:
- [x] Input over 8,000 characters handled cleanly.
  - Evidence: Input length test verifies over-limit input raises `InputValidationError`; CLI catches it and continues.
  - Date: 2026-07-08
  - Notes:
- [x] Provider timeout handled cleanly.
  - Evidence: Provider timeout tests map timeout cases to `ProviderTimeoutError`; CLI catches `ProviderError`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider authentication failure handled cleanly.
  - Evidence: Provider status mapping tests cover `401` and `403` as `ProviderAuthenticationError`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider rate limit handled cleanly.
  - Evidence: Provider status mapping test covers `429` as `ProviderRateLimitError`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider unavailable handled cleanly.
  - Evidence: Assistant, provider, and CLI tests verify bounded retries, provider-neutral output, diagnostic logging, and continued CLI control after failure; user previously observed a live `500` failure.
  - Date: 2026-07-11
  - Notes:
- [x] Keyboard interrupt handled cleanly.
  - Evidence: `tests/test_cli.py` covers interruption during input and request processing; `tests/test_gemini_provider.py` simulates interruption during transient-error retry delay.
  - Date: 2026-07-12
  - Notes: `KeyboardInterrupt` remains uncaught by the provider and is handled at the CLI loop boundary.
- [x] Log write failure handled cleanly.
  - Evidence: Logging failure tests cover `LogWriteError`, provider-error replies, and CLI output of attached log-write failures. Added assistant and CLI tests now explicitly verify successful replies remain available when logging fails.
  - Date: 2026-09-15
  - Notes:
- [x] User-facing error messages are specific enough to act on.
  - Evidence: Startup, config, validation, provider auth, rate-limit, timeout, and unavailable messages are specific in `core/errors.py`, `core/config.py`, `core/safety.py`, and `providers/gemini_provider.py`.
  - Date: 2026-07-08
  - Notes:
- [x] User-facing error messages do not expose secrets.
  - Evidence: Provider exception details and logger fields redact API-key-shaped text; missing-key message names the env var but not the secret value.
  - Date: 2026-07-08
  - Notes:

## 8. Automated Tests

- [x] Test suite runs from the documented command.
  - Evidence: `python -m unittest discover -s tests` ran successfully; 32 tests passed.
  - Date: 2026-07-08
  - Notes: This matches the README test command.
- [x] Assistant request flow is tested.
  - Evidence: `tests/test_assistant.py::test_assistant_request_flow_updates_session_and_logs_success`.
  - Date: 2026-07-08
  - Notes: Uses a fake provider; no live network call.
- [x] Session history behavior is tested.
  - Evidence: `tests/test_session.py` covers storage, truncation, invalid limits, invalid roles, and empty content; `tests/test_assistant.py::test_assistant_passes_current_bounded_history_to_provider` covers the assistant/provider boundary.
  - Date: 2026-07-12
  - Notes: The integration test overfills the session and verifies the provider receives the current bounded snapshot plus the new request.
- [x] Session history truncation at 10 conversation messages is tested.
  - Evidence: `tests/test_session.py::test_session_truncates_to_last_10_messages` verifies storage; `tests/test_assistant.py::test_assistant_passes_current_bounded_history_to_provider` verifies the truncated history crosses the assistant/provider boundary.
  - Date: 2026-07-12
  - Notes:
- [x] Input validation is tested.
  - Evidence: `tests/test_safety.py::test_validate_user_input_accepts_text` and `test_validate_user_input_rejects_empty_text`.
  - Date: 2026-07-08
  - Notes:
- [x] Input length validation is tested.
  - Evidence: `tests/test_safety.py::test_validate_user_input_rejects_too_long_text`.
  - Date: 2026-07-08
  - Notes:
- [x] Config loading is tested.
  - Evidence: `tests/test_config.py::test_load_config_reads_required_values`.
  - Date: 2026-07-08
  - Notes:
- [x] Missing config behavior is tested.
  - Evidence: `tests/test_config.py::test_load_config_rejects_missing_file`.
  - Date: 2026-07-08
  - Notes:
- [x] Invalid config behavior is tested.
  - Evidence: `tests/test_config.py::test_load_config_rejects_invalid_integer` and `test_load_config_rejects_invalid_values`, including boolean-as-integer and odd history-limit cases.
  - Date: 2026-07-12
  - Notes:
- [x] Missing API key behavior is tested.
  - Evidence: `tests/test_config.py::test_load_api_key_rejects_missing_environment_variable`.
  - Date: 2026-07-08
  - Notes:
- [x] Prompt loading is tested.
  - Evidence: `tests/test_config.py` covers valid text, missing files, empty and whitespace-only prompts, and invalid UTF-8 including UTF-16 input.
  - Date: 2026-09-15
  - Notes:
- [x] `/exit` command behavior is tested.
  - Evidence: `tests/test_cli.py::test_run_loop_exits_on_exit_command`.
  - Date: 2026-07-08
  - Notes:
- [x] `/quit` command behavior is tested.
  - Evidence: `tests/test_cli.py::test_run_loop_exits_on_quit_command`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider success is tested with a fake or mock.
  - Evidence: `tests/test_gemini_provider.py::test_generate_response_sends_text_history_and_config`.
  - Date: 2026-07-08
  - Notes:
- [x] Provider failure is tested with a fake or mock.
  - Evidence: `tests/test_assistant.py::test_assistant_logs_provider_failure_without_updating_session`; provider tests use fake clients with both local fake exceptions and real official SDK exception instances.
  - Date: 2026-07-12
  - Notes: No live network call or API key is required.
- [x] Provider timeout configuration is tested.
  - Evidence: `tests/test_gemini_provider.py::test_generate_response_sends_text_history_and_config` asserts `http_options.timeout == 30000`.
  - Date: 2026-07-08
  - Notes: 30 seconds is converted to milliseconds for the provider SDK.
- [x] Logging success is tested.
  - Evidence: `tests/test_logging.py::test_log_interaction_writes_jsonl_record`.
  - Date: 2026-07-08
  - Notes:
- [x] Logging failure is tested.
  - Evidence: Direct logger and provider-error failure tests are supplemented by `test_assistant_preserves_successful_reply_when_logging_fails` and `test_run_displays_successful_reply_and_log_warning_before_eof`.
  - Date: 2026-09-15
  - Notes:
- [x] JSONL log formatting is tested.
  - Evidence: `tests/test_logging.py::test_log_interaction_writes_jsonl_record` parses the written line with `json.loads`.
  - Date: 2026-07-08
  - Notes:
- [x] Graceful shutdown paths are tested where practical.
  - Evidence: `tests/test_cli.py` covers `/exit`, `/quit`, input-stage keyboard interrupt, request-stage keyboard interrupt, successful provider cleanup, cleanup failure after normal completion, cleanup failure during an active loop exception, and the concrete CLI-to-`GeminiProvider` client-close chain; provider tests cover retry-sleep interruption propagation.
  - Date: 2026-07-12
  - Notes: A normal cleanup failure prints a generic message and returns `1`; an active loop exception is preserved when cleanup also fails. `test_run_closes_gemini_provider_client_after_shutdown` verifies the SDK client fake is closed.
- [x] Tests do not depend on execution order.
  - Evidence: All 64 tests passed in normal discovery order and in a flattened `unittest.TestSuite` shuffled with `random.Random(20260915)`.
  - Date: 2026-09-15
  - Notes: One reproducible shuffled order was checked; this is not an exhaustive check of every ordering.
- [x] Tests do not depend on a real API key.
  - Evidence: Tests use fakes, mocks, and patched environment variables; full test run passed without requiring a real key.
  - Date: 2026-07-08
  - Notes:
- [x] Tests do not make live network calls by default.
  - Evidence: Provider tests inject fake clients; assistant tests inject fake providers; full test run passed without live provider access.
  - Date: 2026-07-08
  - Notes:
- [x] All tests pass.
  - Evidence: `python -m unittest discover -s tests` returned OK; 34 tests passed.
  - Date: 2026-07-09
  - Notes:

## 9. Static Validation

- [x] Formatting command has been run, if configured.
  - Evidence: `.\.venv\Scripts\python.exe -m ruff format --check .` passed after `ruff format core\config.py core\safety.py`.
  - Date: 2026-07-08
  - Notes: Ruff reported `20 files already formatted`.
- [x] Linting command has been run.
  - Evidence: `.\.venv\Scripts\python.exe -m ruff check .`.
  - Date: 2026-07-08
  - Notes:
- [x] Linting passes.
  - Evidence: Ruff returned `All checks passed!`.
  - Date: 2026-07-08
  - Notes:
- [x] Type checking has been run if configured.
  - Evidence: `pyproject.toml` was reviewed; no type checker is configured and `mypy` is not listed as a dependency.
  - Date: 2026-07-08
  - Notes: Not applicable for the current Phase 1 scaffold.
- [x] Type checking passes if configured.
  - Evidence: No type checker is configured in `pyproject.toml`.
  - Date: 2026-07-08
  - Notes: Not applicable for the current Phase 1 scaffold.
- [x] Dependency list has been reviewed.
  - Evidence: `pyproject.toml` reviewed.
  - Date: 2026-07-08
  - Notes: Runtime dependency is `google-genai`; development dependency is `ruff`.
- [x] No unapproved runtime dependency was added.
  - Evidence: `pyproject.toml` lists only `google-genai>=1.0,<2.0` as the runtime dependency.
  - Date: 2026-07-08
  - Notes: This matches the Phase 1 allowance for one official LLM client package.
- [x] No unapproved development dependency was added.
  - Evidence: `pyproject.toml` lists only `ruff>=0.8,<1` under `dev`.
  - Date: 2026-07-08
  - Notes: Ruff is an allowed development dependency.
- [x] Import structure has been reviewed for obvious circular dependencies.
  - Evidence: Source files in `core/`, `interfaces/`, and `providers/` were read; full test import run and Ruff checks passed.
  - Date: 2026-07-08
  - Notes:

## 10. Manual Verification

- [x] Fresh setup was performed from the README instructions.
  - Evidence: User confirmed fresh setup from the README instructions was performed successfully.
  - Date: 2026-07-08
  - Notes:
- [x] Virtual environment creation works as documented.
  - Evidence: User confirmed virtual environment creation works as documented; current commands are being run from `.venv`.
  - Date: 2026-07-08
  - Notes:
- [x] Dependency installation works as documented.
  - Evidence: User confirmed dependency installation works as documented; installed dependencies support live provider use and Ruff validation.
  - Date: 2026-07-08
  - Notes:
- [x] Valid config starts the assistant successfully.
  - Evidence: `python -c "... build_assistant() ..."` with a fake `GEMINI_API_KEY` returned `assistant=Assistant provider=gemini`.
  - Date: 2026-07-08
  - Notes: This was a non-live startup check and did not contact Gemini.
- [x] Missing config fails clearly.
  - Evidence: `python -c "... run(Path('missing-settings-for-verification.toml')) ..."` returned `exit_code=1` and `Startup error: Missing config file: missing-settings-for-verification.toml`.
  - Date: 2026-07-08
  - Notes:
- [x] Invalid config fails clearly.
  - Evidence: User manually tested an invalid config and confirmed it failed clearly.
  - Date: 2026-07-08
  - Notes:
- [x] Missing API key fails clearly.
  - Evidence: `python -c "... patch.dict('os.environ', {}, clear=True) ... run() ..."` returned `exit_code=1` and `Startup error: Missing required environment variable: GEMINI_API_KEY`.
  - Date: 2026-07-08
  - Notes:
- [x] Normal prompt and response works.
  - Evidence: User-reported live manual runs with `python main.py`; the latest inspected session logged 10 successful provider responses.
  - Date: 2026-07-12
  - Notes: Live provider behavior depends on Gemini availability and quota.
- [x] Empty input is handled cleanly.
  - Evidence: User confirmed manual empty-input behavior can be marked complete; automated validation also covers empty input rejection.
  - Date: 2026-07-08
  - Notes:
- [x] Input over 8,000 characters is handled cleanly.
  - Evidence: User manually tested over-8,000-character input and confirmed it was handled cleanly.
  - Date: 2026-07-08
  - Notes:
- [x] Multi-turn session behaves as expected.
  - Evidence: The latest user-run live session logged 11 interactions in one session, including successful continuation after transient provider failures.
  - Date: 2026-07-12
  - Notes: Metadata-only inspection found 10 successes and 1 handled provider failure.
- [x] Session history remains bounded to the last 10 conversation messages.
  - Evidence: User manually tested bounded session history and confirmed it remains limited to the last 10 conversation messages.
  - Date: 2026-07-08
  - Notes:
- [x] `/exit` exits cleanly.
  - Evidence: User confirmed `/exit` manual behavior can be marked complete; automated CLI test also covers `/exit`.
  - Date: 2026-07-08
  - Notes:
- [x] `/quit` exits cleanly.
  - Evidence: User confirmed `/quit` manual behavior can be marked complete; automated CLI test also covers `/quit`.
  - Date: 2026-07-08
  - Notes:
- [x] Logs are created.
  - Evidence: Local inspection command reported `logs/interactions.jsonl` exists with 12 lines.
  - Date: 2026-07-08
  - Notes: Conversation text was not printed during inspection.
- [x] Logs are JSONL.
  - Evidence: Local inspection parsed 12 lines from `logs/interactions.jsonl` as 12 JSON records.
  - Date: 2026-07-08
  - Notes:
- [x] Logs are local only.
  - Evidence: Code inspection shows `InteractionLogger` writes to `config.log_file` on the local filesystem; README documents local JSONL logging.
  - Date: 2026-07-08
  - Notes:
- [x] Logs are reviewable.
  - Evidence: Local inspection parsed `logs/interactions.jsonl` successfully as JSONL.
  - Date: 2026-07-08
  - Notes:
- [x] Logs do not contain secrets.
  - Evidence: Local inspection found `api_key_like_leaks=0`; automated tests cover configured-secret and Google API-key-shaped redaction.
  - Date: 2026-07-08
  - Notes:
- [x] Logs may contain conversation text, and this is documented clearly.
  - Evidence: README Logging section documents that Phase 1 logs may include conversation text and describes API-key redaction limits.
  - Date: 2026-07-08
  - Notes:
- [x] Keyboard interrupt exits cleanly.
  - Evidence: User-reported manual keyboard interrupt at the input prompt passed. Automated tests now also cover interruption during provider request processing and retry delay.
  - Date: 2026-07-12
  - Notes: The mid-retry path is deterministically simulated because a live transient-error retry window is not reliably reproducible on demand.
- [x] Provider failure produces a useful error.
  - Evidence: The latest live session recorded one final status `500` after 3 attempts and 2 retries as `ProviderUnavailableError`; automated CLI tests verify the user-facing message is `I've encountered an error. Please retry.`
  - Date: 2026-07-12
  - Notes: The CLI retained control and later interactions in the same session succeeded.
- [x] Provider timeout uses the configured timeout, defaulting to 30 seconds.
  - Evidence: Provider test asserts timeout config is sent as `30000` milliseconds; `config/settings.toml` sets `provider_timeout_seconds = 30`.
  - Date: 2026-07-08
  - Notes:
- [x] README commands match actual commands.
  - Evidence: README reviewed; documented `python -m unittest discover -s tests` and Ruff commands were run successfully.
  - Date: 2026-07-08
  - Notes:
- [x] README limitations match actual Phase 1 limits.
  - Evidence: README reviewed against `PHASE_1.md`; listed out-of-scope items match the Phase 1 contract.
  - Date: 2026-07-08
  - Notes:

## 11. Documentation

- [x] README explains what the assistant does.
  - Evidence: README `What It Does` section reviewed.
  - Date: 2026-07-08
  - Notes: It describes config loading, prompt loading, environment-secret loading, CLI input, bounded session history, local JSONL logs, and graceful exits.
- [x] README explains what the assistant does not do.
  - Evidence: README `What It Does Not Do` section reviewed against `PHASE_1.md`.
  - Date: 2026-07-08
  - Notes: Listed exclusions match the Phase 1 out-of-scope boundary.
- [x] README includes setup instructions.
  - Evidence: README `Setup` section documents virtual environment creation, activation, and editable install.
  - Date: 2026-07-08
  - Notes: User confirmed fresh setup, virtual environment creation, and dependency installation worked from the README instructions.
- [x] README includes configuration instructions.
  - Evidence: README `Configuration` section reviewed.
  - Date: 2026-07-11
  - Notes: It documents `config/settings.toml`, the API-key environment variable, defaults, model, thinking level, bounded retry settings, and backoff behavior.
- [x] README documents the default session history limit of 10 conversation messages.
  - Evidence: README `Configuration` section lists `session_history_max_messages = 10`.
  - Date: 2026-07-08
  - Notes:
- [x] README documents the default maximum input length of 8,000 characters.
  - Evidence: README `Configuration` section lists `max_user_input_chars = 8000`.
  - Date: 2026-07-08
  - Notes:
- [x] README documents the default provider timeout of 30 seconds.
  - Evidence: README `Configuration` section lists `provider_timeout_seconds = 30`.
  - Date: 2026-07-08
  - Notes:
- [x] README documents `/exit` and `/quit`.
  - Evidence: README `Configuration` and `What It Does` sections mention `/exit` and `/quit`.
  - Date: 2026-07-08
  - Notes:
- [x] README explains required environment variables.
  - Evidence: README `Configuration` section documents `GEMINI_API_KEY` and shows a placeholder PowerShell example.
  - Date: 2026-07-08
  - Notes: The example uses a placeholder, not a real key.
- [x] README includes run instructions.
  - Evidence: README `Run` section documents `python main.py`.
  - Date: 2026-07-08
  - Notes:
- [x] README includes test instructions.
  - Evidence: README `Test` section documents `python -m unittest discover -s tests` and optional Ruff linting.
  - Date: 2026-07-12
  - Notes: README and `pyproject.toml` record that Phase 1 deliberately uses standard-library `unittest`, with Ruff as its only external development tool.
- [x] README includes troubleshooting notes.
  - Evidence: README `Troubleshooting` section reviewed.
  - Date: 2026-07-12
  - Notes: It covers missing config, missing prompt, missing API key, invalid config, auth, rate limit, timeout, provider unavailability, and provider cleanup failure.
- [x] README documents that logs are local JSONL files.
  - Evidence: README `Logging` section says runtime logs are written locally as JSONL to `logs/interactions.jsonl` by default.
  - Date: 2026-07-08
  - Notes:
- [x] README documents that Phase 1 logs may include conversation text.
  - Evidence: README `Logging` section explicitly states that Phase 1 logs may include conversation text.
  - Date: 2026-07-08
  - Notes:
- [x] README documents that logs must never include secrets.
  - Evidence: README `Logging` section states logs must never include API keys, raw environment dumps, or unnecessary system information.
  - Date: 2026-07-08
  - Notes:
- [x] README references `PHASE_1.md`.
  - Evidence: README opening section and `Phase 1 Exit` section reference `PHASE_1.md`.
  - Date: 2026-07-08
  - Notes:
- [x] README references this exit criteria document.
  - Evidence: README opening section and `Phase 1 Exit` section reference `PHASE_1_EXIT_CRITERIA.md`.
  - Date: 2026-07-08
  - Notes:
- [x] `AGENTS.md` exists and enforces Phase 1 boundaries.
  - Evidence: `AGENTS.md` was re-read and requires Phase 1 scope control, architecture boundaries, dependency limits, and no Phase 2 work.
  - Date: 2026-07-08
  - Notes:
- [x] Documentation has been checked against current behavior.
  - Evidence: README reviewed against `PHASE_1.md`, `config/settings.toml`, `.gitignore`, `interfaces/cli.py`, `core/logging.py`, and `providers/gemini_provider.py`.
  - Date: 2026-07-08
  - Notes: Documented commands, defaults, logging behavior, and limitations match current implementation.

## 12. Security And Privacy

- [x] Secrets are never committed.
  - Evidence: Source/config/docs were reviewed for hardcoded secrets; `rg --count-matches "AIza[0-9A-Za-z_-]{20,}" -g "!logs/**" -g "!*.jsonl" .` returned no matches.
  - Date: 2026-07-08
  - Notes: No commit was made during Phase 1 checklist work; real API keys are loaded from environment variables.
- [x] Example config files contain placeholders only.
  - Evidence: `config/settings.toml` contains only the environment variable name `GEMINI_API_KEY`; README uses `"replace-with-your-real-key"` as the setup placeholder.
  - Date: 2026-07-08
  - Notes:
- [x] `.gitignore` excludes local secrets and runtime logs where appropriate.
  - Evidence: `.gitignore` excludes `.env`, `.env.*`, `*.key`, `*.pem`, local config overrides, and `logs/*` while preserving `logs/.gitkeep`.
  - Date: 2026-07-08
  - Notes:
- [x] Error messages do not print API keys.
  - Evidence: `providers/gemini_provider.py::_safe_exception_message` redacts the configured API key and Google API-key-shaped strings; missing-key errors name only the required environment variable.
  - Date: 2026-07-08
  - Notes:
- [x] Logs do not print API keys.
  - Evidence: `InteractionLogger` redacts configured secrets and Google API-key-shaped strings; automated logger tests cover redaction and local log inspection found zero API-key-shaped leaks.
  - Date: 2026-07-08
  - Notes:
- [x] Logs are local only.
  - Evidence: `InteractionLogger` writes to a local `Path`; `config/settings.toml` points to `logs/interactions.jsonl`.
  - Date: 2026-07-08
  - Notes:
- [x] Logs use JSONL.
  - Evidence: `core/logging.py` appends one JSON object plus newline per interaction; tests parse generated records with `json.loads`.
  - Date: 2026-07-08
  - Notes:
- [x] Phase 1 conversation-text logging is clearly documented.
  - Evidence: README `Logging` section states that Phase 1 logs may include conversation text.
  - Date: 2026-07-08
  - Notes:
- [x] Tests do not require real secrets.
  - Evidence: Tests use fake providers, fake clients, and patched environment variables; full test suite passed without a real API key.
  - Date: 2026-07-08
  - Notes:
- [x] No unnecessary personal data is collected.
  - Evidence: Log records are limited to interaction fields and bounded provider request diagnostics needed for local troubleshooting.
  - Date: 2026-07-11
  - Notes: Conversation text logging is a documented Phase 1 behavior.
- [x] No external service is contacted except the configured LLM provider during normal live use.
  - Evidence: Source review shows the only live external client path is `GeminiProvider` creating `google.genai.Client` for configured provider requests.
  - Date: 2026-07-08
  - Notes: Automated tests inject fakes and do not make live provider calls.
- [x] No external logging service is contacted during normal use.
  - Evidence: `InteractionLogger` writes only to the local filesystem and no external logging dependency or client exists.
  - Date: 2026-07-08
  - Notes:

## 13. Reliability Review

- [x] The assistant can run more than one prompt in a single session.
  - Evidence: User reported a live `python main.py` run with 4 messages sent and 4 replies received.
  - Date: 2026-07-08
  - Notes:
- [x] The assistant can recover from a provider error and continue when appropriate.
  - Evidence: `test_run_recovers_after_provider_failure_and_exits_cleanly` drives real startup, assistant, session, logging, and CLI code through success, provider failure, recovery, and exit. It verifies failed turns are excluded from the next request, all three interactions are logged, and provider cleanup runs. SDK mock-transport tests cover bounded transient retries and no retry on rate limits.
  - Date: 2026-09-15
  - Notes: Providers or HTTP transport are faked; no live request is required. Retry remains provider-local and bounded; it is not provider fallback.
- [x] The assistant can exit without corrupting logs.
  - Evidence: User confirmed `/exit` and `/quit` manual checks passed; local log inspection parsed all 12 lines as valid JSONL records.
  - Date: 2026-07-08
  - Notes:
- [x] The assistant behaves predictably with whitespace-only input.
  - Evidence: User confirmed empty input is handled cleanly; `validate_user_input` strips whitespace and raises `InputValidationError` for empty text.
  - Date: 2026-07-08
  - Notes:
- [x] The assistant behaves predictably with unusually long input within configured limits.
  - Evidence: User confirmed Section 13 reliability testing is complete; code inspection shows inputs at or below `max_user_input_chars` are accepted after stripping.
  - Date: 2026-07-08
  - Notes:
- [x] The assistant rejects or handles input over 8,000 characters predictably.
  - Evidence: User manually tested over-8,000-character input and confirmed it was handled cleanly; automated input length validation test covers this path.
  - Date: 2026-07-08
  - Notes:
- [x] The assistant has a clear session history limit of 10 conversation messages.
  - Evidence: `config/settings.toml` sets `session_history_max_messages = 10`; user manually tested bounded session history; automated session truncation test covers the limit.
  - Date: 2026-07-08
  - Notes:
- [x] The assistant has a clear user input limit of 8,000 characters.
  - Evidence: `config/settings.toml` sets `max_user_input_chars = 8000`; README documents the limit; validation tests cover over-limit input.
  - Date: 2026-07-08
  - Notes:
- [x] Failure behavior has been reviewed manually.
  - Evidence: User manually verified invalid config, over-limit input, keyboard interrupt, provider failure, exit commands, empty input, and bounded session history.
  - Date: 2026-07-08
  - Notes:

## 14. Final Review

- [x] `PHASE_1.md` and implementation agree.
  - Evidence: `PHASE_1.md` was re-read and checked against `main.py`, `config/`, `core/`, `interfaces/`, `providers/`, tests, README, and `pyproject.toml`.
  - Date: 2026-07-09
  - Notes: Implementation remains CLI-only, text-only, one Gemini provider, local config, env-secret loading, bounded in-memory session history, and local JSONL logging.
- [x] `PHASE_1_EXIT_CRITERIA.md` is fully checked or documented.
  - Evidence: Sections 1 through 14 are checked; Phase 1 Exit Decision is approved; no waived items are required.
  - Date: 2026-07-10
  - Notes:
- [x] `AGENTS.md` reflects the current Phase 1 rules.
  - Evidence: `AGENTS.md` was re-read and still requires Phase 1 scope limits, architecture boundaries, dependency limits, safety rules, verification, and no Phase 2 work.
  - Date: 2026-07-09
  - Notes:
- [x] README accurately explains the current project.
  - Evidence: README was checked against `PHASE_1.md`, `config/settings.toml`, `interfaces/cli.py`, `core/logging.py`, and `providers/gemini_provider.py`.
  - Date: 2026-07-09
  - Notes: README matches current setup, config defaults, run/test commands, logging behavior, troubleshooting, and Phase 1 limitations.
- [x] No obvious dead code remains.
  - Evidence: Production modules in `main.py`, `core/`, `interfaces/`, and `providers/` were reviewed; the unreachable post-retry raise was removed from `GeminiProvider._generate_with_retries`; Ruff check passed.
  - Date: 2026-07-12
  - Notes:
- [x] No temporary debug prints remain.
  - Evidence: `rg -n "TODO|FIXME|XXX|HACK|debug|breakpoint\(|pdb|print\(" . -g "!logs/**" -g "!*.jsonl" -g "!.venv/**" -g "!.git/**" -g "!.ruff_cache/**"` found only documentation uses of "debug" and intentional CLI `print` calls.
  - Date: 2026-07-09
  - Notes:
- [x] No test-only shortcuts are present in production code.
  - Evidence: Production code was reviewed; `rg -n "fake|mock|test_|unittest|fixture|patch\.dict" main.py core interfaces providers config -g "*.py"` returned no matches.
  - Date: 2026-07-09
  - Notes: Tests use fakes/mocks, but production code does not.
- [x] No local-only absolute paths are required for normal use.
  - Evidence: Config uses relative paths by default; `rg -n "D:\\|C:\\|/home/|/Users/" . -g "!logs/**" -g "!*.jsonl" -g "!.venv/**" -g "!.git/**" -g "!.ruff_cache/**"` returned no matches.
  - Date: 2026-07-09
  - Notes:
- [x] The full validation command set has been run.
  - Evidence: `python -m unittest discover -s tests`, `.\.venv\Scripts\python.exe -m ruff check .`, `.\.venv\Scripts\python.exe -m ruff format --check .`, and `git diff --check` all exited successfully.
  - Date: 2026-07-09
  - Notes: Type checking is not configured in `pyproject.toml`; `git diff --check` reported only the expected CRLF normalization warning for the checklist file.
- [x] Final manual smoke test has been run.
  - Evidence: Latest live `python main.py` conversation in `logs/interactions.jsonl` used session `c17247e5-3016-4fe1-adaa-a704f7b977cd`; 14 records, 14 successes, 0 failures, final response confirmed the test run as successful.
  - Date: 2026-07-10
  - Notes:

## Required Evidence Summary

Complete this section before Phase 1 exit.

```text
Automated tests:
Command: python -m unittest discover -s tests
Result: OK, 34 tests passed.
Date: 2026-07-10

Lint:
Command: .\.venv\Scripts\python.exe -m ruff check .
Result: All checks passed.
Date: 2026-07-10

Format:
Command: .\.venv\Scripts\python.exe -m ruff format --check .
Result: 20 files already formatted.
Date: 2026-07-10

Type check, if enabled:
Command: Not run; no type checker is configured in pyproject.toml.
Result: Not applicable.
Date: 2026-07-10

Whitespace check:
Command: git diff --check
Result: Exit code 0; only CRLF normalization warning for PHASE_1_EXIT_CRITERIA.md.
Date: 2026-07-10

Manual smoke test:
Command: python main.py
Result: User reported the latest conversation went well. Log inspection found latest session c17247e5-3016-4fe1-adaa-a704f7b977cd with 14 records, 14 successes, 0 failures, and a final assistant response confirming the test run as successful.
Date: 2026-07-10

Log inspection:
File inspected: logs/interactions.jsonl
Result: Exists, 35 JSONL records parsed. Latest session had 14 successes and 0 failures; total file contained 31 successes and 4 older ProviderUnavailableError failures from previous testing.
Date: 2026-07-10

Config failure test:
Result: Missing config returned exit_code=1 with a clear startup error. User manually tested invalid config and confirmed it failed clearly.
Date: 2026-07-08

Provider failure test:
Result: User observed a clear Gemini 500 error; automated provider tests cover timeout/auth/rate-limit/unavailable mappings.
Date: 2026-07-08
```

## Post-Exit Phase 1 Stabilization

Phase 1 was originally approved on 2026-07-10. On 2026-07-11, an in-scope stabilization pass added bounded transient provider retries, exponential backoff, local provider request diagnostics, secret-safe diagnostic logging, and provider-neutral runtime errors.

The stabilization pass also amended `PHASE_1.md` and `AGENTS.md` to record the implemented retry defaults and limits. It did not add any Phase 2 feature, provider fallback, background task, or additional external service. The original Phase 1 approval date remains unchanged.

On 2026-07-12, follow-up stabilization aligned the local Gemini client protocol with the official SDK's read-only `models` property and added a narrow type cast at the SDK boundary. The user confirmed that both VS Code/Pylance diagnostics cleared. The same pass expanded CLI keyboard-interrupt handling across the complete loop iteration, including provider request and retry-delay processing; made CLI shutdown deterministically close provider resources while handling cleanup failures without replacing active exceptions; tightened integer and session-limit validation; verified mapping against official SDK exception instances; and removed an unreachable provider fallback.

```text
Stabilization automated tests:
Command: python -m unittest discover -s tests
Result: OK, 38 tests passed.
Date: 2026-07-11

Stabilization lint:
Command: .\.venv\Scripts\python.exe -m ruff check .
Result: All checks passed.
Date: 2026-07-11

Stabilization format:
Command: .\.venv\Scripts\python.exe -m ruff format --check .
Result: 20 files already formatted.
Date: 2026-07-11

Stabilization type check:
Command: Not run; no type checker is configured in pyproject.toml.
Result: Not applicable.
Date: 2026-07-11

Stabilization whitespace check:
Command: git diff --check
Result: Exit code 0; Git reported expected CRLF normalization warnings for modified text files.
Date: 2026-07-11

Stabilization editor diagnostics:
Result: User confirmed the Gemini client protocol and SDK factory return warnings are cleared in VS Code/Pylance.
Date: 2026-07-12

Stabilization follow-up validation:
Commands: python -m unittest discover -s tests; Ruff check; Ruff format check; git diff --check
Result: 40 tests passed; lint and format checks passed; whitespace check exited 0 with expected CRLF warnings.
Date: 2026-07-12

Stabilization keyboard interrupt coverage:
Result: Automated tests verify clean CLI shutdown during input and request processing, plus KeyboardInterrupt propagation from Gemini retry sleep.
Date: 2026-07-12

Stabilization lifecycle and policy validation:
Commands: python -m unittest discover -s tests; Ruff check; Ruff format check; git diff --check
Result: 54 tests passed; lint and format checks passed; whitespace check exited 0 with expected CRLF warnings.
Coverage: Concrete CLI-to-Gemini client cleanup, cleanup-failure behavior, bounded complete-turn history, integer and Session guards, official SDK exception mapping, longest-first overlapping-secret redaction, and exclusion of failed turns from session history.
Date: 2026-07-12

Stabilization SDK exception-shape verification:
Source: Installed official `google-genai` package, `google/genai/errors.py`.
Result: `APIError` assigns HTTP status to `.code`; automated tests instantiate real `ClientError` and `ServerError` objects and verify mapping and retry behavior through that attribute.
Date: 2026-07-12

Stabilization live provider test:
Command: python main.py
Result: User ran a live Gemini session. Metadata-only inspection of session daeedeaf-d519-4334-aab2-6a8eb1a0dacf parsed 11 JSONL records: 10 successes and 1 handled failure. Eight interactions retried, seven recovered after retry, and one status 500 exhausted 3 attempts and 2 retries. Every record contained the provider diagnostic fields.
Date: 2026-07-11
```

### Encoding And Recovery Hardening (2026-09-15)

This in-scope pass addressed two reproduced encoding failures and reconciled test evidence with the current suite. Config and prompt files containing invalid UTF-8 now raise `ConfigurationError` with a file-specific UTF-8 instruction. JSONL writes escape unpaired surrogate characters while preserving readable valid Unicode and existing secret redaction.

Added tests cover invalid config/prompt encodings (including UTF-16), empty prompts, successful replies surviving filesystem log failures, CLI success/failure/recovery with failed-turn exclusion, EOF shutdown and cleanup, and real SDK request serialization and retry behavior through an in-memory HTTP transport. No runtime dependency, retry policy, phase scope, or original approval date changed.

```text
Automated regression tests:
Command: .\.venv\Scripts\python.exe -m unittest discover -s tests
Result: OK, 64 tests passed (10 added). Encoding regressions failed before the fixes and passed afterward.

Test-order check:
Method: Flatten unittest discovery, shuffle with random.Random(20260915), run with TextTestRunner.
Result: All 64 tests passed.

Lint:
Command: .\.venv\Scripts\python.exe -m ruff check .
Result: All checks passed.

Format:
Command: .\.venv\Scripts\python.exe -m ruff format --check .
Result: 20 files already formatted.

Whitespace:
Command: git diff --check
Result: Passed; only Git LF-to-CRLF normalization warnings.

Offline CLI smoke checks:
Method: Call run() with fake environment credentials and controlled stdin; use a temporary invalid-encoding config for the startup failure case.
Result: /exit and EOF returned 0 with Goodbye.; invalid config encoding returned 1 with a UTF-8 startup error. No provider request was made.

SDK transport checks:
Environment: Installed google-genai 1.75.0, using its existing httpx dependency and MockTransport.
Result: Serialized system prompt, history roles, thinking level, model path, and 30-second read timeout verified. HTTP 500 then 503 then success caused exactly 3 attempts with simulated 3/6-second backoff. HTTP 429 caused exactly 1 attempt and no retry.
Limits: No live Gemini request, fresh installation, SDK version matrix, or type checking performed. No type checker is configured.
Date: 2026-09-15
```

## Deferred Or Waived Items

Any incomplete item must be listed here before Phase 1 can exit.

```text
Item: None.
Reason: No required Phase 1 item was waived.
Risk: Not applicable.
Approved by: Kaelion
Date: 2026-07-10
Follow-up: Not applicable.
```

## Phase 1 Exit Decision

Phase 1 exit is approved only when the following is true:

- [x] Every required item is checked or explicitly documented as waived.
- [x] Waived items do not undermine the Phase 1 contract.
- [x] Evidence summary is complete.
- [x] No Phase 2 feature work has started.
- [x] Final reviewer agrees Phase 1 is stable enough to build on.

```text
Phase 1 exit approved: yes
Approved by: Kaelion
Date: 2026-07-10
Notes: Original approval after final manual smoke test, log inspection, full automated tests, Ruff lint, Ruff format check, and whitespace check passed. See `Post-Exit Phase 1 Stabilization` for subsequent in-scope maintenance records through 2026-09-15.
```
