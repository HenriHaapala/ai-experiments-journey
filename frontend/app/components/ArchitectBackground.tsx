"use client";

import { useEffect, useState } from "react";
import Image from "next/image";

const IMAGES = [
  "/images/architect/1.jpg",
  "/images/architect/2.jpg",
  "/images/architect/3.jpg",
];

export default function ArchitectBackground() {
  const [activeImage, setActiveImage] = useState<string | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Initial delay
    const startTimeout = setTimeout(() => {
      triggerRandomImage();
    }, 1000);

    const triggerRandomImage = () => {
      // Pick a random image
      const randomImg = IMAGES[Math.floor(Math.random() * IMAGES.length)];
      setActiveImage(randomImg);
      setIsVisible(true);

      // Hide after some time (e.g., 4-6 seconds)
      const visibleDuration = 4000 + Math.random() * 2000;
      setTimeout(() => {
        setIsVisible(false);

        // Wait before showing next one (e.g., 2-4 seconds)
        const hiddenDuration = 2000 + Math.random() * 2000;
        setTimeout(triggerRandomImage, hiddenDuration + 1000); // +1000 for fade out
      }, visibleDuration);
    };

    return () => clearTimeout(startTimeout);
  }, []);

  return (
    <div className="pointer-events-none absolute inset-0 z-[-1] overflow-hidden">
      {IMAGES.map((src) => (
        <div
          key={src}
          className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${activeImage === src && isVisible ? "opacity-20" : "opacity-0"
            }`}
        >
          <Image
            src={src}
            alt="Background"
            fill
            className="object-cover grayscale"
            priority
          />
          {/* Vignette overlay to blend with dark background */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-transparent to-[#0a0a0a]" />
          <div className="absolute inset-0 bg-gradient-to-r from-[#0a0a0a] via-transparent to-[#0a0a0a]" />
        </div>
      ))}
    </div>
  );
}
