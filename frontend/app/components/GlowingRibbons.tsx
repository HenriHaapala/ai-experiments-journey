"use client";

import { useEffect, useRef } from "react";

export default function GlowingRibbons() {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // Use absolute sizing to ensure it covers a good portion of the top-left without causing a scrollbar
        let width = window.innerWidth;
        let height = 150;

        canvas.width = width;
        canvas.height = height;

        // Configuration for the ribbons using RGB strings to allow dynamic alpha fading
        const ribbons = [
            { rgb: "139, 0, 0", coreAlpha: 0.8, glowAlpha: 0.5, yOffset: 36, amplitude: 15, frequency: 0.0015, speed: 0.001 },
            { rgb: "255, 26, 26", coreAlpha: 0.7, glowAlpha: 0.4, yOffset: 36, amplitude: 20, frequency: 0.002, speed: 0.0015 },
            { rgb: "74, 4, 4", coreAlpha: 0.9, glowAlpha: 0.6, yOffset: 36, amplitude: 10, frequency: 0.0025, speed: 0.002 },
            { rgb: "255, 77, 77", coreAlpha: 0.6, glowAlpha: 0.3, yOffset: 36, amplitude: 18, frequency: 0.0018, speed: 0.0012 },
        ];

        let animationFrameId: number;
        let time = 0;

        const render = () => {
            // Clear canvas completely
            ctx.clearRect(0, 0, width, height);

            // Use a blend mode that mimics lighting
            ctx.globalCompositeOperation = "screen";

            for (let i = 0; i < ribbons.length; i++) {
                const ribbon = ribbons[i];

                ctx.beginPath();

                // Calculate starting and ending X positions dynamically based on a max-width layout of 1400px.
                // Assuming "HENRI HAAPALA" takes up roughly left + 200px width.
                const navContainerStart = Math.max(16, (width - 1400) / 2);
                const drawStartX = navContainerStart + 220;

                // Assuming "CASE FILES" starts around width - containerPadding - rightNavWidth
                // Right nav takes roughly 400px down to medium screens
                const drawEndX = Math.min(width - 16, navContainerStart + 1400 - 450);

                // Set the render boundary
                const drawWidth = Math.max(0, drawEndX - drawStartX);

                // Start path at our calculated left boundary
                ctx.moveTo(drawStartX, ribbon.yOffset);

                for (let x = drawStartX; x <= drawEndX; x += 5) {
                    // Slight taper at the very edges just to keep it smooth
                    const taper = 1;
                    const normalizedX = x - drawStartX; // Reset phase
                    const y = ribbon.yOffset +
                        Math.sin(normalizedX * ribbon.frequency + time * ribbon.speed * 1000) * ribbon.amplitude * taper +
                        Math.cos(time * ribbon.speed * 500 + i) * 5;

                    if (x === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                }

                // Simple gradients to fade out exactly at the calculated gap edges
                const gradientGlow = ctx.createLinearGradient(drawStartX, 0, drawEndX, 0);
                gradientGlow.addColorStop(0, `rgba(${ribbon.rgb}, 0)`);
                gradientGlow.addColorStop(0.05, `rgba(${ribbon.rgb}, ${ribbon.glowAlpha})`);
                gradientGlow.addColorStop(0.95, `rgba(${ribbon.rgb}, ${ribbon.glowAlpha})`);
                gradientGlow.addColorStop(1, `rgba(${ribbon.rgb}, 0)`);

                const gradientCore = ctx.createLinearGradient(drawStartX, 0, drawEndX, 0);
                gradientCore.addColorStop(0, `rgba(${ribbon.rgb}, 0)`);
                gradientCore.addColorStop(0.05, `rgba(${ribbon.rgb}, ${ribbon.coreAlpha})`);
                gradientCore.addColorStop(0.95, `rgba(${ribbon.rgb}, ${ribbon.coreAlpha})`);
                gradientCore.addColorStop(1, `rgba(${ribbon.rgb}, 0)`);

                // Draw the outer glow (thick, blurred)
                ctx.lineJoin = "round";
                ctx.lineCap = "round";

                ctx.shadowBlur = 30;
                ctx.shadowColor = `rgba(${ribbon.rgb}, ${ribbon.glowAlpha})`;
                ctx.lineWidth = 15;
                ctx.strokeStyle = gradientGlow;
                ctx.stroke();

                // Draw the inner core (thin, brighter)
                ctx.shadowBlur = 10;
                ctx.lineWidth = 4;
                ctx.strokeStyle = gradientCore;
                ctx.stroke();
            }

            time += 0.016; // approx 60fps increment
            animationFrameId = requestAnimationFrame(render);
        };

        render();

        const handleResize = () => {
            width = window.innerWidth;
            height = 150;
            canvas.width = width;
            canvas.height = height;
        };

        window.addEventListener("resize", handleResize);

        return () => {
            window.removeEventListener("resize", handleResize);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return (
        <div className="pointer-events-none fixed top-0 left-0 z-[110] h-[150px] w-full overflow-hidden opacity-90 mix-blend-screen">
            <canvas ref={canvasRef} className="h-full w-full" />
        </div>
    );
}
