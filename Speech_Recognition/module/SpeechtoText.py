# Import speech recognition module
import time
import speech_recognition as sr
import os

from utils import check_french

class SpeechtoText:
    def __init__(self) -> None:
        self.r = sr.Recognizer()
        self.audio_disabled = os.environ.get('AUDIO_DISABLED', False) == '1'
        if not self.audio_disabled:
            self.mic = sr.Microphone()


    def listen(self) -> sr.AudioData:
        """
        Listens to audio input from the microphone and returns an AudioData object.

        Args:
            None

        Returns:
            audio (AudioData): AudioData object
        """
        if self.audio_disabled:
            print("Audio input is disabled.")
            return None
        mic = self.mic 

        with mic as source:
            time.sleep(1)
            print("Où voulez-vous partir ? Donnez votre lieu de départ et votre lieu d'arrivée.")
                
            self.r.adjust_for_ambient_noise(source, duration=1)

            audio = self.r.listen(source)
        return audio



    def transcription(self, audio: sr.AudioData) -> str:
        """
        Transcribes the audio input to text using Google Speech Recognition API.

        Args:
            audio (AudioData): AudioData object

        Returns:
            text (str): Transcribed text
        """
        if self.audio_disabled:
            raise Exception("Audio input is disabled.")
        print("Veuillez patienter...")

        # Transcribe audio to text
        text = self.r.recognize_google(
                audio, 
                language='fr-FR',
                pfilter=1
            )
        
        is_french = check_french(text)
        if is_french:
            print("Transcription: ", str(text))

            return str(text)