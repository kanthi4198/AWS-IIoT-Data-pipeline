import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SmartFactoryIoTMessages')  # Name matches the CDK Table ID

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    try:
        for record in event.get('Records', [event]):
            # Parse individual record if coming from IoT Rule directly
            message = record.get('message') if 'message' in record else record

            # Generate a timestamp-based partition key
            timestamp = datetime.now(timezone.UTC).isoformat()

            # Insert into DynamoDB
            table.put_item(
                Item={
                    'timestamp': timestamp,
                    'message': message
                }
            )
            print(f"Stored message at {timestamp}")

        return {
            'statusCode': 200,
            'body': 'Messages written to DynamoDB'
        }

    except Exception as e:
        print("Error:", str(e))
        raise