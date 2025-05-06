import time
import random
import threading
import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
TOPIC = {
    "temp": "forest/temp",
    "humidity": "forest/humidity",
    "air_quality": "forest/air_quality",
    "alert": "forest/fire_alert",
}
THRESHOLDS = {
    "temp": 45,
    "humidity": 20,
    "air_quality": 200,
}

stop_threads = False
client = mqtt.Client()
client.connect(BROKER)

def simulate_sensor(sensor_type="temp", interval=3):
    global stop_threads
    while not stop_threads:
        try:
            if sensor_type=="temp":
                value = random.uniform(30, 50)
            elif sensor_type=="humidity":
                value = random.uniform(10, 60)
            elif sensor_type=="air_quality":
                value = random.randint(100, 300)

            if value > THRESHOLDS[sensor_type]:
                payload = f"{sensor_type}:{value:.2f}"
                client.publish(TOPIC[sensor_type], payload)
                print(f"[Publish] {payload}")

            time.sleep(interval)
        except Exception as e:
            print(f"Error in {sensor_type} thread: {e}")
            break

def heartbeat():
    global stop_threads
    while not stop_threads:
        try:
            msg = "heartbeat:alive"
            client.publish("forest/heartbeat", msg)
            print("[Heartbeat] Node aktif")
            time.sleep(30)
        except Exception as e:
            print(f"Error in heartbeat thread: {e}")
            break

threads = [
    threading.Thread(target=simulate_sensor, args=("temp",)),
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
    print("\nMenerima sinyal interrupt, menghentikan program...")
    stop_threads = True

    for t in threads:
        t.join(timeout=1)

    client.disconnect()
    print("Program selesai.")