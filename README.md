# Voice Agent 🤖🎤

A simple, modular Python voice agent you can talk to. Built for learning and easy to extend.

## Architecture

```
Microphone → STT (Google Web Speech) → LLM (Gemini) → TTS (pyttsx3) → Speaker
```

Each component is a separate class in `agent.py`:

| Component | Class | Tech | Cost |
|-----------|-------|------|------|
| Speech-to-Text | `SpeechToText` | Google Web Speech API | Free |
| Brain (LLM) | `Brain` | Google Gemini 2.0 Flash | Free tier |
| Text-to-Speech | `TextToSpeech` | pyttsx3 (offline) | Free |

## Setup

### 1. Get a Gemini API key (free)
Go to [Google AI Studio](https://aistudio.google.com/apikey) and create a key.

### 2. Configure
```bash
cp .env.example .env
# Edit .env and paste your API key
```

### 3. Install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **macOS note**: `pyaudio` needs PortAudio. If install fails:
> ```bash
> brew install portaudio
> pip install pyaudio
> ```

### 4. Run
```bash
source .venv/bin/activate
python agent.py
```

Speak naturally. Say **"quit"** or **"bye"** to exit.

## Future expansion ideas
- Swap TTS with ElevenLabs for natural-sounding voices
- Add function calling (weather, calendar, smart home)
- Add wake word detection ("Hey Agent")
- Stream responses for lower latency
- Add a web UI with WebSockets
