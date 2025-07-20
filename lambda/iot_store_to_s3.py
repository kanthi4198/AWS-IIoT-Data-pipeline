import json
import boto3
import os
from datetime import datetime, UTC

s3 = boto3.client('s3')
bucket_name = os.environ["BUCKET_NAME"]

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    try:
        timestamp = datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H-%M-%S-%f")
        filename = f"iot-data/{timestamp}.json"

        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=json.dumps(event),
            ContentType='application/json'
        )

        return {
            'statusCode': 200,
            'body': f"Saved to S3: {filename}"
        }

    except Exception as e:
        print("Error:", str(e))
        raise
