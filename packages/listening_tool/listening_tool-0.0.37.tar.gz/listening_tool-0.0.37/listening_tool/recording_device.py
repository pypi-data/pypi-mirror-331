import speech_recognition as sr
from .mic import Mic, MicConfig


class RecordingDevice:

    def __init__(self, mic_config: MicConfig) -> None:
        self.mic_config = mic_config
        self.mic = Mic(
            config=self.mic_config,
        )

        # We use SpeechRecognizer to record our audio because it has a nice
        # feature where it can detect when speech ends.
        self.recorder = sr.Recognizer()

        # TODO: Could add more config here.
        self.recorder.energy_threshold = self.mic_config.energy_threshold

        # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
        self.recorder.dynamic_energy_threshold = False

        with self.mic.source:
            self.recorder.adjust_for_ambient_noise(self.mic.source)
