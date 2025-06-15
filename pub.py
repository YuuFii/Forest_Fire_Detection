import time
import random
import threading
import paho.mqtt.client as mqtt
import json
import argparse

# MQTT Broker
BROKER = "test.mosquitto.org"

# Daftar koordinat untuk simulasi lokasi sensor
COORDINATES = {
    "sensor01": {"lat": -6.2100, "lon": 106.8400},
    "sensor02": {"lat": -6.2150, "lon": 106.8420},
    "sensor03": {"lat": -6.2000, "lon": 106.8500},
    "sensor04": {"lat": -6.2200, "lon": 106.8600}
}

# Threshold deteksi kebakaran
THRESHOLDS = {
    "temperature": 45,
    "humidity": 20,
    "air_quality": 200,
}

# Setup argumen CLI
parser = argparse.ArgumentParser(description="Sensor Node Publisher")
parser.add_argument("--node_id", type=str, required=True, help="ID Sensor (misal: sensor01)")
args = parser.parse_args()

NODE_ID = args.node_id
SENSOR_COORD = COORDINATES.get(NODE_ID, {"lat": -6.9147, "lon": 107.6098})  # Default Bandung

# Buat klien MQTT
client = mqtt.Client(client_id=f"sensor-node-{NODE_ID}")

try:
    client.connect(BROKER)
except Exception as e:
    print(f"[{NODE_ID}] Gagal terhubung ke broker: {e}")
    exit(1)

def simulate_sensor(sensor_type="temperature", interval=3):
    while not stop_threads:
        try:
            if sensor_type == "temperature":
                value = round(random.uniform(30, 50), 2)
            elif sensor_type == "humidity":
                value = round(random.uniform(10, 60), 2)
            elif sensor_type == "air_quality":
                value = random.randint(100, 300)

            payload = {
                "node": NODE_ID,
                "timestamp": int(time.time()),
                "latitude": SENSOR_COORD["lat"],
                "longitude": SENSOR_COORD["lon"],
                "unit": "°C" if sensor_type == "temperature" else "%" if sensor_type == "humidity" else "AQI",
                "value": value
            }

            topic = f"forest/sensor/{NODE_ID}/{sensor_type}"
            client.publish(topic, json.dumps(payload))
            print(f"[{NODE_ID}][Publish] {topic} | {json.dumps(payload)}")

            time.sleep(interval)
        except Exception as e:
            print(f"[{NODE_ID}] Error in {sensor_type} thread: {e}")
            break

def heartbeat():
    while not stop_threads:
        try:
            payload = {
                "node": NODE_ID,
                "timestamp": int(time.time()),
                "status": "aktif",
                "pesan": "Sensor normal",
                "latitude": SENSOR_COORD["lat"],
                "longitude": SENSOR_COORD["lon"]
            }
            topic = f"forest/sensor/{NODE_ID}/status"
            client.publish(topic, json.dumps(payload))
            print(f"[{NODE_ID}][Heartbeat] Sent to {topic}")
            time.sleep(30)
        except Exception as e:
            print(f"[{NODE_ID}] Error in heartbeat thread: {e}")
            break

stop_threads = False

threads = [
    threading.Thread(target=simulate_sensor, args=("temperature",)),
    threading.Thread(target=simulate_sensor, args=("humidity",)),
    threading.Thread(target=simulate_sensor, args=("air_quality",)),
    threading.Thread(target=heartbeat)
]

for t in threads:
    t.daemon = True
    t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(f"\n[{NODE_ID}] Menerima sinyal interrupt, menghentikan program...")
    stop_threads = True

    for t in threads:
        t.join(timeout=1)

    client.disconnect()
    print(f"[{NODE_ID}] Program selesai.")