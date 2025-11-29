"use client";

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

  if (loading) {
    return (
      <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
        <h1>Learning Log</h1>
        <p>Loading…</p>
      </main>
    );
  }

  if (error) {
    return (
      <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
        <h1>Learning Log</h1>
        <p style={{ color: "red" }}>{error}</p>
      </main>
    );
  }

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Learning Log</h1>
      {entries.length === 0 && <p>No entries yet.</p>}

      <ul style={{ listStyle: "none", padding: 0 }}>
        {entries.map((entry) => (
          <li
            key={entry.id}
            style={{
              marginBottom: "1.5rem",
              padding: "1rem",
              border: "1px solid #333",
              borderRadius: "8px",
            }}
          >
            <h2>{entry.title}</h2>

            {(entry.section_title || entry.roadmap_item_title) && (
              <p style={{ fontSize: "0.9rem", opacity: 0.8 }}>
                {entry.section_title && <span>{entry.section_title} – </span>}
                {entry.roadmap_item_title && (
                  <span>{entry.roadmap_item_title}</span>
                )}
              </p>
            )}

            <p style={{ whiteSpace: "pre-wrap" }}>{entry.content}</p>

            <p style={{ fontSize: "0.8rem", opacity: 0.7 }}>
              Created: {new Date(entry.created_at).toLocaleString()}
            </p>

            {entry.media.length > 0 && (
              <div style={{ marginTop: "0.5rem" }}>
                <strong>Media:</strong>
                <ul>
                  {entry.media.map((m) => (
                    <li key={m.id}>
                      {m.media_type === "image" ? (
                        <img
                          src={m.url}
                          alt={m.caption || ""}
                          style={{ maxWidth: "300px" }}
                        />
                      ) : (
                        <a href={m.url} target="_blank" rel="noreferrer">
                          {m.caption || m.url}
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}
