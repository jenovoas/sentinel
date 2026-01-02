"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import {
    Brain,
    Heart,
    Shield,
    Zap,
    Database,
    Network,
    Eye,
    Sparkles,
    Activity,
    Terminal,
    Cpu,
    Lock
} from "lucide-react";

export type DimensionalLayer =
    | "merkabah"      // Centro - Estado unificado
    | "neural"        // Capa neural - eBPF, Kernel
    | "cognitive"     // Capa cognitiva - AI, Oracle
    | "security"      // Capa seguridad - TruthSync, Guardian
    | "quantum"       // Capa cuántica - Coherence, Entropy
    | "observability" // Capa observabilidad - Metrics, Logs
    | "devops";       // Capa DevOps - Infrastructure

interface DimensionalNavProps {
    currentLayer: DimensionalLayer;
    onLayerChange: (layer: DimensionalLayer) => void;
}

export const DimensionalNav = ({ currentLayer, onLayerChange }: DimensionalNavProps) => {
    const [hoveredLayer, setHoveredLayer] = useState<DimensionalLayer | null>(null);

    const layers: Array<{
        id: DimensionalLayer;
        name: string;
        icon: React.ReactNode;
        color: string;
        description: string;
        frequency: string; // Frecuencia de resonancia
    }> = [
            {
                id: "merkabah",
                name: "Merkabah Core",
                icon: <Sparkles size={20} />,
                color: "purple",
                description: "Unified coherence state - Brain-Heart-Field synchronization",
                frequency: "432 Hz"
            },
            {
                id: "neural",
                name: "Neural Layer",
                icon: <Brain size={20} />,
                color: "cyan",
                description: "eBPF kernel monitoring, Ring-0 security, system calls",
                frequency: "40 Hz"
            },
            {
                id: "cognitive",
                name: "Cognitive Layer",
                icon: <Eye size={20} />,
                color: "indigo",
                description: "AI Oracle, semantic analysis, predictive intelligence",
                frequency: "8 Hz"
            },
            {
                id: "security",
                name: "Security Layer",
                icon: <Shield size={20} />,
                color: "emerald",
                description: "TruthSync verification, Guardian Alpha, threat detection",
                frequency: "528 Hz"
            },
            {
                id: "quantum",
                name: "Quantum Layer",
                icon: <Zap size={20} />,
                color: "amber",
                description: "Coherence optimization, entropy reduction, ground state",
                frequency: "963 Hz"
            },
            {
                id: "observability",
                name: "Observability Layer",
                icon: <Activity size={20} />,
                color: "rose",
                description: "Prometheus metrics, Grafana dashboards, real-time telemetry",
                frequency: "256 Hz"
            },
            {
                id: "devops",
                name: "DevOps Layer",
                icon: <Terminal size={20} />,
                color: "orange",
                description: "Infrastructure control, Docker, networking, system logs",
                frequency: "128 Hz"
            }
        ];

    const activeLayer = layers.find(l => l.id === currentLayer);
    const displayLayer = hoveredLayer ? layers.find(l => l.id === hoveredLayer) : activeLayer;

    return (
        <div className="relative w-full">
            {/* Dimensional Frequency Display */}
            <div className="mb-8 text-center">
                <motion.div
                    key={displayLayer?.id}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="inline-block"
                >
                    <div className="flex items-center gap-3 mb-2">
                        <div className={`w-2 h-2 rounded-full bg-${displayLayer?.color}-500 animate-pulse`} />
                        <span className="text-[10px] font-black uppercase tracking-[0.4em] text-gray-500">
                            Resonance Frequency
                        </span>
                        <div className={`w-2 h-2 rounded-full bg-${displayLayer?.color}-500 animate-pulse`} />
                    </div>
                    <div className={`text-4xl font-black text-${displayLayer?.color}-400 tracking-tighter mb-2`}>
                        {displayLayer?.frequency}
                    </div>
                    <p className="text-xs text-gray-600 italic max-w-md mx-auto">
                        {displayLayer?.description}
                    </p>
                </motion.div>
            </div>

            {/* Circular Dimensional Navigator */}
            <div className="relative w-full max-w-2xl mx-auto aspect-square">
                {/* Center Merkabah */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <motion.button
                        onClick={() => onLayerChange("merkabah")}
                        onHoverStart={() => setHoveredLayer("merkabah")}
                        onHoverEnd={() => setHoveredLayer(null)}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        className={`relative w-32 h-32 rounded-full bg-gradient-to-br from-purple-900/60 to-purple-600/40 backdrop-blur-xl border-2 ${currentLayer === "merkabah"
                                ? "border-purple-400 shadow-[0_0_40px_rgba(168,85,247,0.6)]"
                                : "border-purple-500/30"
                            } flex flex-col items-center justify-center group transition-all`}
                    >
                        <Sparkles className="w-8 h-8 text-purple-400 mb-2 group-hover:animate-pulse" />
                        <span className="text-[9px] font-black uppercase tracking-wider text-purple-300">
                            Core
                        </span>

                        {currentLayer === "merkabah" && (
                            <motion.div
                                animate={{
                                    scale: [1, 1.5, 1],
                                    opacity: [0.5, 0, 0.5]
                                }}
                                transition={{
                                    duration: 2,
                                    repeat: Infinity
                                }}
                                className="absolute inset-0 border-2 border-purple-400 rounded-full"
                            />
                        )}
                    </motion.button>
                </div>

                {/* Orbital Layers */}
                {layers.filter(l => l.id !== "merkabah").map((layer, index) => {
                    const angle = (index * 360) / 6; // 6 layers orbitales
                    const radius = 180; // Radio de la órbita
                    const x = Math.cos((angle - 90) * Math.PI / 180) * radius;
                    const y = Math.sin((angle - 90) * Math.PI / 180) * radius;

                    return (
                        <div
                            key={layer.id}
                            className="absolute top-1/2 left-1/2"
                            style={{
                                transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`
                            }}
                        >
                            <motion.button
                                onClick={() => onLayerChange(layer.id)}
                                onHoverStart={() => setHoveredLayer(layer.id)}
                                onHoverEnd={() => setHoveredLayer(null)}
                                whileHover={{ scale: 1.15 }}
                                whileTap={{ scale: 0.9 }}
                                className={`relative w-24 h-24 rounded-full bg-gradient-to-br from-${layer.color}-900/60 to-${layer.color}-600/40 backdrop-blur-xl border-2 ${currentLayer === layer.id
                                        ? `border-${layer.color}-400 shadow-[0_0_30px_rgba(168,85,247,0.5)]`
                                        : `border-${layer.color}-500/30`
                                    } flex flex-col items-center justify-center group transition-all`}
                            >
                                <div className={`text-${layer.color}-400 mb-1 group-hover:animate-pulse`}>
                                    {layer.icon}
                                </div>
                                <span className={`text-[8px] font-black uppercase tracking-wider text-${layer.color}-300 text-center px-1`}>
                                    {layer.name.split(" ")[0]}
                                </span>

                                {/* Connection line to center */}
                                <motion.div
                                    animate={{
                                        opacity: currentLayer === layer.id ? [0.3, 0.6, 0.3] : 0.1
                                    }}
                                    transition={{
                                        duration: 2,
                                        repeat: Infinity
                                    }}
                                    className={`absolute w-[2px] bg-gradient-to-b from-${layer.color}-500/50 to-transparent`}
                                    style={{
                                        height: `${radius - 60}px`,
                                        bottom: "50%",
                                        left: "50%",
                                        transformOrigin: "bottom",
                                        transform: `translateX(-50%) rotate(${180 - angle}deg)`
                                    }}
                                />

                                {/* Active pulse */}
                                {currentLayer === layer.id && (
                                    <motion.div
                                        animate={{
                                            scale: [1, 1.5, 1],
                                            opacity: [0.5, 0, 0.5]
                                        }}
                                        transition={{
                                            duration: 2,
                                            repeat: Infinity
                                        }}
                                        className={`absolute inset-0 border-2 border-${layer.color}-400 rounded-full`}
                                    />
                                )}
                            </motion.button>
                        </div>
                    );
                })}

                {/* Orbital Ring */}
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-0 border border-white/5 rounded-full"
                    style={{ margin: "25%" }}
                />
            </div>

            {/* Layer Information Panel */}
            <AnimatePresence mode="wait">
                {currentLayer && (
                    <motion.div
                        key={currentLayer}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="mt-12 bg-slate-900/40 backdrop-blur-xl border border-white/5 rounded-3xl p-8"
                    >
                        <div className="flex items-center gap-4 mb-4">
                            <div className={`p-3 bg-${activeLayer?.color}-500/10 rounded-2xl text-${activeLayer?.color}-400 border border-${activeLayer?.color}-500/20`}>
                                {activeLayer?.icon}
                            </div>
                            <div>
                                <h3 className="text-xl font-black text-white uppercase tracking-tighter">
                                    {activeLayer?.name}
                                </h3>
                                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest">
                                    Active Dimensional Layer
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mt-6">
                            <div className="bg-black/40 rounded-2xl p-4 border border-white/5">
                                <p className="text-[9px] font-black text-gray-600 uppercase tracking-widest mb-2">
                                    Resonance
                                </p>
                                <p className={`text-2xl font-black text-${activeLayer?.color}-400`}>
                                    {activeLayer?.frequency}
                                </p>
                            </div>
                            <div className="bg-black/40 rounded-2xl p-4 border border-white/5">
                                <p className="text-[9px] font-black text-gray-600 uppercase tracking-widest mb-2">
                                    Status
                                </p>
                                <div className="flex items-center gap-2">
                                    <div className={`w-2 h-2 rounded-full bg-${activeLayer?.color}-500 animate-pulse`} />
                                    <p className="text-sm font-black text-white uppercase">
                                        ACTIVE
                                    </p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
