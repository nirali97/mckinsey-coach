from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# REQUEST MODEL (IMPORTANT)
# -----------------------------
class ChatRequest(BaseModel):
    history: List[Dict[str, str]]
    session_type: str

# -----------------------------
# HEALTH
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# MOCK CASE QUESTIONS
# -----------------------------
CASE_QUESTIONS = [
    "A client’s profits are declining despite rising revenue. What would you do?",
    "How would you estimate the size of the ride-sharing market in India?",
    "A retail chain is losing customers. What could be the reasons?",
]

FIT_QUESTIONS = [
    "Tell me about a time you showed leadership.",
    "Why do you want to join consulting?",
    "Describe a failure and what you learned.",
]

# -----------------------------
# SIMPLE SCORING ENGINE
# -----------------------------
def score_answer(answer: str):
    text = answer.lower()
    words = len(answer.split())

    structure = 7 if any(w in text for w in ["first", "second", "because", "therefore"]) else 4
    clarity = 8 if words > 60 else 5
    business = 7 if any(w in text for w in ["market", "customer", "revenue", "cost"]) else 5
    professionalism = 8 if "like" not in text else 6

    overall = int((structure + clarity + business + professionalism) / 4)

    return {
        "structure": structure,
        "clarity": clarity,
        "business_acumen": business,
        "professionalism": professionalism,
        "score": overall,
        "feedback": "Good structure, but sharpen your reasoning and be more MECE.",
        "what_good_looks_like": "Use: Framework → Drivers → Evidence → Recommendation"
    }

# -----------------------------
# MAIN CHAT LOGIC
# -----------------------------
@app.post("/chat")
def chat(req: ChatRequest):

    last_user = ""
    for msg in reversed(req.history):
        if msg["role"] == "user":
            last_user = msg["content"]
            break

    # pick question
    if req.session_type == "fit":
        next_q = random.choice(FIT_QUESTIONS)
    else:
        next_q = random.choice(CASE_QUESTIONS)

    assessment = score_answer(last_user) if last_user else None

    return {
        "assessment": assessment,
        "next_question": next_q
    }