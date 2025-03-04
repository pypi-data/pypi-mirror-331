import ast
from dataclasses import dataclass, asdict
from ast import literal_eval
from typing import List, Optional, Tuple, Union
from datetime import datetime

PHRASES_TO_IGNORE = [
    "",
    "urn.com urn.schemas-microsoft-com.h",
]


@dataclass
class Word:
    word: str
    start: float
    end: float
    probability: float

    @classmethod
    def load(cls, data):
        return cls(**data)

    def to_dict(self):
        return asdict(self)


@dataclass
class Segment:
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float
    words: List[Word]

    def __post_init__(self):
        self.words = [Word(**word) for word in self.words]

    @classmethod
    def load(cls, data):
        return cls(**data)

    def to_dict(self):
        return asdict(self)


@dataclass
class TranscriptionResult:
    text: str
    segments: list[Segment]
    language: str
    processing_secs: int
    local_starttime: datetime
    processing_rolling_avg_secs: float = 0

    def __post_init__(self):
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                self.__dict__[key] = value.isoformat()

    @classmethod
    def load(cls, data):
        return cls(**data)

    def to_dict(self):
        return asdict(self)


@dataclass
class TranscribeConfig:
    """
      transcribe_config:
    #  'tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large', 'large-v3-turbo', 'turbo'
    model: medium

    # Whether to display the text being decoded to the console. If True, displays all the details, If False, displays minimal details. If None, does not display anything
    verbose: False

    # Temperature for sampling. It can be a tuple of temperatures,
    # which will be successively used upon failures according to
    # either compression_ratio_threshold or logprob_threshold.
    temperature: "(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)" # "(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)"

    # If the gzip compression ratio is above this value,
    # treat as failed
    compression_ratio_threshold: 2.4 # 2.4

    # If the average log probability over sampled tokens is below this value, treat as failed
    logprob_threshold: -1.0 # -1.0

    # If the no_speech probability is higher than this value AND
    # the average log probability over sampled tokens is below
    # logprob_threshold, consider the segment as silent
    no_speech_threshold: 0.6 # 0.6

    # if True, the previous output of the model is provided as a
    # prompt for the next window; disabling may make the text
    # inconsistent across windows, but the model becomes less
    # prone to getting stuck in a failure loop, such as repetition
    # looping or timestamps going out of sync.
    condition_on_previous_text: True # True

    # Extract word-level timestamps using the cross-attention
    # pattern and dynamic time warping, and include the timestamps
    # for each word in each segment.
    word_timestamps: False # False

    # If word_timestamps is True, merge these punctuation symbols
    # with the next word
    prepend_punctuations: >
      "\"'“¿([{-"

    # If word_timestamps is True, merge these punctuation symbols with the previous word
    append_punctuations: >
      "\"'.。,，!！?？:：”)]}、"

    # Optional text to provide as a prompt for the first window.
    # This can be used to provide, or "prompt-engineer" a context
    # for transcription, e.g. custom vocabularies or proper nouns
    # to make it more likely to predict those word correctly.
    initial_prompt: "" # ""

    # Keyword arguments to construct DecodingOptions instances
    decode_options: dict

    # Comma-separated list start,end,start,end,... timestamps
    # (in seconds) of clips to process. The last end timestamp
    # defaults to the end of the file.
    clip_timestamps: Union[str, List[float]]

    # When word_timestamps is True, skip silent periods longer
    # than this threshold (in seconds) when a possible
    # hallucination is detected
    hallucination_silence_threshold: ""
    """

    model: str
    device: str
    verbose: bool | None
    temperature: Union[float, Tuple[float, ...]]
    compression_ratio_threshold: float
    logprob_threshold: float
    no_speech_threshold: float
    condition_on_previous_text: bool
    word_timestamps: bool
    prepend_punctuations: str
    append_punctuations: str
    initial_prompt: Optional[str]
    clip_timestamps: Union[str, List[float]]
    hallucination_silence_threshold: Optional[float]
    phrases_to_ignore: list[str] = None

    @classmethod
    def load(cls, data):
        return cls(**data)

    def __post_init__(self):

        if self.phrases_to_ignore is None:
            self.phrases_to_ignore = PHRASES_TO_IGNORE

        if isinstance(self.verbose, str):
            self.verbose = literal_eval(self.verbose)
        if isinstance(self.temperature, str):
            self.temperature = literal_eval(self.temperature)
        if isinstance(self.clip_timestamps, str):
            if "," in self.clip_timestamps:
                values = self.clip_timestamps.split(",")
                self.clip_timestamps = (float(v) for v in values)
        if isinstance(self.hallucination_silence_threshold, str):
            self.hallucination_silence_threshold = literal_eval(
                self.hallucination_silence_threshold
            )
        if isinstance(self.temperature, str):
            self.temperature = ast.literal_eval(self.temperature)

        if isinstance(self.logprob_threshold, str):
            self.logprob_threshold = float(self.logprob_threshold)

        if isinstance(self.no_speech_threshold, str):
            self.no_speech_threshold = float(self.no_speech_threshold)

    def to_dict(self):
        return asdict(self)
