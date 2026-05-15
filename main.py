from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import os

from database import engine, get_db
from models import Base, User, Device, Telemetry
from schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    DeviceCreate, DeviceResponse, DeviceUpdate,
    TelemetryCreate, TelemetryResponse
)
from auth import get_password_hash, authenticate_user, create_access_token, get_current_user, get_current_admin
from mqtt_bridge import start_mqtt_thread

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="IoT Device Management Platform", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start MQTT bridge thread
start_mqtt_thread()

# ============================================
# FRONTEND ROUTES
# ============================================

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

print(f"📁 Frontend directory: {FRONTEND_DIR}")
print(f"   login.html exists: {os.path.exists(os.path.join(FRONTEND_DIR, 'login.html'))}")
print(f"   index.html exists: {os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))}")

@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/login")
async def login_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/dashboard")
async def dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/index.html")
async def index_html():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
def health_check():
    return {"status": "ok"}

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    hashed = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ============================================
# DEVICE MANAGEMENT ENDPOINTS
# ============================================

@app.post("/devices", response_model=DeviceResponse)
def create_device(device: DeviceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Device).filter(Device.device_id == device.device_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Device ID already exists")
    db_device = Device(
        device_id=device.device_id, 
        name=device.name, 
        location=device.location, 
        device_type=device.device_type, 
        owner_id=current_user.id
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.get("/devices", response_model=List[DeviceResponse])
def get_devices(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Device).filter(Device.owner_id == current_user.id).all()

@app.delete("/devices/{device_id}")
def delete_device(device_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id, Device.owner_id == current_user.id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()
    return {"message": "Device deleted"}

# ============================================
# TELEMETRY ENDPOINTS
# ============================================

@app.get("/telemetry/{device_id}", response_model=List[TelemetryResponse])
def get_telemetry(device_id: int, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id, Device.owner_id == current_user.id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return db.query(Telemetry).filter(Telemetry.device_id == device_id).order_by(Telemetry.timestamp.desc()).limit(limit).all()

@app.get("/telemetry/{device_id}/latest")
def get_latest_telemetry(device_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id, Device.owner_id == current_user.id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    latest = db.query(Telemetry).filter(Telemetry.device_id == device_id).order_by(Telemetry.timestamp.desc()).first()
    if not latest:
        return {"message": "No telemetry data yet"}
    return {
        "temperature": latest.temperature,
        "humidity": latest.humidity,
        "battery": latest.battery,
        "timestamp": latest.timestamp
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)