import glob
import boto3
import json
import csv
import sys

csv_array = []
ACCESS_KEY=
SECRET_KEY=
client = boto3.client('textract',region_name='us-west-2', aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
for filename in glob.glob('raw_images/*.jpg'):
    csv_row = {}
    print(f"Processing: {filename}")
    with open(filename, 'rb') as fd:
        file_bytes = fd.read()

    response = client.analyze_document(
        Document={'Bytes': file_bytes},
        FeatureTypes=["QUERIES"],
        QueriesConfig={
            'Queries': [
                {'Text': 'What is the response id', 'Alias': 'ResponseId'},
                {'Text': 'What are the notes?', 'Alias': 'Notes'},
            ]
        }
    )

    # uncomment this to see the format of the reponse
    print(json.dumps(response, indent=2))

    #####
    # Replace this code with a solution to populate a dictionary with the results from textract
    #####
    for i in range(len(response['Blocks'])):
        if response['Blocks'][i].get('Text') == 'Response ID' and response['Blocks'][i+2].get('Text')=='Notes':
            csv_row['ResponseId'] = response['Blocks'][i+1]['Text']
            csv_row["Notes"] = response['Blocks'][i+3]['Text']
    csv_array.append(csv_row)

writer = csv.DictWriter(sys.stdout, fieldnames=["ResponseId", "Notes"], dialect='excel')
writer.writeheader()
for row in csv_array:
    writer.writerow(row)
