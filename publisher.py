import paho.mqtt.client as mqtt
import random
import time
import json
from datetime import datetime

# MQTT settings
BROKER = "localhost"
PORT = 1883
TOPIC = "time_series/data"

def generate_random_data():
    """Generate random time-series data."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    value = random.uniform(10.0, 100.0)  # Random value between 10 and 100
    return {"timestamp": timestamp, "value": value}

def publish_data():
    """Connect to MQTT broker and publish random data."""
    client = mqtt.Client()
    client.connect(BROKER, PORT)

    try:
        while True:
            data = generate_random_data()
            client.publish(TOPIC, json.dumps(data))
            print(f"Published: {data}")
            time.sleep(1)  # Publish every second
    except KeyboardInterrupt:
        print("Publisher stopped.")
    finally:
        client.disconnect()

if __name__ == "__main__":
    publish_data()
