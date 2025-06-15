import paho.mqtt.client as mqtt
from concurrent.futures import ThreadPoolExecutor
import json
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("ForestFireSubscriber")

BROKER = "broker.hivemq.com"
PORT = 1883

# Subscribe semua sensor dari semua lokasi dan jenis
TOPICS = [
    "forest/area/+/sensor/+/temperature",
    "forest/area/+/sensor/+/humidity",
    "forest/area/+/sensor/+/smoke",
    "forest/area/+/sensor/+/pm25",
    "forest/area/+/sensor/+/status"
]

executor = ThreadPoolExecutor(max_workers=10)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("[Connected] Sukses terhubung ke broker")
        for topic in TOPICS:
            client.subscribe(topic)
            logger.info(f"[Subscribe] {topic}")
    else:
        logger.error(f"[Connection Failed] Code: {rc}")

def parse_topic(topic):
    """
    Parsing topik MQTT menjadi informasi lokasi, node_id, dan tipe sensor.
    Contoh input: forest/area/jakarta/sensor/sensor01/temperature
    Output: {'location': 'jakarta', 'node_id': 'sensor01', 'sensor_type': 'temperature'}
    """
    parts = topic.split('/')
    if len(parts) != 6 or parts[0] != "forest" or parts[1] != "area":
        return None
    return {
        "location": parts[2],
        "node_id": parts[4],
        "sensor_type": parts[5]
    }

def is_fire_condition(data):
    """
    Deteksi potensi kebakaran berdasarkan kombinasi sensor
    """
    temp = data.get("temperature")
    humidity = data.get("humidity")
    smoke = data.get("smoke")
    pm25 = data.get("pm25")

    # Threshold sederhana untuk deteksi api
    if temp and temp > 45 and humidity < 30 and smoke > 200 and pm25 > 150:
        return True
    return False

def process_message(topic, payload):
    parsed = parse_topic(topic)
    if not parsed:
        logger.warning(f"[Invalid Topic] {topic}")
        return

    location = parsed["location"]
    node_id = parsed["node_id"]
    sensor_type = parsed["sensor_type"]

    try:
        data = json.loads(payload)
        value = data.get("value")
        unit = data.get("unit", "")

        logger.info(f"[{location}][{node_id}] {sensor_type}: {value}{unit}")

        # Simpan data ke dalam context untuk analisis multi-sensor
        if not hasattr(process_message, "context"):
            process_message.context = {}

        key = f"{location}_{node_id}"
        if key not in process_message.context:
            process_message.context[key] = {}

        process_message.context[key][sensor_type] = value

        # Analisis multi-sensor
        ctx = process_message.context[key]
        if len(ctx) >= 4 and is_fire_condition(ctx):  # Jika semua sensor ada datanya
            alert_msg = {
                "node": node_id,
                "location": location,
                "timestamp": int(time.time()),
                "alert": "🔥 Potensi kebakaran terdeteksi!",
                "details": ctx
            }
            logger.critical(f"[ALERT] {alert_msg}")
            client.publish(f"forest/alert/{location}/{node_id}", json.dumps(alert_msg), qos=1)

    except Exception as e:
        logger.error(f"[Error processing message] {e}")

def on_message(client, userdata, msg):
    executor.submit(process_message, msg.topic, msg.payload.decode())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, PORT)
    logger.info("[Server] Menunggu data dari sensor...")
    client.loop_forever()
except Exception as e:
    logger.error(f"[Connection Error] Tidak dapat terhubung ke broker: {e}")