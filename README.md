# Voice Assistant

This repository contains the completed Phase 1 text-first command-line assistant foundation.

Phase 1 is governed by `PHASE_1.md` and was approved in `PHASE_1_EXIT_CRITERIA.md` on 2026-07-10. No Phase 2 work has started.

## Phase 1 Status

Phase 1 is complete and signed off. The project has a CLI-only, text-only assistant loop, local config files, bounded in-memory session history, local JSONL interaction logging, one Gemini provider, and automated tests.

On 2026-07-11 and 2026-07-12, Phase 1 received in-scope stabilization updates covering bounded provider retries, local diagnostics, provider-neutral errors, SDK alignment, complete-turn session limits, request-stage interruption, deterministic provider cleanup, cleanup-failure handling, and expanded tests. These updates did not add Phase 2 scope or change the original 2026-07-10 approval date.

On 2026-09-15, a further Phase 1 hardening pass added clear file-encoding errors, safe logging of malformed Unicode, and expanded offline startup, recovery, logging, shutdown, and SDK transport tests.

Later-phase work must not start until the next phase scope is explicitly documented and approved.

## What It Does

- Loads local non-secret settings from `config/settings.toml`.
- Loads the editable system prompt from `config/system_prompt.txt`.
- Reads the Gemini API key from an environment variable.
- Accepts text input from the command line.
- Maintains bounded in-memory session history for the current process.
- Writes local JSONL interaction logs.
- Handles `/exit`, `/quit`, empty input, provider errors, and Ctrl+C while waiting for input or provider work.

Only complete user/assistant turns are added to session history. A provider failure is logged locally but is not replayed to the provider on the next request.

## What It Does Not Do

Phase 1 does not include voice input, voice output, wake words, GUI, web UI, Home Assistant, smart-home control, tool calling, background tasks, long-term memory, retrieval, embeddings, vector databases, autonomous agents, plugin systems, user accounts, or multi-provider routing.

## Requirements

- Python 3.11 or newer.
- Runtime dependency: `google-genai`, the official Gemini API SDK.
- Optional development dependency: `ruff` for linting. It is development-only and is used because the standard library does not provide a Python linter.

`google-genai` is used because Phase 1 needs one live Gemini provider. The Python standard library can make HTTP requests, but hand-rolling the Gemini API transport, request schema, and provider error handling would be more fragile than using the official client.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

If you only want to run the standard-library test suite, installing the optional development dependencies is not required.

## Configuration

Non-secret settings live in `config/settings.toml`.

Save both `config/settings.toml` and `config/system_prompt.txt` as UTF-8 text. Invalid encoding produces a startup error identifying the file.

Defaults in the scaffold:

- `session_history_max_messages = 10`
- `max_user_input_chars = 8000`
- `provider_timeout_seconds = 30`
- `provider_model = "gemma-4-31b-it"`
- `provider_thinking_level = "minimal"`
- `provider_max_retries = 2`
- `provider_retry_delay_seconds = 3`
- `provider_name = "gemini"`
- Exit commands: `/exit` and `/quit`

`session_history_max_messages` must be a positive even integer. This keeps assistant-managed history bounded in complete user/assistant turns instead of allowing trimming to leave an orphaned assistant message.

Gemma 4 supports `provider_thinking_level = "minimal"` or `"high"`. The default `minimal` setting requests thinking off/minimized for Phase 1.

`provider_max_retries = 2` allows two retries after transient Gemini server-side failures (`500` or `503`), for at most three total attempts. `provider_retry_delay_seconds = 3` is the base delay: the assistant waits 3 seconds before the first retry and 6 seconds before the second. It does not retry invalid requests, authentication failures, rate limits, or input validation errors.

`provider_max_retries` accepts integers from 0 through 2. `provider_retry_delay_seconds` accepts integers from 0 through 10. At the maximum allowed values, exponential backoff sleeps for 10 seconds and then 20 seconds, limiting intentional retry delay to 30 seconds; provider request timeouts are separate.

The API key must come from the environment. Do not put secrets in config files.

PowerShell example:

```powershell
$env:GEMINI_API_KEY = "replace-with-your-real-key"
```

## Run

```powershell
python main.py
```

The assistant starts only if the config, prompt file, and `GEMINI_API_KEY` are present.

## Test

Phase 1 deliberately uses Python's standard-library `unittest`. The contract permits `pytest`, `pytest-cov`, and `mypy`, but they are not required or installed; Ruff is the only external development tool.

```powershell
python -m unittest discover -s tests
```

Tests use fake providers or an in-memory HTTP transport with the real Gemini SDK; they do not contact Gemini or require a real API key. The transport tests use `httpx`, already installed as a dependency of `google-genai`. SDK transport behavior was verified with `google-genai` 1.75.0; the full allowed version range has not been tested.

Optional lint command after installing development dependencies:

```powershell
python -m ruff check .
```

## Logging

Runtime logs are written locally as JSONL to `logs/interactions.jsonl` by default. Each line is one interaction record with timestamp, session ID, user input, assistant response when available, provider name, success state, error type when applicable, provider attempt and retry counts, final error status code when available, sanitized provider error detail, and total provider elapsed time in milliseconds. Elapsed time includes retry delays.

Valid Unicode remains readable in the UTF-8 log. Unpaired surrogate characters are written as JSON Unicode escapes so malformed text cannot interrupt logging. Filesystem write failures produce a warning while preserving a successful assistant reply.

Phase 1 logs may include conversation text. Before writing JSONL, the logger redacts the loaded API key and Google API-key-shaped text from user, assistant, and provider-error fields. Provider error detail is also sanitized and limited to 500 characters by the adapter. These are safety guards, not general-purpose secret management; avoid pasting secrets into the assistant because they may still be sent to the configured provider during the live request.

Logs must never include API keys, raw environment dumps, or unnecessary system information. Runtime logs are ignored by git; `logs/.gitkeep` exists only to keep the directory.

## Troubleshooting

- Missing config: confirm `config/settings.toml` exists.
- Missing prompt: confirm `config/system_prompt.txt` exists.
- Invalid file encoding: save the identified config or prompt file as UTF-8 instead of UTF-16 or a legacy encoding.
- Missing API key: set the environment variable named by `api_key_env_var`.
- Invalid config: check that numeric values are integers rather than booleans, `session_history_max_messages` is positive and even, `provider_max_retries` is from 0 through 2, `provider_retry_delay_seconds` is from 0 through 10, and `provider_name` is `gemini`.
- Provider authentication failed: check that `GEMINI_API_KEY` is set and valid.
- Provider rate limit reached: wait and try again later, or use a model/key with more quota.
- Provider request timed out: check network connectivity or increase `provider_timeout_seconds`.
- Provider unavailable: check the configured model name, Gemini API availability, and installed dependencies. A `500 INTERNAL` or `503 UNAVAILABLE` response is usually transient; the assistant waits 3 seconds, retries, waits 6 seconds if needed, and retries once more by default. If all attempts fail, the CLI prints `I've encountered an error. Please retry.` and the local JSONL record retains the sanitized final status and diagnostic detail.
- Shutdown error: provider-client cleanup failed. After an otherwise normal exit the CLI returns code `1`; if another error is already active, that original error is preserved.

## Phase 1 Exit

Phase 1 is complete. The original exit decision and the post-exit stabilization record, evidence, manual verification, log inspection, and validation results are recorded in `PHASE_1_EXIT_CRITERIA.md`.
