import socketio
from fastapi import APIRouter
router = APIRouter(prefix="/api/transport/trip", tags=["Trip Tracking"])

# Initialize socket.io server
sio = socketio.AsyncServer(async_mode="asgi")
socket_app = socketio.ASGIApp(sio)

# In-memory storage for tracking bus locations (for simplicity)
bus_locations = {}

# Handle mobile location updates from frontend (driver's device)
@sio.event
async def mobile_location_update(sid, data):
    # data contains lat, lng, and potentially bus_id
    print(f"Received location from mobile: {data}")

    bus_id = data.get("bus_id")
    lat = data.get("lat")
    lng = data.get("lng")

    # Store or update the bus's location
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