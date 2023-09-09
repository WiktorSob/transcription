import argparse
import os
import shutil

from google.api_core.exceptions import PreconditionFailed
from google.cloud import speech, storage
from loguru import logger

from utils import transcribe_gcs, upload_blob, youtube_to_audio

BASE_URI = os.environ["BASE_URI"]


def transcribe_link(link, audio_language):
    audio_file_path = youtube_to_audio(link, output_format="mp3")
    audio_file_name = audio_file_path.split("/")[-1]
    try:
        upload_blob(
            bucket_name="transcription-storage-witek",
            source_file_name=audio_file_path,
            destination_blob_name="input/" + audio_file_name,
        )
    except PreconditionFailed:
        logger.info("Audio file seems to be already uploaded to GSC")

    shutil.rmtree(".temp/")
    logger.info(f"Transcribing file: {audio_file_name}")
    file_uri = BASE_URI + audio_file_name
    transcription = transcribe_gcs(gcs_uri=file_uri, language_code=audio_language)
    txt_file_name = audio_file_name.replace("mp3", "txt")

    with open("texts/" + txt_file_name, "w") as f:
        f.write(transcription)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe youtube video directly from link"
    )
    parser.add_argument(
        "-f", "--file", type=str, help="Path to file with youtube links"
    )
    parser.add_argument(
        "-l", "--language", type=str, help="Language code for audio transcription"
    )
    args = parser.parse_args()

    links_file = args.file
    language_code = args.language

    with open(links_file, "r") as f:
        for line in f.readlines():
            link = line
            transcribe_link(link, language_code)
