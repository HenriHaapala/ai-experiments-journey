"use client";

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

  if (loading) {
    return (
      <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
        <h1>AI Roadmap</h1>
        <p>Loading…</p>
      </main>
    );
  }

  if (error) {
    return (
      <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
        <h1>AI Roadmap</h1>
        <p style={{ color: "red" }}>{error}</p>
      </main>
    );
  }

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>AI Roadmap</h1>
      {sections.map((section) => (
        <section
          key={section.id}
          style={{
            marginBottom: "2rem",
            padding: "1rem",
            border: "1px solid #333",
            borderRadius: "8px",
          }}
        >
          <h2>
            {section.order}. {section.title}
          </h2>
          {section.description && (
            <p style={{ opacity: 0.8 }}>{section.description}</p>
          )}

          <ul style={{ marginTop: "1rem" }}>
            {section.items
              .filter((item) => item.is_active)
              .map((item) => (
                <li key={item.id} style={{ marginBottom: "0.5rem" }}>
                  <strong>{item.title}</strong>
                  {item.description && (
                    <div style={{ opacity: 0.8 }}>{item.description}</div>
                  )}
                </li>
              ))}
          </ul>
        </section>
      ))}
    </main>
  );
}
