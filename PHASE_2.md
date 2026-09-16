# Phase 2 Contract: Controlled Voice Input

## Status And Goal

On 2026-09-16, Kaelion agreed to Windows-first development with a portable core, a free cloud speech-to-text trial, English as the initial language, and separate phases for voice input and voice output.

Phase 1 exit is approved in [the archived exit criteria](phases/phase_1/PHASE_1_EXIT_CRITERIA.md). The [archived contract](phases/phase_1/PHASE_1.md) records the compatibility baseline. Completed phase files are immutable history; their historical paths and evidence are preserved. Current phase documents remain at the repository root. Phase 2 starts with transcription evaluation. Runtime implementation is still the completed Phase 1 text assistant; this document defines intended behavior, not delivered functionality.

Goal: deliberately record an English question, review or correct its transcript, submit it to the existing Gemini assistant, and receive a text response.

Phase 3 is reserved for voice output. Its detailed contract and implementation require a separate transition after Phase 2 exit.

## Scope

- Windows is the initial supported and manually tested platform. Keep core logic platform-independent; do not claim Linux/macOS support before testing.
- Explicit terminal-controlled recording start and stop, one recording/request at a time, with a bounded duration.
- One cloud transcription adapter selected through a small evaluation checkpoint.
- Display the transcript and require explicit submit, correction, or discard before calling Gemini.
- Retain typed input and all Phase 1 validation, bounded complete-turn history, logging, and shutdown behavior.
- Text mode must work without an STT key, audio dependencies, or available microphone.
- Test recording and transcription failures with fakes; verify actual microphone behavior manually on Windows.
- Document setup, data flow, free-tier limits, dependencies, and measured recognition quality.

## Exclusions

No voice output, wake words, always-listening behavior, streaming conversations, global keyboard hooks, GUI, web UI, Home Assistant, tool calling, computer control, autonomous agents, scheduling, persistent memory, retrieval, or provider fallback.

Gemini remains the single conversation provider. A separate transcription service is permitted only to convert audio into text; it is not a second conversation provider. Do not build routing or a plugin system.

A local STT comparison may be performed as an isolated evaluation if hardware and setup make it practical. Shipping or installing a second runtime engine is not required for Phase 2. If the cloud candidate fails evaluation, revisit the selection explicitly instead of adding automatic fallback.

## User Flow

1. Start the existing terminal assistant in text mode.
2. Enter `/voice`; show the selected microphone, audio format, duration limit, and cloud destination. Do not start recording yet.
3. Enter `start` to record. Enter `stop` or reach the duration limit to stop and release the microphone.
4. Enter `transcribe` to upload the completed recording, or `cancel` to abandon it without upload.
5. Display the transcript. Enter `submit`, `edit`, or `discard`. Review happens after the audio has reached the STT service, but before any transcript reaches Gemini.
6. Pass only the accepted text through the existing input validation and assistant flow. A transcript is content, not a source of executable commands.
7. Print the response and return to the text prompt.

Recording/STT failures and discarded transcripts must not update conversation history or invoke Gemini. An interrupted operation must not later submit a stale result. Ctrl+C retains the existing clean-exit behavior and releases resources.

## Exact CLI Contract

This is the required interface for implementation and tests, not a list of commands available in the current runtime. Commands are whole lines terminated by Enter. Strip surrounding whitespace and compare command words case-insensitively. There are no command arguments, extra aliases, global shortcuts, or spoken control commands. Replacement text uses the separate literal-text rule below.

| State / prompt | Accepted input | Required action and next state |
| --- | --- | --- |
| Text / `> ` | `/voice` | Validate voice prerequisites without recording; show settings and enter ready. Failure returns to text with a useful message. |
| Ready / `voice> ` | `start` | Open the selected microphone with the frozen format and enter recording. |
| Ready / `voice> ` | `cancel` | Return to text without recording or network activity. |
| Recording / `recording> ` | `stop` | Stop capture, close microphone, retain the bounded clip in memory and enter captured. No upload. |
| Recording / `recording> ` | `cancel` | Stop capture, close microphone, discard clip and return to text. No upload. |
| Captured / `audio> ` | `transcribe` | Upload once to STT; show processing status, then enter review with the returned transcript. Release raw audio after success or failure. |
| Captured / `audio> ` | `cancel` | Discard the clip and return to text without upload. |
| Review / `transcript> ` | `submit` | Validate the displayed text, call the existing assistant once, print its response and return to text. Validation failure stays in review; Gemini failure is handled by the existing error/logging policy and returns to text. |
| Review / `transcript> ` | `edit` | Enter replacement-text mode. |
| Review / `transcript> ` | `discard` or `cancel` | Discard transcript and return to text; no Gemini call. |
| Replacement / `replacement> ` | One line of text | Replace the whole transcript after existing non-empty/length validation; show the new text and return to review. Invalid text stays in replacement mode and preserves the previous transcript. Never auto-submit. |

Additional rules:

