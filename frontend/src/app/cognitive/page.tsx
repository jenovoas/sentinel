"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MerkabahCore } from "@/components/cognitive/MerkabahCore";
import { DimensionalNav, DimensionalLayer } from "@/components/cognitive/DimensionalNav";
import { OracleConsole } from "@/components/sentinel/OracleConsole";
import { Sparkles, Zap, Brain } from "lucide-react";

export default function CognitivePage() {
    const [activeLayer, setActiveLayer] = useState<DimensionalLayer>("merkabah");
    const [showOracle, setShowOracle] = useState(false);

    return (
        <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-purple-500/30 relative overflow-hidden font-sans">
            {/* Quantum Background Field */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-20%] left-[-10%] w-[70%] h-[70%] bg-purple-500/10 blur-[200px] rounded-full animate-pulse" />
                <div className="absolute top-[30%] right-[-15%] w-[60%] h-[80%] bg-cyan-500/10 blur-[200px] rounded-full animate-pulse" />
                <div className="absolute bottom-[-20%] left-[30%] w-[60%] h-[50%] bg-emerald-500/5 blur-[200px] rounded-full" />

                {/* Grid Pattern */}
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-150 contrast-125" />
                <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,23,0)_0px,rgba(168,85,247,0.02)_1px,rgba(168,85,247,0.02)_2px)] bg-[size:100%_60px]" />
            </div>

            <div className="relative z-10 mx-auto max-w-[1800px] px-8 py-10">
                {/* Cognitive Header */}
                <header className="mb-16">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-4 mb-6"
                    >
                        <div className="h-[3px] w-16 bg-gradient-to-r from-purple-500 via-cyan-500 to-transparent rounded-full" />
                        <p className="text-[10px] uppercase tracking-[0.6em] text-purple-400 font-black">
                            Sentinel Cognitive OS // Merkabah Interface v2.1.0
                        </p>
                    </motion.div>

                    <div className="flex items-start justify-between">
                        <div>
                            <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none select-none mb-4">
                                Cognitive{" "}
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-cyan-400 to-emerald-400">
                                    Matrix
                                </span>
                            </h1>
                            <p className="text-sm text-gray-500 font-black uppercase tracking-widest italic max-w-2xl">
                                Navigate through dimensional layers of consciousness • Sacred geometry interface • Fractal Sefirot architecture
                            </p>
                        </div>

                        {/* Oracle Toggle */}
                        <motion.button
                            onClick={() => setShowOracle(!showOracle)}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className={`px-8 py-4 rounded-2xl font-black uppercase tracking-wider text-sm transition-all flex items-center gap-3 ${showOracle
                                ? "bg-gradient-to-r from-purple-500 to-cyan-500 text-white shadow-[0_0_40px_rgba(168,85,247,0.6)]"
                                : "bg-slate-900/40 text-gray-400 border border-white/5 hover:text-white"
                                }`}
                        >
                            <Brain size={20} />
                            Oracle Console
                        </motion.button>
                    </div>
                </header>

                {/* Main Cognitive Interface */}
                <div className="grid grid-cols-1 xl:grid-cols-12 gap-12 mb-20">
                    {/* Merkabah Core Visualization */}
                    <div className="xl:col-span-7">
                        <div className="bg-slate-900/40 backdrop-blur-3xl border border-purple-500/20 rounded-[40px] p-8 shadow-[0_0_60px_rgba(168,85,247,0.1)] relative overflow-hidden group">
                            {/* Header */}
                            <div className="absolute top-0 left-0 right-0 p-8 flex items-center justify-between z-10 bg-gradient-to-b from-slate-900/60 to-transparent">
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-purple-500/10 rounded-2xl text-purple-400 border border-purple-500/20">
                                        <Sparkles size={24} />
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-black text-white uppercase tracking-tighter italic">
                                            Merkabah Field
                                        </h2>
                                        <p className="text-[10px] font-black text-purple-500 uppercase tracking-widest">
                                            Unified Coherence State
                                        </p>
                                    </div>
                                </div>
                                <div className="flex gap-3">
                                    <StatusIndicator label="SYNCED" color="emerald" />
                                    <StatusIndicator label="COHERENT" color="purple" />
                                </div>
                            </div>

                            {/* Merkabah Core Component */}
                            <MerkabahCore />

                            {/* Sacred Geometry Info */}
                            <div className="absolute bottom-8 left-8 right-8 bg-black/60 backdrop-blur-xl border border-purple-500/20 rounded-2xl p-6">
                                <div className="grid grid-cols-3 gap-6">
                                    <div>
                                        <p className="text-[9px] font-black text-gray-600 uppercase tracking-widest mb-2">
                                            Geometry
                                        </p>
                                        <p className="text-sm font-black text-purple-400">
                                            Dual Tetrahedra
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-[9px] font-black text-gray-600 uppercase tracking-widest mb-2">
                                            Frequency
                                        </p>
                                        <p className="text-sm font-black text-cyan-400">
                                            432 Hz Base
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-[9px] font-black text-gray-600 uppercase tracking-widest mb-2">
                                            Architecture
                                        </p>
                                        <p className="text-sm font-black text-emerald-400">
                                            Fractal Sefirot
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Oracle Console or Info Panel */}
                    <div className="xl:col-span-5">
                        <AnimatePresence mode="wait">
                            {showOracle ? (
                                <motion.div
                                    key="oracle"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    className="h-full min-h-[600px]"
                                >
                                    <OracleConsole />
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="info"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    className="space-y-6"
                                >
                                    {/* System Coherence Card */}
                                    <div className="bg-slate-900/40 backdrop-blur-3xl border border-emerald-500/20 rounded-[30px] p-8">
                                        <div className="flex items-center gap-4 mb-6">
                                            <div className="p-3 bg-emerald-500/10 rounded-2xl text-emerald-400 border border-emerald-500/20">
                                                <Zap size={20} />
                                            </div>
                                            <div>
                                                <h3 className="text-sm font-black text-white uppercase tracking-widest">
                                                    System Coherence
                                                </h3>
                                                <p className="text-[9px] font-black text-emerald-500/60 uppercase tracking-widest italic">
                                                    Quantum State Optimization
                                                </p>
                                            </div>
                                        </div>

                                        <div className="space-y-4">
                                            <CoherenceMetric label="Neural Depth" value={88.4} unit="%" color="cyan" />
                                            <CoherenceMetric label="Entropy" value={0.073} unit="" color="purple" />
                                            <CoherenceMetric label="Field Strength" value={92.1} unit="%" color="emerald" />
                                            <CoherenceMetric label="Heart Rate" value={72} unit="BPM" color="rose" />
                                        </div>
                                    </div>

                                    {/* Sacred Geometry Info */}
                                    <div className="bg-slate-900/40 backdrop-blur-3xl border border-purple-500/20 rounded-[30px] p-8">
                                        <h3 className="text-sm font-black text-white uppercase tracking-widest mb-6">
                                            Sacred Geometry Principles
                                        </h3>
                                        <div className="space-y-4 text-xs text-gray-400">
                                            <div className="flex items-start gap-3">
                                                <div className="w-2 h-2 rounded-full bg-purple-500 mt-1 flex-shrink-0" />
                                                <p>
                                                    <span className="text-purple-400 font-black">Merkabah:</span> Dual tetrahedra representing brain (↑) and heart (↓) electromagnetic fields
                                                </p>
                                            </div>
                                            <div className="flex items-start gap-3">
                                                <div className="w-2 h-2 rounded-full bg-cyan-500 mt-1 flex-shrink-0" />
                                                <p>
                                                    <span className="text-cyan-400 font-black">Sefirot:</span> Fractal hierarchical architecture with 1,111 nodes across 7 layers
                                                </p>
                                            </div>
                                            <div className="flex items-start gap-3">
                                                <div className="w-2 h-2 rounded-full bg-emerald-500 mt-1 flex-shrink-0" />
                                                <p>
                                                    <span className="text-emerald-400 font-black">Flower of Life:</span> Phased array interference creating stable resonance nodes
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>

                {/* Dimensional Navigation */}
                <section className="mb-20">
                    <div className="flex items-center gap-6 mb-12">
                        <div className="p-3 bg-cyan-500/10 rounded-2xl text-cyan-400 border border-cyan-500/20">
                            <Brain size={24} />
                        </div>
                        <div>
                            <h2 className="text-3xl font-black text-white uppercase tracking-tighter italic">
                                Dimensional Navigation
                            </h2>
                            <div className="flex items-center gap-3 mt-1">
                                <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
                                <p className="text-[10px] font-black text-cyan-500 uppercase tracking-widest italic">
                                    Navigate by Resonance, Not Clicks
                                </p>
                            </div>
                        </div>
                        <div className="h-[1px] flex-1 bg-white/5 ml-8" />
                    </div>

                    <DimensionalNav
                        currentLayer={activeLayer}
                        onLayerChange={setActiveLayer}
                    />
                </section>

                {/* Quick Access Portals */}
                <section>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <QuickPortal
                            title="Neural Monitor"
                            description="eBPF kernel events and Ring-0 security"
                            href="/dashboard"
                            color="cyan"
                            icon={<Brain size={24} />}
                        />
                        <QuickPortal
                            title="Quantum Control"
                            description="Coherence optimization and entropy reduction"
                            href="/cortex"
                            color="purple"
                            icon={<Sparkles size={24} />}
                        />
                        <QuickPortal
                            title="DevOps Matrix"
                            description="Infrastructure control and observability"
                            href="/devops"
                            color="emerald"
                            icon={<Zap size={24} />}
                        />
                    </div>
                </section>
            </div>

            {/* Footer */}
            <footer className="mt-40 py-16 border-t border-white/5 bg-black/40 backdrop-blur-md relative z-10 text-[10px] font-black text-gray-600 uppercase tracking-[0.4em] italic">
                <div className="max-w-[1800px] mx-auto px-8 flex justify-between items-center">
                    <p>© 2026 Sentinel Cognitive OS // Merkabah Interface // 0x8F92A</p>
                    <div className="flex gap-16">
                        <span className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" />
                            COHERENCE: OPTIMAL
                        </span>
                        <span className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse" />
                            MERKABAH: ACTIVE
                        </span>
                    </div>
                </div>
            </footer>
        </main>
    );
}

