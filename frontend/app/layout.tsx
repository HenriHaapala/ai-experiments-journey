import type { Metadata } from "next";
import { Playfair_Display, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import AntigravityBackground from "./components/AntigravityBackground";
import CustomCursor from "./components/CustomCursor";

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "The Architect | Henri Haapala",
  description: "AI Portfolio and Confidential Case Files",
};

// Disable Next.js App Router caching for all pages
// This ensures users always see the latest content without hard refresh
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${playfair.variable} ${jetbrainsMono.variable} antialiased`}
      >
        <AntigravityBackground />
        <CustomCursor />
        {children}
      </body>
    </html>
  );
}
