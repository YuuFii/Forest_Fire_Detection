import paho.mqtt.client as mqtt
import random
import time
import json

# Konfigurasi MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = {
    "temp": "forest/sensor/temp",
    "heartbeat": "forest/sensor/heartbeat",
}

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[Publisher] Terhubung ke broker MQTT")
    else:
        print(f"[Publisher] Gagal terhubung, kode kesalahan: {rc}")

client.on_connect = on_connect
try:
    client.connect(BROKER, PORT)
except Exception as e:
    print(f"[Publisher] Gagal terhubung ke broker: {e}")
    exit(1)

# Parameter Simulasi
current_temp = 25.0
fire_active = False
heartbeat_interval = 30
last_heartbeat = time.time()

def simulate_temperature_sensor():
    global current_temp, fire_active
    
    # Trigger kebakaran acak (0.2% chance)
    if not fire_active and current_temp < 50.0 and random.random() < 0.01:
        fire_active = True
        print("[ALERT] 🔥 Terindikasi kebakaran!")
    
    # Naikkan suhu selama kebakaran
    if fire_active:
        current_temp += random.uniform(1.0, 5.0)  # Naik perlahan
        print(f"[ALERT] 🔥 Suhu kebakaran: {round(current_temp, 1)}°C")
        if current_temp >= 80.0:
            fire_active = False
            print("[INFO] ✅ Kebakaran selesai.")
    else:
        # Fluktuasi suhu normal
        current_temp += random.uniform(-0.5, 0.5)
        if current_temp > 30.0:
            current_temp -= random.uniform(0.5, 1.0)
    
    current_temp = max(15.0, min(current_temp, 100.0))
    return round(current_temp, 1)

try:
    client.loop_start()
    while True:
        current_time = time.time()
        temp = simulate_temperature_sensor()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))

        # Selama kebakaran, kirim data suhu real-time ke subscriber
        if fire_active:
            client.publish(TOPIC["temp"], json.dumps({
                "timestamp": timestamp,
                "temperature": temp,
                "status": "kebakaran"
            }))
            print(f"[Publish] Suhu: {temp}°C")

        # Kirim heartbeat jika tidak kebakaran
        elif current_time - last_heartbeat >= heartbeat_interval:
            client.publish(TOPIC["heartbeat"], json.dumps({
                "timestamp": timestamp,
                "status": "aktif",
                "pesan": "Sensor normal"
            }))
            last_heartbeat = current_time
            print(f"[Publisher] 💓 Heartbeat dikirim")
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[Publisher] Program dihentikan.")
    client.loop_stop()
    client.disconnect()
    print("[Publisher] Terputus dari broker MQTT.")