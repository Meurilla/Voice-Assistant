# Phase 2 Contract: Controlled Voice Input

## Status And Goal

On 2026-09-16, Kaelion agreed to Windows-first development with a portable core, a free cloud speech-to-text trial, English as the initial language, and separate phases for voice input and voice output.

Phase 1 exit is approved in `PHASE_1_EXIT_CRITERIA.md`. Phase 2 starts with transcription evaluation. Runtime implementation is still the completed Phase 1 text assistant; this document defines intended behavior, not delivered functionality.

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
2. Deliberately enter the recording flow; show the selected microphone and that audio will be sent to the configured STT service.
3. Start recording only after explicit activation. Stop manually or at the duration limit, then release the microphone.
4. Allow cancellation before upload. Transcribe the completed recording using the selected cloud service.
5. Display the transcript. Allow submission, text replacement, or discard. Review happens after the audio has reached the STT service, but before any transcript reaches Gemini.
6. Pass only the accepted text through the existing input validation and assistant flow. A transcript is content, not a source of executable commands.
7. Print the response and return to the text prompt.

Recording/STT failures and discarded transcripts must not update conversation history or invoke Gemini. An interrupted operation must not later submit a stale result. Ctrl+C retains the existing clean-exit behavior and releases resources.

## Initial Engineering Defaults

These are implementation starting points; the evaluation should confirm they are usable before integration:

- English transcription (`en`); transcribe rather than translate.
- Maximum recording duration: 60 seconds. Any configurable value must be validated against documented finite bounds.
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

Also test silence and noise without speech. Record the intended words before testing. Compare against the raw transcript, not a corrected version. Record model, language setting, device, audio duration, request elapsed time, word errors, meaning-changing errors, and corrections needed. Report median and slowest request time; do not confuse transcription time with total Gemini response time.

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
- Exact recording controls, audio library, installation commands and evaluation targets: settle before their dependent implementation/testing.
- No voice code, audio packages, account changes, recordings or cloud requests were made when creating this contract.

## Phase Progression

Phase 2 exit requires every item in `PHASE_2_EXIT_CRITERIA.md` to be verified or explicitly waived with reasons and user approval. Phase 3 voice output requires that exit, a documented Phase 3 scope, and explicit approval to start. Its roadmap placement does not authorize implementation now.
