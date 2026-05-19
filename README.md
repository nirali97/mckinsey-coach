McKinsey Interview Coach (AI Mock Interview System)
Overview:

The McKinsey Interview Coach is a structured mock interview simulation platform designed to replicate consulting-style interview environments with real-time evaluation and feedback.

The project was independently developed out of a personal need to practice case and behavioral interviews in a more realistic, feedback-driven format. Traditional preparation methods tend to be static and passive; this system was built to introduce an interactive loop where structured thinking, communication clarity, and business reasoning are continuously assessed and improved.

The objective is to approximate the pressure and structure of real consulting interviews while providing actionable, criterion-based feedback after every response.

Key Features:
Simulated consulting interview sessions (case / fit / mixed formats)
Real-time evaluation of user responses
Structured scoring across:
Answer structure
Clarity of communication
Business acumen
Professional tone
Dynamic follow-up question generation
Session-based progression with performance tracking
Lightweight mock AI engine (no external API dependency)

Evaluation Philosophy:
The system is designed around core consulting evaluation principles:
Structured thinking over unorganized reasoning
Clarity and precision over verbosity
Use of examples and logical connectors
MECE-style breakdown of ideas where applicable
Continuous iterative improvement through feedback loops

The goal is not only practice, but measurable improvement across successive interview attempts.

Tech Stack:
Frontend: React (Vite)
Backend: FastAPI (Python)
State Management: Local React state
AI Layer: Rule-based evaluation engine (custom mock logic)
Networking: REST APIs with CORS-enabled backend

Project Structure:
backend/   → FastAPI server handling interview logic  
frontend/  → React UI for interview interaction  
venv/      → Python virtual environment (ignored)  
node_modules/ → Frontend dependencies (ignored)

How It Works:
User selects interview type (case / fit / mixed)
Backend generates an initial question
User submits response
Backend evaluates response using structured heuristics
System returns:
Score breakdown
Qualitative feedback
Next interview question
Process repeats iteratively

Motivation:
This project was created as a personal tool to strengthen consulting interview preparation through active simulation rather than passive study. It also serves as an exploration into lightweight AI-driven evaluation systems that do not rely on external LLM APIs.

Future Improvements:
Integration with LLM APIs for more advanced evaluation
Voice-based interview simulation
Adaptive difficulty progression
Interview performance analytics dashboard
Real-world case dataset expansion

Author:
Built as an independent project focused on improving structured thinking and interview readiness for consulting roles.