'use client';

import { useEffect, useState } from 'react';

export default function CustomCursor() {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isPointer, setIsPointer] = useState(false);
    const [isClicking, setIsClicking] = useState(false);

    useEffect(() => {
        const updateCursor = (e: MouseEvent) => {
            setPosition({ x: e.clientX, y: e.clientY });

            const target = e.target as HTMLElement;
            setIsPointer(
                window.getComputedStyle(target).cursor === 'pointer' ||
                target.tagName === 'BUTTON' ||
                target.tagName === 'A' ||
                target.closest('button') !== null ||
                target.closest('a') !== null
            );
        };

        const onMouseDown = () => setIsClicking(true);
        const onMouseUp = () => setIsClicking(false);

        window.addEventListener('mousemove', updateCursor);
        window.addEventListener('mousedown', onMouseDown);
        window.addEventListener('mouseup', onMouseUp);

        return () => {
            window.removeEventListener('mousemove', updateCursor);
            window.removeEventListener('mousedown', onMouseDown);
            window.removeEventListener('mouseup', onMouseUp);
        };
    }, []);

    return (
        <div
            className="fixed top-0 left-0 pointer-events-none z-[9999] transition-[opacity] duration-300"
            style={{
                transform: `translate3d(${position.x}px, ${position.y}px, 0)`,
                opacity: position.x === 0 && position.y === 0 ? 0 : 1,
            }}
        >
            {/* HUD Container - centered on cursor */}
            <div className="relative">

                {/* Outer Rotating Scan Ring (Dashed) */}
                <div
                    className={`absolute top-0 left-0 -translate-x-1/2 -translate-y-1/2 rounded-full border border-red-600/60 border-dashed transition-all duration-500 ease-out animate-[spin_10s_linear_infinite] ${isPointer ? 'w-10 h-10 opacity-80 border-red-500' : 'w-12 h-12 opacity-30'
                        }`}
                />

                {/* Inner Target Ring (Solid/Cornered) */}
                <div
                    className={`absolute top-0 left-0 -translate-x-1/2 -translate-y-1/2 rounded-full border border-red-500 transition-all duration-200 ease-out ${isPointer ? 'w-5 h-5 opacity-100 scale-110 shadow-[0_0_15px_rgba(255,0,0,0.6)]' : 'w-2 h-2 opacity-80'
                        }`}
                />

                {/* Crosshair Lines - Reduced Size */}
                <div className={`absolute top-0 left-0 -translate-x-1/2 -translate-y-1/2 bg-red-600 transition-all duration-300 ${isPointer ? 'w-[16px] h-[1px]' : 'w-[20px] h-[1px]'}`} />
                <div className={`absolute top-0 left-0 -translate-x-1/2 -translate-y-1/2 bg-red-600 transition-all duration-300 ${isPointer ? 'w-[1px] h-[16px]' : 'w-[1px] h-[20px]'}`} />

                {/* Center Dot */}
                <div className={`absolute top-0 left-0 -translate-x-1/2 -translate-y-1/2 rounded-full bg-red-500 shadow-[0_0_10px_rgba(255,0,0,0.8)] transition-all duration-150 ${isClicking ? 'w-1.5 h-1.5' : 'w-1 h-1'}`} />

                {/* HUD Data Text - Scaled down and moved closer */}
                <div className="absolute top-3 left-4 text-[9px] font-mono text-red-500/80 leading-tight hidden sm:block whitespace-nowrap pointer-events-none scale-90 origin-top-left">
                    <div className="flex flex-col gap-0.5">
                        <span className="tracking-widest">T-800 SYS</span>
                        <span>POS: {Math.round(position.x)} / {Math.round(position.y)}</span>
                        {isPointer && <span className="font-bold animate-pulse text-red-400">TARGET ACQUIRED</span>}
                    </div>
                </div>

            </div>
        </div>
    );
}
