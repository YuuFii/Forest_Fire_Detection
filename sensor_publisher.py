import paho.mqtt.client as mqtt
import random
import time
import json
from datetime import datetime
import threading

BROKER = "broker.hivemq.com"
PORT = 1883

# Konfigurasi sensor dengan lokasi & koordinat
SENSOR_CONFIG = {
    "sensor_01": {"location": "kalimantan_barat", "lat": -0.062, "lon": 109.342},
    "sensor_02": {"location": "kalimantan_barat", "lat": 0.152, "lon": 109.312},
    "sensor_03": {"location": "kalimantan_barat", "lat": 0.256, "lon": 109.562}
}

THRESHOLDS = {
    "FFMC": 85, "DMC": 100, "DC": 500, "ISI": 10,
    "temp": 30, "RH": 35, "wind": 6, "rain": 0.5
}

def simulate_sensor(sensor_id, config):
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)

    while True:
        FFMC = round(random.uniform(18.7, 96.2), 2)
        DMC = round(random.uniform(1.1, 291.3), 2)
        DC = round(random.uniform(7.9, 860.6), 2)
        ISI = round(random.uniform(0.0, 56.1), 2)
        temp = round(random.uniform(2.2, 33.3), 2)
        RH = round(random.uniform(15.0, 100.0), 2)
        wind = round(random.uniform(0.4, 9.4), 2)
        rain = round(random.uniform(0.0, 6.4), 2)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "sensor_id": sensor_id,
            "location": config["location"],
            "lat": config["lat"],
            "lon": config["lon"],
            "type": "data",
            "timestamp": timestamp,
            "data": {
                "FFMC": FFMC, "DMC": DMC, "DC": DC, "ISI": ISI,
                "temp": temp, "RH": RH, "wind": wind, "rain": rain
            }
        }

        # Evaluasi threshold
        if any(payload["data"][k] > THRESHOLDS[k] for k in THRESHOLDS):
            topic = f"forest/area/{config['location']}/sensor/{sensor_id}"
            client.publish(topic, json.dumps(payload))
            print(f"[PUBLISH] 🚨 Data dikirim oleh {sensor_id}")
        else:
            if int(time.time()) % 30 == 0:
                payload["type"] = "heartbeat"
                topic = f"forest/area/{config['location']}/sensor/{sensor_id}/heartbeat"
                client.publish(topic, json.dumps(payload))
                print(f"[HEARTBEAT] 💓 {sensor_id} OK")

        time.sleep(30)

# Jalankan multi-thread untuk semua sensor
for sensor_id, config in SENSOR_CONFIG.items():
    threading.Thread(target=simulate_sensor, args=(sensor_id, config), daemon=True).start()

while True:
    time.sleep(1)
