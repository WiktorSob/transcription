Goal of this project is to create a script for transcribing youtube videos.

## Background

Background for this projects comes from (not mine) idea to compare two politics corpuses - polish and french. In order to utilize NLP tools and methods, the data has to be represented in a textual form. Afer profound research, it turns out that there are very few sources providing transcriptions of political speeches, especially for french and polish language.

As a solution, I've decided to use speech-to-text tools and transcribe selected youtube videos. 

## Implementation

### Download youtube video

First step of the pipeline is to download youtube videos. For that purpose `pytube` library is used.

Snippet below shows simple usage that is a part of the implementation. Firstly, `pytube` connects to given youtube video and lists all available streamings. Then, all results are filtered to contain only `mp4` files. Using options `only_video=False` asserts that given videos contain sound. Then firs result meeting the criteria is being downloaded. 

```python
from pytbue import YouTube

YouTube(link).streams.filter(file_extension='mp4',
							 only_video=False).first().download()
```

### Convert video to audio file

In order to convert `mp4` file to audio file (such as `mp3`) you can use `ffmpeg` and `pydub` library. When `ffmpeg` is installed and configured properly on your machine, you can convert files as described below:

```python
from pydub import AudioSegment

sound = AudioSegment.from_file(input_file, format="input format")
sound.export(output_file, format="desired format")
```

### Transcribe audio file

One of the most prominent examples of speech-to-text tools is `Google Speech-to-text` utility accessible via API endpoint which can be accessed using Python client.  Once it is set and enabled on GCP, you can send short audio file (less than 1 minute or 10MB) directly from local machine:

```python
from google.cloud import speech


def speech_to_text(
    config: speech.RecognitionConfig,
    audio: speech.RecognitionAudio,
) -> speech.RecognizeResponse:
    client = speech.SpeechClient()

    # Synchronous speech recognition request
    response = client.recognize(config=config, audio=audio)

    return response


def print_response(response: speech.RecognizeResponse):
    for result in response.results:
        print_result(result)


def print_result(result: speech.SpeechRecognitionResult):
    best_alternative = result.alternatives[0]
    print("-" * 80)
    print(f"language_code: {result.language_code}")
    print(f"transcript:    {best_alternative.transcript}")
    print(f"confidence:    {best_alternative.confidence:.0%}")
```
## Usage

For now, files can be transcribed in batches. You can select text file with links to youtube videos and specify transcription language code ([BCP 47 codes](https://www.techonthenet.com/js/language_tags.php)):

```python
python main.py --file='path/to/file.txt' --language='en-EN'
```
