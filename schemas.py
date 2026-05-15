from pydantic import BaseModel, EmailStr # type: ignore
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class DeviceCreate(BaseModel):
    device_id: str
    name: str
    location: Optional[str] = None
    device_type: str = "ESP8266"

class DeviceResponse(BaseModel):
    id: int
    device_id: str
    name: str
    location: Optional[str] = None
    device_type: str
    status: str
    last_seen: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

class TelemetryCreate(BaseModel):
    temperature: float
    humidity: float
    battery: Optional[int] = 100

class TelemetryResponse(BaseModel):
    id: int
    device_id: int
    temperature: float
    humidity: float
    battery: int
    timestamp: datetime

    class Config:
        from_attributes = True