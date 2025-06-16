from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],  # Ubah ke ["http://localhost:5500"] untuk lebih aman
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
alerts_db = []

class SensorData(BaseModel):
    sensor_id: str
    location: str
    type: str
    timestamp: str
    lat: float
    lon: float
    data: Dict[str, float]

class Alert(BaseModel):
    location: str
    timestamp: str
    detected: int
    sensors: List[SensorData]

@app.post("/alert")
async def receive_alert(alert: Alert):
    alerts_db.append(alert.dict())
    print(f"[RECEIVED] 🔥 Alert dari {alert.location}")
    return {"status": "success"}

@app.get("/alerts")
async def get_alerts():
    return {"alerts": alerts_db}

@app.get("/")
async def root():
    return {"message": "Cloud Receiver is running."}