- At the text prompt, bare `start`, `stop`, `transcribe`, `submit`, `edit`, `discard` and `cancel` remain ordinary assistant text. Only `/voice` adds a new top-level command; existing `/exit` and `/quit` remain exits.
- At voice command prompts, blank or invalid input lists the valid commands and leaves the state unchanged. `/voice` cannot nest a recording flow. Invalid input never becomes an assistant request.
- In replacement mode, `cancel` returns to review without changing the transcript. `/exit` and `/quit` exit the application. All other non-empty input is replacement content, even if it says `submit` or `/voice`. To use a reserved replacement word as content, enter `text: <content>`; strip only this prefix and its one separating space before normal text validation. For example, `text: cancel` produces the literal transcript `cancel`.
- At all interactive prompts, `/exit` and `/quit` exit the application, close resources and discard pending audio/text. Ctrl+C and EOF also exit cleanly. Transcribed text is never parsed as a command, including text that says `/exit`.
- At 60 seconds, capture stops without waiting for Enter, closes the microphone, announces the limit and enters captured. No automatic upload or submission. Any partial recording-control line must be discarded at the transition; do not carry it into a later prompt. A late `stop` is invalid in captured and cannot trigger upload.
- STT and Gemini processing are synchronous from the user's perspective: no command prompt or queued command execution while waiting. Ctrl+C exits and cleans up; do not advertise typed `cancel` as available during a request. An upload already started cannot be recalled.
- Capture failure, empty audio, invalid WAV, or STT failure/empty result produces a clear message, releases pending resources and returns to text without invoking Gemini. Silence/noise may still yield incorrect STT text, so transcript acceptance remains mandatory.
- `stop` does not mean `cancel`: stopped audio remains available for `transcribe`; cancelled audio is discarded. After a discarded, failed, or submitted turn, a new recording requires `/voice` then `start` again.

Any helper worker needed for responsive capture/terminal controls is limited to the foreground operation and must shut down with it. This does not permit persistent background tasks.

## Frozen Evaluation And Runtime Audio Format

Use the same capture and encoding path for the 25-sample evaluation and the shipped voice interface:

- Container: RIFF/WAVE (`.wav`).
- Encoding: uncompressed signed 16-bit little-endian PCM (2 bytes/sample), not floating point or compressed audio.
- Sample rate: 16,000 Hz.
- Channels: one (mono).
- Maximum duration: 60 seconds, at most 960,000 samples / 1,920,000 PCM data bytes, plus WAV headers.
- Request 16 kHz mono int16 from the capture library and validate the resulting WAV header, sample count, and payload before upload. No application-side format fallback, resampling, channel mixing, normalization, or silence trimming in this evaluation.

