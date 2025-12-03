"use client";

import { useEffect, useState } from "react";
import Navigation from "../components/layout/Navigation";
import Footer from "../components/layout/Footer";
import PageWrapper from "../components/layout/PageWrapper";
import Card from "../components/ui/Card";

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
    <PageWrapper>
      <Navigation />

      {/* Hero Section */}
      <section className="bg-radial-red p-16 text-center">
        <div className="mx-auto max-w-[900px]">
          <h1 className="text-gradient-red mb-4 text-[3.5rem] font-black tracking-tight">
            AI Career Roadmap 2025
          </h1>
          <p className="mb-4 text-xl font-light text-text-gray">
            My journey through AI engineering and machine learning
          </p>
          <div className="divider-red mx-auto" />
        </div>
      </section>

      {/* Content Section */}
      <section className="mx-auto max-w-[1200px] px-8 py-8 pb-16">
        {loading && (
          <div className="p-12 text-center text-text-gray">
            <p className="text-lg">Loading roadmap...</p>
          </div>
        )}

        {error && (
          <div className="bg-card rounded-lg border border-primary-red/50 p-12 text-center">
            <p className="text-lg text-primary-red">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <div className="flex flex-col gap-8">
            {sections.map((section) => (
              <Card key={section.id}>
                <h2 className="mb-4 text-[1.75rem] font-bold text-primary-red">
                  {section.order}. {section.title}
                </h2>

                {section.description && (
                  <p className="mb-6 leading-relaxed text-text-gray">
                    {section.description}
                  </p>
                )}

                <ul className="flex flex-col gap-4 p-0">
                  {section.items
                    .filter((item) => item.is_active)
                    .map((item) => (
                      <li
                        key={item.id}
                        className="list-none rounded border border-primary-red/20 bg-black/30 p-4 transition-colors hover:bg-primary-red/10"
                      >
                        <div className="mb-2 flex items-center gap-2 font-semibold text-text-light">
                          <span className="text-primary-red">▸</span>
                          {item.title}
                        </div>
                        {item.description && (
                          <div className="pl-5 text-sm leading-normal text-text-gray">
                            {item.description}
                          </div>
                        )}
                      </li>
                    ))}
                </ul>
              </Card>
            ))}
          </div>
        )}
      </section>

      <Footer />
    </PageWrapper>
  );
}
