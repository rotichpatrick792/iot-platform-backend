# 🌐 IoT Device Management Platform

A production-ready IoT device management backend built with FastAPI, featuring JWT authentication, MQTT bridge, and SQLite database.

## 🚀 Features

- **User Authentication**: JWT-based registration and login
- **Device Management**: Register, update, delete, and monitor IoT devices
- **Telemetry Ingestion**: Store temperature, humidity, and battery data
- **MQTT Bridge**: Automatically subscribes to ESP8266 sensor data
- **Auto-generated API Docs**: Swagger UI at `/docs`
- **Admin Endpoints**: User and system statistics

## 🛠️ Tech Stack

- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- SQLite (Database)
- JWT (Authentication)
- Paho-MQTT (MQTT client)
- Uvicorn (ASGI server)

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/rotichpatrick792/iot-platform-backend.git
cd iot-platform-backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py