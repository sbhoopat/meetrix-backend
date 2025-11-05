from fastapi import APIRouter
from select import select

from database import get_session
from models import Route
from schemas import RouteCreate, RouteRead

router = APIRouter()

@router.post("/", response_model=RouteRead)
def create_route(payload: RouteCreate):
    with get_session() as s:
        r = Route(**payload.dict())
        s.add(r); s.commit(); s.refresh(r)
        return r

@router.get("/", response_model=list[RouteRead])
def list_routes():
    with get_session() as s:
        return s.exec(select(Route)).all()
