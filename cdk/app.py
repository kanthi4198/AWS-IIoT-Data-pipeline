import aws_cdk as cdk
from smart_factory_iot_stack import SmartFactoryStack

app = cdk.App()

SmartFactoryStack(app, "SmartFactoryStack",
    env=cdk.Environment(account="218508884047", region="eu-north-1")
)

app.synth()