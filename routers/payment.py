# routers/payment.py
import os
import hmac
import hashlib
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RZP_WEBHOOK_SECRET = os.getenv("RZP_WEBHOOK_SECRET", "")

if not (RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET):
    raise RuntimeError("RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET must be set in env")

import razorpay
rzp_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

router = APIRouter(prefix="/api/transport", tags=["transport-payments"])

# request body when frontend asks to create an order
class CreateOrderRequest(BaseModel):
    studentId: str
    planAmount: float  # INR rupees (frontend will pass)
    currency: str = "INR"
    receipt: str = None  # optional

# frontend will call this to create order
@router.post("/opt/{studentId}")
def create_order(studentId: str, body: CreateOrderRequest):
    # compute amount in paise (Razorpay uses smallest currency unit)
    amount_paise = int(round(body.planAmount * 100))
    receipt_id = body.receipt or f"transport_{studentId}_{os.urandom(4).hex()}"

    order_data = {
        "amount": amount_paise,
        "currency": body.currency,
        "receipt": receipt_id,
        "notes": {
            "studentId": studentId,
            "purpose": "Transport Plan Opt-in",
        },
    }
    try:
        order = rzp_client.order.create(data=order_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Razorpay order creation failed: {e}")

    # Return order details to frontend
    return {
        "success": True,
        "order": {
            "id": order.get("id"),
            "amount": order.get("amount"),
            "currency": order.get("currency"),
            "receipt": order.get("receipt"),
        },
        "razorpayKeyId": RAZORPAY_KEY_ID,
    }

# frontend POSTs payment success payload to verify
class VerifyPayload(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str
    studentId: str
    planAmount: float

@router.post("/verify_payment")
def verify_payment(payload: VerifyPayload):
    # Verify signature per Razorpay docs
    generated_signature = hmac.new(
        bytes(RAZORPAY_KEY_SECRET, "utf-8"),
        msg=bytes(f"{payload.razorpay_order_id}|{payload.razorpay_payment_id}", "utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if generated_signature != payload.razorpay_signature:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    # At this point payment is verified. Persist in DB:
    # - mark student as opted (isOpted=True)
    # - store payment record: payment id, order id, amount, method, timestamp
    # For demo, return success
    # TODO: replace with actual DB save logic

    return {"success": True, "message": "Payment verified and opt-in completed"}

# Razorpay webhook receiver (optional): verify header and signature
@router.post("/webhook")
async def rzp_webhook(request: Request, x_razorpay_signature: str = Header(None)):
    body = await request.body()
    # verify signature
    if not RZP_WEBHOOK_SECRET:
        return {"received": True, "warning": "No webhook secret configured; skipping verify"}

    generated = hmac.new(
        bytes(RZP_WEBHOOK_SECRET, "utf-8"),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()

    if generated != x_razorpay_signature:
        raise HTTPException(status_code=400, detail="Webhook signature mismatch")

    # process webhook JSON
    event = await request.json()
    # example: handle payment.captured event
    # TODO: process event -> update DB
    return {"received": True, "event": event.get("event")}
