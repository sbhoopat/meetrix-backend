from fastapi import APIRouter
from database import get_session
from models import Student
from schemas import StudentCreate, StudentRead

router = APIRouter()

@router.post("/", response_model=StudentRead)
def create_student(payload: StudentCreate):
    with get_session() as s:
        st = Student(**payload.dict())
        s.add(st); s.commit(); s.refresh(st)
        return st

@router.get("/", response_model=list[StudentRead])
def list_students():
    with get_session() as s:
        return s.exec(select(Student)).all()
