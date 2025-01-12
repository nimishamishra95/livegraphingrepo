import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from scipy.interpolate import CubicSpline
from datetime import datetime
import matplotlib.dates as mdates
import numpy as np
import json
import queue
import threading
import time

# Set font to something similar to Calibri
mpl.rcParams['font.family'] = 'DejaVu Sans'  # Replace with 'Calibri' if installed

# MQTT settings
BROKER = "localhost"
PORT = 1883
TOPIC = "time_series/data"

# Data storage
timestamps = []
values = []
data_queue = queue.Queue()

def on_message(client, userdata, msg):
    """Callback for receiving MQTT messages."""
    data = json.loads(msg.payload.decode())
    data_queue.put(data)

def mqtt_subscriber():
    """Subscribe to the MQTT topic in a separate thread."""
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(TOPIC)
    client.loop_forever()

def plot_data():
    """Plot data from the queue with smooth curves and straight lines."""
    global timestamps, values

    # Set Seaborn theme
    sns.set_theme(style="whitegrid")

    plt.ion()
    fig, ax = plt.subplots(figsize=(12, 6))

    while True:
        # Process new data from the queue
        while not data_queue.empty():
            data = data_queue.get()
            timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
            value = data["value"]

            timestamps.append(timestamp)
            values.append(value)

            # Keep only the latest 100 points
            if len(timestamps) > 100:
                timestamps.pop(0)
                values.pop(0)

        # Update the plot
        ax.clear()

        # Plot the straight line connecting all data points
        sns.lineplot(
            x=timestamps,
            y=values,
            ax=ax,
            color="darkorange",
            label="Straight Line Connection",
            linewidth=2,
            marker="o",
        )

        if len(values) > 3:  # Need at least 4 points for cubic spline
            # Convert timestamps to numeric for interpolation
            numeric_timestamps = mdates.date2num(timestamps)

            # Cubic spline interpolation
            cs = CubicSpline(numeric_timestamps, values)
            fine_timestamps = np.linspace(numeric_timestamps[0], numeric_timestamps[-1], 500)
            smooth_values = cs(fine_timestamps)

            # Plot the interpolated curve
            sns.lineplot(
                x=mdates.num2date(fine_timestamps),
                y=smooth_values,
                ax=ax,
                color="dodgerblue",
                label="Smoothed Curve",
                linewidth=2,
            )

        # Formatting and aesthetics
        ax.set_title("Live Time-Series Data with Smooth Interpolation and Straight Lines", fontsize=18, fontweight="bold")
        ax.set_xlabel("Timestamp", fontsize=14)
        ax.set_ylabel("Value", fontsize=14)
        ax.legend(loc="upper left", fontsize=12)

        # Format x-axis with readable timestamps
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        fig.autofmt_xdate()

        plt.tight_layout()
        plt.pause(0.01)
        time.sleep(0.1)  # Reduce CPU usage

if __name__ == "__main__":
    # Start MQTT subscriber in a separate thread
    subscriber_thread = threading.Thread(target=mqtt_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    # Start the plotting function in the main thread
    plot_data()
