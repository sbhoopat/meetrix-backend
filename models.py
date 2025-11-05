from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Driver(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: Optional[str]
    license_number: Optional[str]
    license_expiry: Optional[datetime]
    training_records: Optional[str]  # JSON string or text
    behavior_score: Optional[float] = 0.0

class Vehicle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reg_no: str
    capacity: Optional[int] = 0
    last_service_date: Optional[datetime]

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    roll_no: Optional[str]
    parent_contact: Optional[str]
    route_id: Optional[int] = Field(default=None, foreign_key="route.id")
    rfid_tag: Optional[str]
    face_model_ref: Optional[str]
    # attendance stored elsewhere / or aggregated

class Route(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    stops: Optional[str]  # JSON array text: [{"lat":..,"lon":..,"name":..}]
    assigned_vehicle_id: Optional[int] = Field(default=None, foreign_key="vehicle.id")
    assigned_driver_id: Optional[int] = Field(default=None, foreign_key="driver.id")
    estimated_time_min: Optional[int]
    active: bool = True

class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    alert_type: str
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    meta_info: Optional[str]

# Simple lead example for CRM-like functionality
class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    contact: Optional[str]
    requirements: Optional[str]
    budget: Optional[float]
    preferred_location: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
