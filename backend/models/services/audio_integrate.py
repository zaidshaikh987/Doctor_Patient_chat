import os
import sounddevice as sd
import numpy as np
import wave
import speech_recognition as sr

# Define file paths
AUDIO_FILE_PATH = os.path.join(os.path.expanduser("~"), "Documents", "patient_conversation.wav")
TEXT_OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "Documents", "transcription.txt")
LANGUAGE = "en-US"

def record_audio(duration=15, sample_rate=44100):
    """Records audio and saves it as a WAV file."""
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(AUDIO_FILE_PATH), exist_ok=True)

    print("Recording... Speak now!")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    print("Recording complete. Saving file...")

    with wave.open(AUDIO_FILE_PATH, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    print(f"Audio saved as {AUDIO_FILE_PATH}")

def transcribe_audio():
    """Transcribes the recorded audio and saves it as a text file."""
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(AUDIO_FILE_PATH) as source:
            audio_data = recognizer.record(source)
        
        text = recognizer.recognize_google(audio_data, language=LANGUAGE)
        
        if text.strip():  # Ensure transcription is not empty
            with open(TEXT_OUTPUT_PATH, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print("\nTranscription complete. Text saved at:", TEXT_OUTPUT_PATH)
            print("\nTranscribed Text:\n", text)
        else:
            print("No speech detected in the audio.")
    
    except sr.UnknownValueError:
        print("Speech recognition could not understand the audio.")
    except sr.RequestError as e:
        print(f"Error connecting to speech recognition service: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    """Runs the audio recording and transcription process."""
    record_audio(duration=15)
    transcribe_audio()

if __name__ == "__main__":
    main()
