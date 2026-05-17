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
    api_key = os.getenv("GROQ_API_KEY")
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in req.history])

    prompt = f"""You are a strict McKinsey partner conducting a {req.session_type} interview.

IMPORTANT: Ask varied questions across different industries and topics. Do NOT repeat similar questions. Mix between:
- Profitability cases (declining margins, cost reduction)
- Market entry cases (new products, new geographies)
- Market sizing (estimate X in country Y)
- M&A cases (should client acquire company X)
- Operations cases (supply chain, efficiency)
- Fit questions (leadership, failure, teamwork)

Conversation so far:
{history_text}

Respond ONLY with valid JSON, no extra text, no markdown:
{{
  "assessment": {{
    "score": 1,
    "structure": 1,
    "clarity": 1,
    "business_acumen": 1,
    "professionalism": 1,
    "feedback": "your feedback here",
    "what_good_looks_like": "example here"
  }},
  "next_question": "your next question here"
}}

If no user answer yet, set assessment to null and ask a random opening case question from a random industry."""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9
            },
            timeout=30
        )

    resp_json = response.json()
    print("Groq response:", resp_json)

    try:
        text = resp_json["choices"][0]["message"]["content"]
        text = text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
    except Exception as e:
        print("Error:", e)
        data = {"assessment": None, "next_question": "Tell me about a time you solved a complex business problem."}

    return data