# Voice Assistant

This repository contains the completed Phase 1 text-first command-line assistant foundation.

Phase 1 is governed by `PHASE_1.md` and was approved in `PHASE_1_EXIT_CRITERIA.md` on 2026-07-10. No Phase 2 work has started.

## Phase 1 Status

Phase 1 is complete and signed off. The project has a CLI-only, text-only assistant loop, local config files, bounded in-memory session history, local JSONL interaction logging, one Gemini provider, and automated tests.

Later-phase work must not start until the next phase scope is explicitly documented and approved.

## What It Does

- Loads local non-secret settings from `config/settings.toml`.
- Loads the editable system prompt from `config/system_prompt.txt`.
- Reads the Gemini API key from an environment variable.
- Accepts text input from the command line.
- Maintains bounded in-memory session history for the current process.
- Writes local JSONL interaction logs.
- Handles `/exit`, `/quit`, empty input, provider errors, and keyboard interruption paths.

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

Defaults in the scaffold:

- `session_history_max_messages = 10`
- `max_user_input_chars = 8000`
- `provider_timeout_seconds = 30`
- `provider_model = "gemma-4-31b-it"`
- `provider_thinking_level = "minimal"`
- `provider_max_retries = 1`
- `provider_name = "gemini"`
- Exit commands: `/exit` and `/quit`

Gemma 4 supports `provider_thinking_level = "minimal"` or `"high"`. The default `minimal` setting requests thinking off/minimized for Phase 1.

`provider_max_retries = 1` retries one transient Gemini server-side failure (`500` or `503`) before returning an error. It does not retry invalid requests, authentication failures, rate limits, or input validation errors.

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

```powershell
python -m unittest discover -s tests
```

Optional lint command after installing development dependencies:

```powershell
python -m ruff check .
```

## Logging

Runtime logs are written locally as JSONL to `logs/interactions.jsonl` by default. Each line is one interaction record with timestamp, session ID, user input, assistant response when available, provider name, success state, and error type when applicable.

Phase 1 logs may include conversation text. Before writing JSONL, the logger redacts the loaded API key and Google API-key-shaped text from user and assistant conversation fields. This is a safety guard, not general-purpose secret management; avoid pasting secrets into the assistant because they may still be sent to the configured provider during the live request.

Logs must never include API keys, raw environment dumps, or unnecessary system information. Runtime logs are ignored by git; `logs/.gitkeep` exists only to keep the directory.

## Troubleshooting

- Missing config: confirm `config/settings.toml` exists.
- Missing prompt: confirm `config/system_prompt.txt` exists.
- Missing API key: set the environment variable named by `api_key_env_var`.
- Invalid config: check that numeric values are positive integers and `provider_name` is `gemini`.
- Provider authentication failed: check that `GEMINI_API_KEY` is set and valid.
- Provider rate limit reached: wait and try again later, or use a model/key with more quota.
- Provider request timed out: check network connectivity or increase `provider_timeout_seconds`.
- Provider unavailable: check the configured model name, Gemini API availability, and installed dependencies. A `500 INTERNAL` or `503 UNAVAILABLE` response is usually a transient provider-side issue; the assistant retries once by default.

## Phase 1 Exit

Phase 1 is complete. The exit decision, evidence, manual verification, log inspection, and validation results are recorded in `PHASE_1_EXIT_CRITERIA.md`.
