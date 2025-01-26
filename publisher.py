import paho.mqtt.client as mqtt
import random
import time
import json
from datetime import datetime
import threading

# MQTT settings
BROKER = "localhost"
PORT = 1883
TOPIC1 = "time_series/data"
TOPIC2 = "time_series/data_stream_2"
TOPIC3 = "time_series/data_stream_3"

# Shared flag to signal threads to stop
stop_event = threading.Event()

def generate_random_data():
    """Generate random time-series data."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    value = random.uniform(10.0, 100.0)  # Random value between 10 and 100
    return {"timestamp": timestamp, "value": value}

def publish_data(topic, interval):
    """Connect to MQTT broker and publish random data."""
    client = mqtt.Client()
    client.connect(BROKER, PORT)

    try:
        while not stop_event.is_set():
            data = generate_random_data()
            client.publish(topic, json.dumps(data))
            print(f"Published to {topic}: {data}")
            time.sleep(interval)
    except Exception as e:
        print(f"Error in publisher for {topic}: {e}")
    finally:
        client.disconnect()
        print(f"Publisher for {topic} stopped.")

if __name__ == "__main__":
    # Create separate threads for the three publishers
    thread1 = threading.Thread(target=publish_data, args=(TOPIC1, 1))
    thread2 = threading.Thread(target=publish_data, args=(TOPIC2, 2))
    thread3 = threading.Thread(target=publish_data, args=(TOPIC3, 3))

    # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()

    try:
        while True:
            time.sleep(0.1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Main program stopped.")
        stop_event.set()  # Signal threads to stop

    # Wait for threads to finish
    thread1.join()
    thread2.join()
    thread3.join()
    print("All publishers stopped.")
