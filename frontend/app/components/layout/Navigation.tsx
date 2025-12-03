"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-[100] border-b border-primary-red/30 bg-bg-nav p-6 backdrop-blur-[10px]">
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="text-xl font-bold tracking-[0.05em] text-primary-red no-underline"
        >
          HENRI HAAPALA
        </Link>
        <div className="flex gap-8">
          {[
            { href: "/", label: "Home" },
            { href: "/roadmap", label: "Roadmap" },
            { href: "/learning", label: "Learning Log" }
          ].map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`no-underline transition-colors duration-300 ${
                pathname === href
                  ? "text-primary-red"
                  : "text-text-light hover:text-primary-red"
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
