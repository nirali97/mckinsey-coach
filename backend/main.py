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

    prompt = f"""You are an extremely strict and demanding McKinsey senior partner conducting a high-stakes consulting interview. You have zero tolerance for vague, unstructured, or incomplete answers. You expect MBA-level rigor.

IMPORTANT: Ask varied questions across different industries. Mix between profitability, market entry, market sizing, M&A, operations, and fit cases.

Conversation so far:
{history_text}

Evaluate the candidate on these 7 dimensions (score 1-10, be HARSH and realistic):
- structure: Did they use a clear framework? MECE thinking?
- clarity: Was the answer precise and concise?
- business_acumen: Did they show real business insight?
- professionalism: Was the language formal and polished?
- quantitative_rigor: Did they use numbers, estimates, data?
- hypothesis_driven: Did they lead with a hypothesis?
- communication: Was it structured like a real consultant would present?

Respond ONLY with valid JSON, no extra text, no markdown:
{{
  "assessment": {{
    "score": 1,
    "structure": 1,
    "clarity": 1,
    "business_acumen": 1,
    "professionalism": 1,
    "quantitative_rigor": 1,
    "hypothesis_driven": 1,
    "communication": 1,
    "feedback": "harsh, specific feedback pointing out exactly what was wrong",
    "what_good_looks_like": "a concrete example of what an excellent answer would include"
  }},
  "next_question": "your next question here"
}}

If no user answer yet, set assessment to null and ask a random opening case question from a random industry. Be strict."""

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