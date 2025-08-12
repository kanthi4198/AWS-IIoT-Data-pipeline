import boto3
import csv
import os
import io
import datetime
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
BUCKET_NAME = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    # Determine the time range for the last full hour
    now = datetime.datetime.now(datetime.UTC).replace(minute=0, second=0, microsecond=0)
    end_time = now.isoformat()
    start_time = (now - datetime.timedelta(hours=1)).isoformat()

    print(f"Querying from {start_time} to {end_time}")

    # Query items within the time range
    response = table.scan()
    items = response['Items']

    # Filter by timestamp range
    filtered = [item for item in items if start_time <= item['timestamp'] < end_time]

    if not filtered:
        print("No records found in the past hour.")
        return {'statusCode': 200, 'body': 'No records to process'}

    # Prepare CSV
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(['timestamp', 'machine_id', 'temperature', 'vibration'])

    for item in filtered:
        message = item['message']
        writer.writerow([
            item['timestamp'],
            message['machine_id'],
            float(message['temperature']),
            float(message['vibration']),
        ])

    filename = f"iot-data/batch_{start_time.replace(':','-')}.csv"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=filename,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )

    print(f"Wrote {len(filtered)} records to S3 as {filename}")
    return {'statusCode': 200, 'body': f"Wrote {len(filtered)} records to S3 as {filename}"}
