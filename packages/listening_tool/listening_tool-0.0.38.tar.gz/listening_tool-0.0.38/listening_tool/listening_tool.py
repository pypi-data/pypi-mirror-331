from typing import Any, Callable, Dict, Optional
import numpy as np
import speech_recognition as sr
import whisper
import torch
from datetime import datetime, timedelta, timezone
from queue import Queue
from time import sleep
from rich import print
import logging

from .config import ListeningToolConfig
from .transcription import Segment, TranscriptionResult
from .recording_device import RecordingDevice


class ListeningTool:
    """
    A ListeningTool is a class that listens to audio input from a microphone and transcribes it into text.

    """

    def __init__(
        self,
        config: ListeningToolConfig,
        recording_device: RecordingDevice,
    ) -> None:

        self.config = config
        self.recording_device = recording_device
        self.recorder = sr.Recognizer()

        self.processing_rolling_avg_secs = 0.0

        print(f"Loading model: {self.config.transcribe_config.model}")
        self.audio_model = whisper.load_model(
            self.config.transcribe_config.model,
            self.config.transcribe_config.device,
            in_memory=self.config.in_memory,
        )

        # Thread safe Queue for passing data from the threaded recording callback.
        self.data_queue = Queue()

        self.transcription = [""]
        self.phrase_time = None

        # Create a background thread that will pass us raw audio bytes.
        # We could do this manually but SpeechRecognizer provides a nice helper.
        def record_callback(_, audio: sr.AudioData) -> None:
            """
            Threaded callback function to receive audio data when recordings finish.
            audio: An AudioData containing the recorded bytes.
            """
            # Grab the raw bytes and push it into the thread safe queue.
            data = audio.get_raw_data()
            self.data_queue.put(data)

        self.recording_device.recorder.listen_in_background(
            self.recording_device.mic.source,
            record_callback,
            phrase_time_limit=self.config.record_timeout,
        )

    def transcribe(self, audio_np: np.ndarray) -> TranscriptionResult:

        utc_dt = datetime.now(timezone.utc)  # UTC time
        local_datetime = utc_dt.astimezone()  # local time

        start_time = datetime.now()
        config = self.config.transcribe_config.to_dict()

        # TODO: Would be better if we broke out these config
        # into their own dataclass. Then, wouldn't need to delete them.
        del config["model"]
        del config["device"]
        del config["phrases_to_ignore"]

        result = self.audio_model.transcribe(
            audio_np,
            fp16=torch.cuda.is_available(),
            **config,
        )

        result["segments"] = self._deep_convert_np_float_to_float(result["segments"])

        segments = [Segment(**segment) for segment in result["segments"]]

        processing_secs = (datetime.now() - start_time).total_seconds()

        # TODO: Create rolling average window for processing time.
        self.processing_rolling_avg_secs = (
            (self.processing_rolling_avg_secs * 0.9 + processing_secs * 0.1)
            if self.processing_rolling_avg_secs
            else processing_secs
        )

        return TranscriptionResult(
            text=result["text"].strip(),
            segments=segments,
            language=result["language"],
            processing_secs=processing_secs,
            processing_rolling_avg_secs=self.processing_rolling_avg_secs,
            local_starttime=local_datetime,
        )

    def listen(self, callback: Optional[Callable[[str, Dict], None]] = None) -> None:
        while True:
            try:
                now = datetime.now(datetime.now().astimezone().tzinfo)

                # Pull raw recorded audio from the queue.
                if not self.data_queue.empty():

                    phrase_complete = False

                    # If enough time has passed between recordings, consider the phrase complete.
                    # Clear the current working audio buffer to start over with the new data.
                    if self._phrase_complete(self.phrase_time, now):
                        phrase_complete = True

                    # This is the last time we received new audio data from the queue.
                    self.phrase_time = now

                    # Combine audio data from queue
                    audio_data = b"".join(self.data_queue.queue)
                    self.data_queue.queue.clear()

                    # Convert in-ram buffer to something the model can use directly without needing a temp file.
                    # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                    # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                    audio_np = (
                        np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                        / 32768.0
                    )

                    # Read the transcription.
                    result = self.transcribe(audio_np)

                    # If we detected a pause between recordings, add a new item to our transcription.
                    # Otherwise edit the existing one.
                    if phrase_complete:
                        self.transcription.append(result.text)
                    else:
                        self.transcription[-1] = result.text

                    if (
                        callback
                        and result.text
                        not in self.config.transcribe_config.phrases_to_ignore
                    ):
                        if self.config.log:
                            logging.info(result.text)

                        callback(self.transcription, result)
                else:
                    # Infinite loops are bad for processors, must sleep.
                    sleep(0.25)
            except KeyboardInterrupt:
                break

    def _phrase_complete(self, phrase_time: datetime, now: datetime) -> bool:
        return phrase_time and now - phrase_time > timedelta(
            seconds=self.config.phrase_timeout
        )

    def _deep_convert_np_float_to_float(self, data: dict) -> dict:

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, np.float64):
                    data[key] = float(value)
                if isinstance(value, list):
                    data[key] = self._deep_convert_np_float_to_float(value)
                elif isinstance(value, dict):
                    data[key] = self._deep_convert_np_float_to_float(value)
        if isinstance(data, list):
            for i, value in enumerate(data):
                if isinstance(value, np.float64):
                    data[i] = float(value)
                if isinstance(value, list):
                    data[i] = self._deep_convert_np_float_to_float(value)
                elif isinstance(value, dict):
                    data[i] = self._deep_convert_np_float_to_float(value)

        return data
