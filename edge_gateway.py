import paho.mqtt.client as mqtt
import json
from datetime import datetime
import requests

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "forest/area/+/sensor/+"

THRESHOLDS = {
    "FFMC": 85, "DMC": 100, "DC": 500, "ISI": 10,
    "temp": 30, "RH": 35, "wind": 6, "rain": 0.5
}

sensor_data = {}

def is_anomalous(data):
    return any(data[k] > THRESHOLDS[k] for k in THRESHOLDS)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        if payload["type"] == "data":
            sid = payload["sensor_id"]
            sensor_data[sid] = payload
            check_and_alert(payload["location"])
    except Exception as e:
        print(f"[ERROR] Parsing failed: {e}")

def check_and_alert(location):
    latest = [d for d in sensor_data.values() if d["location"] == location]
    anomalies = [s for s in latest if is_anomalous(s["data"])]

    if anomalies:
        alert = {
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "detected": len(anomalies),
            "sensors": anomalies
        }

        print(f"[ALERT] 🚨 Anomali di {location} ({len(anomalies)} sensor)")
        try:
            r = requests.post("http://localhost:8000/alert", json=alert)
            print(f"[CLOUD] Status: {r.status_code}")
        except Exception as e:
            print(f"[CLOUD] ❌ Error: {e}")

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
client.loop_forever()
