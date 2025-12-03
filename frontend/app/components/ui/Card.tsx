import { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
}

export default function Card({ children, className = "" }: CardProps) {
  return (
    <div
      className={`bg-card rounded-lg border border-primary-red/30 p-8 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary-red/50 ${className}`}
    >
      {children}
    </div>
  );
}
