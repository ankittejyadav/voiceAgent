"""
Voice Agent - A conversational voice assistant powered by Gemini.

Architecture:
  Microphone → STT (Gemini 2.5 Flash) → LLM (Gemini 2.5 Flash) → TTS (Gemini 3.1 Flash TTS) → Speaker

Each component is a separate class for easy swapping.
"""

from __future__ import annotations

import io
import os
import sys
import wave
import struct
import ctypes
import warnings

warnings.filterwarnings("ignore")

import pyaudio
from google import genai
from google.genai import types
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Suppress PortAudio stderr noise on macOS
# ---------------------------------------------------------------------------
def _suppress_stderr():
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        saved = os.dup(2)
        os.dup2(devnull, 2)
        os.close(devnull)
        return saved
    except Exception:
        return None


def _restore_stderr(saved):
    if saved is not None:
        os.dup2(saved, 2)
        os.close(saved)


# ---------------------------------------------------------------------------
# Audio Recorder
# ---------------------------------------------------------------------------
class AudioRecorder:
    """Records audio from the microphone with voice activity detection."""

    RATE = 16000
    CHANNELS = 1
    FORMAT = pyaudio.paInt16
    CHUNK = 1024

    def __init__(self):
        saved = _suppress_stderr()
        self.pa = pyaudio.PyAudio()
        _restore_stderr(saved)
        self.speech_threshold = 300

    def calibrate(self):
        """Measure ambient noise for 2 seconds and set speech threshold."""
        print("🔇 Calibrating mic... (stay quiet for 2 seconds)")
        stream = self.pa.open(
            format=self.FORMAT, channels=self.CHANNELS,
            rate=self.RATE, input=True, frames_per_buffer=self.CHUNK,
        )
        energies = []
        for _ in range(int(self.RATE / self.CHUNK * 2)):
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            energies.append(self._rms(data))
        stream.stop_stream()
        stream.close()

        ambient = sum(energies) / len(energies)
        self.speech_threshold = max(ambient * 1.5, 150)
        print(f"   Ambient: {int(ambient)}, threshold: {int(self.speech_threshold)}")

    @staticmethod
    def _rms(data: bytes) -> float:
        count = len(data) // 2
        shorts = struct.unpack(f"<{count}h", data)
        return (sum(s * s for s in shorts) / count) ** 0.5

    def record(self, max_seconds: int = 30) -> bytes | None:
        """Record until 2.0s of silence after speech, or max_seconds."""
        print("\n🎤 Listening... (speak now, pause when done)")

        stream = self.pa.open(
            format=self.FORMAT, channels=self.CHANNELS,
            rate=self.RATE, input=True, frames_per_buffer=self.CHUNK,
        )

        frames = []
        silence_chunks = 0
        max_silence = int(self.RATE / self.CHUNK * 2.0)
        max_start_delay = int(self.RATE / self.CHUNK * 5.0)
        max_chunks = int(self.RATE / self.CHUNK * max_seconds)
        started = False

        for i in range(max_chunks):
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            frames.append(data)
            energy = self._rms(data)

            if energy > self.speech_threshold:
                if not started:
                    sys.stdout.write("🗣️  [")
                    sys.stdout.flush()
                started = True
                silence_chunks = 0
                sys.stdout.write("*")
                sys.stdout.flush()
            else:
                if started:
                    silence_chunks += 1
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    if silence_chunks > max_silence:
                        sys.stdout.write("] Done.\n")
                        sys.stdout.flush()
                        break
                else:
                    if i > max_start_delay:
                        print("⏳ No speech detected (timeout).")
                        break

        stream.stop_stream()
        stream.close()

        if not started:
            return None

        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.pa.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))

        duration = len(frames) * self.CHUNK / self.RATE
        print(f"   Captured {duration:.1f}s of audio")
        return buf.getvalue()

    def cleanup(self):
        self.pa.terminate()


# ---------------------------------------------------------------------------
# Speech-to-Text (Gemini 3.1 Flash Lite)
# ---------------------------------------------------------------------------
class SpeechToText:
    """Transcribes audio using Gemini 3.1 Flash Lite."""

    MODEL = "gemini-3.1-flash-lite"

    def __init__(self, client: genai.Client):
        self.client = client
        self.recorder = AudioRecorder()

    def listen(self) -> str | None:
        wav_bytes = self.recorder.record(max_seconds=30)
        if wav_bytes is None:
            return None

        print("🔄 Transcribing...")
        try:
            response = self.client.models.generate_content(
                model=self.MODEL,
                contents=[
                    {
                        "parts": [
                            {"inline_data": {"mime_type": "audio/wav", "data": wav_bytes}},
                            {"text": (
                                "Transcribe this audio exactly as spoken. "
                                "Return ONLY the transcription text, nothing else. "
                                "If empty or unintelligible, return: [EMPTY]"
                            )},
                        ]
                    }
                ],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            # Extract text parts to avoid thought_signature warnings
            text = "".join(part.text for part in response.candidates[0].content.parts if part.text).strip()

            if not text or "[EMPTY]" in text:
                print("❓ Couldn't understand that.")
                return None

            print(f"📝 You said: {text}")
            return text

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None


# ---------------------------------------------------------------------------
# LLM Brain (Gemini 3.1 Flash Lite)
# ---------------------------------------------------------------------------
class Brain:
    """Conversational LLM with chat history."""

    SYSTEM_PROMPT = (
        "You are a friendly, helpful voice assistant. "
        "Keep responses concise (1-3 sentences) since they will be spoken aloud. "
        "Be conversational and natural. "
        "Make sure to reference or integrate what the user said in your response, acknowledging their input clearly."
    )

    def __init__(self, client: genai.Client, model: str = "gemini-3.1-flash-lite"):
        self.client = client
        self.chat = self.client.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=256,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )

    def think(self, user_input: str, image_bytes: bytes | None = None) -> str:
        parts = [user_input]
        if image_bytes:
            parts.append(
                types.Part.from_bytes(data=image_bytes, mime_type="image/png")
            )
        response = self.chat.send_message(parts)
        # Extract text parts to avoid thought_signature warnings
        text = "".join(part.text for part in response.candidates[0].content.parts if part.text).strip()
        return text


