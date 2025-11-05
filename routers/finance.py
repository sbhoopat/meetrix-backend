
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Expense(BaseModel):
    vehicleNumber: str
    category: str
    amount: float
    date: str
    notes: str | None = None

# 🧾 Mock data for testing (pre-filled)
expenses = [
    Expense(
        vehicleNumber="TS09AB1234",
        category="Fuel",
        amount=4200.50,
        date="2025-11-01",
        notes="Diesel refill - 60L"
    ),
    Expense(
        vehicleNumber="TS09AB5678",
        category="Maintenance",
        amount=8500.00,
        date="2025-10-28",
        notes="Brake pad and oil change"
    ),
    Expense(
        vehicleNumber="TS09AB7890",
        category="Tyres",
        amount=12500.00,
        date="2025-10-20",
        notes="Replaced 2 rear tyres"
    ),
    Expense(
        vehicleNumber="TS09AB1234",
        category="Insurance",
        amount=18000.00,
        date="2025-09-15",
        notes="Annual insurance renewal"
    ),
    Expense(
        vehicleNumber="TS09AB5678",
        category="Other",
        amount=1500.00,
        date="2025-11-02",
        notes="Driver uniform and cleaning supplies"
    ),
    Expense(
        vehicleNumber="TS09AB9876",
        category="Fuel",
        amount=3900.00,
        date="2025-11-03",
        notes="Diesel refill - 55L"
    ),
]

@router.get("/api/transport/finance")
def get_expenses() -> List[Expense]:
    """Return all mock transport expenses."""
    return expenses

@router.post("/api/transport/finance/add")
def add_expense(exp: Expense):
    """Add a new expense record."""
    expenses.append(exp)
    return {"message": "Expense added successfully", "data": exp}
