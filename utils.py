import os
from pytube import YouTube
from pydub import AudioSegment
from google.cloud import storage
from google.cloud import speech
from google.api_core.exceptions import PreconditionFailed


BASE_URI = 'gs://transcription-storage-witek/input/'

# converts youtube video to mp3 audio
def youtube_to_wav(link, output_format='mp3'):

    file_path = YouTube(link).streams.filter(file_extension='mp4', only_video=False).first().download()
    out_file_name = file_path.split('/')[-1].replace('mp4',
                                                    output_format)
    sound = AudioSegment.from_file(file_path,
                                   format="mp4")
    sound.export('audio/'+out_file_name,
                 format=output_format)
    
    
# uploads mp3 file to cloud storage
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, generation_match_precondition=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )
    
# async transcription for large files 
def transcribe_gcs(gcs_uri: str, language_code: str) -> str:
    """Asynchronously transcribes the audio file specified by the gcs_uri.

    Args:
        gcs_uri: The Google Cloud Storage path to an audio file.

    Returns:
        The generated transcript from the audio file provided.
    """
    from google.cloud import speech

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        sample_rate_hertz=44100,
        language_code=language_code,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result()

    transcript_builder = []
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        transcript_builder.append(result.alternatives[0].transcript)


    transcript = "".join(transcript_builder)
    print(transcript)

    return transcript


def main():
    file = 'links.txt'
    with open(file, 'r') as f:
        for line in f.readlines():
            link = line
            youtube_to_wav(link, output_format='mp3')
    
    for audio_file in os.listdir('audio'):
        
        try:
            upload_blob(bucket_name='transcription-storage-witek',
                        source_file_name='audio/'+audio_file,
                        destination_blob_name='input/'+audio_file)
        except PreconditionFailed:
            print('file seems to be already uploaded/')
        print(f'Transcription of file: {audio_file}...')
        
        transcription = transcribe_gcs(BASE_URI+audio_file, language_code='pl-PL')
        output_file_name = audio_file.replace('mp3', 'txt')
        
        with open('texts/'+output_file_name, 'w') as f:
            f.write(transcription)


if __name__ == '__main__':
    main()
        
        
    
    
    