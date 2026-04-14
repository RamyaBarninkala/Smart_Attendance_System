
from __future__ import print_function
import boto3
import urllib.parse

print('Loading function')

# AWS Clients
dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

# ---------- Helper Functions ----------

def index_faces(bucket, key):
    response = rekognition.index_faces(
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        CollectionId="students"   # UPDATED
    )
    return response

def update_index(face_id, full_name):
    dynamodb.put_item(
        TableName="studentsCollection",
        Item={
            'RekognitionId': {'S': face_id},
            'FullName': {'S': full_name}
        }
    )

# ---------- Main Lambda Handler ----------

def lambda_handler(event, context):
    try:
        print("Event:", event)

        records = event.get('Records', [])
        if not records:
            return {'statusCode': 400, 'body': 'No records found'}

        record = records[0]
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])

        print(f"Processing: s3://{bucket}/{key}")

        # Ensure correct bucket
        if bucket != "studentfaces-1":
            print("Wrong bucket triggered")
            return {'statusCode': 400, 'body': 'Wrong bucket'}

        # Call Rekognition
        response = index_faces(bucket, key)

        face_records = response.get('FaceRecords', [])

        if not face_records:
            print("No face detected")
            return {'statusCode': 400, 'body': 'No face detected'}

        # Get FaceId
        face_id = face_records[0]['Face']['FaceId']

        # Get metadata (student name)
        metadata = s3.head_object(Bucket=bucket, Key=key)
        full_name = metadata['Metadata'].get('fullname', 'Unknown')

        # Store in DynamoDB
        update_index(face_id, full_name)

        print(f"Stored → FaceId: {face_id}, Name: {full_name}")

        return {
            'statusCode': 200,
            'body': 'Face indexed successfully'
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': str(e)
        }