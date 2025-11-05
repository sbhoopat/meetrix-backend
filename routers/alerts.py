from fastapi import APIRouter
from database import get_session
from models import Alert

router = APIRouter()

@router.get("/")
def list_alerts():
    with get_session() as s:
        return s.exec(select(Alert)).all()
