from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    history: List[Dict[str, str]]
    session_type: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in req.history])

    prompt = f"""You are a strict McKinsey partner conducting a {req.session_type} interview.

Conversation so far:
{history_text}

Respond ONLY with valid JSON, no extra text:
{{
  "assessment": {{
    "score": <1-10>,
    "structure": <1-10>,
    "clarity": <1-10>,
    "business_acumen": <1-10>,
    "professionalism": <1-10>,
    "feedback": "<sharp specific feedback>",
    "what_good_looks_like": "<example of ideal answer>"
  }},
  "next_question": "<your next interview question>"
}}

If no user answer yet, set assessment to null and just ask an opening question."""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )

    resp_json = response.json()
    if "candidates" not in resp_json:
        print("Gemini error:", resp_json)
        return {"assessment": None, "next_question": "Tell me about a time you solved a complex business problem."}
    
    text = resp_json["candidates"][0]["content"]["parts"][0]["text"]
    text = text.strip().replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(text)
    except:
        data = {"assessment": None, "next_question": "Tell me about a time you solved a complex business problem."}

    return data