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
      <section className="bg-radial-red px-4 py-8 text-center md:p-16">
        <div className="mx-auto max-w-[900px]">
          <h1 className="text-text-light mb-3 text-[2rem] font-black tracking-tight md:mb-4 md:text-[3.5rem]">
            AI Career Roadmap 2025
          </h1>
          <p className="mb-3 text-base font-light text-text-gray md:mb-4 md:text-xl">
            My journey through AI engineering and machine learning
          </p>
          <div className="divider-red mx-auto" />
        </div>
      </section>

      {/* Content Section */}
      <section className="mx-auto max-w-[1200px] px-4 py-6 pb-12 md:px-8 md:py-8 md:pb-16">
        {loading && (
          <div className="p-8 text-center text-text-gray md:p-12">
            <p className="text-base md:text-lg">Loading roadmap...</p>
          </div>
        )}

        {error && (
          <div className="bg-card rounded-lg border border-primary-red/50 p-8 text-center md:p-12">
            <p className="text-base text-primary-red red-text-stroke md:text-lg">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <div className="flex flex-col gap-6 md:gap-8">
            {sections.map((section) => (
              <Card key={section.id}>
                <h2 className="mb-3 text-xl font-bold red-text-stroke text-primary-red md:mb-4 md:text-[1.75rem]">
                  {section.order}. {section.title}
                </h2>

                {section.description && (
                  <p className="mb-4 text-sm leading-relaxed text-text-gray md:mb-6 md:text-base">
                    {section.description}
                  </p>
                )}

                <ul className="flex flex-col gap-3 p-0 md:gap-4">
                  {section.items
                    .filter((item) => item.is_active)
                    .map((item) => (
                      <li
                        key={item.id}
                        className="list-none rounded border border-primary-red/20 bg-black/30 p-3 transition-colors hover:bg-primary-red/10 md:p-4"
                      >
                        <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-text-light md:mb-2 md:text-base">
                          <span className="text-primary-red red-text-stroke">▸</span>
                          {item.title}
                        </div>
                        {item.description && (
                          <div className="pl-4 text-xs leading-normal text-text-gray md:pl-5 md:text-sm">
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
