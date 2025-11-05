# ai.py (updated for Groq)
import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
USE_MOCK = os.getenv("USE_MOCK_AI", "true").lower() in ("1","true","yes")

if GROQ_API_KEY and not USE_MOCK:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None

ROUTE_OPTIMIZE_PROMPT = """
You are an optimization assistant. Given stops and vehicles, produce an optimized assignment ...
Input JSON:
{input_json}
Output JSON: {{ "routes": [...], "estimatedTotalMinutes": <number> }}
"""

CHAT_PROMPT = """
You are a helpful assistant for the Transport Management System.
Context:
{context}
User question:
{prompt}
Respond:
"""

async def call_llm_for_chat(prompt: str, max_tokens: int = 200) -> Dict[str, Any]:
    if USE_MOCK or not groq_client:
        return {"text": f"[MOCK] Echo: {prompt}", "raw": {"mock": True}}

    # Call Groq chat completions
    resp = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    text = resp.choices[0].message.content
    return {"text": text, "raw": resp}

async def optimize_route_via_ai(stops: List[Dict[str, Any]], vehicles: List[Dict[str, Any]] = None, liveTraffic: Dict[str, Any] = None) -> Dict[str, Any]:
    input_payload = {"stops": stops, "vehicles": vehicles or [], "liveTraffic": liveTraffic or {}}
    prompt = ROUTE_OPTIMIZE_PROMPT.replace("{input_json}", json.dumps(input_payload))
    result = await call_llm_for_chat(prompt, max_tokens=800)
    text = result.get("text", "")
    try:
        parsed = json.loads(text)
    except Exception:
        parsed = {
            "routes": [
                {
                    "vehicleId": vehicles[0]["id"] if vehicles else "vehicle-1",
                    "orderedStops": [s["id"] for s in stops],
                    "etaPerStop": []
                }
            ],
            "estimatedTotalMinutes": 30
        }
    return {"parsed": parsed, "raw": result.get("raw", {}), "text": text}
