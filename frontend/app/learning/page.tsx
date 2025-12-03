"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Media = {
  id: number;
  media_type: "image" | "video" | "link" | "file";
  url: string;
  caption: string;
};

type LearningEntry = {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  is_public: boolean;
  roadmap_item: number | null;
  roadmap_item_title?: string;
  section_title?: string;
  media: Media[];
};

export default function LearningPage() {
  const [entries, setEntries] = useState<LearningEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/learning/public/`
        );

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        setEntries(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load learning entries");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

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
            <Link href="/" style={{ color: "#E8E8E8", textDecoration: "none", transition: "color 0.3s" }}>
              Home
            </Link>
            <Link href="/roadmap" style={{ color: "#E8E8E8", textDecoration: "none" }}>
              Roadmap
            </Link>
            <Link href="/learning" style={{ color: "#CC0000", textDecoration: "none" }}>
              Learning Log
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{
        padding: "4rem 2rem",
        textAlign: "center",
        background: "radial-gradient(circle at center, rgba(204, 0, 0, 0.1) 0%, transparent 70%)"
      }}>
        <div style={{ maxWidth: "900px", margin: "0 auto" }}>
          <h1 style={{
            fontSize: "3.5rem",
            fontWeight: "900",
            marginBottom: "1rem",
            background: "linear-gradient(135deg, #CC0000 0%, #FF3333 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
            letterSpacing: "-0.02em"
          }}>
            Learning Log
          </h1>
          <p style={{
            fontSize: "1.25rem",
            color: "#808080",
            marginBottom: "1rem",
            fontWeight: "300"
          }}>
            My documented journey through AI and software development
          </p>
          <div style={{
            width: "60px",
            height: "3px",
            background: "linear-gradient(90deg, #CC0000, transparent)",
            margin: "0 auto"
          }} />
        </div>
      </section>

      {/* Content Section */}
      <section style={{
        padding: "2rem 2rem 4rem",
        maxWidth: "1200px",
        margin: "0 auto"
      }}>
        {loading && (
          <div style={{
            textAlign: "center",
            padding: "3rem",
            color: "#808080"
          }}>
            <p style={{ fontSize: "1.1rem" }}>Loading learning entries...</p>
          </div>
        )}

        {error && (
          <div style={{
            textAlign: "center",
            padding: "3rem",
            background: "linear-gradient(135deg, rgba(204, 0, 0, 0.2) 0%, rgba(0, 0, 0, 0.5) 100%)",
            border: "1px solid rgba(204, 0, 0, 0.5)",
            borderRadius: "8px"
          }}>
            <p style={{ color: "#CC0000", fontSize: "1.1rem" }}>{error}</p>
          </div>
        )}

        {!loading && !error && entries.length === 0 && (
          <div style={{
            textAlign: "center",
            padding: "3rem",
            background: "linear-gradient(135deg, rgba(204, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.5) 100%)",
            border: "1px solid rgba(204, 0, 0, 0.3)",
            borderRadius: "8px"
          }}>
            <p style={{ color: "#808080", fontSize: "1.1rem" }}>No learning entries yet.</p>
          </div>
        )}

        {!loading && !error && entries.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
            {entries.map((entry) => (
              <article
                key={entry.id}
                style={{
                  background: "linear-gradient(135deg, rgba(204, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.5) 100%)",
                  border: "1px solid rgba(204, 0, 0, 0.3)",
                  borderRadius: "8px",
                  padding: "2rem",
                  transition: "transform 0.2s, border-color 0.2s"
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-2px)";
                  e.currentTarget.style.borderColor = "rgba(204, 0, 0, 0.5)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.borderColor = "rgba(204, 0, 0, 0.3)";
                }}
              >
                <h2 style={{
                  color: "#CC0000",
                  fontSize: "1.75rem",
                  marginBottom: "0.75rem",
                  fontWeight: "700"
                }}>
                  {entry.title}
                </h2>

                {(entry.section_title || entry.roadmap_item_title) && (
                  <div style={{
                    fontSize: "0.95rem",
                    color: "#808080",
                    marginBottom: "1rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem"
                  }}>
                    <span style={{ color: "#CC0000" }}>▸</span>
                    {entry.section_title && <span>{entry.section_title}</span>}
                    {entry.section_title && entry.roadmap_item_title && <span>→</span>}
                    {entry.roadmap_item_title && <span>{entry.roadmap_item_title}</span>}
                  </div>
                )}

                <div style={{
                  color: "#E8E8E8",
                  lineHeight: "1.8",
                  whiteSpace: "pre-wrap",
                  marginBottom: "1.5rem",
                  padding: "1rem",
                  background: "rgba(0, 0, 0, 0.3)",
                  borderRadius: "4px",
                  border: "1px solid rgba(204, 0, 0, 0.1)"
                }}>
                  {entry.content}
                </div>

                {entry.media.length > 0 && (
                  <div style={{
                    marginBottom: "1rem",
                    padding: "1rem",
                    background: "rgba(0, 0, 0, 0.3)",
                    borderRadius: "4px",
                    border: "1px solid rgba(204, 0, 0, 0.2)"
                  }}>
                    <h3 style={{
                      color: "#CC0000",
                      fontSize: "1rem",
                      marginBottom: "1rem",
                      fontWeight: "600"
                    }}>
                      Media Attachments
                    </h3>
                    <ul style={{
                      listStyle: "none",
                      padding: 0,
                      margin: 0,
                      display: "flex",
                      flexDirection: "column",
                      gap: "1rem"
                    }}>
                      {entry.media.map((m) => (
                        <li key={m.id}>
                          {m.media_type === "image" ? (
                            <div>
                              <img
                                src={m.url}
                                alt={m.caption || "Media attachment"}
                                style={{
                                  maxWidth: "100%",
                                  height: "auto",
                                  borderRadius: "4px",
                                  border: "1px solid rgba(204, 0, 0, 0.2)"
                                }}
                              />
                              {m.caption && (
                                <p style={{
                                  color: "#808080",
                                  fontSize: "0.875rem",
                                  marginTop: "0.5rem",
                                  fontStyle: "italic"
                                }}>
                                  {m.caption}
                                </p>
                              )}
                            </div>
                          ) : (
                            <a
                              href={m.url}
                              target="_blank"
                              rel="noreferrer"
                              style={{
                                color: "#CC0000",
                                textDecoration: "none",
                                display: "flex",
                                alignItems: "center",
                                gap: "0.5rem",
                                padding: "0.5rem",
                                background: "rgba(204, 0, 0, 0.1)",
                                borderRadius: "4px",
                                transition: "background 0.2s"
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.background = "rgba(204, 0, 0, 0.2)";
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = "rgba(204, 0, 0, 0.1)";
                              }}
                            >
                              <span>🔗</span>
                              <span>{m.caption || m.url}</span>
                            </a>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div style={{
                  fontSize: "0.85rem",
                  color: "#808080",
                  paddingTop: "1rem",
                  borderTop: "1px solid rgba(204, 0, 0, 0.2)"
                }}>
                  Created: {new Date(entry.created_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit"
                  })}
                </div>
              </article>
            ))}
          </div>
        )}
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
