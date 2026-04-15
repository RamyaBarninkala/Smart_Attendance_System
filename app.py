from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)

AWS_REGION = "us-east-1"

# AWS Clients (no credentials here)
rekognition = boto3.client('rekognition', region_name=AWS_REGION)
dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)

COLLECTION_ID = "students"
TABLE_NAME = "studentsCollection"
from flask import render_template

@app.route('/')
def home():
    return render_template('index.html')  


@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        file = request.files['image']

        response = rekognition.search_faces_by_image(
            CollectionId=COLLECTION_ID,
            Image={'Bytes': file.read()}
        )

        matches = response.get('FaceMatches', [])

        if not matches:
            return jsonify({"message": "No match found"})

        face_id = matches[0]['Face']['FaceId']

        result = dynamodb.get_item(
            TableName=TABLE_NAME,
            Key={'RekognitionId': {'S': face_id}}
        )

        if 'Item' not in result:
            return jsonify({"message": "Face found but not in database"})

        name = result['Item']['FullName']['S']

        return jsonify({"name": name})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
