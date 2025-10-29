import json
import boto3
import datetime
import decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SmartFactoryIoTMessages')

def convert_floats(obj):
    if isinstance(obj, float):
        return decimal.Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats(i) for i in obj]
    return obj

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    try:
        # The IoT Core payload should be directly the JSON payload sent via MQTT
        message = convert_floats(event)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        table.put_item(
            Item={
                'id': f"{timestamp}",  
                'timestamp': timestamp,
                'message': message
            }
        )

        print(f"Stored message at {timestamp}")

        return {
            'statusCode': 200,
            'body': 'Message written to DynamoDB'
        }

    except Exception as e:
        print("Error:", str(e))
        raise