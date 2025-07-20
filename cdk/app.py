import aws_cdk as cdk
from smart_factory_iot_stack import SmartFactoryStack

app = cdk.App()
SmartFactoryStack(app, "SmartFactoryStack")
app.synth()