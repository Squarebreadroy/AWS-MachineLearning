import glob
import boto3
import json

ACCESS_KEY=
SECRET_KEY=
client = boto3.client('rekognition',region_name='us-west-2', aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
combined = []
for filename in glob.glob('public/photos/*.jpeg'):
    with open(filename, 'rb') as fd:
        response = client.detect_labels(Image={'Bytes': fd.read()})
        entry = {  "Filename": filename.replace("public/", "") }
        entry["Labels"] = response["Labels"]
        combined.append(entry)

print(json.dumps(combined, indent=2))
