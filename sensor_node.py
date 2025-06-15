import paho.mqtt.client as mqtt
import random
import time
import json
import argparse
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("ForestFirePublisher")

# Parse argument
parser = argparse.ArgumentParser()
parser.add_argument("--node_id", type=str, required=True, help="ID dari node sensor")
parser.add_argument("--location", type=str, default="unknown", help="Lokasi sensor (misal: sumatera)")
args = parser.parse_args()

NODE_ID = args.node_id
LOCATION = args.location

# Konfigurasi MQTT
BROKER = "broker.hivemq.com"
PORT = 1883

# Struktur topic yang lebih informatif dan scalable
TOPIC_BASE = f"forest/area/{LOCATION}/sensor/{NODE_ID}"
TOPIC = {
    "temp": f"{TOPIC_BASE}/temperature",
    "humidity": f"{TOPIC_BASE}/humidity",
    "smoke": f"{TOPIC_BASE}/smoke",
    "pm25": f"{TOPIC_BASE}/pm25",
    "heartbeat": f"{TOPIC_BASE}/status",
    "lwt": f"{TOPIC_BASE}/status/lwt"
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"[{NODE_ID}] Terhubung ke broker MQTT")
    else:
        logger.error(f"[{NODE_ID}] Gagal terhubung, kode kesalahan: {rc}")

def connect_with_retry(client, retries=5, delay=5):
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"[{NODE_ID}] Mencoba terhubung ke broker... (Upaya {attempt}/{retries})")
            client.connect(BROKER, PORT)
            return True
        except Exception as e:
            logger.warning(f"[{NODE_ID}] Gagal terhubung: {e}")
            if attempt < retries:
                time.sleep(delay)
    return False

# Buat klien MQTT
client = mqtt.Client(client_id=f"sensor-node-{NODE_ID}")
client.on_connect = on_connect

# Set Last Will and Testament (LWT)
lwt_message = json.dumps({
    "node": NODE_ID,
    "timestamp": int(time.time()),
    "status": "offline",
    "pesan": "Sensor terputus secara mendadak"
})
client.will_set(TOPIC["lwt"], payload=lwt_message, qos=1, retain=True)

# Coba terhubung ke broker
if not connect_with_retry(client):
    logger.error(f"[{NODE_ID}] Gagal terhubung ke broker setelah beberapa upaya. Keluar.")
    exit(1)

client.loop_start()

# Parameter Simulasi
current_temp = 25.0
current_humidity = 70.0
current_smoke = 50  # ppm
current_pm25 = 15   # µg/m³
fire_active = False
heartbeat_interval = 30
last_heartbeat = time.time()

def simulate_sensors():
    global current_temp, current_humidity, current_smoke, current_pm25, fire_active
    
    # Trigger kebakaran acak (0.2% chance)
    if not fire_active and current_temp < 50.0 and random.random() < 0.002:
        fire_active = True
        logger.warning(f"[{NODE_ID}] 🔥 Kebakaran Terdeteksi!")

    # Naikkan suhu selama kebakaran
    if fire_active:
        current_temp += random.uniform(1.0, 5.0)
        current_humidity -= random.uniform(0.5, 2.0)
        current_smoke += random.randint(50, 200)
        current_pm25 += random.randint(20, 50)
        logger.warning(f"[{NODE_ID}] 🔥 Suhu: {round(current_temp, 1)}°C | Asap: {current_smoke}ppm | PM2.5: {current_pm25}µg/m³")
        
        if current_temp >= 80.0:
            fire_active = False
            logger.info(f"[{NODE_ID}] ✅ Kebakaran selesai.")
    else:
        # Fluktuasi normal
        current_temp += random.uniform(-0.5, 0.5)
        current_humidity += random.uniform(-1.0, 1.0)
        current_smoke += random.randint(-10, 10)
        current_pm25 += random.randint(-5, 5)

    # Batasan nilai
    current_temp = max(15.0, min(current_temp, 100.0))
    current_humidity = max(20.0, min(current_humidity, 100.0))
    current_smoke = max(0, min(current_smoke, 1000))
    current_pm25 = max(0, min(current_pm25, 500))

    return {
        "temp": round(current_temp, 1),
        "humidity": round(current_humidity, 1),
        "smoke": current_smoke,
        "pm25": current_pm25
    }

try:
    while True:
        current_time = time.time()
        timestamp_unix = int(current_time)
        timestamp_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))

        data = simulate_sensors()

        # Kirim semua data sensor jika ada kebakaran
        if fire_active:
            payload = {
                "node": NODE_ID,
                "timestamp": {
                    "unix": timestamp_unix,
                    "readable": timestamp_readable
                },
                "temperature": data["temp"],
                "humidity": data["humidity"],
                "smoke": data["smoke"],
                "pm25": data["pm25"],
                "status": "kebakaran"
            }
            client.publish(TOPIC["temp"], json.dumps({"value": data["temp"], "unit": "°C"}), qos=1)
            client.publish(TOPIC["humidity"], json.dumps({"value": data["humidity"], "unit": "%"}), qos=1)
            client.publish(TOPIC["smoke"], json.dumps({"value": data["smoke"], "unit": "ppm"}), qos=1)
            client.publish(TOPIC["pm25"], json.dumps({"value": data["pm25"], "unit": "µg/m³"}), qos=1)
            logger.warning(f"[{NODE_ID}][Publish] 🔥 Data kebakaran dikirim.")

        # Kirim heartbeat jika tidak kebakaran
        elif current_time - last_heartbeat >= heartbeat_interval:
            payload = json.dumps({
                "node": NODE_ID,
                "timestamp": timestamp_unix,
                "status": "aktif",
                "pesan": "Sensor normal"
            })
            client.publish(TOPIC["heartbeat"], payload, qos=1, retain=True)
            logger.info(f"[{NODE_ID}] 💓 Heartbeat dikirim")
            last_heartbeat = current_time
            
        time.sleep(1)

except KeyboardInterrupt:
    logger.info("\n[Publisher] Program dihentikan oleh pengguna.")
finally:
    client.loop_stop()
    client.disconnect()
    logger.info("[Publisher] Terputus dari broker MQTT.")