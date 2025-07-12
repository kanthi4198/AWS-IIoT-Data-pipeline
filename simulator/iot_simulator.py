from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json, time, random

# Setup
client = AWSIoTMQTTClient("smart-factory-sim")
client.configureEndpoint("a2fmpkia3ov9nz-ats.iot.eu-north-1.amazonaws.com", 8883)
client.configureCredentials("AmazonRootCA1.pem", "7ec13e5c01c628e795354d3ea0c2c400c476dbcfd00f751485cd2e4d8a23dd9f-private.pem.key", "7ec13e5c01c628e795354d3ea0c2c400c476dbcfd00f751485cd2e4d8a23dd9f-certificate.pem.crt")

# Configure client
client.configureOfflinePublishQueueing(20)
client.configureDrainingFrequency(1)
client.configureConnectDisconnectTimeout(5)
client.configureMQTTOperationTimeout(3)

# Connect
print("Connecting to AWS IoT Core...")
client.connect()

# Publish simulated data
print("Publishing messages...\n")
while True:
    payload = {
        "machine_id": "M01",
        "temperature": round(random.uniform(65.0, 90.0), 2),
        "vibration": round(random.uniform(0.1, 0.9), 3),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    client.publish("factory/line1/data", json.dumps(payload), 1)
    print("Sent:", payload)
    time.sleep(60)




