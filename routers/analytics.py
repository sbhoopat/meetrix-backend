from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/lead-summary")
def lead_summary():
    # placeholder sample summary
    return {"total_routes": 12, "on_time_pct": 92, "avg_delay_min": 6}
