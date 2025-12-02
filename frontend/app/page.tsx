"use client";

import Link from "next/link";
import { useEffect, useState, FormEvent } from "react";

type ContextChunk = {
  id: number;
  source_type: string;
  title: string;
  section_title?: string | null;
  roadmap_item_title?: string | null;
  tags?: string | null;
  document_title?: string | null;
  document_filename?: string | null;
  source_label?: string | null;
  content: string;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  confidence?: number | null;
  status?: string | null; // retrieval_debug.status
  contextUsed?: ContextChunk[];
  followUpQuestions?: string[];
};

export default function Homepage() {
  const [backendStatus, setBackendStatus] = useState<string>("checking…");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // which assistant messages have context expanded
  const [expandedContexts, setExpandedContexts] = useState<
    Record<number, boolean>
  >({});

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
          headers: { "Content-Type": "application/json" },
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
        confidence: data.confidence ?? null,
        status: data.retrieval_debug?.status ?? null,
        contextUsed: (data.context_used || []) as ContextChunk[],
        followUpQuestions: data.follow_up_questions || [],
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

  const toggleContext = (index: number) => {
    setExpandedContexts((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const handleFollowUpClick = (followUpQuestion: string) => {
    setQuestion(followUpQuestion);
    // Optionally auto-submit
    // Or let user edit before submitting
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
          {messages.map((msg, idx) => {
            const isAssistant = msg.role === "assistant";
            const isLowConfidence =
              isAssistant &&
              (msg.status === "low_confidence" ||
                msg.status === "very_low_confidence" ||
                (typeof msg.confidence === "number" &&
                  msg.confidence < 0.25));

            const hasContext =
              isAssistant && msg.contextUsed && msg.contextUsed.length > 0;
            const isExpanded = expandedContexts[idx] ?? false;

            return (
              <div
                key={idx}
                style={{
                  marginBottom: "0.75rem",
                  textAlign: msg.role === "user" ? "right" : "left",
                }}
              >
                {isAssistant && isLowConfidence && (
                  <div
                    style={{
                      display: "inline-block",
                      padding: "0.4rem 0.6rem",
                      marginBottom: "0.3rem",
                      borderRadius: "6px",
                      border: "1px solid #f2c14f",
                      backgroundColor: "#fff8e1",
                      fontSize: "0.85rem",
                      color: "#7a5b00",
                    }}
                  >
                    ⚠️ Low confidence answer — based on weak matches in your
                    notes. It may be incomplete or uncertain.
                    {typeof msg.confidence === "number" && (
                      <span style={{ marginLeft: "0.5rem", opacity: 0.8 }}>
                        (score: {msg.confidence.toFixed(2)})
                      </span>
                    )}
                  </div>
                )}

                <div
                  style={{
                    display: "inline-block",
                    padding: "0.5rem 0.75rem",
                    borderRadius: "8px",
                    background:
                      msg.role === "user"
                        ? "#444"
                        : "rgba(255, 255, 255, 0.05)",
                  }}
                >
                  <strong>{msg.role === "user" ? "You: " : "AI: "}</strong>
                  <span>{msg.content}</span>
                </div>

                {isAssistant && msg.followUpQuestions && msg.followUpQuestions.length > 0 && (
                  <div
                    style={{
                      marginTop: "0.5rem",
                      textAlign: "left",
                    }}
                  >
                    <div style={{ fontSize: "0.85rem", marginBottom: "0.4rem", opacity: 0.9 }}>
                      💡 You might want to ask:
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                      {msg.followUpQuestions.map((question, qIdx) => (
                        <button
                          key={qIdx}
                          type="button"
                          onClick={() => handleFollowUpClick(question)}
                          style={{
                            fontSize: "0.8rem",
                            padding: "0.4rem 0.75rem",
                            borderRadius: "16px",
                            border: "1px solid #4a90e2",
                            backgroundColor: "rgba(74, 144, 226, 0.1)",
                            color: "#66b3ff",
                            cursor: "pointer",
                            transition: "all 0.2s ease",
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = "rgba(74, 144, 226, 0.2)";
                            e.currentTarget.style.borderColor = "#66b3ff";
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = "rgba(74, 144, 226, 0.1)";
                            e.currentTarget.style.borderColor = "#4a90e2";
                          }}
                        >
                          {question}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {isAssistant && hasContext && (
                  <div
                    style={{
                      marginTop: "0.35rem",
                      textAlign: "left",
                    }}
                  >
                    <button
                      type="button"
                      onClick={() => toggleContext(idx)}
                      style={{
                        fontSize: "0.8rem",
                        padding: "0.25rem 0.5rem",
                        borderRadius: "4px",
                        border: "1px solid #555",
                        backgroundColor: "#222",
                        color: "#eee",
                        cursor: "pointer",
                      }}
                    >
                      {isExpanded
                        ? "Hide sources"
                        : `Show sources (${msg.contextUsed!.length})`}
                    </button>

                    {isExpanded && (
                      <div
                        style={{
                          marginTop: "0.5rem",
                          fontSize: "0.85rem",
                          borderLeft: "2px solid #555",
                          paddingLeft: "0.75rem",
                        }}
                      >
                        {msg.contextUsed!.map((chunk, cIdx) => (
                          <div
                            key={chunk.id ?? cIdx}
                            style={{ marginBottom: "0.5rem" }}
                          >
                            <div style={{ fontWeight: 600 }}>
                              [Chunk {cIdx + 1}] {chunk.title}
                            </div>
                            <div
                              style={{
                                fontSize: "0.8rem",
                                opacity: 0.8,
                                marginBottom: "0.2rem",
                              }}
                            >
                              {chunk.source_label
                                ? chunk.source_label
                                : chunk.source_type}
                              {chunk.section_title && (
                                <> · Section: {chunk.section_title}</>
                              )}
                              {chunk.roadmap_item_title && (
                                <> · Item: {chunk.roadmap_item_title}</>
                              )}
                            </div>
                            <div style={{ whiteSpace: "pre-wrap" }}>
                              {chunk.content.length > 260
                                ? chunk.content.slice(0, 260) + "…"
                                : chunk.content}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}
