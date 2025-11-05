# routes/ai_chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ai import call_llm_for_chat, CHAT_PROMPT

router = APIRouter(prefix="/api/ai", tags=["AI"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = ""

class ChatResponse(BaseModel):
    reply: str
    raw: Optional[Dict[str, Any]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Handles AI chat requests for Transport Management System.
    Uses Groq (or mock) backend defined in ai.py.
    """
    # Build formatted prompt
    prompt = CHAT_PROMPT.format(context=req.context or "General Transport Context", prompt=req.message)

    # Call the AI
    result = await call_llm_for_chat(prompt)

    # Extract main reply
    reply_text = result.get("text", "[Error: No reply generated]")

    return ChatResponse(reply=reply_text, raw=result.get("raw"))
