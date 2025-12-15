export default function Footer() {
  return (
    <footer className="border-t border-primary-red/20 bg-black px-4 py-8 md:px-8">
      <div className="mx-auto max-w-[1400px]">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <p className="font-mono text-xs uppercase tracking-wider text-text-gray">
            © 2025 HENRI HAAPALA
          </p>
          <div className="flex gap-6 font-mono text-xs uppercase tracking-wider text-text-gray">
            <span>DJANGO</span>
            <span>·</span>
            <span>NEXT.JS</span>
            <span>·</span>
            <span>AI</span>
          </div>
          <p className="font-mono text-xs uppercase tracking-wider text-text-gray">
            CLASSIFIED
          </p>
        </div>
      </div>
    </footer>
  );
}
