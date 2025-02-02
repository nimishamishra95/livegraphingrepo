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
import sys

# Set font to something similar to Calibri
mpl.rcParams['font.family'] = 'DejaVu Sans'  # Replace with 'Calibri' if installed

# MQTT settings
BROKER = "localhost"
PORT = 1883
TOPIC1 = "time_series/data"
TOPIC2 = "time_series/data_stream_2"
TOPIC3 = "time_series/data_stream_3"

# Data storage
timestamps_stream1 = []
values_stream1 = []
timestamps_stream2 = []
values_stream2 = []
timestamps_stream3 = []
values_stream3 = []
data_queue1 = queue.Queue()
data_queue2 = queue.Queue()
data_queue3 = queue.Queue()

def on_message(client, userdata, msg):
    """Callback for receiving MQTT messages."""
    data = json.loads(msg.payload.decode())
    if msg.topic == TOPIC1:
        data_queue1.put(data)
    elif msg.topic == TOPIC2:
        data_queue2.put(data)
    elif msg.topic == TOPIC3:
        data_queue3.put(data)

def mqtt_subscriber():
    """Subscribe to the MQTT topics in a separate thread."""
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe([(TOPIC1, 0), (TOPIC2, 0), (TOPIC3, 0)])  # Subscribe to all topics
    client.loop_forever()

def plot_data():
    """Plot data from the queues with smooth curves and straight lines."""
    global timestamps_stream1, values_stream1, timestamps_stream2, values_stream2, timestamps_stream3, values_stream3

    # Set Seaborn theme
    sns.set_theme(style="whitegrid")

    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharex=True)

    try:
        while plt.fignum_exists(fig.number):  # Check if the figure still exists
            # Process new data from stream 1
            while not data_queue1.empty():
                data = data_queue1.get()
                timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
                value = data["value"]

                timestamps_stream1.append(timestamp)
                values_stream1.append(value)

                # Keep only the latest 100 points
                if len(timestamps_stream1) > 100:
                    timestamps_stream1.pop(0)
                    values_stream1.pop(0)

            # Process new data from stream 2
            while not data_queue2.empty():
                data = data_queue2.get()
                timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
                value = data["value"]

                timestamps_stream2.append(timestamp)
                values_stream2.append(value)

                # Keep only the latest 100 points
                if len(timestamps_stream2) > 100:
                    timestamps_stream2.pop(0)
                    values_stream2.pop(0)

            # Process new data from stream 3
            while not data_queue3.empty():
                data = data_queue3.get()
                timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
                value = data["value"]

                timestamps_stream3.append(timestamp)
                values_stream3.append(value)

                # Keep only the latest 100 points
                if len(timestamps_stream3) > 100:
                    timestamps_stream3.pop(0)
                    values_stream3.pop(0)

            # Update the plot for streams 1 and 2
            ax1.clear()

            # Plot Stream 1
            sns.lineplot(
                x=timestamps_stream1,
                y=values_stream1,
                ax=ax1,
                color="darkorange",
                label="Stream 1 (Straight Line)",
                linewidth=2,
                marker="o",
            )

            # Add cubic spline interpolation for Stream 1
            if len(values_stream1) > 3:  # Need at least 4 points for cubic spline
                numeric_timestamps1 = mdates.date2num(timestamps_stream1)
                cs1 = CubicSpline(numeric_timestamps1, values_stream1)
                fine_timestamps1 = np.linspace(numeric_timestamps1[0], numeric_timestamps1[-1], 500)
                smooth_values1 = cs1(fine_timestamps1)
                sns.lineplot(
                    x=mdates.num2date(fine_timestamps1),
                    y=smooth_values1,
                    ax=ax1,
                    color="darkorange",
                    label="Stream 1 (Interpolated)",
                    linewidth=2,
                    linestyle="--",  # Dashed line
                )

            # Plot Stream 2
            sns.lineplot(
                x=timestamps_stream2,
                y=values_stream2,
                ax=ax1,
                color="green",
                label="Stream 2 (Straight Line)",
                linewidth=2,
                marker="o",
            )

            # Add cubic spline interpolation for Stream 2
            if len(values_stream2) > 3:  # Need at least 4 points for cubic spline
                numeric_timestamps2 = mdates.date2num(timestamps_stream2)
                cs2 = CubicSpline(numeric_timestamps2, values_stream2)
                fine_timestamps2 = np.linspace(numeric_timestamps2[0], numeric_timestamps2[-1], 500)
                smooth_values2 = cs2(fine_timestamps2)
                sns.lineplot(
                    x=mdates.num2date(fine_timestamps2),
                    y=smooth_values2,
                    ax=ax1,
                    color="green",
                    label="Stream 2 (Interpolated)",
                    linewidth=2,
                    linestyle="--",  # Dashed line
                )

            ax1.set_title("Live Time-Series Data: Streams 1 and 2", fontsize=18, fontweight="bold")
            ax1.set_xlabel("", fontsize=14)  # No xlabel for the top plot
            ax1.set_ylabel("Value", fontsize=14)
            ax1.legend(loc="upper left", fontsize=12)

            # Update the plot for stream 3
            ax2.clear()

            sns.lineplot(
                x=timestamps_stream3,
                y=values_stream3,
                ax=ax2,
                color="blue",
                label="Stream 3 (Straight Line)",
                linewidth=2,
                marker="o",
            )

            # Add cubic spline interpolation for Stream 3
            if len(values_stream3) > 3:  # Need at least 4 points for cubic spline
                numeric_timestamps3 = mdates.date2num(timestamps_stream3)
                cs3 = CubicSpline(numeric_timestamps3, values_stream3)
                fine_timestamps3 = np.linspace(numeric_timestamps3[0], numeric_timestamps3[-1], 500)
                smooth_values3 = cs3(fine_timestamps3)
                sns.lineplot(
                    x=mdates.num2date(fine_timestamps3),
                    y=smooth_values3,
                    ax=ax2,
                    color="blue",
                    label="Stream 3 (Interpolated)",
                    linewidth=2,
                    linestyle="--",  # Dashed line
                )

            ax2.set_title("Live Time-Series Data: Stream 3", fontsize=18, fontweight="bold")
            ax2.set_xlabel("Timestamp", fontsize=14)
            ax2.set_ylabel("Value", fontsize=14)
            ax2.legend(loc="upper left", fontsize=12)

            # Format x-axis with readable timestamps
            ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            fig.autofmt_xdate()

            plt.tight_layout()
            plt.pause(0.01)
            time.sleep(0.1)  # Reduce CPU usage

    finally:
        plt.close()
        print("Plot window closed. Exiting.")

if __name__ == "__main__":
    # Start MQTT subscriber in a separate thread
    subscriber_thread = threading.Thread(target=mqtt_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    # Start the plotting function in the main thread
    plot_data()
