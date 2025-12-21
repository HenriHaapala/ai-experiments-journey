"use client";

import { useEffect, useRef } from "react";

interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    size: number;
    color: string;
}

export default function AntigravityBackground() {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let animationFrameId: number;
        let particles: Particle[] = [];
        let mouse = { x: -9999, y: -9999 };

        // Configuration
        const PARTICLE_COUNT = 1500; // Adjust for density
        const REPULSION_RADIUS = 200;
        const REPULSION_FORCE = 5;
        const FRICTION = 0.95;
        const BASE_SPEED = 0.2;
        // Brighter red colors with higher opacity for better visibility
        const COLORS = ["rgba(255, 0, 0, 0.8)", "rgba(255, 80, 80, 0.6)", "rgba(200, 40, 40, 0.7)"];

        const init = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            particles = [];
            for (let i = 0; i < PARTICLE_COUNT; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: (Math.random() - 0.5) * BASE_SPEED,
                    vy: (Math.random() - 0.5) * BASE_SPEED,
                    size: Math.random() * 2 + 1, // Dash length/size
                    color: COLORS[Math.floor(Math.random() * COLORS.length)],
                });
            }
        };

        const handleMouseMove = (e: MouseEvent) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        };

        const handleResize = () => {
            init();
        };

        const update = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vignette effect
            const gradient = ctx.createRadialGradient(
                canvas.width / 2,
                canvas.height / 2,
                canvas.height / 3,
                canvas.width / 2,
                canvas.height / 2,
                canvas.height
            );
            gradient.addColorStop(0, "rgba(0,0,0,0)");
            gradient.addColorStop(1, "rgba(0,10,30,0.4)"); // Subtle blue tint at edges
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            particles.forEach((p) => {
                // Physics
                const dx = p.x - mouse.x;
                const dy = p.y - mouse.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < REPULSION_RADIUS) {
                    const angle = Math.atan2(dy, dx);
                    const force = (REPULSION_RADIUS - distance) / REPULSION_RADIUS;
                    const pushX = Math.cos(angle) * force * REPULSION_FORCE;
                    const pushY = Math.sin(angle) * force * REPULSION_FORCE;

                    p.vx += pushX;
                    p.vy += pushY;
                }

                // Apply friction to return to normal speed
                p.vx *= FRICTION;
                p.vy *= FRICTION;

                // Minimum movement (Brownian-ish)
                if (Math.abs(p.vx) < BASE_SPEED) p.vx += (Math.random() - 0.5) * 0.05;
                if (Math.abs(p.vy) < BASE_SPEED) p.vy += (Math.random() - 0.5) * 0.05;

                // Limit max speed
                const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
                const MAX_SPEED = 8;
                if (speed > MAX_SPEED) {
                    p.vx = (p.vx / speed) * MAX_SPEED;
                    p.vy = (p.vy / speed) * MAX_SPEED;
                }

                p.x += p.vx;
                p.y += p.vy;

                // Wrap around screen
                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;

                // Draw Dash
                ctx.beginPath();
                ctx.strokeStyle = p.color;
                ctx.lineWidth = 2;
                // Draw a small dash in direction of movement or just a small line
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p.x + p.vx * 2 + 1, p.y + p.vy * 2 + 1); // Elongate with speed
                ctx.stroke();
            });

            animationFrameId = requestAnimationFrame(update);
        };

        init();
        window.addEventListener("resize", handleResize);
        window.addEventListener("mousemove", handleMouseMove);
        update();

        return () => {
            window.removeEventListener("resize", handleResize);
            window.removeEventListener("mousemove", handleMouseMove);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className="fixed top-0 left-0 w-full h-full pointer-events-none z-[0]"
            aria-hidden="true"
        />
    );
}
