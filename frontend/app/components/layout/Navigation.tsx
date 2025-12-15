"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

export default function Navigation() {
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navLinks = [
    { href: "/", label: "CASE FILES" },
    { href: "/roadmap", label: "STUDIES" },
    { href: "/learning", label: "MCP LEARNING LOG" }
  ];

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);
  const closeMenu = () => setIsMenuOpen(false);

  return (
    <nav className="sticky top-0 z-[100] border-b border-primary-red/20 bg-black/90 px-4 py-4 backdrop-blur-md md:px-8 md:py-5">
      <div className="mx-auto flex max-w-[1400px] items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-3 font-mono text-sm uppercase tracking-wider text-text-light no-underline md:text-base"
          onClick={closeMenu}
        >
          <span className="text-primary-red">Ⅱ</span>
          <span>HENRI HAAPALA</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden gap-8 md:flex">
          {navLinks.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`font-mono text-xs uppercase tracking-wider no-underline transition-colors duration-200 ${
                pathname === href
                  ? "text-primary-red"
                  : "text-text-gray hover:text-text-light"
              }`}
            >
              {label}
            </Link>
          ))}
        </div>

        {/* Mobile Hamburger Button */}
        <button
          onClick={toggleMenu}
          className="flex h-10 w-10 flex-col items-center justify-center gap-1.5 md:hidden"
          aria-label="Toggle menu"
        >
          <span
            className={`h-0.5 w-6 bg-primary-red transition-all duration-300 ${
              isMenuOpen ? "translate-y-2 rotate-45" : ""
            }`}
          />
          <span
            className={`h-0.5 w-6 bg-primary-red transition-all duration-300 ${
              isMenuOpen ? "opacity-0" : ""
            }`}
          />
          <span
            className={`h-0.5 w-6 bg-primary-red transition-all duration-300 ${
              isMenuOpen ? "-translate-y-2 -rotate-45" : ""
            }`}
          />
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      <div
        className={`overflow-hidden transition-all duration-300 md:hidden ${
          isMenuOpen ? "max-h-48 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="flex flex-col gap-4 pb-4 pt-6">
          {navLinks.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              onClick={closeMenu}
              className={`text-center text-lg no-underline transition-colors duration-300 ${
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