# ---------------------------------------------------------------------------
# Text-to-Speech (Gemini 3.1 Flash TTS)
# ---------------------------------------------------------------------------
class TextToSpeech:
    """High-quality TTS using gemini-3.1-flash-tts-preview.
    Outputs natural-sounding speech via Gemini's voice synthesis."""

    MODEL = "gemini-3.1-flash-tts-preview"
    VOICE = "Kore"  # Prebuilt voice. Options: Kore, Charon, Fenrir, Aoede, Puck, etc.
    SAMPLE_RATE = 24000  # Gemini TTS outputs 24kHz PCM

    def __init__(self, client: genai.Client, voice: str = "Kore"):
        self.client = client
        self.VOICE = voice

        # Reuse the PyAudio instance for playback
        saved = _suppress_stderr()
        self.pa = pyaudio.PyAudio()
        _restore_stderr(saved)

    def speak(self, text: str):
        """Generate speech with Gemini TTS and play it."""
        print(f"🔊 Agent: {text}")

        try:
            response = self.client.models.generate_content(
                model=self.MODEL,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=self.VOICE
                            )
                        )
                    ),
                ),
            )

            # Extract PCM audio data from response
            audio_data = None
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    audio_data = part.inline_data.data
                    break

            if audio_data is None:
                print("   ⚠️ No audio in response, falling back to text.")
                return

            # Play the PCM audio directly
            self._play_pcm(audio_data)

        except Exception as e:
            print(f"   ⚠️ TTS error: {e}")

    def _play_pcm(self, pcm_data: bytes):
        """Play raw PCM 16-bit 24kHz audio through speakers."""
        stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.SAMPLE_RATE,
            output=True,
        )
        # Play in chunks to avoid blocking issues
        chunk_size = 4096
        for i in range(0, len(pcm_data), chunk_size):
            stream.write(pcm_data[i:i + chunk_size])
        stream.stop_stream()
        stream.close()

    def cleanup(self):
        self.pa.terminate()


# ---------------------------------------------------------------------------
# Voice Agent (orchestrator)
# ---------------------------------------------------------------------------
class VoiceAgent:
    """Ties together STT, LLM, and TTS into a conversational loop."""

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            print("❌ Set your GEMINI_API_KEY in the .env file.")
            print("   Get a free key at: https://aistudio.google.com/apikey")
            sys.exit(1)

        client = genai.Client(api_key=api_key)

        self.stt = SpeechToText(client=client)
        self.brain = Brain(client=client)
        self.tts = TextToSpeech(client=client)

    def capture_screenshot(self) -> bytes | None:
        """Capture a screenshot using macOS built-in screencapture utility."""
        import subprocess
        import tempfile
        
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "gemini_screenshot.png")
        
        try:
            # -x: silent (no sound)
            subprocess.run(["screencapture", "-x", temp_path], check=True)
            if os.path.exists(temp_path):
                with open(temp_path, "rb") as f:
                    data = f.read()
                os.remove(temp_path)
                return data
        except Exception as e:
            print(f"⚠️ Failed to capture screenshot: {e}")
            print("   Make sure Terminal/VS Code has Screen Recording permissions in macOS System Settings.")
        return None

    def run(self):
        """Main conversation loop."""
        self.stt.recorder.calibrate()

        print("=" * 50)
        print("🤖 Voice Agent Ready")
        print("   Speak naturally. Say 'quit' or 'bye' to exit.")
        print("   Press Ctrl+C to force quit.")
        print("=" * 50)

        self.tts.speak("Hey there! What can I help you with?")

        while True:
            # 1. Listen
            user_text = self.stt.listen()
            if user_text is None:
                continue

            # 2. Exit check
            if user_text.lower().strip() in ("quit", "exit", "bye", "goodbye", "stop"):
                self.tts.speak("See you later!")
                break

            # Check if user is asking to see the screen
            image_bytes = None
            visual_keywords = ["look", "see", "screen", "screenshot", "window", "display", "visual"]
            if any(kw in user_text.lower() for kw in visual_keywords):
                print("📸 Capturing screenshot...")
                image_bytes = self.capture_screenshot()

            # 3. Think
            try:
                response = self.brain.think(user_text, image_bytes=image_bytes)
            except Exception as e:
                print(f"❌ LLM error: {e}")
                self.tts.speak("Sorry, I had a problem thinking about that.")
                continue

            # 4. Speak
            self.tts.speak(response)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # --echo mode: record → transcribe → speak back (no LLM)
    if "--echo" in sys.argv:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        stt = SpeechToText(client=client)
        tts = TextToSpeech(client=client)
        stt.recorder.calibrate()
        print("\n🔁 Echo mode — I'll repeat what you say. Ctrl+C to stop.")
        try:
            while True:
                text = stt.listen()
                if text:
                    tts.speak(f"You said: {text}")
        except KeyboardInterrupt:
            print("\n👋 Done.")
            sys.exit(0)

    try:
        agent = VoiceAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Bye.")
        sys.exit(0)
