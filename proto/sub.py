import paho.mqtt.client as mqtt
import json
import time

# Konfigurasi MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPICS = [
    "forest/sensor/temp",
    "forest/sensor/heartbeat"
]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[Subscriber] Terhubung ke broker MQTT")
        for topic in TOPICS:
            client.subscribe(topic)
            print(f"[Subscriber] Subscribe ke topic: {topic}")
    else:
        print(f"[Subscriber] Gagal terhubung, kode kesalahan: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        timestamp = payload.get('timestamp', 'N/A')
        
        if msg.topic == TOPICS[0]:  # Temperature topic
            temp = payload['temperature']
            status = payload['status']
            print(f"🌡️ [SUHU] {timestamp} | {temp}°C | Status: {status}")
            
            # Visual indicator for fire status
            if status == "kebakaran":
                print("🔥🔥🔥 WARNING: KEBAKARAN TERDETEKSI! 🔥🔥🔥")
                
        elif msg.topic == TOPICS[1]:  # Heartbeat topic
            status = payload['status']
            message = payload['pesan']
            print(f"💓 [HEARTBEAT] {timestamp} | Status: {status} | {message}")
            
    except Exception as e:
        print(f"[ERROR] Gagal memproses pesan: {e}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"[Subscriber] Terputus tiba-tiba, kode: {rc}")
    else:
        print("[Subscriber] Terputus dengan sengaja")

# Setup client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

try:
    client.connect(BROKER, PORT)
    print("[Subscriber] Menghubungkan ke broker...")
    client.loop_forever()
    
except KeyboardInterrupt:
    print("\n[Subscriber] Memutus koneksi...")
    client.disconnect()
    
except Exception as e:
    print(f"[Subscriber] Error: {e}")
    client.disconnect()