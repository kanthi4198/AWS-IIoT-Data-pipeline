from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_iam as iam,
    aws_iot as iot,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    RemovalPolicy,
)
from constructs import Construct

class SmartFactoryStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # S3 bucket for batched CSV output (used by dynamodb_to_s3)
        bucket = s3.Bucket(
            self, "SmartFactoryIoTBucket",
            removal_policy=RemovalPolicy.RETAIN
        )

        # DynamoDB table for buffering IoT messages
        table = dynamodb.Table(
            self, "SmartFactoryIoTMessages",
            table_name="SmartFactoryIoTMessages",
            partition_key={"name": "id", "type": dynamodb.AttributeType.STRING},
            sort_key={"name": "timestamp", "type": dynamodb.AttributeType.STRING},
            removal_policy=RemovalPolicy.RETAIN,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        # Lambda A: Store MQTT messages to DynamoDB
        lambda_store = _lambda.Function(
            self, "IoTStoreToDynamoDBFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="iot_store_to_dynamodb.lambda_handler",
            code=_lambda.Code.from_asset("../lambda"),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "DYNAMODB_TABLE_NAME": table.table_name,
            },
        )
        table.grant_write_data(lambda_store)
        bucket.grant_put(lambda_store)  # Optional, if S3 is used later

        # IoT Core rule to trigger Lambda A on MQTT
        topic_rule_name = "TriggerLambdaOnMQTTMessage"
        iot.CfnTopicRule(
            self, "IoTTopicRule",
            rule_name=topic_rule_name,
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                sql="SELECT * FROM 'factory/line1/data'",
                actions=[
                    iot.CfnTopicRule.ActionProperty(
                        lambda_=iot.CfnTopicRule.LambdaActionProperty(
                            function_arn=lambda_store.function_arn
                        )
                    )
                ],
                rule_disabled=False
            )
        )
        lambda_store.add_permission(
            "AllowIoTInvoke",
            principal=iam.ServicePrincipal("iot.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=f"arn:aws:iot:{self.region}:{self.account}:rule/{topic_rule_name}"
        )

        # Lambda B: Run hourly to batch DynamoDB to S3
        lambda_batch = _lambda.Function(
            self, "DynamoDBToS3Function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="dynamodb_to_s3.lambda_handler",
            code=_lambda.Code.from_asset("../lambda"),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "DYNAMODB_TABLE_NAME": table.table_name,
            },
        )
        table.grant_read_data(lambda_batch)
        bucket.grant_put(lambda_batch)

        # EventBridge rule to trigger Lambda B hourly
        hourly_rule = events.Rule(
            self, "HourlyDynamoDBToS3Rule",
            schedule=events.Schedule.cron(minute="0", hour="*")
        )
        hourly_rule.add_target(targets.LambdaFunction(lambda_batch))







