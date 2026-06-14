# Architectural Decision Record: Switching to Gemini 3.1 Flash Lite & Adding Multimodal Screen Capability

* **Date**: 2026-06-07

## 1. Context & Problem Statement
The initial implementation of the Voice Agent was using `gemini-2.5-flash` for transcription (Speech-to-Text) and the LLM brain (Chat). This frequently resulted in `429 RESOURCE_EXHAUSTED` errors due to strict Free Tier project limits. Furthermore:
- The default VAD (Voice Activity Detection) configuration was too insensitive, causing the agent to stop listening prematurely and recognize only 2-3 words.
- The agent was unable to assist with screen visual context (e.g., questions about "what's on my screen") because it had no eyes/camera integration.
- The standard `response.text` SDK helper printed warnings about `thought_signature` non-text parts.

## 2. Options Considered

### Option 1: Retain Gemini 2.5 Flash
* **Description**: Continue using `gemini-2.5-flash` for the brain and speech-to-text, and try to manage the rate limits or instruct the user to upgrade their billing.
* **Pros**: No model migration or refactoring required.
* **Cons**: Fails to solve the 429 quota exhaustion; does not address visual context requests or VAD cutting off early.

### Option 2: Switch to Gemini 3.1 Flash Lite + Implement Native macOS Screen Capture + Optimize VAD
* **Description**:
  1. Migrate STT and Brain to `gemini-3.1-flash-lite` and TTS to `gemini-3.1-flash-tts-preview`.
  2. Implement visual keyword detection (e.g., "look", "see", "screen") to silently capture a macOS screenshot via the native `screencapture` CLI utility.
  3. Send the raw image bytes in a multimodal request payload along with the user's question to the brain.
  4. Lower the VAD sensitivity threshold multiplier to `1.5` (min `150`) and implement a 5-second silence timeout if no speech is detected.
  5. Parse Gemini response parts manually to avoid `thought_signature` warnings.
* **Pros**:
  - Eliminates the 429 rate limit errors under the free tier.
  - Successfully handles multimodal visual queries without third-party Python dependencies (like Pillow or PyAutoGUI).
  - Resolves microphone cutting off and provides real-time voice feedback (`*` and `.`).
* **Cons**: Requires code refactoring in `agent.py` to handle sub-process screenshotting and multimodal parts payload.

## 3. Chosen Decision & Rationale
Option 2 was chosen. Upgrading to `gemini-3.1-flash-lite` resolves the quota limitations and enables warning-free manual text parsing. Implementing screen capture via macOS's built-in `screencapture` command is highly lightweight and works natively without complicating the Python environment. The refined VAD settings and real-time visual output dramatically improve the voice conversation loop's responsiveness.

## 4. Rejected Alternatives
Option 1 was rejected because keeping the outdated version would leave the voice agent unusable due to frequent API rate limit blocks and poor speech sensitivity.
