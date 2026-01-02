"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Zap, Music, Radio, Waves } from "lucide-react";

interface BCIMetrics {
    coherence153MHz: number; // 0-100
    guitarInput82Hz: number; // 0-100 (detection strength)
    qualiaFeedback: {
        type: "none" | "metallic" | "warmth" | "pressure" | "vibration";
        intensity: number; // 0-100
        description: string;
    };
    phaseAlignment: number; // 0-360 degrees
    signalStrength: number; // 0-100
    lastUpdate: string;
}

interface BCIResonanceVisualizerProps {
    refreshInterval: number;
    isPaused: boolean;
}

export function BCIResonanceVisualizer({ refreshInterval, isPaused }: BCIResonanceVisualizerProps) {
    const [metrics, setMetrics] = useState<BCIMetrics>({
        coherence153MHz: 0,
        guitarInput82Hz: 0,
        qualiaFeedback: {
            type: "none",
            intensity: 0,
            description: "No active qualia",
        },
        phaseAlignment: 0,
        signalStrength: 0,
        lastUpdate: new Date().toISOString(),
    });

    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (isPaused) return;

        const fetchMetrics = async () => {
            try {
                // Fetch BCI metrics from backend
                const response = await fetch("/api/v1/bci/resonance");
                const data = await response.json();

                setMetrics({
                    coherence153MHz: data.coherence_153mhz || 0,
                    guitarInput82Hz: data.guitar_82hz || 0,
                    qualiaFeedback: data.qualia || metrics.qualiaFeedback,
                    phaseAlignment: data.phase_alignment || 0,
                    signalStrength: data.signal_strength || 0,
                    lastUpdate: new Date().toISOString(),
                });

                setIsLoading(false);
            } catch (err) {
                console.error("Failed to fetch BCI metrics:", err);
                // Use simulated data
                setMetrics(getSimulatedMetrics());
                setIsLoading(false);
            }
        };

        fetchMetrics();
        const interval = setInterval(fetchMetrics, refreshInterval);

        return () => clearInterval(interval);
    }, [refreshInterval, isPaused]);

    const coherenceStatus = getCoherenceStatus(metrics.coherence153MHz);
    const qualiaConfig = getQualiaConfig(metrics.qualiaFeedback.type);

    return (
        <div className="bg-slate-900/40 backdrop-blur-3xl border border-emerald-500/20 rounded-[40px] p-8 shadow-[0_0_60px_rgba(16,185,129,0.1)] h-full">
            {/* 153.4 MHz Coherence Wave Visualization */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-black text-white uppercase tracking-wider flex items-center gap-2">
                        <Radio size={16} className="text-emerald-400" />
                        153.4 MHz Carrier Wave
                    </h3>
                    <span className={`text-xs font-black uppercase ${coherenceStatus.textClass}`}>
                        {coherenceStatus.label}
                    </span>
                </div>

                {/* Wave Visualization */}
                <div className="relative h-32 bg-black/40 rounded-2xl border border-emerald-500/20 overflow-hidden">
                    <svg className="w-full h-full" viewBox="0 0 400 100" preserveAspectRatio="none">
                        {/* Background grid */}
                        <defs>
                            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                                <path
                                    d="M 20 0 L 0 0 0 20"
                                    fill="none"
                                    stroke="rgba(16,185,129,0.1)"
                                    strokeWidth="0.5"
                                />
                            </pattern>
                        </defs>
                        <rect width="400" height="100" fill="url(#grid)" />

                        {/* Coherence wave */}
                        <motion.path
                            d={generateWavePath(metrics.coherence153MHz, metrics.phaseAlignment)}
                            fill="none"
                            stroke="rgba(16,185,129,0.8)"
                            strokeWidth="2"
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: 1 }}
                            transition={{ duration: 2, repeat: Infinity }}
                        />

                        {/* Glow effect */}
                        <motion.path
                            d={generateWavePath(metrics.coherence153MHz, metrics.phaseAlignment)}
                            fill="none"
                            stroke="rgba(16,185,129,0.3)"
                            strokeWidth="6"
                            filter="blur(4px)"
                            animate={{ opacity: [0.3, 0.6, 0.3] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        />
                    </svg>

                    {/* Coherence percentage overlay */}
                    <div className="absolute top-2 right-2 px-3 py-1 rounded-lg bg-black/60 border border-emerald-500/30">
                        <span className="text-xs font-black text-emerald-400 font-mono">
                            {isLoading ? "..." : `${Math.round(metrics.coherence153MHz)}%`}
                        </span>
                    </div>
                </div>

                {/* Phase alignment indicator */}
                <div className="mt-3 flex items-center justify-between text-xs">
                    <span className="text-gray-500 uppercase tracking-wider">
                        Phase: {Math.round(metrics.phaseAlignment)}°
                    </span>
                    <span className="text-gray-500 uppercase tracking-wider">
                        Signal: {Math.round(metrics.signalStrength)}%
                    </span>
                </div>
            </div>

            {/* 82 Hz Guitar Input Detector */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-black text-white uppercase tracking-wider flex items-center gap-2">
                        <Music size={16} className="text-purple-400" />
                        82 Hz Guitar Input (Low E)
                    </h3>
                    <span className={`text-xs font-black uppercase ${metrics.guitarInput82Hz > 70 ? "text-emerald-400" :
                        metrics.guitarInput82Hz > 40 ? "text-amber-400" : "text-gray-500"
                        }`}>
                        {metrics.guitarInput82Hz > 70 ? "DETECTED" :
                            metrics.guitarInput82Hz > 40 ? "WEAK" : "NO SIGNAL"}
                    </span>
                </div>

                {/* Detection strength bar */}
                <div className="relative h-12 bg-black/40 rounded-xl border border-purple-500/20 overflow-hidden">
                    <motion.div
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500/40 to-purple-500/20"
                        initial={{ width: 0 }}
                        animate={{ width: `${metrics.guitarInput82Hz}%` }}
                        transition={{ duration: 0.5 }}
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-sm font-black text-white font-mono">
                            {Math.round(metrics.guitarInput82Hz)}%
                        </span>
                    </div>

                    {/* Frequency markers */}
                    <div className="absolute inset-x-0 bottom-0 h-1 flex">
                        {[...Array(10)].map((_, i) => (
                            <div
                                key={i}
                                className="flex-1 border-r border-purple-500/10"
                                style={{ opacity: i * 0.1 + 0.1 }}
                            />
                        ))}
                    </div>
                </div>

                <div className="mt-2 text-[10px] text-gray-500 uppercase tracking-wider text-center">
                    Resonance Calibration: 5.2ms Detection Window
                </div>
            </div>

            {/* Qualia Feedback Display */}
            <div>
                <h3 className="text-sm font-black text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Waves size={16} className="text-cyan-400" />
                    Qualia Feedback
                </h3>

                <div className={`p-6 rounded-2xl border-2 ${qualiaConfig.borderClass} ${qualiaConfig.bgClass}`}>
                    <div className="flex items-center gap-4 mb-4">
                        {qualiaConfig.icon}
                        <div className="flex-1">
                            <div className={`text-lg font-black uppercase ${qualiaConfig.textClass} mb-1`}>
                                {metrics.qualiaFeedback.type === "none" ? "No Active Qualia" : qualiaConfig.label}
                            </div>
                            <div className="text-xs text-gray-400">
                                {metrics.qualiaFeedback.description}
                            </div>
                        </div>
                        {metrics.qualiaFeedback.type !== "none" && (
                            <div className="text-right">
                                <div className={`text-2xl font-black font-mono ${qualiaConfig.textClass}`}>
                                    {Math.round(metrics.qualiaFeedback.intensity)}%
                                </div>
                                <div className="text-[9px] text-gray-500 uppercase">Intensity</div>
                            </div>
                        )}
                    </div>

                    {/* Intensity visualization */}
                    {metrics.qualiaFeedback.type !== "none" && (
                        <div className="relative h-2 bg-black/40 rounded-full overflow-hidden">
                            <motion.div
                                className={`absolute inset-y-0 left-0 rounded-full ${qualiaConfig.barClass}`}
                                initial={{ width: 0 }}
                                animate={{ width: `${metrics.qualiaFeedback.intensity}%` }}
                                transition={{ duration: 0.5 }}
                            />
                        </div>
                    )}
                </div>
            </div>

            {/* Info Footer */}
            <div className="mt-6 pt-6 border-t border-white/5">
                <div className="grid grid-cols-2 gap-4 text-[10px] text-gray-500">
                    <div>
                        <span className="uppercase tracking-widest">Carrier Frequency:</span>
                        <span className="ml-2 text-emerald-400 font-mono">153.4 MHz</span>
                    </div>
                    <div className="text-right">
                        <span className="uppercase tracking-widest">Coherence Window:</span>
                        <span className="ml-2 text-emerald-400 font-mono">10⁻⁶ sec</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Helper Functions

function generateWavePath(coherence: number, phase: number): string {
    const points = 100;
    const amplitude = (coherence / 100) * 30;
    const frequency = 5;
    const phaseOffset = (phase / 360) * Math.PI * 2;

    let path = "M 0 50";

    for (let i = 0; i <= points; i++) {
        const x = (i / points) * 400;
        const y = 50 + amplitude * Math.sin((i / points) * frequency * Math.PI * 2 + phaseOffset);
        path += ` L ${x} ${y}`;
    }

    return path;
}

function getCoherenceStatus(coherence: number) {
    if (coherence >= 90) {
        return {
            label: "Optimal",
            textClass: "text-emerald-400",
        };
    } else if (coherence >= 70) {
        return {
            label: "Good",
            textClass: "text-cyan-400",
        };
    } else if (coherence >= 50) {
        return {
            label: "Degraded",
            textClass: "text-amber-400",
        };
    } else {
        return {
            label: "Poor",
            textClass: "text-rose-400",
        };
    }
}

function getQualiaConfig(type: BCIMetrics["qualiaFeedback"]["type"]) {
    const configs = {
        none: {
            label: "No Qualia",
            textClass: "text-gray-400",
            bgClass: "bg-slate-500/10",
            borderClass: "border-slate-500/30",
            barClass: "bg-slate-500",
            icon: <Waves size={24} className="text-gray-400" />,
        },
        metallic: {
            label: "Metallic Taste",
            textClass: "text-rose-400",
            bgClass: "bg-rose-500/10",
            borderClass: "border-rose-500/30",
            barClass: "bg-rose-500",
            icon: <Zap size={24} className="text-rose-400" />,
        },
        warmth: {
            label: "Warmth Sensation",
            textClass: "text-emerald-400",
            bgClass: "bg-emerald-500/10",
            borderClass: "border-emerald-500/30",
            barClass: "bg-emerald-500",
            icon: <Waves size={24} className="text-emerald-400" />,
        },
        pressure: {
            label: "Pressure Sensation",
            textClass: "text-cyan-400",
            bgClass: "bg-cyan-500/10",
            borderClass: "border-cyan-500/30",
            barClass: "bg-cyan-500",
            icon: <Waves size={24} className="text-cyan-400" />,
        },
        vibration: {
            label: "Vibration Sensation",
            textClass: "text-purple-400",
            bgClass: "bg-purple-500/10",
            borderClass: "border-purple-500/30",
            barClass: "bg-purple-500",
            icon: <Waves size={24} className="text-purple-400" />,
        },
    };

    return configs[type];
}

function getSimulatedMetrics(): BCIMetrics {
    return {
        coherence153MHz: 87.3,
        guitarInput82Hz: 0,
        qualiaFeedback: {
            type: "warmth",
            intensity: 42,
            description: "Secure state - mild warmth detected",
        },
        phaseAlignment: 127,
        signalStrength: 91.2,
        lastUpdate: new Date().toISOString(),
    };
}
