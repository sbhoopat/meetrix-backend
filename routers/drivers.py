from fastapi import APIRouter, HTTPException
from database import get_session
from models import Driver
from schemas import DriverCreate, DriverRead

router = APIRouter()

@router.post("/", response_model=DriverRead)
def create_driver(payload: DriverCreate):
    with get_session() as s:
        d = Driver(**payload.dict())
        s.add(d); s.commit(); s.refresh(d)
        return d

@router.get("/", response_model=list[DriverRead])
def list_drivers():
    with get_session() as s:
        return s.exec(select(Driver)).all()
