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
  content: string;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  confidence?: number | null;
  status?: string | null;
  contextUsed?: ContextChunk[];
  followUpQuestions?: string[];
};

export default function HomePage() {
  const [backendStatus, setBackendStatus] = useState<string>("checking…");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedContexts, setExpandedContexts] = useState<Record<number, boolean>>({});

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/health/`);
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
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/ai/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

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
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #1a0a0a 0%, #2a1515 100%)",
      color: "#E8E8E8",
      fontFamily: "system-ui, -apple-system, sans-serif"
    }}>
      {/* Inner Container */}
      <div style={{
        maxWidth: "1400px",
        margin: "0 auto",
        background: "linear-gradient(135deg, #1a1414 0%, #2d1f1f 30%, #331a1a 70%, #281818 100%)",
        minHeight: "100vh",
        boxShadow: "0 0 60px rgba(150, 50, 50, 0.4)",
        position: "relative"
      }}>
        {/* Navigation */}
        <nav style={{
          padding: "1.5rem 2rem",
          borderBottom: "1px solid rgba(204, 0, 0, 0.3)",
          background: "rgba(25, 15, 15, 0.9)",
          backdropFilter: "blur(10px)",
          position: "sticky",
          top: 0,
          zIndex: 100
        }}>
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
          <Link href="/" style={{
            color: "#CC0000",
            textDecoration: "none",
            fontSize: "1.25rem",
            fontWeight: "bold",
            letterSpacing: "0.05em"
          }}>
            HENRI HAAPALA
          </Link>
          <div style={{ display: "flex", gap: "2rem" }}>
            <Link href="/" style={{ color: "#CC0000", textDecoration: "none" }}>
              Home
            </Link>
            <Link href="/roadmap" style={{ color: "#E8E8E8", textDecoration: "none" }}>
              Roadmap
            </Link>
            <Link href="/learning" style={{ color: "#E8E8E8", textDecoration: "none" }}>
              Learning Log
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section with Chatbot */}
      <section style={{
        padding: "4rem 2rem",
        maxWidth: "1400px",
        margin: "0 auto"
      }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "4rem",
          alignItems: "center"
        }}>
          {/* Left: Name and Title */}
          <div>
            <h1 style={{
              fontSize: "4rem",
              fontWeight: "900",
              marginBottom: "1rem",
              background: "linear-gradient(135deg, #CC0000 0%, #FF3333 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              letterSpacing: "-0.02em",
              lineHeight: "1.1"
            }}>
              Henri Haapala
            </h1>
            <p style={{
              fontSize: "1.5rem",
              color: "#808080",
              marginBottom: "2rem",
              fontWeight: "300"
            }}>
              AI Engineer & Full-Stack Developer
            </p>
            <div style={{
              width: "60px",
              height: "3px",
              background: "linear-gradient(90deg, #CC0000, transparent)",
              marginBottom: "2rem"
            }} />
            <p style={{
              color: "#E8E8E8",
              lineHeight: "1.8",
              fontSize: "1.05rem",
              marginBottom: "1.5rem"
            }}>
              Building intelligent systems with RAG, embeddings, and LLMs.
              Passionate about semantic search, vector databases, and production AI applications.
            </p>
            <p style={{
              color: "#808080",
              fontSize: "0.95rem",
              marginBottom: "0.5rem"
            }}>
              Backend health: <span style={{ color: backendStatus === "ok" ? "#CC0000" : "#808080" }}>{backendStatus}</span>
            </p>
          </div>

          {/* Right: Chat Interface */}
          <div style={{
            background: "linear-gradient(135deg, rgba(204, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.5) 100%)",
            border: "1px solid rgba(204, 0, 0, 0.3)",
            borderRadius: "8px",
            padding: "2rem",
            maxHeight: "500px",
            display: "flex",
            flexDirection: "column"
          }}>
            <h2 style={{
              color: "#CC0000",
              fontSize: "1.5rem",
              marginBottom: "1rem",
              fontWeight: "700"
            }}>
              Ask My AI Assistant
            </h2>

            {/* Chat Messages */}
            <div style={{
              flex: 1,
              overflowY: "auto",
              marginBottom: "1rem",
              minHeight: "250px"
            }}>
              {messages.length === 0 && (
                <p style={{ color: "#808080", fontSize: "0.95rem", fontStyle: "italic" }}>
                  Ask me anything about Henri's work, skills, or AI learning journey...
                </p>
              )}
              {messages.map((msg, idx) => {
                const isAssistant = msg.role === "assistant";
                const isLowConfidence = isAssistant && (
                  msg.status === "low_confidence" ||
                  msg.status === "very_low_confidence" ||
                  (typeof msg.confidence === "number" && msg.confidence < 0.25)
                );

                return (
                  <div key={idx} style={{ marginBottom: "1rem" }}>
                    {isAssistant && isLowConfidence && (
                      <div style={{
                        padding: "0.5rem",
                        marginBottom: "0.5rem",
                        borderRadius: "4px",
                        border: "1px solid #f2c14f",
                        backgroundColor: "rgba(242, 193, 79, 0.1)",
                        fontSize: "0.8rem",
                        color: "#f2c14f"
                      }}>
                        ⚠️ Low confidence answer
                      </div>
                    )}
                    <div style={{
                      padding: "0.75rem 1rem",
                      borderRadius: "6px",
                      background: msg.role === "user"
                        ? "rgba(204, 0, 0, 0.2)"
                        : "rgba(255, 255, 255, 0.05)",
                      border: msg.role === "user"
                        ? "1px solid rgba(204, 0, 0, 0.3)"
                        : "1px solid rgba(255, 255, 255, 0.1)"
                    }}>
                      <strong style={{ color: msg.role === "user" ? "#CC0000" : "#E8E8E8" }}>
                        {msg.role === "user" ? "You: " : "AI: "}
                      </strong>
                      <span style={{ color: "#E8E8E8" }}>{msg.content}</span>
                    </div>

                    {isAssistant && msg.followUpQuestions && msg.followUpQuestions.length > 0 && (
                      <div style={{ marginTop: "0.5rem" }}>
                        <div style={{ fontSize: "0.8rem", marginBottom: "0.5rem", color: "#808080" }}>
                          💡 You might want to ask:
                        </div>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                          {msg.followUpQuestions.map((q, qIdx) => (
                            <button
                              key={qIdx}
                              onClick={() => handleFollowUpClick(q)}
                              style={{
                                fontSize: "0.75rem",
                                padding: "0.4rem 0.75rem",
                                borderRadius: "12px",
                                border: "1px solid #CC0000",
                                background: "rgba(204, 0, 0, 0.1)",
                                color: "#CC0000",
                                cursor: "pointer"
                              }}
                            >
                              {q}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Chat Input */}
            <form onSubmit={handleSubmit}>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask about Henri's experience..."
                  style={{
                    flex: 1,
                    padding: "0.75rem",
                    background: "rgba(0, 0, 0, 0.5)",
                    border: "1px solid rgba(204, 0, 0, 0.3)",
                    borderRadius: "4px",
                    color: "#E8E8E8",
                    fontSize: "0.95rem"
                  }}
                />
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    padding: "0.75rem 1.5rem",
                    background: "linear-gradient(135deg, #CC0000 0%, #8B0000 100%)",
                    color: "#E8E8E8",
                    border: "1px solid #CC0000",
                    borderRadius: "4px",
                    fontWeight: "600",
                    cursor: loading ? "not-allowed" : "pointer",
                    opacity: loading ? 0.6 : 1
                  }}
                >
                  {loading ? "..." : "Ask"}
                </button>
              </div>
              {error && <p style={{ color: "#f2c14f", fontSize: "0.85rem", marginTop: "0.5rem" }}>{error}</p>}
            </form>
          </div>
        </div>
      </section>

      {/* Bio Section */}
      <section style={{
        padding: "4rem 2rem",
        maxWidth: "1400px",
        margin: "0 auto"
      }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "4rem",
          alignItems: "start"
        }}>
          {/* Left Column */}
          <div>
            <div style={{
              background: "linear-gradient(135deg, rgba(204, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.5) 100%)",
              border: "1px solid rgba(204, 0, 0, 0.3)",
              borderRadius: "8px",
              padding: "2rem",
              marginBottom: "2rem"
            }}>
              <h2 style={{ color: "#CC0000", fontSize: "1.5rem", marginBottom: "1.5rem", fontWeight: "700" }}>
                About Me
              </h2>
              <p style={{ color: "#E8E8E8", lineHeight: "1.8", marginBottom: "1rem" }}>
                I'm an AI engineer passionate about building intelligent systems that solve real-world problems.
                My focus is on RAG systems, embeddings, vector databases, and LLM applications.
              </p>
              <p style={{ color: "#E8E8E8", lineHeight: "1.8" }}>
                Currently building production-grade AI applications with Django, Next.js, and modern AI tools.
                I specialize in retrieval-augmented generation, semantic search, and full-stack development.
              </p>
            </div>

            <div style={{
              background: "linear-gradient(135deg, rgba(204, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.5) 100%)",
              border: "1px solid rgba(204, 0, 0, 0.3)",
              borderRadius: "8px",
              padding: "2rem"
            }}>
              <h3 style={{ color: "#CC0000", fontSize: "1.25rem", marginBottom: "1.5rem", fontWeight: "700" }}>
                Core Skills
              </h3>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem" }}>
                {["Python", "Django", "Next.js", "React", "TypeScript", "PostgreSQL", "pgvector",
                  "RAG Systems", "LLM Integration", "Cohere", "Groq", "Vector Search", "Full-Stack Development"]
                  .map((skill) => (
                    <span key={skill} style={{
                      padding: "0.5rem 1rem",
                      background: "rgba(204, 0, 0, 0.2)",
                      border: "1px solid rgba(204, 0, 0, 0.4)",
                      borderRadius: "4px",
                      fontSize: "0.875rem",
                      color: "#E8E8E8"
                    }}>
                      {skill}
                    </span>
                  ))}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div>
            <div style={{
              background: "linear-gradient(135deg, rgba(204, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.5) 100%)",
              border: "1px solid rgba(204, 0, 0, 0.3)",
              borderRadius: "8px",
              padding: "2rem",
              marginBottom: "2rem"
            }}>
              <h3 style={{ color: "#CC0000", fontSize: "1.25rem", marginBottom: "1.5rem", fontWeight: "700" }}>
                Education
              </h3>
              <div>
                <h4 style={{ color: "#E8E8E8", fontSize: "1.1rem", marginBottom: "0.5rem" }}>
                  Bachelor of Business Administration (BBA)
                </h4>
                <p style={{ color: "#808080", fontSize: "0.95rem", marginBottom: "0.25rem" }}>
                  Oulu University of Applied Sciences
                </p>
                <p style={{ color: "#808080", fontSize: "0.875rem" }}>
                  Specialization: Web Application Development
                </p>
              </div>
            </div>

            <div style={{
              background: "linear-gradient(135deg, rgba(204, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.5) 100%)",
              border: "1px solid rgba(204, 0, 0, 0.3)",
              borderRadius: "8px",
              padding: "2rem"
            }}>
              <h3 style={{ color: "#CC0000", fontSize: "1.25rem", marginBottom: "1.5rem", fontWeight: "700" }}>
                Current Focus
              </h3>
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {[
                  "Building production RAG systems with confidence scoring",
                  "Semantic search with pgvector and Cohere embeddings",
                  "LLM integration for intelligent applications",
                  "Full-stack development with Django + Next.js",
                  "Following AI Career Roadmap 2025 (10 sections)"
                ].map((item, idx) => (
                  <li key={idx} style={{
                    padding: "0.75rem 0",
                    borderBottom: idx < 4 ? "1px solid rgba(204, 0, 0, 0.2)" : "none",
                    color: "#E8E8E8",
                    fontSize: "0.95rem",
                    lineHeight: "1.6"
                  }}>
                    <span style={{ color: "#CC0000", marginRight: "0.5rem" }}>▸</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section style={{
        padding: "4rem 2rem",
        textAlign: "center",
        background: "linear-gradient(180deg, transparent 0%, rgba(204, 0, 0, 0.05) 100%)"
      }}>
        <div style={{ maxWidth: "600px", margin: "0 auto" }}>
          <h2 style={{ color: "#CC0000", fontSize: "2rem", marginBottom: "1rem", fontWeight: "700" }}>
            Explore My Work
          </h2>
          <p style={{ color: "#808080", marginBottom: "2rem", lineHeight: "1.6" }}>
            Check out my AI learning roadmap or explore my learning log to see my projects and journey.
          </p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
            <Link href="/roadmap" style={{
              display: "inline-block",
              padding: "0.75rem 2rem",
              background: "linear-gradient(135deg, #CC0000 0%, #8B0000 100%)",
              color: "#E8E8E8",
              textDecoration: "none",
              borderRadius: "4px",
              fontWeight: "600",
              border: "1px solid #CC0000"
            }}>
              View Roadmap
            </Link>
            <Link href="/learning" style={{
              display: "inline-block",
              padding: "0.75rem 2rem",
              background: "transparent",
              color: "#CC0000",
              textDecoration: "none",
              borderRadius: "4px",
              fontWeight: "600",
              border: "1px solid #CC0000"
            }}>
              Learning Log
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: "2rem",
        textAlign: "center",
        borderTop: "1px solid rgba(204, 0, 0, 0.3)",
        background: "rgba(0, 0, 0, 0.8)"
      }}>
        <p style={{ color: "#808080", fontSize: "0.875rem" }}>
          © 2025 Henri Haapala. Built with Django, Next.js, and AI.
        </p>
      </footer>
      </div>
    </div>
  );
}
