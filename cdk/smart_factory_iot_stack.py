from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_iam as iam,
    aws_iot as iot,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_glue as glue,
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

        #Glue catalog database and crawler
        GLUE_DB_NAME = "smart_factory_db"
        CRAWLER_NAME = "iot_hourly_crawler"
        S3_PREFIX = "iot-data/"  # <-- ensure Lambda B writes CSVs here

        # 1) Glue Data Catalog Database
        glue_db = glue.CfnDatabase(
            self, "SmartFactoryGlueDb",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(name=GLUE_DB_NAME),
        )

        # 2) IAM Role for Glue Crawler (minimal S3 read + managed Glue role)
        glue_role = iam.Role(
            self, "SmartFactoryGlueCrawlerRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
            ],
        )
        glue_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:ListBucket", "s3:GetBucketLocation"],
            resources=[bucket.bucket_arn],
        ))
        glue_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[f"{bucket.bucket_arn}/*"],
        ))

        # 3) Glue Crawler scanning your batched CSVs in S3
        s3_path = f"s3://{bucket.bucket_name}/{S3_PREFIX}"
        crawler = glue.CfnCrawler(
            self, "SmartFactoryGlueCrawler",
            name=CRAWLER_NAME,
            role=glue_role.role_arn,
            database_name=GLUE_DB_NAME,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[glue.CfnCrawler.S3TargetProperty(path=s3_path)]
            ),
            schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                delete_behavior="LOG",
                update_behavior="UPDATE_IN_DATABASE",
            ),
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(
                recrawl_behavior="CRAWL_NEW_FOLDERS",
            ),
           
        )
        crawler.add_dependency(glue_db)

        # 4) EventBridge rule to start Glue Crawler shortly after Lambda B runs

        # Lambda B runs at minute 0; crawler starts 5 minutes later.
        #crawler_rule = events.Rule(
        #    self, "StartGlueCrawlerHourly",
        #    schedule=events.Schedule.cron(minute="5", hour="*"),
        #)
        #crawler_rule.add_target(
        #    targets.AwsApi(
        #        service="Glue",
        #        action="startCrawler",
        #        parameters={"Name": CRAWLER_NAME},
        #        policy_statement=iam.PolicyStatement(
        #            actions=["glue:StartCrawler"],
        #            resources=["*"],
        #        ),
        #    )
        #)

        




