"use client";

import { useEffect, useState } from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Label } from "recharts";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BrainCircuit, Info } from "lucide-react";
import { useSentinelStatus } from "@/hooks/useSentinelStatus";

interface ResonanceData {
    score: number;
    status: "nominal" | "degraded" | "critical";
    inferenceType: string;
    lastConcept: string;
}

export const ResonanceRateCard = () => {
    const { status } = useSentinelStatus();
    const [data, setData] = useState<ResonanceData>({
        score: 94,
        status: "nominal",
        inferenceType: "Bayesian Engine",
        lastConcept: "System stabilizing after kernel update",
    });

    useEffect(() => {
        if (status) {
            // Map status to Resonance score (logic: higher CPU/Mem -> lower resonance)
            const cpu = parseFloat(status.cpu) || 0;
            const mem = parseFloat(status.memory) || 0;
            const newScore = Math.max(70, 100 - (cpu * 0.15 + mem * 0.1));

            setData(prev => ({
                ...prev,
                score: newScore,
                status: cpu > 80 ? "degraded" : "nominal"
            }));
        }
    }, [status]);

    const chartData = [
        { name: "Resonance", value: data.score },
        { name: "Noise", value: 100 - data.score },
    ];

    const COLORS = ["#22d3ee", "rgba(255, 255, 255, 0.05)"];

    return (
        <Card className="bg-slate-950/50 backdrop-blur-2xl border-white/5 overflow-hidden relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-50 pointer-events-none" />
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-cyan-200/50 uppercase tracking-widest flex items-center gap-2">
                        <BrainCircuit className="w-4 h-4 text-cyan-400" />
                        Resonance Rate
                    </CardTitle>
                    <Badge variant="outline" className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20 font-mono">
                        {data.inferenceType}
                    </Badge>
                </div>
            </CardHeader>
            <CardContent>
                <div className="flex flex-col md:flex-row items-center gap-8">
                    <div className="w-48 h-48 relative">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={chartData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    startAngle={90}
                                    endAngle={450}
                                    paddingAngle={0}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    <Cell key="cell-0" fill={COLORS[0]} className="drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]" />
                                    <Cell key="cell-1" fill={COLORS[1]} />
                                    <Label
                                        value={`${Math.round(data.score)}%`}
                                        position="center"
                                        fill="#fff"
                                        style={{ fontSize: "24px", fontWeight: "bold", fontFamily: "monospace" }}
                                    />
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                        <motion.div
                            className="absolute inset-0 flex items-center justify-center -z-10"
                            animate={{
                                scale: [1, 1.1, 1],
                                opacity: [0.1, 0.2, 0.1]
                            }}
                            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                        >
                            <div className="w-32 h-32 rounded-full bg-cyan-500 blur-3xl opacity-20" />
                        </motion.div>
                    </div>

                    <div className="flex-1 space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                                <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Status</p>
                                <p className="text-white font-mono flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                    NOMINAL
                                </p>
                            </div>
                            <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                                <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Entropy Offset</p>
                                <p className="text-white font-mono">0.0032μ</p>
                            </div>
                        </div>

                        <div className="bg-cyan-500/5 rounded-lg p-3 border border-cyan-500/10">
                            <p className="text-[10px] text-cyan-400/70 uppercase font-bold mb-2 flex items-center gap-1">
                                <Info className="w-3 h-3" />
                                Latest Cognitive Link
                            </p>
                            <AnimatePresence mode="wait">
                                <motion.p
                                    key={data.lastConcept}
                                    initial={{ opacity: 0, y: 5 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -5 }}
                                    className="text-xs text-cyan-100 font-medium leading-relaxed"
                                >
                                    "{data.lastConcept}"
                                </motion.p>
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};
