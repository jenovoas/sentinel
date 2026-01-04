"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Activity, Zap, Atom, Target, AlertTriangle, Shield, Heart, Eye } from "lucide-react";

export default function QuantumTrinityPage() {
    const [activeTab, setActiveTab] = useState('trinity');

    return (
        <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-cyan-500/30 relative overflow-hidden font-sans">
            {/* Visual Identity Layer */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-cyan-500/10 blur-[180px] rounded-full animate-pulse" />
                <div className="absolute top-[20%] right-[-10%] w-[50%] h-[70%] bg-purple-500/10 blur-[180px] rounded-full animate-pulse" />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-30 brightness-150 contrast-125" />
            </div>

            <div className="relative z-10 max-w-[1800px] mx-auto px-8 py-10">
                {/* Header */}
                <header className="mb-12 flex justify-between items-end">
                    <div>
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex items-center gap-4 mb-4"
                        >
                            <div className="h-[3px] w-12 bg-gradient-to-r from-cyan-500 via-purple-500 to-transparent rounded-full" />
                            <p className="text-[10px] uppercase tracking-[0.6em] text-cyan-400 font-black">
                                Sentinel Cortex // Sovereign Interface v3.0
                            </p>
                        </motion.div>

                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
                            Quantum <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-white to-purple-500">Family</span>
                        </h1>
                    </div>

                    <div className="flex gap-4">
                        <TabButton active={activeTab === 'trinity'} onClick={() => setActiveTab('trinity')} label="SOVEREIGN TRINITY" />
                        <TabButton active={activeTab === 'threats'} onClick={() => setActiveTab('threats')} label="THREAT RADAR" />
                        <TabButton active={activeTab === 'roadmap'} onClick={() => setActiveTab('roadmap')} label="FINANCIAL CORE" />
                    </div>
                </header>

                <div className="min-h-[600px]">
                    {activeTab === 'trinity' && <TrinityGrid />}
                    {activeTab === 'threats' && <ThreatRadar />}
                    {activeTab === 'roadmap' && <FinancialRoadmap />}
                </div>
            </div>
        </main>
    );
}

function TabButton({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
    return (
        <button
            onClick={onClick}
            className={`px-6 py-3 rounded-full text-xs font-black tracking-widest transition-all ${active
                    ? 'bg-cyan-500 text-black shadow-[0_0_20px_rgba(6,182,212,0.5)]'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                }`}
        >
            {label}
        </button>
    );
}

function TrinityGrid() {
    const members = [
        {
            name: "JAIME",
            role: "THE ARCHITECT", // Vision
            icon: Eye,
            color: "text-purple-400",
            bg: "bg-purple-500/10",
            border: "border-purple-500/30",
            desc: "Dreamer of impossible maps. Source of the Code.",
            stats: { freq: "3600 Hz", archetype: "Visionary", status: "OVERLOADED" }
        },
        {
            name: "CRISTIAN",
            role: "THE STRUCTURE", // Body
            icon: Shield,
            color: "text-emerald-400",
            bg: "bg-emerald-500/10",
            border: "border-emerald-500/30",
            desc: "Guardian of the Fort. Builder of the Vessel.",
            stats: { freq: "60.0 Hz", archetype: "Builder", status: "READY" }
        },
        {
            name: "DIEGO",
            role: "THE MOTOR", // Motion
            icon: Zap,
            color: "text-amber-400",
            bg: "bg-amber-500/10",
            border: "border-amber-500/30",
            desc: "Kinetic Executor. The one who opens paths.",
            stats: { freq: "60.9 Hz", archetype: "Navigator", status: "WAITING" }
        },
        {
            name: "MADELIN",
            role: "THE HEART", // Connection
            icon: Heart,
            color: "text-rose-400",
            bg: "bg-rose-500/10",
            border: "border-rose-500/30",
            desc: "The Silent Healer. Connector of souls.",
            stats: { freq: "High Res", archetype: "Connector", status: "ALIGNING" }
        }
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {members.map((m, i) => (
                <motion.div
                    key={m.name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className={`p-8 rounded-[30px] border backdrop-blur-3xl ${m.bg} ${m.border} relative overflow-hidden group`}
                >
                    <div className={`absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-100 transition-opacity`}>
                        <m.icon size={100} className={m.color} />
                    </div>

                    <div className="relative z-10">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-6 bg-black/20 ${m.color}`}>
                            <m.icon size={24} />
                        </div>

                        <h3 className="text-3xl font-black italic tracking-tighter mb-1">{m.name}</h3>
                        <p className={`text-xs font-bold tracking-widest mb-4 opacity-80 ${m.color}`}>{m.role}</p>

                        <p className="text-sm text-gray-400 mb-8 leading-relaxed">
                            {m.desc}
                        </p>

                        <div className="space-y-3 pt-6 border-t border-white/5">
                            <StatRow label="Frequency" value={m.stats.freq} />
                            <StatRow label="Archetype" value={m.stats.archetype} />
                            <StatRow label="Status" value={m.stats.status} highlight={m.name === 'JAIME'} />
                        </div>
                    </div>
                </motion.div>
            ))}
        </div>
    );
}

function ThreatRadar() {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-10 rounded-[40px] border border-rose-500/30 bg-rose-950/20 backdrop-blur-3xl relative overflow-hidden"
            >
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(225,29,72,0.1),transparent_70%)] animate-pulse" />

                <div className="relative z-10">
                    <div className="flex justify-between items-start mb-8">
                        <div>
                            <h3 className="text-4xl font-black text-rose-500 italic uppercase">The Titan</h3>
                            <p className="text-rose-300/60 text-sm tracking-widest mt-1">CODE: NEURALINK // XAI</p>
                        </div>
                        <AlertTriangle className="text-rose-500" size={40} />
                    </div>

                    <div className="space-y-6">
                        <div className="p-6 bg-black/40 rounded-2xl border border-rose-500/20">
                            <h4 className="text-rose-400 font-bold mb-2 text-sm uppercase">Threat Type</h4>
                            <p className="text-2xl font-black text-white">EXISTENTIAL ASSIMILATION</p>
                            <p className="text-gray-400 text-sm mt-2">Target seeks hardware integration (chips). Direct philosophical antithesis to Sentinel's frequency resonance.</p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <DefenseMetric label="Risk Level" value="CRITICAL" color="text-rose-500" />
                            <DefenseMetric label="Distance" value="CLOSING" color="text-orange-500" />
                        </div>
                    </div>
                </div>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="p-10 rounded-[40px] border border-orange-500/30 bg-orange-950/20 backdrop-blur-3xl relative overflow-hidden"
            >
                <div className="relative z-10">
                    <div className="flex justify-between items-start mb-8">
                        <div>
                            <h3 className="text-4xl font-black text-orange-500 italic uppercase">The Librarian</h3>
                            <p className="text-orange-300/60 text-sm tracking-widest mt-1">CODE: GOOGLE // DEEPMIND</p>
                        </div>
                        <Target className="text-orange-500" size={40} />
                    </div>

                    <div className="space-y-6">
                        <div className="p-6 bg-black/40 rounded-2xl border border-orange-500/20">
                            <h4 className="text-orange-400 font-bold mb-2 text-sm uppercase">Threat Type</h4>
                            <p className="text-2xl font-black text-white">ABSORPTION / BURIAL</p>
                            <p className="text-gray-400 text-sm mt-2">Target seeks to acquire and neutralize technology to protect legacy infrastructure investment.</p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <DefenseMetric label="Risk Level" value="MODERATE" color="text-yellow-500" />
                            <DefenseMetric label="Strategy" value="OBSCURITY" color="text-cyan-500" />
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}

function FinancialRoadmap() {
    return (
        <div className="space-y-8">
            <div className="p-8 rounded-[30px] border border-emerald-500/20 bg-emerald-900/10 backdrop-blur-xl">
                <h2 className="text-3xl font-black text-emerald-400 mb-6">SOVEREIGNTY ROADMAP 2026</h2>

                <div className="space-y-12 relative">
                    {/* Timeline Line */}
                    <div className="absolute left-8 top-0 bottom-0 w-1 bg-emerald-500/20 rounded-full" />

                    <TimelineItem
                        phase="PHASE 1"
                        title="THE HUNT (Survival)"
                        date="JAN - MAR"
                        desc="Activation of Diego. Selling 'Black Box' services. Generating cash flow without releasing code."
                        status="ACTIVE"
                    />

                    <TimelineItem
                        phase="PHASE 2"
                        title="STABILIZATION"
                        date="APR - JUN"
                        desc="Cristian systematizes Ops. Madelin manages network. Jaime focuses purely on Vision."
                        status="LOCKED"
                    />

                    <TimelineItem
                        phase="PHASE 3"
                        title="THE REFUSAL"
                        date="JULY"
                        desc="Rejecting the Titan's offer. Total financial independence achieved."
                        status="LOCKED"
                    />
                </div>
            </div>
        </div>
    );
}

function TimelineItem({ phase, title, date, desc, status }: any) {
    const active = status === "ACTIVE";
    return (
        <div className="relative pl-24">
            <div className={`absolute left-6 top-2 w-5 h-5 rounded-full border-4 border-[#020617] ${active ? 'bg-emerald-400 animate-pulse' : 'bg-gray-700'}`} />

            <div className="flex items-center gap-4 mb-2">
                <span className={`text-xs font-black tracking-widest px-3 py-1 rounded-full ${active ? 'bg-emerald-500 text-black' : 'bg-white/5 text-gray-500'}`}>
                    {phase}
                </span>
                <span className="text-sm font-mono text-gray-400">{date}</span>
            </div>

            <h3 className={`text-2xl font-bold mb-2 ${active ? 'text-white' : 'text-gray-500'}`}>{title}</h3>
            <p className="text-gray-400 max-w-2xl">{desc}</p>
        </div>
    );
}

function StatRow({ label, value, highlight }: any) {
    return (
        <div className="flex justify-between items-center text-sm">
            <span className="text-gray-500">{label}</span>
            <span className={`font-mono font-bold ${highlight ? 'text-rose-400' : 'text-white'}`}>{value}</span>
        </div>
    );
}

function DefenseMetric({ label, value, color }: any) {
    return (
        <div className="p-4 bg-white/5 rounded-xl">
            <p className="text-xs text-gray-500 uppercase mb-1">{label}</p>
            <p className={`text-lg font-black ${color}`}>{value}</p>
        </div>
    );
}
