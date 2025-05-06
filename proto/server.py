import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
TOPICS = ["forest/temp", "forest/humidity", "forest/air_quality", "forest/heartbeat"]

def on_connect(client, userdata, flags, rc):
    print("[Connected] Code:", rc)
    for topic in TOPICS:
        client.subscribe(topic)
        print(f"[Subscribe] {topic}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    topic = msg.topic
    print(f"[Received] Topic: {topic} | Message: {payload}")

    # Deteksi kondisi kebakaran (misalnya suhu tinggi dan kelembaban rendah)
    if topic == "forest/temp" and float(payload.split(":")[1]) > 45:
        print("🚨 ALERT: Suhu ekstrem!")
        client.publish("forest/fire_alert", "ALERT: Potensi kebakaran hutan!")

    if topic == "forest/humidity" and float(payload.split(":")[1]) < 20:
        print("🚨 ALERT: Kelembaban rendah!")

    if topic == "forest/air_quality" and float(payload.split(":")[1]) > 200:
        print("🚨 ALERT: Kualitas udara buruk!")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER)
client.loop_forever()