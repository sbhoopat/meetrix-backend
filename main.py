
import socketio
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from routers import finance, routes, chat, drivers, analytics, alerts, students, transport_parent, \
    payment, trip_tracking, osrm_route

# Initialize FastAPI app
app = FastAPI()
router = APIRouter(prefix="/api/transport/trip", tags=["Trip Tracking"])
# Include all routers (if you have other API routes)
app.include_router(router)
app.include_router(finance.router)
app.include_router(routes.router)
app.include_router(drivers.router)
app.include_router(chat.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(students.router)
# app.include_router(trip_tracking.router)
app.include_router(transport_parent.router)
app.include_router(payment.router)
app.include_router(osrm_route.router)
# ===================== SOCKET.IO SERVER =====================
# Initialize socket.io server with CORS configuration for WebSocket
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",  # Allow only the frontend to connect
)


# Mount the Socket.IO app for handling WebSocket connections
# app.mount("/socket.io", socket_app)

# ===================== CORS SETUP =====================
# Enable CORS for HTTP APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Only allow requests from your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
socket_app = socketio.ASGIApp(sio,other_asgi_app=app)



# In-memory storage for tracking bus locations (for simplicity)
bus_locations = {}
scheduler = BackgroundScheduler()
scheduler.configure({'apscheduler.daemon': False})
scheduler.configure({'apscheduler.daemonic': False})
scheduler.start()

# Handle mobile location updates from frontend (driver's device)
@sio.event
async def mobile_location_update(sid, data):
    print(f"Received location from mobile: {data}")  # Debugging log

    # Check if data contains the expected fields
    if not data.get("bus_id") or not data.get("lat") or not data.get("lng"):
        print("Error: Invalid location data received.")
        return

    bus_id = data.get("bus_id")
    lat = data.get("lat") +1
    lng = data.get("lng") +1

    # Store or update the bus's location in-memory
    bus_locations[bus_id] = {"lat": lat, "lng": lng}

    # Broadcast the updated location to all connected clients (e.g., admin dashboard)
    await sio.emit("mobile_location_update", data)


# Notify when a bus starts the trip
@router.post("/notify_start")
async def notify_trip_start(bus_id: str):
    # Notify all clients when a bus starts its trip
    await sio.emit("trip_started", {"bus_id": bus_id, "message": "Trip has started!"})
    return {"status": "success", "message": f"Bus {bus_id} has started the trip."}

# Handle disconnects (optional cleanup)
@sio.event
async def disconnect(sid):
    print(f"Device disconnected: {sid}")
    # Remove bus from in-memory storage
    bus_locations.pop(sid, None)
# ===================== START SERVER =====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=5000)
