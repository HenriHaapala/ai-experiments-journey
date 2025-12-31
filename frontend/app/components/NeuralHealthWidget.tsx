"use client";

import { useEffect, useState } from "react";

type Metrics = {
    faithfulness: number;
    answer_relevancy: number;
    context_precision: number;
    timestamp: string;
};

export default function NeuralHealthWidget() {
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                // Try localhost:8001 directly (standard docker mapping)
                const res = await fetch("http://localhost:8001/metrics");
                if (res.ok) {
                    const data = await res.json();
                    setMetrics(data);
                    setError(false);
                } else {
                    setError(true);
                }
            } catch (e) {
                console.error("Failed to fetch neural metrics", e);
                setError(true);
            } finally {
                setLoading(false);
            }
        };

        fetchMetrics();
        const interval = setInterval(fetchMetrics, 30000);
        return () => clearInterval(interval);
    }, []);

    // Helper to colorize scores
    const getScoreColor = (score: number) => {
        if (score >= 0.8) return "text-emerald-400";
        if (score >= 0.5) return "text-yellow-400";
        return "text-primary-red";
    };

    const getScoreLabel = (score: number) => {
        return (score * 100).toFixed(0) + "%";
    };

    return (
        <div className="mt-8 border-t border-[#241010] pt-6">
            <div className="mb-3 flex items-center justify-between">
                <h3 className="font-mono text-[11px] uppercase tracking-[0.2em] text-[#c35b5b]">
                    Neural Health Status
                </h3>
                <div className="flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${loading ? "bg-yellow-400" : error ? "bg-red-500" : "bg-emerald-400"}`}></span>
                        <span className={`relative inline-flex rounded-full h-2 w-2 ${loading ? "bg-yellow-500" : error ? "bg-red-600" : "bg-emerald-500"}`}></span>
                    </span>
                    <span className="font-mono text-[10px] uppercase text-text-gray">
                        {loading ? "INITIALIZING..." : error ? "CONNECTION LOST" : "LIVE MONITORING"}
                    </span>
                </div>
            </div>

            {loading ? (
                <div className="border border-[#1a1a1a] bg-[#0b0b0b] p-4 text-center">
                    <p className="font-mono text-xs text-text-gray uppercase tracking-widest animate-pulse">
                        Establish Link...
                    </p>
                </div>
            ) : error || !metrics ? (
                <div className="border border-[#1a1a1a] bg-[#0b0b0b] p-4 text-center">
                    <p className="font-mono text-xs text-primary-red uppercase tracking-widest animate-pulse">
                        Signal Lost - Reconnecting...
                    </p>
                </div>
            ) : (
                <>
                    <div className="grid grid-cols-3 gap-2">
                        {/* Faithfulness */}
                        <div className="bg-[#0b0b0b] border border-[#1a1a1a] p-3 rounded-sm relative overflow-hidden group">
                            <div className="absolute top-0 left-0 w-[2px] h-full bg-emerald-500/20 group-hover:bg-emerald-500/50 transition-colors"></div>
                            <p className="font-mono text-[9px] uppercase tracking-wider text-text-gray mb-1">Faithfulness</p>
                            <p className={`font-mono text-xl font-bold ${getScoreColor(metrics.faithfulness)}`}>
                                {getScoreLabel(metrics.faithfulness)}
                            </p>
                        </div>

                        {/* Relevancy */}
                        <div className="bg-[#0b0b0b] border border-[#1a1a1a] p-3 rounded-sm relative overflow-hidden group">
                            <div className="absolute top-0 left-0 w-[2px] h-full bg-blue-500/20 group-hover:bg-blue-500/50 transition-colors"></div>
                            <p className="font-mono text-[9px] uppercase tracking-wider text-text-gray mb-1">Relevancy</p>
                            <p className={`font-mono text-xl font-bold ${getScoreColor(metrics.answer_relevancy)}`}>
                                {getScoreLabel(metrics.answer_relevancy)}
                            </p>
                        </div>

                        {/* Precision */}
                        <div className="bg-[#0b0b0b] border border-[#1a1a1a] p-3 rounded-sm relative overflow-hidden group">
                            <div className="absolute top-0 left-0 w-[2px] h-full bg-purple-500/20 group-hover:bg-purple-500/50 transition-colors"></div>
                            <p className="font-mono text-[9px] uppercase tracking-wider text-text-gray mb-1">Precision</p>
                            <p className={`font-mono text-xl font-bold ${getScoreColor(metrics.context_precision)}`}>
                                {getScoreLabel(metrics.context_precision)}
                            </p>
                        </div>
                    </div>

                    <div className="mt-2 text-right">
                        <p className="font-mono text-[9px] text-[#444]">
                            LAST UPDATE: {new Date(metrics.timestamp).toLocaleTimeString()}
                        </p>
                    </div>
                </>
            )}
        </div>
    );
}
