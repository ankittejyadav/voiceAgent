# Architectural Decision Record: Voice Agent Simplification and Noise Handling

* **Date**: 2026-06-14

## 1. Context & Problem Statement
The voice agent implemented in `agent.py` was too complex, using multiple classes (`AudioRecorder`, `SpeechToText`, `Brain`, `TextToSpeech`, `VoiceAgent`) and significant boilerplate. Furthermore, the microphone capture relied on simple amplitude thresholding, which frequently mistriggered due to background noise (such as keyboards, breathing, or fans) or cut off the user's speech prematurely.

## 2. Options Considered

### Option 1: Maintain OOP Structure with Dynamic Amplitude Calibration
* **Description**: Retain the existing multi-class structure but add a startup calibration step to measure ambient noise and dynamically adjust the volume threshold.
* **Pros**: Maintains the original modular class design.
* **Cons**: Does not prevent false triggers from transient non-speech sounds like keyboard typing. The class structure remains verbose and hard to debug.

### Option 2: Consolidate to Procedural Code with Static Thresholds
* **Description**: Simplify the code by removing classes, but keep the simple amplitude threshold checks.
* **Pros**: Significantly simplifies the codebase and reduces lines of code.
* **Cons**: Still highly sensitive to ambient noise shifts, leading to unstable speech detection across different environments.

### Option 3: Consolidate to Procedural Code with Neural VAD, Turn-Taking State Machine, and Noise Suppression
* **Description**: Rewrite `agent.py` into streamlined procedural functions. Integrate the deep-learning `silero-vad` model (using ONNX Runtime) for real-time speech detection, control recording via a 3-state turn-taking state machine, and apply `noisereduce` spectral gating to clean up final recording buffers.
* **Pros**: Highly robust to background noises, handles turn-taking pauses gracefully, cleans up microphone audio before transcription, and reduces codebase complexity.
* **Cons**: Introduces external dependencies (`onnxruntime`, `torch`, `noisereduce`, `scipy`, `numpy`) which increases the virtual environment footprint.

## 3. Chosen Decision & Rationale
Option 3 was chosen. 
Consolidating the codebase to procedural functions reduced lines of code from 429 to 134, making the codebase easier to understand and maintain. Integrating `silero-vad` allows the system to distinguish human speech from background sounds with high precision, while `noisereduce` removes static hums from the final audio. The turn-taking state machine ensures the agent only cuts off recording after a continuous 1.4-second silence period, reducing premature cutoffs.

## 4. Rejected Alternatives
* **Option 1** was rejected because volume-based thresholds are inherently unreliable in noisy environments, regardless of startup calibration.
* **Option 2** was rejected because static thresholds fail when user distances or room acoustics change.