Groq documents 16 kHz mono preprocessing and recommends WAV for lower latency: [audio preprocessing](https://console.groq.com/docs/speech-to-text#working-with-audio-files). The signed 16-bit PCM choice is this project's fixed encoding decision.

Before collecting scored samples, verify that the selected Windows device/library opens and reliably records this format, produces a valid WAV with the expected duration, and releases the device on stop/cancel/limit. Operating-system/driver conversion may occur; native hardware support is not assumed. If the capture interface cannot provide this format reliably, stop and resolve the device/library choice or explicitly amend the format contract before gathering results. Never relabel a different sample rate as 16 kHz.

Record microphone, capture library/version, device settings and format with the evaluation results. A later capture/format/preprocessing change requires repeating the scored evaluation; do not combine results from different pipelines.

## Initial Engineering Defaults

The CLI controls and audio format above are fixed before evaluation. Other initial settings are:

- English transcription (`en`); transcribe rather than translate.
- Maximum recording duration: fixed at 60 seconds in Phase 2; no configurable extension.
- STT request timeout: 30 seconds; no automatic STT retries initially. Quota/rate-limit failures return control with a useful message.
- Retain the existing 8,000-character accepted-input limit and 10-message session default.
- Microphone closed outside explicit recording; no capture during transcription or Gemini requests.
- No application-retained raw audio by default. Prefer bounded in-memory audio; document and clean up any unavoidable temporary files.

The STT timeout/retry policy is separate from the existing Gemini policy. Do not change Gemini settings to accommodate speech.

## Architecture And Dependencies

- `interfaces/`: terminal controls and microphone capture boundary. Isolate any operating-system-specific code here.
- `providers/`: narrow transcription interface and one cloud adapter, separate from the Gemini conversation adapter.
- `core/`: validated text assistant flow, session and errors. Keep audio transport details out of assistant orchestration.
- `config/`: non-secret speech settings in the existing local configuration system; secrets remain environment variables.
- `tests/`: fake audio devices, fake STT responses, and integration tests without live services.

Prefer the standard library. Phase 2 permits a narrowly justified audio-capture dependency and official STT client if needed, installed as optional voice dependencies so text mode stays independent. Before adding packages, record why the standard library/existing tools are insufficient, supported platforms, maintenance implications, and installation/test effects. No packages are added by this contract.

## First Evaluation Candidate: Groq

Start with Groq `whisper-large-v3` using the direct audio transcription endpoint. Groq recommends this model for error-sensitive multilingual transcription. English is the initial project test language. This is a candidate selection, not a claim of verified accuracy on Kaelion's microphone.

Groq hosts a Whisper model; cloud hosting removes local model installation and compute requirements but does not inherently outperform the same local model.

As checked on 2026-09-16, Groq lists a Free tier with recurring limits for this model: 20 requests/minute, 2,000 requests/day, 7,200 audio seconds/hour, and 28,800 audio seconds/day. These are shared organization limits and all apply; actual account limits must be verified. This is a free-tier trial, not authorization to upgrade to paid service. On quota exhaustion, stop STT requests and retain typed input.

Official references:

- [Speech-to-text models and API](https://console.groq.com/docs/speech-to-text)
- [Free-tier limits](https://console.groq.com/docs/rate-limits)
- [Billing and tier changes](https://console.groq.com/docs/billing-faqs)
- [Account/key setup](https://console.groq.com/docs/quickstart)
- [Data retention controls](https://console.groq.com/docs/your-data)

## Account Setup And Data Flow

1. Sign in or create an account at [Groq Console](https://console.groq.com/). Keep the organization on the Free tier; do not upgrade or enable paid usage for this trial.
2. Check the account Limits page for `whisper-large-v3` availability and allowances.
3. Review Data Controls. Groq documents Zero Data Retention as available to all customers; enable it for transcription for this trial. Confirm the setting before recording test audio.
4. Create an API key and configure `GROQ_API_KEY` locally as an environment variable. Do not paste it into chat, source files, screenshots, or test results. Gemini continues to use `GEMINI_API_KEY` separately.
5. Select the intended Windows microphone, check permissions and recording quality, then run a short non-sensitive English transcription test once the evaluation runner is implemented. No project voice command exists yet.

Audio goes to Groq for transcription. Accepted text goes to Gemini, and accepted conversations may be written to the existing local JSONL logs. Do not send conversation history or the assistant system prompt to STT. Do not persist rejected transcript text or raw provider response bodies in runtime logs. Secret redaction must cover both loaded keys.

Local audio deletion does not control cloud retention. Groq documents default non-retention of inference content with exceptions for reliability/abuse monitoring; its Zero Data Retention control disables that content retention. Usage metadata is still retained. Record the account setting used during evaluation rather than asserting that the application guarantees provider-side deletion.

## Evaluation And Integration Checkpoints

### 1. Establish Recognition Quality

Use 25 short English utterances on the actual microphone:

- 10 ordinary assistant questions.
- 5 names or technical terms.
- 5 numbers, dates, units, or negations where one wrong word changes meaning.
- 5 utterances with natural pauses or moderate background noise.

Complete the frozen-format capture preflight before gathering scored samples. Also test silence and noise without speech. Record the intended words before testing. Compare against the raw transcript, not a corrected version. Record model, language setting, device, capture library/version, WAV format, audio duration, request elapsed time, word errors, meaning-changing errors, and corrections needed. Measure STT elapsed time from the explicit transcription action to displayed transcript, excluding time spent reviewing or deciding to upload. Report median and slowest request time; do not confuse transcription time with total Gemini response time.

Proposed acceptance targets, to be agreed before scoring: at least 23/25 utterances usable without a meaning-changing correction, and median STT turnaround within 5 seconds for clips up to 15 seconds on the target connection. Record difficult cases individually, including incorrect numbers and negations. These targets are engineering proposals, not user-approved measurements or provider guarantees.

Retained evaluation recordings are an explicit exception to the runtime no-retention default: use only intentionally recorded test material, choose a local location outside version control, and agree retention before capture. No background recording or unrelated existing audio uploads. A local comparison, if performed, uses the same clips and reference text.

If quality is inadequate, review capture quality and candidate choice before integration. Do not mask poor transcription by asking Gemini to guess the intended input.

### 2. Integrate Controlled Voice Input

After the candidate is accepted, implement recording, transcript review/correction/discard, and the existing text-core handoff. Add the minimum dependencies and configuration required by the chosen design. Keep text-only startup independent of voice initialization.

### 3. Verify Reliability And Exit

Complete `PHASE_2_EXIT_CRITERIA.md`, including fresh Windows setup, real microphone use, fake-provider failures, privacy checks, and Phase 1 regression validation. A successful demo alone is insufficient.

## Current Evidence And Remaining Decisions

- Scope direction: agreed by Kaelion on 2026-09-16.
- Initial language: English, confirmed by Kaelion.
- Cloud candidate: Groq Whisper Large V3, chosen for evaluation based on official free-tier documentation.
- Account availability, quota, data controls, microphone, API call, latency and accuracy: not yet verified.
- CLI controls and audio encoding: fixed in this contract before implementation and evaluation.
- Audio library, actual device compatibility, installation commands and evaluation targets: settle before their dependent implementation/testing.
- No voice code, audio packages, account changes, recordings or cloud requests were made when creating this contract.

## Phase Progression

Phase 2 exit requires every item in `PHASE_2_EXIT_CRITERIA.md` to be verified or explicitly waived with reasons and user approval. Phase 3 voice output requires that exit, a documented Phase 3 scope, and explicit approval to start. Its roadmap placement does not authorize implementation now.
