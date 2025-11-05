from pydantic import BaseModel
from typing import Optional, List

class DriverCreate(BaseModel):
    name: str
    phone: Optional[str]
    license_number: Optional[str]
    license_expiry: Optional[str]
    training_records: Optional[str]

class DriverRead(DriverCreate):
    id: int
    behavior_score: Optional[float] = 0.0

class StudentCreate(BaseModel):
    name: str
    roll_no: Optional[str]
    parent_contact: Optional[str]
    route_id: Optional[int]
    rfid_tag: Optional[str]
    face_model_ref: Optional[str]

class StudentRead(StudentCreate):
    id: int

class RouteCreate(BaseModel):
    name: str
    stops: Optional[str]
    assigned_vehicle_id: Optional[int]
    assigned_driver_id: Optional[int]

class RouteRead(RouteCreate):
    id: int

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    reply: str
    raw: Optional[dict] = None
