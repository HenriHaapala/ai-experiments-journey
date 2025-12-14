"use client";

import Link from "next/link";
import { useEffect, useState, FormEvent } from "react";
import Navigation from "./components/layout/Navigation";
import Footer from "./components/layout/Footer";
import PageWrapper from "./components/layout/PageWrapper";
import Card from "./components/ui/Card";

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
    <PageWrapper>
      <Navigation />

      {/* Hero Section with Chatbot */}
      <section className="bg-section mx-auto max-w-[1400px] px-4 py-8 md:px-8 md:py-16">
        <div className="grid-responsive-900 items-stretch">
          {/* Left: Name and Title */}
          <div>
            <h1 className="text-gradient-red mb-4 text-[2.5rem] font-black leading-[1.1] tracking-tight md:text-[4rem]">
              Henri Haapala
            </h1>
            <p className="mb-6 text-xl font-light text-text-gray md:mb-8 md:text-2xl">
              AI Engineer & Full-Stack Developer
            </p>
            <div className="divider-red mb-6 md:mb-8" />
            <p className="mb-4 text-base leading-relaxed text-text-light md:mb-6 md:text-[1.05rem]">
              Building intelligent systems with RAG, embeddings, and LLMs.
              Passionate about semantic search, vector databases, and production AI applications.
            </p>
            <p className="text-sm text-text-gray md:text-[0.95rem]">
              Backend health: <span className={backendStatus === "ok" ? "text-primary-red" : "text-text-gray"}>{backendStatus}</span>
            </p>
          </div>

          {/* Right: Chat Interface */}
          <Card className="flex h-full min-h-[500px] flex-col">
            <h2 className="mb-3 text-xl font-bold text-primary-red md:mb-4 md:text-2xl">
              Ask My AI Assistant
            </h2>

            {/* Chat Messages */}
            <div className="mb-3 min-h-[200px] flex-1 overflow-y-auto md:mb-4 md:min-h-[250px]">
              {messages.length === 0 && (
                <p className="text-sm italic text-text-gray md:text-[0.95rem]">
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
                  <div key={idx} className="mb-4">
                    {isAssistant && isLowConfidence && (
                      <div className="mb-2 rounded border border-[#f2c14f] bg-[#f2c14f]/10 p-2 text-xs text-[#f2c14f]">
                        ⚠️ Low confidence answer
                      </div>
                    )}
                    <div className={`rounded-md px-4 py-3 ${
                      msg.role === "user"
                        ? "border border-primary-red/30 bg-primary-red/20"
                        : "border border-white/10 bg-white/5"
                    }`}>
                      <strong className={msg.role === "user" ? "text-primary-red" : "text-text-light"}>
                        {msg.role === "user" ? "You: " : "AI: "}
                      </strong>
                      <span className="text-text-light">{msg.content}</span>
                    </div>

                    {isAssistant && msg.followUpQuestions && msg.followUpQuestions.length > 0 && (
                      <div className="mt-2">
                        <div className="mb-2 text-xs text-text-gray">
                          💡 You might want to ask:
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {msg.followUpQuestions.map((q, qIdx) => (
                            <button
                              key={qIdx}
                              onClick={() => handleFollowUpClick(q)}
                              className="cursor-pointer rounded-xl border border-primary-red bg-primary-red/10 px-3 py-2 text-xs text-primary-red hover:bg-primary-red/20"
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
              <div className="flex gap-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask about Henri's experience..."
                  className="flex-1 rounded border border-primary-red/30 bg-black/50 px-3 py-2 text-sm text-text-light focus:outline-none focus:ring-2 focus:ring-primary-red md:py-3 md:text-[0.95rem]"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="cursor-pointer rounded border border-primary-red bg-gradient-to-br from-primary-red to-dark-red px-4 py-2 font-semibold text-text-light transition-opacity disabled:cursor-not-allowed disabled:opacity-60 md:px-6 md:py-3"
                >
                  {loading ? "..." : "Ask"}
                </button>
              </div>
              {error && <p className="mt-2 text-sm text-[#f2c14f]">{error}</p>}
            </form>
          </Card>
        </div>
      </section>

      {/* Bio Section */}
      <section className="bg-section mx-auto max-w-[1400px] px-4 py-8 md:px-8 md:py-16">
        <div className="grid-responsive-900 items-start">
          {/* Left Column */}
          <div>
            <Card className="mb-6 md:mb-8">
              <h2 className="mb-4 text-xl font-bold text-primary-red md:mb-6 md:text-2xl">
                About Me
              </h2>
              <p className="mb-3 text-sm leading-relaxed text-text-light md:mb-4 md:text-base">
                I'm an AI engineer passionate about building intelligent systems that solve real-world problems.
                My focus is on RAG systems, embeddings, vector databases, and LLM applications.
              </p>
              <p className="text-sm leading-relaxed text-text-light md:text-base">
                Currently building production-grade AI applications with Django, Next.js, and modern AI tools.
                I specialize in retrieval-augmented generation, semantic search, and full-stack development.
              </p>
            </Card>

            <Card>
              <h3 className="mb-4 text-lg font-bold text-primary-red md:mb-6 md:text-xl">
                Core Skills
              </h3>
              <div className="flex flex-wrap gap-2 md:gap-3">
                {["Python", "Django", "Next.js", "React", "TypeScript", "PostgreSQL", "pgvector",
                  "RAG Systems", "LLM Integration", "Cohere", "Groq", "Vector Search", "Full-Stack Development"]
                  .map((skill) => (
                    <span key={skill} className="rounded border border-primary-red/40 bg-primary-red/20 px-3 py-1.5 text-xs text-text-light md:px-4 md:py-2 md:text-sm">
                      {skill}
                    </span>
                  ))}
              </div>
            </Card>
          </div>

          {/* Right Column */}
          <div>
            <Card className="mb-6 md:mb-8">
              <h3 className="mb-4 text-lg font-bold text-primary-red md:mb-6 md:text-xl">
                Education
              </h3>
              <div>
                <h4 className="mb-2 text-base text-text-light md:text-lg">
                  Bachelor of Business Administration (BBA)
                </h4>
                <p className="mb-1 text-sm text-text-gray md:text-[0.95rem]">
                  Oulu University of Applied Sciences
                </p>
                <p className="text-xs text-text-gray md:text-sm">
                  Specialization: Web Application Development
                </p>
              </div>
            </Card>

            <Card>
              <h3 className="mb-4 text-lg font-bold text-primary-red md:mb-6 md:text-xl">
                Current Focus
              </h3>
              <ul className="m-0 list-none p-0">
                {[
                  "Building production RAG systems with confidence scoring",
                  "Semantic search with pgvector and Cohere embeddings",
                  "LLM integration for intelligent applications",
                  "Full-stack development with Django + Next.js",
                  "Following AI Career Roadmap 2025 (10 sections)"
                ].map((item, idx) => (
                  <li key={idx} className={`py-2 text-sm leading-normal text-text-light md:py-3 md:text-[0.95rem] ${idx < 4 ? "border-b border-primary-red/20" : ""}`}>
                    <span className="mr-2 text-primary-red">▸</span>
                    {item}
                  </li>
                ))}
              </ul>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-section px-4 py-8 text-center md:px-8 md:py-16">
        <div className="mx-auto max-w-[600px]">
          <h2 className="mb-3 text-xl font-bold text-primary-red md:mb-4 md:text-[2rem]">
            Explore My Work
          </h2>
          <p className="mb-6 text-sm leading-relaxed text-text-gray md:mb-8 md:text-base">
            Check out my AI learning roadmap or explore my learning log to see my projects and journey.
          </p>
          <div className="flex flex-col justify-center gap-3 md:flex-row md:gap-4">
            <Link href="/roadmap" className="inline-block rounded border border-primary-red bg-gradient-to-br from-primary-red to-dark-red px-6 py-2.5 font-semibold text-text-light no-underline md:px-8 md:py-3">
              View Roadmap
            </Link>
            <Link href="/learning" className="inline-block rounded border border-primary-red bg-transparent px-6 py-2.5 font-semibold text-primary-red no-underline hover:bg-primary-red/10 md:px-8 md:py-3">
              Learning Log
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </PageWrapper>
  );
}
