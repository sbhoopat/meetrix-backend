# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn
import asyncio
import random
from routers import finance, routes, drivers, chat, analytics, alerts, students, trip_tracking, transport_parent, \
    payment
from twilio.rest import Client
import os

# ===================== FASTAPI SETUP =====================
app = FastAPI(title="Transport Management System")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(finance.router)
app.include_router(routes.router)
app.include_router(drivers.router)
app.include_router(chat.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(students.router)
app.include_router(trip_tracking.router)
app.include_router(transport_parent.router)
app.include_router(payment.router)

# ===================== SOCKET.IO SETUP =====================
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Active bus tracking store
active_buses = {}

@sio.event
async def connect(sid, environ):
    print(f"✅ Client connected: {sid}")
    await sio.emit("connection_ack", {"status": "connected"})

@sio.event
async def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")

@sio.event
async def update_bus(sid, data):
    """
    Receives live bus updates from driver app or GPS module
    Example data:
    {
        "id": "BUS101",
        "lat": 17.392,
        "lng": 78.496,
        "speed": 40,
        "delay": 2
    }
    """
    active_buses[data["id"]] = data
    print(f"📡 Bus update from {data['id']}: {data}")
    await sio.emit("bus_update", data)

@app.get("/api/buses")
async def get_buses():
    """Fetch all live buses (for debug/UI)"""
    return list(active_buses.values())

# ===================== WHATSAPP ALERT =====================
# Twilio configuration (set these as environment variables)
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP = "whatsapp:+14155238886"  # Twilio sandbox number

if TWILIO_SID and TWILIO_TOKEN:
    twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
else:
    twilio_client = None
    print("⚠️ Twilio not configured. WhatsApp alerts disabled.")

async def send_whatsapp_alert(bus_id: str, parent_numbers: list[str]):
    """Send WhatsApp alert to parents when bus starts."""
    if not twilio_client:
        print("⚠️ WhatsApp alert skipped: Twilio not configured.")
        return

    for num in parent_numbers:
        try:
            twilio_client.messages.create(
                from_=TWILIO_WHATSAPP,
                body=f"🚍 Your ward's bus ({bus_id}) has started from school. Please be ready!",
                to=f"whatsapp:{num}"
            )
            print(f"✅ WhatsApp alert sent to {num}")
        except Exception as e:
            print(f"❌ Failed to send WhatsApp alert to {num}: {e}")

# ===================== TRIP START ENDPOINT =====================
from fastapi import Body

@app.post("/api/trip/start")
async def start_trip(
        bus_id: str = Body(...),
        parent_numbers: list[str] = Body(...)
):
    """
    Triggered when the bus starts from school.
    Sends WhatsApp alerts to assigned parents.
    """
    asyncio.create_task(send_whatsapp_alert(bus_id, parent_numbers))
    print(f"🚍 Trip started for {bus_id}, alerts sent to {len(parent_numbers)} parents")
    return {"status": "started", "bus_id": bus_id, "recipients": len(parent_numbers)}

# ===================== TEST BUS MOVEMENT SIMULATION =====================
async def broadcast_bus_updates():
    """Simulate random bus updates (for dev testing)."""
    while True:
        await sio.emit("bus_update", {
            "id": "BUS101",
            "lat": 17.421 + random.uniform(-0.005, 0.005),
            "lng": 78.469 + random.uniform(-0.005, 0.005),
            "speed": random.randint(30, 80),
            "delay": random.randint(0, 5),
        })
        await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_bus_updates())
    print("🚀 Transport backend started with Socket.IO broadcasting")

# ===================== RUN SERVER =====================
if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=5000)