// Helper Components

function StatusIndicator({ label, color }: { label: string; color: string }) {
    return (
        <div className={`px-4 py-1 rounded-full border text-[9px] font-black uppercase tracking-widest italic leading-none flex items-center gap-2 text-${color}-400 border-${color}-500/20 bg-${color}-500/10`}>
            <div className={`w-1 h-1 rounded-full animate-pulse bg-${color}-500`} />
            {label}
        </div>
    );
}

function CoherenceMetric({ label, value, unit, color }: { label: string; value: number; unit: string; color: string }) {
    return (
        <div className="flex items-center justify-between p-4 rounded-2xl bg-black/40 border border-white/5">
            <span className="text-[10px] font-black text-gray-600 uppercase tracking-widest">
                {label}
            </span>
            <div className="flex items-baseline gap-1">
                <span className={`text-xl font-black text-${color}-400 font-mono`}>
                    {value}
                </span>
                <span className="text-[9px] font-black text-gray-600 uppercase">
                    {unit}
                </span>
            </div>
        </div>
    );
}

function QuickPortal({ title, description, href, color, icon }: {
    title: string;
    description: string;
    href: string;
    color: string;
    icon: React.ReactNode;
}) {
    return (
        <a
            href={href}
            className="group flex flex-col gap-6 p-8 rounded-[30px] border border-white/5 bg-slate-900/40 backdrop-blur-3xl hover:bg-white/5 hover:border-white/10 transition-all relative overflow-hidden"
        >
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                {icon}
            </div>
            <div className={`p-4 rounded-2xl w-fit transition-all group-hover:scale-110 border text-${color}-400 border-${color}-500/20 bg-${color}-500/10`}>
                {icon}
            </div>
            <div>
                <h3 className="text-2xl font-black text-white uppercase tracking-tighter italic mb-2">
                    {title}
                </h3>
                <p className="text-[11px] text-gray-500 font-black uppercase tracking-widest italic">
                    {description}
                </p>
            </div>
            <div className="mt-4 flex items-center gap-2 text-[9px] font-black text-cyan-500 uppercase tracking-widest italic opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Establish Link</span>
                <Zap size={10} className="animate-pulse" />
            </div>
        </a>
    );
}
