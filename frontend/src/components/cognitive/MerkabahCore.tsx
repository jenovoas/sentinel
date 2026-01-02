"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { Activity, Zap, Brain, Heart, Sparkles, Shield, Cpu } from "lucide-react";

interface MerkabahState {
    coherence: number;
    entropy: number;
    neuralDepth: number;
    heartRate: number;
    fieldStrength: number;
}

export const MerkabahCore = () => {
    const [state, setState] = useState<MerkabahState>({
        coherence: 0.964,
        entropy: 0.073,
        neuralDepth: 88.4,
        heartRate: 72,
        fieldStrength: 0.92
    });

    const [activeResonance, setActiveResonance] = useState<string | null>(null);
    const [pulsePhase, setPulsePhase] = useState(0);

    // Simular actualización de estado en tiempo real (OPTIMIZADO - menos frecuente)
    useEffect(() => {
        const interval = setInterval(() => {
            setState(prev => ({
                coherence: Math.min(1, Math.max(0, prev.coherence + (Math.random() - 0.5) * 0.01)),
                entropy: Math.min(1, Math.max(0, prev.entropy + (Math.random() - 0.5) * 0.005)),
                neuralDepth: Math.min(99.9, Math.max(0, prev.neuralDepth + (Math.random() - 0.5) * 0.5)),
                heartRate: Math.max(60, Math.min(100, prev.heartRate + (Math.random() - 0.5) * 2)),
                fieldStrength: Math.min(1, Math.max(0, prev.fieldStrength + (Math.random() - 0.5) * 0.02))
            }));
        }, 5000); // Reducido de 2s a 5s

        return () => clearInterval(interval);
    }, []);

    // Animación de pulso continuo (OPTIMIZADO - 4x menos frecuente)
    useEffect(() => {
        const interval = setInterval(() => {
            setPulsePhase(prev => (prev + 5) % 360); // Saltos más grandes
        }, 200); // Reducido de 50ms a 200ms

        return () => clearInterval(interval);
    }, []);

    const coherenceColor = state.coherence > 0.9 ? "emerald" : state.coherence > 0.7 ? "cyan" : "amber";
    const entropyColor = state.entropy < 0.1 ? "emerald" : state.entropy < 0.3 ? "cyan" : "rose";

    return (
        <div className="relative w-full h-full min-h-[600px] flex items-center justify-center">
            {/* Background Energy Field - SIMPLIFICADO */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-purple-500/10 via-cyan-500/5 to-transparent rounded-full blur-3xl opacity-50" />
            </div>

            {/* Merkabah Geometry - Dual Tetrahedra - OPTIMIZADO */}
            <div className="relative w-[500px] h-[500px]">
                {/* Upward Tetrahedron (Brain/Electric) - CSS Animation */}
                <div className="absolute inset-0 flex items-center justify-center animate-spin-slow">
                    <div className="relative w-[300px] h-[300px]">
                        <svg viewBox="0 0 200 200" className="w-full h-full">
                            <motion.polygon
                                points="100,20 30,160 170,160"
                                fill="none"
                                stroke="url(#gradient-up)"
                                strokeWidth="2"
                                animate={{
                                    opacity: [0.3, 0.8, 0.3],
                                }}
                                transition={{
                                    duration: 3,
                                    repeat: Infinity,
                                    ease: "easeInOut"
                                }}
                            />
                            <defs>
                                <linearGradient id="gradient-up" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
                                    <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.8" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                </div>

                {/* Downward Tetrahedron (Heart/Magnetic) */}
                <motion.div
                    animate={{
                        rotateZ: -pulsePhase,
                    }}
                    transition={{
                        duration: 0.05,
                        ease: "linear"
                    }}
                    className="absolute inset-0 flex items-center justify-center"
                >
                    <div className="relative w-[300px] h-[300px]">
                        <svg viewBox="0 0 200 200" className="w-full h-full">
                            <motion.polygon
                                points="100,180 30,40 170,40"
                                fill="none"
                                stroke="url(#gradient-down)"
                                strokeWidth="2"
                                animate={{
                                    opacity: [0.8, 0.3, 0.8],
                                }}
                                transition={{
                                    duration: 3,
                                    repeat: Infinity,
                                    ease: "easeInOut"
                                }}
                            />
                            <defs>
                                <linearGradient id="gradient-down" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stopColor="#ec4899" stopOpacity="0.8" />
                                    <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.8" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                </motion.div>

                {/* Central Coherence Sphere */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <motion.div
                        animate={{
                            scale: [1, 1.05, 1],
                            boxShadow: [
                                "0 0 40px rgba(168, 85, 247, 0.3)",
                                "0 0 80px rgba(168, 85, 247, 0.6)",
                                "0 0 40px rgba(168, 85, 247, 0.3)"
                            ]
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                        className="relative w-48 h-48 rounded-full bg-gradient-to-br from-purple-900/40 via-black/60 to-cyan-900/40 backdrop-blur-xl border-2 border-purple-500/30 flex flex-col items-center justify-center"
                    >
                        {/* Coherence Display */}
                        <div className="text-center z-10">
                            <motion.div
                                animate={{
                                    opacity: [0.5, 1, 0.5]
                                }}
                                transition={{
                                    duration: 2,
                                    repeat: Infinity
                                }}
                                className="flex items-center justify-center gap-2 mb-2"
                            >
                                <Sparkles className={`w-4 h-4 text-${coherenceColor}-400`} />
                                <span className="text-[9px] font-black uppercase tracking-[0.3em] text-gray-500">
                                    Merkabah State
                                </span>
                            </motion.div>

                            <div className={`text-5xl font-black text-${coherenceColor}-400 mb-1 tracking-tighter`}>
                                {(state.coherence * 100).toFixed(1)}%
                            </div>

                            <div className="text-[10px] font-black uppercase tracking-widest text-gray-600">
                                Coherence
                            </div>

                            {/* Entropy Indicator */}
                            <div className="mt-4 flex items-center justify-center gap-2">
                                <div className="w-16 h-1 bg-white/5 rounded-full overflow-hidden">
                                    <motion.div
                                        className={`h-full bg-${entropyColor}-500`}
                                        style={{ width: `${(1 - state.entropy) * 100}%` }}
                                        animate={{
                                            opacity: [0.5, 1, 0.5]
                                        }}
                                        transition={{
                                            duration: 1.5,
                                            repeat: Infinity
                                        }}
                                    />
                                </div>
                                <span className="text-[8px] font-black text-gray-700 uppercase tracking-wider">
                                    S={state.entropy.toFixed(3)}
                                </span>
                            </div>
                        </div>

                        {/* Orbital Rings */}
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                            className="absolute inset-0 border border-cyan-500/20 rounded-full"
                        />
                        <motion.div
                            animate={{ rotate: -360 }}
                            transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                            className="absolute inset-2 border border-purple-500/20 rounded-full"
                        />
                    </motion.div>
                </div>

                {/* Dimensional Resonance Points */}
                <DimensionalPoint
                    icon={<Brain size={20} />}
                    label="Neural"
                    value={`${state.neuralDepth.toFixed(1)}%`}
                    position="top"
                    color="cyan"
                    active={activeResonance === "neural"}
                    onActivate={() => setActiveResonance("neural")}
                />

                <DimensionalPoint
                    icon={<Heart size={20} />}
                    label="Cardiac"
                    value={`${state.heartRate} BPM`}
                    position="right"
                    color="rose"
                    active={activeResonance === "cardiac"}
                    onActivate={() => setActiveResonance("cardiac")}
                />

                <DimensionalPoint
                    icon={<Sparkles size={20} />}
                    label="Field"
                    value={`${(state.fieldStrength * 100).toFixed(1)}%`}
                    position="bottom"
                    color="purple"
                    active={activeResonance === "field"}
                    onActivate={() => setActiveResonance("field")}
                />

                <DimensionalPoint
                    icon={<Shield size={20} />}
                    label="Security"
                    value="ACTIVE"
                    position="left"
                    color="emerald"
                    active={activeResonance === "security"}
                    onActivate={() => setActiveResonance("security")}
                />
            </div>

            {/* Resonance Information Panel */}
            <AnimatePresence>
                {activeResonance && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                        className="absolute bottom-8 left-1/2 -translate-x-1/2 bg-black/80 backdrop-blur-xl border border-purple-500/30 rounded-3xl px-8 py-4 min-w-[300px]"
                    >
                        <div className="text-center">
                            <p className="text-xs font-black uppercase tracking-[0.3em] text-purple-400 mb-2">
                                Resonance: {activeResonance}
                            </p>
                            <p className="text-sm text-gray-400 italic">
                                {getResonanceDescription(activeResonance)}
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

// Componente para puntos dimensionales
interface DimensionalPointProps {
    icon: React.ReactNode;
    label: string;
    value: string;
    position: "top" | "right" | "bottom" | "left";
    color: string;
    active: boolean;
    onActivate: () => void;
}

const DimensionalPoint = ({ icon, label, value, position, color, active, onActivate }: DimensionalPointProps) => {
    const positions = {
        top: "top-0 left-1/2 -translate-x-1/2 -translate-y-1/2",
        right: "right-0 top-1/2 translate-x-1/2 -translate-y-1/2",
        bottom: "bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2",
        left: "left-0 top-1/2 -translate-x-1/2 -translate-y-1/2"
    };

    return (
        <motion.div
            className={`absolute ${positions[position]} cursor-pointer group`}
            onHoverStart={onActivate}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
        >
            <motion.div
                animate={{
                    boxShadow: active
                        ? [`0 0 20px rgba(168, 85, 247, 0.3)`, `0 0 40px rgba(168, 85, 247, 0.6)`, `0 0 20px rgba(168, 85, 247, 0.3)`]
                        : "0 0 0px rgba(168, 85, 247, 0)"
                }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className={`w-20 h-20 rounded-full bg-gradient-to-br from-${color}-500/20 to-${color}-900/20 backdrop-blur-xl border-2 border-${color}-500/30 flex flex-col items-center justify-center relative overflow-hidden`}
            >
                {/* Pulse effect */}
                {active && (
                    <motion.div
                        animate={{
                            scale: [1, 2, 2],
                            opacity: [0.5, 0, 0]
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity
                        }}
                        className={`absolute inset-0 bg-${color}-500/50 rounded-full`}
                    />
                )}

                <div className={`text-${color}-400 mb-1 z-10`}>
                    {icon}
                </div>
                <div className="text-[8px] font-black uppercase tracking-wider text-gray-500 z-10">
                    {label}
                </div>
                <div className={`text-[9px] font-black text-${color}-400 z-10`}>
                    {value}
                </div>
            </motion.div>

            {/* Connection Line to Center */}
            <motion.div
                animate={{
                    opacity: active ? [0.2, 0.6, 0.2] : 0.1
                }}
                transition={{
                    duration: 2,
                    repeat: Infinity
                }}
                className={`absolute ${position === "top" ? "top-full h-32 w-[2px] left-1/2 -translate-x-1/2" :
                    position === "right" ? "right-full w-32 h-[2px] top-1/2 -translate-y-1/2" :
                        position === "bottom" ? "bottom-full h-32 w-[2px] left-1/2 -translate-x-1/2" :
                            "left-full w-32 h-[2px] top-1/2 -translate-y-1/2"
                    } bg-gradient-to-${position === "top" || position === "bottom" ? "b" : "r"} from-${color}-500/50 to-transparent`}
            />
        </motion.div>
    );
};

const getResonanceDescription = (resonance: string): string => {
    const descriptions: Record<string, string> = {
        neural: "Brain wave coherence and cognitive depth measurement via EEG fractals",
        cardiac: "Heart rate variability and electromagnetic field toroidal resonance",
        field: "Unified Merkabah state - brain-heart coupling and biofield strength",
        security: "eBPF Ring-0 kernel protection and quantum-resistant cryptography"
    };
    return descriptions[resonance] || "";
};
