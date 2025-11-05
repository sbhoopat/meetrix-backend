from sqlmodel import SQLModel, create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./transport.db")
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

def init_db():
    from models import Driver, Student, Route, Lead, Alert, Vehicle
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
