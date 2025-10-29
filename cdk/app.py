import os
from dotenv import load_dotenv
import aws_cdk as cdk
from smart_factory_iot_stack import SmartFactoryStack

# Load environment variables from `.env` file
load_dotenv()

account = os.environ.get("CDK_DEFAULT_ACCOUNT")
region = os.environ.get("CDK_DEFAULT_REGION")

app = cdk.App()

SmartFactoryStack(app, "SmartFactoryStack",
    env=cdk.Environment(account=account, region=region)
)

app.synth()