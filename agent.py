import io
import os
import sys
import wave
import struct
import pyaudio
import numpy as np
import torch
import noisereduce as nr
from silero_vad import load_silero_vad
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Optimize PyTorch CPU execution
torch.set_num_threads(1)

# Audio Configuration
RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 512  # 32ms chunk size for 16kHz audio (required for Silero VAD)

def record_audio(pa: pyaudio.PyAudio, model) -> bytes | None:
    """Records audio from microphone using a turn-taking VAD state machine and filters it."""
    stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("\n🎤 Listening... (speak now)")
    
    frames = []
    
    # State Machine Variables
    state = "WAITING_FOR_SPEECH"
    consecutive_speech_chunks = 0
    consecutive_silence_chunks = 0
    
    # Timing variables (CHUNK is 32ms)
    max_wait_chunks = int(5.0 / 0.032)       # 5 seconds timeout to start speaking
    max_silence_chunks = int(1.4 / 0.032)    # 1.4 seconds of silence to finalize turn
    max_record_chunks = int(20.0 / 0.032)    # 20 seconds maximum recording time
    
    model.reset_states()
    
    for i in range(max_record_chunks):
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
        except Exception as e:
            print(f"⚠️ Audio read error: {e}")
            break
            
        frames.append(data)
        
        # Convert audio chunk to torch float32 tensor
        audio_np = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        audio_tensor = torch.from_numpy(audio_np)
        
        # Run VAD model
        speech_prob = model(audio_tensor, RATE).item()
        
        if state == "WAITING_FOR_SPEECH":
            if speech_prob > 0.45:
                consecutive_speech_chunks += 1
                if consecutive_speech_chunks >= 3:  # ~100ms of continuous speech
                    state = "SPEAKING"
                    print("🗣️ Speech detected...")
            else:
                consecutive_speech_chunks = 0
                
            if i > max_wait_chunks:
                print("⏳ Timeout: No speech detected.")
                break
                
        elif state == "SPEAKING":
            if speech_prob < 0.25:
                consecutive_silence_chunks += 1
                if consecutive_silence_chunks >= max_silence_chunks:
                    print("⏹️ Turn completed.")
                    break
            else:
                consecutive_silence_chunks = 0
                
    stream.stop_stream()
    stream.close()
    
    if state == "WAITING_FOR_SPEECH":
        return None
        
    # Concatenate frames and perform Neural Noise Suppression
    print("🧹 Cleaning background noise...")
    raw_pcm = b''.join(frames)
    audio_np = np.frombuffer(raw_pcm, dtype=np.int16).astype(np.float32)
    
    # We use noisereduce to suppress static background noise
    cleaned_np = nr.reduce_noise(y=audio_np, sr=RATE, prop_decrease=0.8)
    cleaned_pcm = np.clip(cleaned_np, -32768.0, 32767.0).astype(np.int16).tobytes()
    
    # Format to WAV bytes
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pa.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(cleaned_pcm)
    return buf.getvalue()

def play_audio(pa: pyaudio.PyAudio, pcm_data: bytes):
    """Plays raw PCM 16-bit 24kHz audio."""
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
    chunk_size = 4096
    for i in range(0, len(pcm_data), chunk_size):
        stream.write(pcm_data[i:i + chunk_size])
    stream.stop_stream()
    stream.close()

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Set GEMINI_API_KEY in your .env file.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    pa = pyaudio.PyAudio()
    
    print("🧠 Loading voice activity detector...")
    model = load_silero_vad(onnx=True)
    
    # Create chat session for conversation history
    chat = client.chats.create(
        model="gemini-3.1-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction="You are a brief conversational voice assistant. Keep answers to 1-2 sentences.",
            temperature=0.7,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
    )
    
    print("🤖 Voice Agent Ready. Say 'quit' to exit.")
    
    try:
        while True:
            wav_bytes = record_audio(pa, model)
            if not wav_bytes:
                continue
                
            # 1. Transcribe audio
            print("🔄 Transcribing...")
            stt_resp = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=[
                    types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"),
                    "Transcribe this audio exactly. Return only the transcription text, nothing else."
                ],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                )
            )
            user_text = "".join(part.text for part in stt_resp.candidates[0].content.parts if part.text).strip()
            if not user_text or "[EMPTY]" in user_text:
                continue
            print(f"📝 You said: {user_text}")
            
            if user_text.lower().strip() in ("quit", "exit", "bye"):
                break
                
            # 2. Get LLM response
            response = chat.send_message(user_text)
            reply_text = "".join(part.text for part in response.candidates[0].content.parts if part.text).strip()
            print(f"🔊 Agent: {reply_text}")
            
            # 3. Generate Speech and play it
            tts_resp = client.models.generate_content(
                model="gemini-3.1-flash-tts-preview",
                contents=reply_text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                        )
                    ),
                ),
            )
            
            # Extract raw audio bytes and play
            audio_data = next((part.inline_data.data for part in tts_resp.candidates[0].content.parts if part.inline_data), None)
            if audio_data:
                play_audio(pa, audio_data)
                
    except KeyboardInterrupt:
        pass
    finally:
        pa.terminate()
        print("\n👋 Done.")

if __name__ == "__main__":
    main()
