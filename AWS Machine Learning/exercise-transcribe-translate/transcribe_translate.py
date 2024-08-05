import json
import re
import boto3
from random import choice
import requests
import time
re_sentence = """(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"""
ACCESS_KEY=
SECRET_KEY=
# =============================================================================
# Upload to s3
# =============================================================================
s3_client = boto3.client('s3', region_name='us-west-2', aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3_client.upload_file('Raf01_320.mov', 'roybucket0317-2', 'Exercise/Raf01_320.mov')

json_config = {
    "TranscriptionJobName": "MyTranscriptionJob",
    "Media": {
        "MediaFileUri": "s3://roybucket0317/Exercise/Raf01_320.mov"
    },
    "LanguageCode": "en-US",
    "OutputBucketName": "roybucket0317"
}
with open('transcription_config.json', 'w') as json_file:
    json.dump(json_config, json_file, indent=4)

s3_client.upload_file('transcription_config.json', 'roybucket0317', 'transcription_config.json')

# =============================================================================
# Transcribe
# =============================================================================
transcribe = boto3.client('transcribe', region_name='us-east-2', aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)

transcribe.start_transcription_job(TranscriptionJobName='MyFirstTranscription',Media={"MediaFileUri": "s3://roybucket0317-2/Exercise/Raf01_320.mov"}, LanguageCode = "pt-BR")

for i in range(5):
    if transcribe.get_transcription_job(TranscriptionJobName='MyFirstTranscription')['TranscriptionJob'].get('Transcript') != None:
        transcribe_json = requests.get(transcribe.get_transcription_job(TranscriptionJobName='MyFirstTranscription')['TranscriptionJob']['Transcript']['TranscriptFileUri']).json()
        break
    else:
        time.sleep(5)
        print('waiting')

transcribe.delete_transcription_job(TranscriptionJobName='MyFirstTranscription')

with open('transcribe.json', 'w') as json_file:
    json.dump(transcribe_json, json_file, indent=4)

# =============================================================================
# Translate
# =============================================================================
with open("transcribe.json") as file:
    transcribe = json.load(file)

# build array of start times
times = [item["start_time"] for item in transcribe["results"]["items"] if "start_time" in item]

translate = boto3.client('translate',region_name='us-west-2', aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
transcript = transcribe["results"]["transcripts"][0]["transcript"]
sentences = re.split(re_sentence, transcript)
word_ptr = 0
translated_arr = []

for sentence in sentences:
    translated = translate.translate_text(
        Text=sentence,
        SourceLanguageCode='pt-BR',
        TargetLanguageCode='en-US'
    )
    translated_text = translated["TranslatedText"]
    translated_arr.append({ "start_time" : times[word_ptr], "translated" : translated_text})
    word_count = len(re.findall(r'\w+', sentence))
    word_ptr += word_count

print(json.dumps(translated_arr, indent=2))
with open('translated.json', 'w') as json_file:
    json.dump(translated_arr, json_file, indent=4)
