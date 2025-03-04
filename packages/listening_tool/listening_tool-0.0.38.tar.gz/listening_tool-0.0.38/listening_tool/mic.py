from sys import platform
from dataclasses import dataclass
import speech_recognition
from rich import print


@dataclass
class MicConfig:
    mic_name: str
    sample_rate: int
    energy_threshold: int

    @classmethod
    def load(cls, data):
        return cls(**data)


@dataclass
class Mic:
    config: MicConfig
    source: speech_recognition.Microphone | None = None

    def __post_init__(self):

        if "linux" in platform:
            self._handle_linux()
        else:
            self.source = speech_recognition.Microphone(
                sample_rate=self.config.sample_rate
            )

    def _handle_linux(self):
        print("Available microphone devices are: ")
        for index, name in enumerate(
            speech_recognition.Microphone.list_microphone_names()
        ):
            print(f'Microphone with name "{name}" found')

        for index, name in enumerate(
            speech_recognition.Microphone.list_microphone_names()
        ):
            if self.config.mic_name in name:
                self.source = speech_recognition.Microphone(
                    sample_rate=self.config.sample_rate,
                    device_index=index,
                )
                print(f"Found target mic: '{self.config.mic_name}'")
                break

        if self.source is None:
            print(f"Target microphone not found: '{self.config.mic_name}'")
            print("Available devices are: ")
            for index, name in enumerate(
                speech_recognition.Microphone.list_microphone_names()
            ):
                print(f'Available microphones "{name}" found')
            quit("Exiting...")
