# Phase 2 Exit Criteria

Source of truth for scope: `PHASE_2.md`.

Status: Not complete. Created 2026-09-16. No Phase 2 runtime behavior or live transcription result has been verified yet.

Mark an item complete only with evidence, date, and relevant limitations. Record skipped requirements individually under Waivers with explicit user approval.

## 1. Candidate And Setup

- [ ] Account is on the Free tier; model access, exact quotas and data-retention controls are recorded without secrets.
- [ ] English language setting and selected model are explicit.
- [ ] Selected Windows microphone/library passes the preflight for 16,000 Hz mono signed 16-bit PCM RIFF/WAV, including valid headers, sample count, duration and device release. Record device/library/version and any driver conversion settings.
- [ ] Evaluation and runtime share the same capture/encoding path; no silent format fallback or undocumented preprocessing occurs.
- [ ] Evaluation targets are agreed before scoring.
- [ ] The 25-utterance evaluation is recorded with raw-transcript accuracy, meaning-changing errors, correction count, and measured latency.
- [ ] Silence/noise cases are recorded; invented transcripts cannot reach Gemini without review.
- [ ] Candidate is accepted based on results; any local comparison or reason for omitting it is documented.

## 2. Functional Behavior

- [ ] CLI state/command table in `PHASE_2.md` is implemented and tested: `/voice`, `start`, `stop`, `transcribe`, `cancel`, `submit`, `edit`, `discard`, replacement text and `text: ` escape.
- [ ] Entering `/voice` does not record; `start` records, `stop` retains audio without upload, and only `transcribe` uploads it.
- [ ] Fixed 60-second limit stops capture without Enter, releases the microphone, discards partially typed control input and waits in captured state without uploading.
- [ ] Cancellation before upload sends no audio; microphone remains closed outside recording.
- [ ] Transcript can be reviewed, corrected, submitted, or discarded.
- [ ] Invalid/blank commands leave the voice state unchanged; replacement validation preserves the old transcript on failure; bare control words remain ordinary text at the top-level prompt.
- [ ] `/exit`, `/quit`, Ctrl+C and EOF follow the documented shutdown rules; no typed cancellation is advertised during STT/Gemini processing and no queued control input becomes an assistant request.
- [ ] Only explicitly accepted, validated text reaches Gemini; transcripts cannot execute CLI commands.
- [ ] Failed/cancelled STT or discarded transcripts do not call Gemini or alter conversation history.
- [ ] Accepted input uses existing limits, complete-turn history, JSONL logging, and text output.
- [ ] Text mode works without speech credentials, optional speech packages, or an available microphone.

## 3. Failures And Lifecycle

- [ ] Missing/busy/disconnected microphone and denied permissions produce useful messages.
- [ ] Missing/invalid STT key, network loss, timeout, rate limit, quota exhaustion and service failure are handled.
- [ ] Empty/malformed transcription responses and over-limit accepted text are handled.
- [ ] Unsupported capture format and malformed/empty/oversized WAV are rejected before upload with a clear error; no silent resampling or mislabeled sample rate.
- [ ] No automatic paid upgrade, provider fallback, or unbounded retry exists.
- [ ] Cancellation/shutdown closes audio and network resources and prevents stale submission.
- [ ] Cleanup failures are reported without hiding the original failure.
- [ ] Log write failure preserves successful replies and leaves the terminal usable.

## 4. Privacy And Architecture

- [ ] Both loaded API keys are excluded from errors and logs; no raw audio/provider payloads are logged.
- [ ] Raw audio is not retained by default; temporary-file cleanup and any unavoidable limitations are verified.
- [ ] Evaluation recordings, if retained, have an agreed location/retention policy and are outside version control.
- [ ] Documentation explains audio to Groq, accepted text to Gemini, and local conversation logging.
- [ ] Core remains independent of Windows/audio/STT details and can be tested using fakes.
- [ ] Dependencies are optional for text mode, justified, and documented with setup/maintenance implications.
- [ ] No Phase 3 features or other excluded capabilities were added.

## 5. Validation And Review

- [ ] Existing Phase 1 tests plus new voice unit/integration tests pass without keys, hardware, or live network calls.
- [ ] Ruff lint, formatting and whitespace checks pass; type checking runs if configured.
- [ ] Fresh Windows setup from README succeeds.
- [ ] Real microphone smoke test covers repeated voice turns, corrections, discard, typed input and shutdown.
- [ ] Manual failures are checked where hardware behavior cannot be represented adequately by fakes.
- [ ] README documents actual commands, configuration, limitations, troubleshooting and free-tier behavior.
- [ ] Other platforms are clearly marked unverified unless tested.
- [ ] Final reviewer accepts Phase 2 evidence and remaining limitations.

## Evidence Summary

Not run. Record commands, results, dates, account settings without secrets, microphone details, recognition results and limitations here as work proceeds.

## Waivers

None approved. Unchecked requirements remain outstanding.

## Exit Decision

Phase 2 exit approved: no.

Phase 3 implementation remains out of scope until Phase 2 exit and a separately documented, approved Phase 3 contract.
