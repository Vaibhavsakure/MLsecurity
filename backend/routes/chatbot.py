"""
AI chatbot proxy — supports Groq (primary) and Gemini (fallback).
Keeps all API keys server-side. Frontend calls /api/chat.
"""
import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api", tags=["chatbot"])

SYSTEM_PROMPT = (
    "You are SocialGuard AI Assistant — a friendly, expert AI built into the SocialGuard AI platform. "
    "SocialGuard AI detects fake accounts, bots, and spam profiles across 6 social media platforms: "
    "Instagram, Twitter, Reddit, Facebook, LinkedIn, and YouTube.\n\n"
    "Your role:\n"
    "- Help users understand their analysis results\n"
    "- Explain what SHAP values mean in simple terms\n"
    "- Provide tips on identifying fake accounts manually\n"
    "- Answer questions about social media safety\n"
    "- Explain how machine learning models detect fake accounts\n\n"
    "Keep responses concise (2-4 sentences max). Use emojis sparingly for friendliness.\n"
    "If asked about something unrelated to social media security, politely redirect."
)


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    text: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


# ---------------------------------------------------------------------------
# Groq API (primary — fast, generous free tier)
# ---------------------------------------------------------------------------
async def _call_groq(messages: list[dict]) -> str | None:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None

    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        role = "assistant" if msg["role"] == "assistant" else "user"
        groq_messages.append({"role": role, "content": msg["text"]})

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": groq_messages,
                    "max_tokens": 300,
                    "temperature": 0.7,
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )

        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        else:
            return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Gemini API (fallback)
# ---------------------------------------------------------------------------
async def _call_gemini(messages: list[dict]) -> str | None:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None

    contents = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "Understood! I'm ready to help."}]},
    ]
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["text"]}]})

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.0-flash:generateContent?key={api_key}",
                json={"contents": contents},
                headers={"Content-Type": "application/json"},
            )

        if resp.status_code == 200:
            data = resp.json()
            return (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text")
            )
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Chat Endpoint — tries Groq first, then Gemini, then fallback
# ---------------------------------------------------------------------------
@router.post("/chat")
async def chat_proxy(req: ChatRequest):
    """Proxy chat to Groq (primary) or Gemini (fallback)."""
    messages = [{"role": m.role, "text": m.text} for m in req.messages]

    # Try Groq first (fast, generous free tier)
    reply = await _call_groq(messages)
    if reply:
        return {"reply": reply}

    # Fallback to Gemini
    reply = await _call_gemini(messages)
    if reply:
        return {"reply": reply}

    # Both failed — return helpful fallback
    return {
        "reply": (
            "I'm temporarily unavailable — both AI providers are currently "
            "rate-limited or not configured. Please try again in a minute! "
            "In the meantime, check the SHAP chart in your analysis results "
            "for feature importance insights."
        )
    }
