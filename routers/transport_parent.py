from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/api/transport/parent", tags=["Parent Tracking"])

# --- Mock database ---
STUDENTS = {
    "STU12345": {
        "id": "STU12345",
        "name": "Aarav Reddy",
        "grade": "7A",
        "route": {
            "source": "NIT Main Campus",
            "destination": "Madhapur",
        },
        "bus_id": "BUS_27"
    },
    "STU56789": {
        "id": "STU56789",
        "name": "Sneha Sharma",
        "grade": "5B",
        "route": {
            "source": "NIT Main Campus",
            "destination": "Gachibowli",
        },
        "bus_id": "BUS_12"
    }
}

BUSES = {
    "BUS_27": {
        "busNumber": "B-27",
        "model": "Tata Starbus 24 Seater",
        "location": {"lat": 17.448, "lng": 78.391},
        "speed": 40,
        "driver": {"name": "Ramesh Kumar", "phone": "+91-9876543210"},
    },
    "BUS_12": {
        "busNumber": "B-12",
        "model": "Eicher School Bus",
        "location": {"lat": 17.432, "lng": 78.356},
        "speed": 38,
        "driver": {"name": "Anil Verma", "phone": "+91-9988776655"},
    },
}


@router.get("/tracking/{student_id}")
async def get_tracking_info(student_id: str):
    """Return live tracking data for a given student."""
    student = STUDENTS.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    bus = BUSES.get(student["bus_id"])
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    # Simulate dynamic location drift and ETA calculation
    lat_offset = random.uniform(-0.002, 0.002)
    lng_offset = random.uniform(-0.002, 0.002)
    current_location = {
        "lat": bus["location"]["lat"] + lat_offset,
        "lng": bus["location"]["lng"] + lng_offset,
    }

    # Random ETA simulation (10–25 min)
    eta = random.randint(10, 25)
    status = random.choice(["On Time", "Delayed", "Arrived"])

    return {
        "student": {
            "id": student["id"],
            "name": student["name"],
            "grade": student["grade"],
        },
        "bus": {
            "busNumber": bus["busNumber"],
            "model": bus["model"],
            "location": current_location,
            "speed": bus["speed"],
        },
        "driver": bus["driver"],
        "route": student["route"],
        "status": status,
        "eta": eta,
        "timestamp": datetime.utcnow().isoformat(),
    }
