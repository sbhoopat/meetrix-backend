# backend/routes/osrm_route.py
from fastapi import APIRouter, Query
import httpx

router = APIRouter(prefix="/api/osrm", tags=["OSRM Routing"])

OSRM_BASE_URL = "https://router.project-osrm.org"

@router.get("/route")
async def get_route(
        start_lat: float = Query(...),
        start_lng: float = Query(...),
        end_lat: float = Query(...),
        end_lng: float = Query(...),
):
    """
    Get route between two coordinates using OSRM (public server).
    """
    try:
        url = (
            f"{OSRM_BASE_URL}/route/v1/driving/"
            f"{start_lng},{start_lat};{end_lng},{end_lat}"
            f"?overview=full&geometries=geojson"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        if data.get("code") != "Ok":
            return {"error": "OSRM failed", "details": data}

        route = data["routes"][0]
        return {
            "distance_km": round(route["distance"] / 1000, 2),
            "duration_min": round(route["duration"] / 60, 2),
            "geometry": route["geometry"],
        }

    except Exception as e:
        return {"error": str(e)}
