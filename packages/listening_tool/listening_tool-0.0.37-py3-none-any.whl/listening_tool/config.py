from dataclasses import dataclass
from ast import literal_eval

import yaml
from .mic import MicConfig
from .logging_config import LoggingConfig
from .transcription import TranscribeConfig


@dataclass
class ListeningToolConfig:
    record_timeout: float
    phrase_timeout: float
    in_memory: bool
    log: bool
    transcribe_config: TranscribeConfig

    @classmethod
    def load(cls, data):
        return cls(**data)

    def __post_init__(self):
        self.transcribe_config = TranscribeConfig.load(self.transcribe_config)


@dataclass
class Config:
    listening_tool: ListeningToolConfig
    mic_config: MicConfig
    logging_config: LoggingConfig | None = None

    @classmethod
    def load(cls, path):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def __post_init__(self):
        self.listening_tool = ListeningToolConfig.load(self.listening_tool)
        self.mic_config = MicConfig.load(self.mic_config)
        if self.logging_config:
            self.logging_config = LoggingConfig(**self.logging_config)
