from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
)
from constructs import Construct

class SmartFactoryStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # S3 bucket to store IoT data
        bucket = s3.Bucket(self, "SmartFactoryIoTBucket")

        # Lambda function to write data to S3
        lambda_fn = _lambda.Function(
            self, "IoTStoreToS3Function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="iot_store_to_s3.lambda_handler",
            code=_lambda.Code.from_asset("../lambda"),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            }
        )

        # Grant Lambda permission to write to S3
        bucket.grant_put(lambda_fn)
