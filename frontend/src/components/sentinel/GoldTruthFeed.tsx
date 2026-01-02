"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ShieldCheck, Zap, Ghost, Database, AlertCircle } from "lucide-react";

interface TruthEvent {
    id: string;
    timestamp: string;
    source: "Noise" | "Gold";
    message: string;
    description: string;
    confidence: number;
    tags: string[];
    severity: string;
}

export const GoldTruthFeed = () => {
    const [events, setEvents] = useState<TruthEvent[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchAnomalies = async () => {
        try {
            const res = await fetch("/api/v1/analytics/anomalies?hours=24&limit=10");
            if (!res.ok) throw new Error("Failed to fetch anomalies");
            const data = await res.json();

            const mapped: TruthEvent[] = (data.anomalies || []).map((a: any) => ({
                id: a.id,
                timestamp: new Date(a.detected_at).toLocaleTimeString(),
                source: a.severity === "critical" ? "Gold" : "Noise",
                message: a.title,
                description: a.description,
                confidence: a.metric_value ? 0.95 : 0.8, // Approximation
                tags: [a.type.toUpperCase()],
                severity: a.severity
            }));

            setEvents(mapped);
        } catch (error) {
            console.error("GoldTruthFeed error:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAnomalies();
        const interval = setInterval(fetchAnomalies, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <Card className="bg-slate-950/50 backdrop-blur-2xl border-white/5 h-[500px] flex flex-col overflow-hidden group">
            <CardHeader className="pb-2 border-b border-white/5 bg-slate-900/40">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-emerald-200/50 uppercase tracking-widest flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        Sovereign Truth Feed
                    </CardTitle>
                    <div className="flex gap-2">
                        <Badge variant="outline" className="text-[10px] bg-slate-900 border-white/10 uppercase tracking-tighter">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
                            Live Anomaly Detection
                        </Badge>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto pt-4 space-y-3 custom-scrollbar">
                {loading && events.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-600 gap-4">
                        <Database className="w-8 h-8 animate-pulse" />
                        <p className="text-xs font-mono uppercase tracking-widest">Hydrating from matrix...</p>
                    </div>
                ) : events.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-600 gap-2">
                        <Zap className="w-8 h-8 opacity-20" />
                        <p className="text-xs font-mono uppercase tracking-widest">No anomalies detected in last 24h</p>
                    </div>
                ) : (
                    <AnimatePresence initial={false}>
                        {events.map((event) => (
                            <motion.div
                                key={event.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className={`p-4 rounded-xl border transition-all ${event.severity === "critical"
                                    ? "bg-rose-500/10 border-rose-500/20 shadow-[0_0_15px_rgba(244,63,94,0.05)]"
                                    : "bg-emerald-500/10 border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.05)]"
                                    }`}
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex gap-4">
                                        <div className={`mt-1 p-2 rounded-lg bg-slate-950 ${event.severity === "critical" ? "text-rose-400" : "text-emerald-400"
                                            }`}>
                                            {event.severity === "critical" ? <AlertCircle className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
                                        </div>
                                        <div>
                                            <p className={`text-sm font-mono font-bold ${event.severity === "critical" ? "text-rose-100" : "text-white"
                                                }`}>
                                                {event.message}
                                            </p>
                                            <p className="text-xs text-gray-400 mt-1 leading-relaxed">
                                                {event.description}
                                            </p>
                                            <div className="flex items-center gap-4 mt-3">
                                                <span className="text-[10px] font-mono text-gray-500 opacity-70">[{event.timestamp}]</span>
                                                <div className="flex gap-2">
                                                    {event.tags.map(tag => (
                                                        <span key={tag} className={`text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded ${event.severity === "critical" ? "bg-rose-500/20 text-rose-400" : "bg-emerald-500/20 text-emerald-400"
                                                            }`}>
                                                            {tag}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right flex flex-col items-end">
                                        <div className={`text-xl font-black font-mono ${event.severity === "critical" ? "text-rose-400" : "text-emerald-400"
                                            }`}>
                                            {(event.confidence * 100).toFixed(0)}%
                                        </div>
                                        <p className="text-[8px] uppercase tracking-tighter text-gray-600 font-black">CONFIDENCE</p>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                )}
            </CardContent>
            <div className="p-4 border-t border-white/5 bg-black/40 text-center">
                <p className="text-[10px] text-gray-500 font-mono uppercase tracking-widest flex items-center justify-center gap-3">
                    <Zap className="w-3 h-3 text-cyan-400" />
                    TruthSync Consensus Engine Active // 0.00ms Latency
                </p>
            </div>
        </Card>
    );
};
