from fastapi import APIRouter
from twilio.rest import Client

router = APIRouter(prefix="/api/transport/trip", tags=["Trip Tracking"])

# --- Twilio setup ---
ACCOUNT_SID = "your_twilio_sid"
AUTH_TOKEN = "your_twilio_auth"
FROM_WHATSAPP = "whatsapp:+14155238886"  # Twilio sandbox number
TO_WHATSAPP = "whatsapp:+919951924933"   # Parent/student number

@router.post("/notify_start")
async def notify_trip_start():
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        from_=FROM_WHATSAPP,
        to=TO_WHATSAPP,
        body="🚌 The school bus has started its route. Please have your ward ready!"
    )
    return {"status": "sent", "sid": message.sid}
