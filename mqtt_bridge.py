import paho.mqtt.client as mqtt # type: ignore
import threading
from sqlalchemy.orm import Session # type: ignore
from database import SessionLocal
from models import Device, Telemetry
from datetime import datetime

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_TEMP = "konza/sensor/temperature"
TOPIC_HUM = "konza/sensor/humidity"

latest_readings = {"temperature": None, "humidity": None}

def save_telemetry(db: Session, device_id: str, temperature: float, humidity: float):
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        print(f"⚠️ Device {device_id} not registered")
        return

    telemetry = Telemetry(device_id=device.id, temperature=temperature, humidity=humidity)
    db.add(telemetry)
    device.last_seen = datetime.now()
    device.status = "online"
    db.commit()
    print(f"✅ Saved: {temperature}°C, {humidity}% for {device_id}")

def on_connect(client, userdata, flags, rc):
    print(f"✅ MQTT Connected (Code: {rc})")
    client.subscribe([(TOPIC_TEMP, 0), (TOPIC_HUM, 0)])

def on_message(client, userdata, msg):
    global latest_readings
    payload = msg.payload.decode().strip()

    if msg.topic == TOPIC_TEMP:
        latest_readings["temperature"] = float(payload)
        print(f"🌡️ Temp: {payload}°C")
    elif msg.topic == TOPIC_HUM:
        latest_readings["humidity"] = float(payload)
        print(f"💧 Humidity: {payload}%")

    if latest_readings["temperature"] is not None and latest_readings["humidity"] is not None:
        db = SessionLocal()
        try:
            save_telemetry(db, "ESP8266_001", latest_readings["temperature"], latest_readings["humidity"])
        finally:
            db.close()
        latest_readings = {"temperature": None, "humidity": None}

def start_mqtt_bridge():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    print("🔄 MQTT Bridge listening...")
    client.loop_forever()

def start_mqtt_thread():
    thread = threading.Thread(target=start_mqtt_bridge, daemon=True)
    thread.start()
    print("🚀 MQTT Bridge thread started")