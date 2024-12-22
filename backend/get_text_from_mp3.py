from pydub import AudioSegment
import speech_recognition as sr

# Postcondition: Returns the full transcribed text
def convertMP3ToText(relativeFilePath: str) -> str:
    # Step 1: Convert MP3 to WAV
    def convert_to_wav(mp3_path, wav_path):
        print(f"Converting MP3 {mp3_path} to WAV...")
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")

    # Step 2: Transcribe Audio Using SpeechRecognition
    def transcribe_audio(wav_path):
        print("Transcribing audio...")
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)  # Load the entire audio file
            try:
                # Use Google Web Speech API for transcription
                text = recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                return "Speech was not clear."
            except sr.RequestError as e:
                return f"Could not request results; {e}"

    # Derived paths
    wav_file = relativeFilePath.replace(".mp3", ".wav")

    # Convert MP3 to WAV
    convert_to_wav(relativeFilePath, wav_file)

    # Transcribe the WAV file
    return transcribe_audio(wav_file)
        
def get_text_from_mp3s(mp3_paths):
    print("Extracting text from MP3 files...")
    f = open("extracted_text.txt", "w")
    for mp3_path in mp3_paths:
        f.write(convertMP3ToText(mp3_path))
    return "extracted_text.txt"
