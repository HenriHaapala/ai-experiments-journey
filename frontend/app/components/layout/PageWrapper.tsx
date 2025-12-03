import { ReactNode } from "react";

interface PageWrapperProps {
  children: ReactNode;
}

export default function PageWrapper({ children }: PageWrapperProps) {
  return (
    <div className="min-h-screen bg-page-outer font-sans text-text-light">
      <div className="relative mx-auto min-h-screen max-w-[1400px] bg-page-inner shadow-red-glow">
        {children}
      </div>
    </div>
  );
}
