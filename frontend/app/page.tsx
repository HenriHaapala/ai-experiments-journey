"use client";

import Link from "next/link";
import { useEffect, useState, FormEvent } from "react";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export default function Homepage() {
  const [backendStatus, setBackendStatus] = useState<string>("checking…");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/health/`
        );
        if (!res.ok) throw new Error("Bad response");
        const data = await res.json();
        setBackendStatus(data.status || "ok");
      } catch (e) {
        setBackendStatus("error");
      }
    };
    checkHealth();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage: ChatMessage = { role: "user", content: question };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/ai/chat/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ question }),
        }
      );

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.answer,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setQuestion("");
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to get AI response");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Henri – AI Portfolio</h1>
      <p>Backend health: {backendStatus}</p>

      <nav style={{ marginTop: "1.5rem", marginBottom: "2rem" }}>
        <ul>
          <li>
            <Link href="/roadmap">View AI Roadmap</Link>
          </li>
          <li>
            <Link href="/learning">View Learning Log</Link>
          </li>
        </ul>
      </nav>

      <section
        style={{
          border: "1px solid #333",
          borderRadius: "8px",
          padding: "1rem",
          maxWidth: "700px",
        }}
      >
        <h2>Ask my AI about my journey</h2>
        <form onSubmit={handleSubmit} style={{ marginBottom: "1rem" }}>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            style={{ width: "100%", marginBottom: "0.5rem" }}
            placeholder="Ask something like: What has Henri done so far on RAG? What kind of employee is Henri? etc."
          />
          <button type="submit" disabled={loading}>
            {loading ? "Thinking..." : "Ask"}
          </button>
        </form>

        {error && <p style={{ color: "red" }}>{error}</p>}

        <div>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                marginBottom: "0.75rem",
                textAlign: msg.role === "user" ? "right" : "left",
              }}
            >
              <div
                style={{
                  display: "inline-block",
                  padding: "0.5rem 0.75rem",
                  borderRadius: "8px",
                  background:
                    msg.role === "user" ? "#444" : "rgba(255, 255, 255, 0.05)",
                }}
              >
                <strong>
                  {msg.role === "user" ? "You: " : "AI: "}
                </strong>
                <span>{msg.content}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
