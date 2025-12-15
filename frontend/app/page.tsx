"use client";

import Link from "next/link";
import { useEffect, useState, FormEvent } from "react";
import Navigation from "./components/layout/Navigation";
import Footer from "./components/layout/Footer";
import PageWrapper from "./components/layout/PageWrapper";

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

  const handleFollowUpClick = (followUpQuestion: string) => {
    setQuestion(followUpQuestion);
  };

  return (
    <PageWrapper>
      <Navigation />

      {/* Hero Section with Chatbot */}
      <section className="mx-auto max-w-[1400px] px-4 py-12 md:px-8 md:py-24">
        <div className="grid-responsive-900 items-stretch gap-8 md:gap-16">
          {/* Left: Name and Title */}
          <div className="flex flex-col justify-center">
            {/* System Status Badge */}
            <p className="mb-8 font-mono text-xs uppercase tracking-wider text-text-gray">
              » SYSTEM STATUS: <span className={backendStatus === "ok" ? "text-primary-red" : "text-text-gray"}>OPERATIONAL</span>
            </p>

            {/* Large Serif Heading */}
            <h1 className="mb-6 font-serif text-[3.5rem] font-light leading-[1.05] tracking-tight md:text-[5rem] lg:text-[6rem]">
              <span className="text-[#B8B8B8]">The</span>
              <br />
              <span className="font-normal text-text-light">Architect</span>
            </h1>

            <p className="mb-8 max-w-md text-base leading-relaxed text-text-gray md:text-lg">
              Building intelligent systems in the shadows. Specializing in RAG, vector databases, and the unseen logic of AI applications.
            </p>

            {/* Metadata */}
            <div className="flex flex-col gap-2 font-mono text-xs text-text-gray">
              <div className="flex items-center gap-2">
                <span className="text-primary-red">●</span>
                <span>Backend Health:</span>
                <span className="uppercase">{backendStatus === "ok" ? "Nominal" : "Checking"}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-primary-red">●</span>
                <span>Last Login:</span>
                <span className="uppercase">Today, 05:45 AM</span>
              </div>
            </div>
          </div>

          {/* Right: CLASSIFIED Card */}
          <div className="classified-panel">
            <div className="classified-inner">
              {/* CLASSIFIED Header */}
              <div className="classified-header flex items-start justify-between">
                <div>
                  <p className="font-mono text-lg font-bold uppercase tracking-[0.16em] text-primary-red">
                    Classified
                  </p>
                  <p className="mt-1 font-mono text-[12px] uppercase tracking-[0.22em] text-[#c35b5b]">
                    AI Assistant Interface
                  </p>
                  <p className="mt-3 font-serif text-sm italic text-text-gray">
                    "Ask me anything about the subject's work, known associates, or technical capabilities..."
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-full border border-[#2d0f0f] bg-[#0c0808] shadow-[0_0_0_1px_rgba(255,0,0,0.08),0_10px_30px_rgba(0,0,0,0.6)]">
                  <span className="h-2 w-2 rounded-full bg-primary-red shadow-[0_0_0_4px_rgba(204,0,0,0.2)]" />
                </div>
              </div>

              {/* Chat Messages */}
              <div className="mt-6 rounded-sm border border-[#1c0e0e] bg-[#070707]/80 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
                {messages.length === 0 ? (
                  <div className="h-10" />
                ) : (
                  <div className="max-h-[260px] space-y-4 overflow-y-auto pr-1">
                    {messages.map((msg, idx) => {
                      const isAssistant = msg.role === "assistant";
                      const isLowConfidence = isAssistant && (
                        msg.status === "low_confidence" ||
                        msg.status === "very_low_confidence" ||
                        (typeof msg.confidence === "number" && msg.confidence < 0.25)
                      );

                      return (
                        <div key={idx} className="rounded-sm bg-black/40 p-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.03)]">
                          {isAssistant && isLowConfidence && (
                            <div className="mb-2 border border-[#f2c14f]/40 bg-[#f2c14f]/10 px-3 py-2 font-mono text-[11px] uppercase text-[#f2c14f]">
                              Low confidence response
                            </div>
                          )}
                          <div className={`rounded-sm border-l-2 px-3 py-2 ${msg.role === "user" ? "border-primary-red/70 bg-primary-red/5" : "border-[#2b2b2b] bg-black/30"}`}>
                            <div className="mb-1 font-mono text-[11px] uppercase tracking-[0.12em] text-text-gray">
                              {msg.role === "user" ? "Query" : "Response"}
                            </div>
                            <p className="text-sm leading-relaxed text-text-light">{msg.content}</p>
                          </div>

                          {isAssistant && msg.followUpQuestions && msg.followUpQuestions.length > 0 && (
                            <div className="mt-3 border-l-2 border-primary-red/40 pl-3">
                              <div className="mb-2 font-mono text-[11px] uppercase tracking-[0.12em] text-text-gray">
                                Suggested queries
                              </div>
                              <div className="flex flex-col gap-1.5">
                                {msg.followUpQuestions.map((q, qIdx) => (
                                  <button
                                    key={qIdx}
                                    onClick={() => handleFollowUpClick(q)}
                                    className="cursor-pointer rounded-sm border border-primary-red/30 bg-primary-red/10 px-3 py-1.5 text-left text-xs text-text-light transition hover:border-primary-red/60 hover:bg-primary-red/15"
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
                )}
              </div>

              {/* Chat Input */}
              <form onSubmit={handleSubmit} className="mt-6 border-t border-[#241010] pt-4">
                <div className="mb-2 font-mono text-[11px] uppercase tracking-[0.16em] text-text-gray">
                  Interrogate the database
                </div>
                <div className="flex items-center gap-3 rounded-sm border border-[#1a1a1a] bg-[#0b0b0b] px-3 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.05),inset_0_-1px_0_rgba(0,0,0,0.6)] focus-within:border-[#b12b2b] focus-within:shadow-[0_0_0_1px_rgba(177,43,43,0.4),inset_0_1px_0_rgba(255,255,255,0.05),inset_0_-1px_0_rgba(0,0,0,0.6)]">
                  <svg
                    aria-hidden="true"
                    className="h-4 w-4 text-text-gray"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="m21 21-4.35-4.35m0 0A6.75 6.75 0 1 0 6.75 6.75a6.75 6.75 0 0 0 9.9 9.9Z"
                    />
                  </svg>
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask about dossiers, systems, or capabilities..."
                    className="flex-1 bg-transparent font-mono text-sm text-text-light placeholder:text-text-gray/60 focus:outline-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="classified-button mt-4 w-full cursor-pointer px-6 py-4 font-mono text-sm font-bold uppercase tracking-[0.15em] text-white"
                >
                  {loading ? "Processing..." : "Initiate Query >>"}
                </button>
                {error && (
                  <p className="mt-3 border border-[#f2c14f]/40 bg-[#f2c14f]/10 px-3 py-2 font-mono text-xs text-[#f2c14f]">
                    {error}
                  </p>
                )}
              </form>

              {/* Footer Metadata */}
              <div className="classified-meta mt-6 flex items-center justify-between border-t border-[#241010] pt-4 font-mono text-[11px] uppercase text-text-gray">
                <span>Secure Connection</span>
                <span>Clearance: L3</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Case Files Section */}
      <section className="mx-auto max-w-[1400px] px-4 py-12 md:px-8 md:py-16">
        <div className="mb-8 flex items-end justify-between border-b border-text-gray/20 pb-4">
          <h2 className="font-serif text-3xl font-light text-text-light md:text-4xl">
            Case Files
          </h2>
          <span className="font-mono text-xs uppercase tracking-wider text-text-gray">
            CONFIDENTIAL
          </span>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Roadmap Card */}
          <Link href="/roadmap" className="group block border border-text-gray/30 bg-black/40 p-6 no-underline transition-all hover:border-primary-red/50 hover:bg-black/60">
            <div className="mb-4 flex items-start justify-between">
              <span className="font-mono text-xs uppercase tracking-wider text-primary-red">001</span>
              <span className="font-mono text-xs text-text-gray">2025-2026</span>
            </div>
            <h3 className="mb-3 font-serif text-xl font-normal text-text-light">
              AI Career Roadmap
            </h3>
            <p className="mb-4 text-sm leading-relaxed text-text-gray">
              Structured learning path covering 10 sections from foundations to production deployment.
            </p>
            <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-primary-red">
              <span>View Case</span>
              <span className="transition-transform group-hover:translate-x-1">»</span>
            </div>
          </Link>

          {/* Learning Log Card */}
          <Link href="/learning" className="group block border border-text-gray/30 bg-black/40 p-6 no-underline transition-all hover:border-primary-red/50 hover:bg-black/60">
            <div className="mb-4 flex items-start justify-between">
              <span className="font-mono text-xs uppercase tracking-wider text-primary-red">002</span>
              <span className="font-mono text-xs text-text-gray">ACTIVE</span>
            </div>
            <h3 className="mb-3 font-serif text-xl font-normal text-text-light">
              Learning Log
            </h3>
            <p className="mb-4 text-sm leading-relaxed text-text-gray">
              Detailed documentation of projects, experiments, and technical discoveries.
            </p>
            <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-primary-red">
              <span>View Case</span>
              <span className="transition-transform group-hover:translate-x-1">»</span>
            </div>
          </Link>

          {/* Technical Dossier Card */}
          <div className="border border-text-gray/30 bg-black/40 p-6">
            <div className="mb-4 flex items-start justify-between">
              <span className="font-mono text-xs uppercase tracking-wider text-primary-red">003</span>
              <span className="font-mono text-xs text-text-gray">CLASSIFIED</span>
            </div>
            <h3 className="mb-3 font-serif text-xl font-normal text-text-light">
              Technical Dossier
            </h3>
            <p className="mb-4 text-sm leading-relaxed text-text-gray">
              Core competencies: RAG systems, vector databases, LLM integration, full-stack development.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {["Python", "Django", "Next.js", "PostgreSQL", "Cohere", "Groq"].map((tech) => (
                <span key={tech} className="border border-primary-red/30 bg-primary-red/10 px-2 py-1 font-mono text-xs text-text-light">
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </PageWrapper>
  );
}
