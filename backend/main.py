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

Conversation so far:
{history_text}

Respond ONLY with valid JSON, no extra text, no markdown:
{{
  "assessment": {{
    "score": 7,
    "structure": 7,
    "clarity": 7,
    "business_acumen": 7,
    "professionalism": 7,
    "feedback": "your feedback here",
    "what_good_looks_like": "example here"
  }},
  "next_question": "your next question here"
}}

If no user answer yet, set assessment to null and just ask an opening question."""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
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