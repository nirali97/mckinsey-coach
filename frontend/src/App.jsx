import { useState, useRef, useEffect } from "react"
import axios from "axios"

const API = "https://case-interview-coach.onrender.com"

function ScoreBar({ label, score }) {
  const color = score >= 8 ? "#16a34a" : score >= 5 ? "#d97706" : "#dc2626"
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 3 }}>
        <span>{label}</span><span style={{ color, fontWeight: 600 }}>{score}/10</span>
      </div>
      <div style={{ background: "#e5e7eb", borderRadius: 4, height: 6 }}>
        <div style={{ width: `${score * 10}%`, background: color, height: 6, borderRadius: 4, transition: "width 0.4s" }} />
      </div>
    </div>
  )
}

function FeedbackCard({ assessment }) {
  if (!assessment) return null
  const overall = assessment.score
  const color = overall >= 8 ? "#16a34a" : overall >= 5 ? "#d97706" : "#dc2626"
  return (
    <div style={{ background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: 10, padding: 16, margin: "12px 0" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <span style={{ fontWeight: 600, fontSize: 13 }}>Assessment</span>
        <span style={{ background: color, color: "white", borderRadius: 20, padding: "2px 12px", fontSize: 13, fontWeight: 600 }}>{overall}/10</span>
      </div>
      <ScoreBar label="Structure" score={assessment.structure} />
      <ScoreBar label="Clarity" score={assessment.clarity} />
      <ScoreBar label="Business Acumen" score={assessment.business_acumen} />
      <ScoreBar label="Professionalism" score={assessment.professionalism} />
      <ScoreBar label="Quantitative Rigor" score={assessment.quantitative_rigor} />
      <ScoreBar label="Hypothesis Driven" score={assessment.hypothesis_driven} />
      <ScoreBar label="Communication" score={assessment.communication} />
      <div style={{ marginTop: 12, padding: "10px 12px", background: "#fef3c7", borderLeft: "3px solid #f59e0b", borderRadius: "0 6px 6px 0", fontSize: 13, lineHeight: 1.5 }}>
        <strong>Partner feedback:</strong> {assessment.feedback}
      </div>
      <div style={{ marginTop: 8, padding: "10px 12px", background: "#ecfdf5", borderLeft: "3px solid #10b981", borderRadius: "0 6px 6px 0", fontSize: 13, lineHeight: 1.5 }}>
        <strong>What good looks like:</strong> {assessment.what_good_looks_like}
      </div>
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [history, setHistory] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [sessionType, setSessionType] = useState("case")
  const [scores, setScores] = useState([])
  const bottomRef = useRef()

  useEffect(() => { startSession() }, [])
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }) }, [messages])

  async function startSession() {
    setMessages([])
    setHistory([])
    setScores([])
    setLoading(true)
    const seed = [{ role: "user", content: `Start a fresh ${sessionType} interview session. Ask me a completely new and different opening question. Be creative and vary the topic.` }]
    try {
      const res = await axios.post(`${API}/chat`, { history: seed, session_type: sessionType })
      const question = res.data.next_question
      setHistory([...seed, { role: "assistant", content: JSON.stringify(res.data) }])
      setMessages([{ type: "interviewer", text: question }])
    } catch (e) {
      setMessages([{ type: "error", text: "Could not connect. Is your backend running?" }])
    }
    setLoading(false)
  }

  async function send() {
    if (!input.trim() || loading) return
    const userText = input.trim()
    setInput("")
    const newHistory = [...history, { role: "user", content: userText }]
    setMessages(prev => [...prev, { type: "user", text: userText }])
    setLoading(true)
    try {
      const res = await axios.post(`${API}/chat`, { history: newHistory, session_type: sessionType })
      const { assessment, next_question } = res.data
      setHistory([...newHistory, { role: "assistant", content: JSON.stringify(res.data) }])
      if (assessment) setScores(prev => [...prev, assessment.score])
      setMessages(prev => [...prev, { type: "feedback", assessment }, { type: "interviewer", text: next_question }])
    } catch (e) {
      setMessages(prev => [...prev, { type: "error", text: "Something went wrong. Try again." }])
    }
    setLoading(false)
  }

  const avg = scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : "—"

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "24px 16px", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Case Interview Coach</h1>
        <p style={{ color: "#6b7280", fontSize: 14, marginTop: 4 }}>Answers assessed on 7 dimensions including quantitative rigor and hypothesis-driven thinking.</p>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16, alignItems: "center", flexWrap: "wrap" }}>
        {["case", "fit", "mixed"].map(t => (
          <button key={t} onClick={() => { setSessionType(t); setTimeout(startSession, 0) }}
            style={{ padding: "5px 14px", borderRadius: 20, border: "1px solid #d1d5db", cursor: "pointer",
              background: sessionType === t ? "#1d4ed8" : "white",
              color: sessionType === t ? "white" : "#374151", fontSize: 13 }}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
        <button onClick={startSession} style={{ marginLeft: "auto", padding: "5px 14px", borderRadius: 20,
          border: "1px solid #d1d5db", cursor: "pointer", fontSize: 13, background: "white" }}>
          New session
        </button>
        <span style={{ fontSize: 13, color: "#6b7280" }}>Avg: <strong>{avg}</strong></span>
      </div>

      <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, minHeight: 400, maxHeight: 520, overflowY: "auto", marginBottom: 12 }}>
        {messages.map((m, i) => (
          <div key={i}>
            {m.type === "interviewer" && (
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: "#9ca3af", marginBottom: 4 }}>Interviewer</div>
                <div style={{ background: "#f3f4f6", borderRadius: "0 10px 10px 10px", padding: "10px 14px", fontSize: 14, lineHeight: 1.6, display: "inline-block", maxWidth: "85%" }}>{m.text}</div>
              </div>
            )}
            {m.type === "user" && (
              <div style={{ textAlign: "right", marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: "#9ca3af", marginBottom: 4 }}>You</div>
                <div style={{ background: "#dbeafe", borderRadius: "10px 0 10px 10px", padding: "10px 14px", fontSize: 14, lineHeight: 1.6, display: "inline-block", maxWidth: "85%", textAlign: "left" }}>{m.text}</div>
              </div>
            )}
            {m.type === "feedback" && <FeedbackCard assessment={m.assessment} />}
            {m.type === "error" && (
              <div style={{ color: "#dc2626", fontSize: 13, padding: "8px 12px", background: "#fee2e2", borderRadius: 8, marginBottom: 12 }}>{m.text}</div>
            )}
          </div>
        ))}
        {loading && (
          <div style={{ color: "#9ca3af", fontSize: 13, padding: "8px 0" }}>Interviewer is thinking...</div>
        )}
        <div ref={bottomRef} />
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <textarea value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send() } }}
          placeholder="Type your answer... (Enter to send, Shift+Enter for new line)"
          style={{ flex: 1, padding: "10px 14px", borderRadius: 10, border: "1px solid #d1d5db",
            fontSize: 14, resize: "none", height: 80, fontFamily: "inherit", outline: "none" }} />
        <button onClick={send} disabled={loading}
          style={{ padding: "0 20px", borderRadius: 10, background: "#1d4ed8", color: "white",
            border: "none", cursor: loading ? "not-allowed" : "pointer", fontSize: 14, fontWeight: 600, opacity: loading ? 0.6 : 1 }}>
          Send
        </button>
      </div>
    </div>
  )
}