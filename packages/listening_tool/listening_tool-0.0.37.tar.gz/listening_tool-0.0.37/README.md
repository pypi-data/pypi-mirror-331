<!-- start setup -->
## Setup
A simple toolset for using [Whisper](https://openai.com/index/whisper/) models to transcribe audio in real-time.

The `listening_tool` is a wrapper around the whisper library that provides a simple interface for transcribing audio in real-time.  The module is designed to be versatile, piping the data to local or remote endpoints for further processing.  All aspects of the transcription can be configured via a config file (see bottom).

## Other Agent Tools
- [Speaking Tool](https://github.com/Ladvien/speech_tool) - A simple text-to-speech server using Kokoro models.

### Prerequisites

#### MacOS
1. Install `brew install portaudio`

#### Linux

##### Ubuntu
```sh
sudo apt install portaudio19-dev -y
```

<!-- end setup -->

<!-- start quick_start -->
## Quick Start

Install the package and create a config file.
```
pip install listening_tool
```

Create a `config.yaml` file with the following content according to configuration options below.

Below is a basic example of how to use the listening tool to transcribe audio in real-time.
```python
from listening_tool import Config, RecordingDevice, ListeningTool, TranscriptionResult

def transcription_callback(text: str, result: TranscriptionResult) -> None:
    print("Here's what I heard: ")
    print(result)

config = Config.load("config.yaml")

recording_device = RecordingDevice(config.mic_config)
listening_tool = ListeningTool(
    config.listening_tool,
    recording_device,
)

listening_tool.listen(transcription_callback)
```

The `transcription_callback` function is called when a transcription is completed. 

<!-- end quick_start -->

## Documentation
- [Documentation](https://listening_tool.readthedocs.io/en/latest/)

## Attribution
The core of this code was heavily influenced and includes some code from:
- https://github.com/davabase/whisper_real_time/tree/master
- https://github.com/openai/whisper/discussions/608

Huge thanks to [davabase](https://github.com/davabase) for the initial code!  All I've done is wrap it up in a nice package.

<!-- start advanced_usage -->
### Send Text to Web API
```py
import requests
from listening_tool import Config, RecordingDevice, ListeningTool, TranscriptionResult

def transcription_callback(text: str, result: TranscriptionResult) -> None:
    # Send the transcription to a REST API
    requests.post(
        "http://localhost:5000/transcribe",
        json={"text": text, "result": result.to_dict()}
    )

config = Config.load("config.yaml")
recording_device = RecordingDevice(config.mic_config)
listening_tool = ListeningTool(
    config.listening_tool,
    recording_device,
)
listening_tool.listen(transcription_callback)
```

The `TranscriptionResult` object has a `.to_dict()` method that converts the object to a dictionary, which can be serialized to JSON.

```json
{
    "text": "This is only a test of words.",
    "segments": [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 1.8,
            "text": " This is only a test of words.",
            "tokens": [50363, 770, 318, 691, 257, 1332, 286, 2456, 13, 50463],
            "temperature": 0.0,
            "avg_logprob": -0.43947878750887787,
            "compression_ratio": 0.8285714285714286,
            "no_speech_prob": 0.0012085052439942956,
            "words": [
                {"word": " This", "start": 0.0, "end": 0.36, "probability": 0.750191330909729},
                {"word": " is", "start": 0.36, "end": 0.54, "probability": 0.997636079788208},
                {"word": " only", "start": 0.54, "end": 0.78, "probability": 0.998072624206543},
                {"word": " a", "start": 0.78, "end": 1.02, "probability": 0.9984667897224426},
                {"word": " test", "start": 1.02, "end": 1.28, "probability": 0.9980781078338623},
                {"word": " of", "start": 1.28, "end": 1.48, "probability": 0.99817955493927},
                {"word": " words.", "start": 1.48, "end": 1.8, "probability": 0.9987621307373047}
            ]
        }
    ],
    "language": "en",
    "processing_secs": 5.410359,
    "local_starttime": "2025-01-31T06:19:03.322642-06:00",
    "processing_rolling_avg_secs": 22.098183908976
}
```
<!-- end advanced_usage -->

<!-- start config -->
## Config
Config is a `yaml` file enabling control of all aspects of the audio recording, model config, and transcription formatting. Below is an example of a config file.

```yaml
mic_config:
  mic_name: "Jabra SPEAK 410 USB: Audio (hw:3,0)" # Linux only
  sample_rate: 16000
  energy_threshold: 3000 # 0-4000

listening_tool:
  record_timeout: 2 # 0-10
  phrase_timeout: 3 # 0-10
  in_memory: True
  transcribe_config:
    #  'tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 
    #'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 
    # 'large', 'large-v3-turbo', 'turbo'
    model: medium.en

    # Whether to display the text being decoded to the console.
    # If True, displays all the details, If False, displays
    # minimal details. If None, does not display anything
    verbose: True

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
    # NOTE: Setting this to true also adds word level data to the
    # output, which can be useful for downstream processing.  E.g.,
    # {
    #   'word': 'test',
    #   'start': np.float64(1.0),
    #   'end': np.float64(1.6),
    #   'probability': np.float64(0.8470910787582397)
    # }
    word_timestamps: True # False

    # If word_timestamps is True, merge these punctuation symbols
    # with the next word

    prepend_punctuations: '"''“¿([{-'

    # If word_timestamps is True, merge these punctuation symbols with the previous word
    append_punctuations: '"''.。,，!！?？:：”)]}、'

    # Optional text to provide as a prompt for the first window.
    # This can be used to provide, or "prompt-engineer" a context
    # for transcription, e.g. custom vocabularies or proper nouns
    # to make it more likely to predict those word correctly.
    initial_prompt: "" # ""

    # Comma-separated list start,end,start,end,... timestamps
    # (in seconds) of clips to process. The last end timestamp
    # defaults to the end of the file.
    clip_timestamps: "0" # "0"

    # When word_timestamps is True, skip silent periods **longer**
    # than this threshold (in seconds) when a possible
    # hallucination is detected
    hallucination_silence_threshold: None # float | None

    # Keyword arguments to construct DecodingOptions instances
    # TODO: How can DecodingOptions work?

logging_config:
  level: INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL
  filepath: "talking.log"
  log_entry_format: "%(asctime)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```
<!-- end config -->