from concurrent.futures import ProcessPoolExecutor

from google.cloud import storage
from google.cloud import speech
from google.api_core.exceptions import PreconditionFailed

from utils import youtube_to_audio, upload_blob, transcribe_gcs

BASE_URI = 'gs://transcription-storage-witek/input/'

def transcribe_link(link, audio_language):
    audio_file_path = youtube_to_audio(link, output_format='mp3')
    audio_file_name = audio_file_path.split('/')[-1]
    try:
        upload_blob(bucket_name='transcription-storage-witek',
                    source_file_name=audio_file_path,
                    destination_blob_name='input/'+audio_file_name)
    except PreconditionFailed:
        print('file seems to be already uploaded')
    
    print(f'Transcription of file: {audio_file_name}...')
    file_uri = BASE_URI+audio_file_name
    transcription = transcribe_gcs(gcs_uri=file_uri,
                                    language_code=audio_language)
    txt_file_name = audio_file_name.replace('mp3', 'txt')
    
    with open('texts/'+txt_file_name, 'w') as f:
        f.write(transcription)

if __name__ == '__main__':
    link = 'https://www.youtube.com/watch?v=3HZYb237m2k&ab_channel=MarcinNajmanOfficial'
    transcribe_link(link, 'pl-PL')
    # path = 'audio/transcript-test.mp3'
    # upload_blob(bucket_name='transcription-storage-witek',
    #                 source_file_name=path,
    #                 destination_blob_name='input/'+'transcript-fr.wav')
    # file_uri = BASE_URI+'transcript-test.mp3'
    # transcription = transcribe_gcs(gcs_uri=file_uri,
    #                                 language_code='fr-FR')
    
