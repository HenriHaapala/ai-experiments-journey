"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type RoadmapItem = {
  id: number;
  title: string;
  description: string;
  order: number;
  is_active: boolean;
};

type RoadmapSection = {
  id: number;
  title: string;
  description: string;
  order: number;
  items: RoadmapItem[];
};

export default function RoadmapPage() {
  const [sections, setSections] = useState<RoadmapSection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/roadmap/sections/`
        );

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        setSections(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load roadmap");
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
            <Link href="/roadmap" style={{ color: "#CC0000", textDecoration: "none" }}>
              Roadmap
            </Link>
            <Link href="/learning" style={{ color: "#E8E8E8", textDecoration: "none" }}>
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
            AI Career Roadmap 2025
          </h1>
          <p style={{
            fontSize: "1.25rem",
            color: "#808080",
            marginBottom: "1rem",
            fontWeight: "300"
          }}>
            My journey through AI engineering and machine learning
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
            <p style={{ fontSize: "1.1rem" }}>Loading roadmap...</p>
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

        {!loading && !error && (
          <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
            {sections.map((section) => (
              <div
                key={section.id}
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
                  marginBottom: "1rem",
                  fontWeight: "700"
                }}>
                  {section.order}. {section.title}
                </h2>

                {section.description && (
                  <p style={{
                    color: "#808080",
                    marginBottom: "1.5rem",
                    lineHeight: "1.6"
                  }}>
                    {section.description}
                  </p>
                )}

                <ul style={{
                  listStyle: "none",
                  padding: 0,
                  margin: 0,
                  display: "flex",
                  flexDirection: "column",
                  gap: "1rem"
                }}>
                  {section.items
                    .filter((item) => item.is_active)
                    .map((item) => (
                      <li
                        key={item.id}
                        style={{
                          padding: "1rem",
                          background: "rgba(0, 0, 0, 0.3)",
                          border: "1px solid rgba(204, 0, 0, 0.2)",
                          borderRadius: "4px",
                          transition: "background 0.2s"
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = "rgba(204, 0, 0, 0.1)";
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = "rgba(0, 0, 0, 0.3)";
                        }}
                      >
                        <div style={{
                          color: "#E8E8E8",
                          fontWeight: "600",
                          marginBottom: "0.5rem",
                          display: "flex",
                          alignItems: "center",
                          gap: "0.5rem"
                        }}>
                          <span style={{ color: "#CC0000" }}>▸</span>
                          {item.title}
                        </div>
                        {item.description && (
                          <div style={{
                            color: "#808080",
                            fontSize: "0.9rem",
                            lineHeight: "1.5",
                            paddingLeft: "1.25rem"
                          }}>
                            {item.description}
                          </div>
                        )}
                      </li>
                    ))}
                </ul>
              </div>
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
