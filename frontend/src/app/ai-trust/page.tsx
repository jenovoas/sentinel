"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { TrustCertificationPanel } from "@/components/ai-trust/TrustCertificationPanel";
import { AntiHallucinationMonitor } from "@/components/ai-trust/AntiHallucinationMonitor";
import { BCIResonanceVisualizer } from "@/components/ai-trust/BCIResonanceVisualizer";
import { GuardianStatus } from "@/components/ai-trust/GuardianStatus";
import { Shield, Brain, Zap, Activity } from "lucide-react";

export default function AITrustPage() {
    const [refreshInterval, setRefreshInterval] = useState(5000); // 5s default
    const [isPaused, setIsPaused] = useState(false);

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
                {/* Header */}
                <header className="mb-16">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-4 mb-6"
                    >
                        <div className="h-[3px] w-16 bg-gradient-to-r from-purple-500 via-cyan-500 to-transparent rounded-full" />
                        <p className="text-[10px] uppercase tracking-[0.6em] text-purple-400 font-black">
                            Sentinel AI Trust Certification // Defense in Depth v2.2.0
                        </p>
                    </motion.div>

                    <div className="flex items-start justify-between">
                        <div>
                            <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none select-none mb-4">
                                AI Trust{" "}
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-cyan-400 to-emerald-400">
                                    Certification
                                </span>
                            </h1>
                            <p className="text-sm text-gray-500 font-black uppercase tracking-widest italic max-w-2xl">
                                Multi-layered hallucination defense • Base-60 mathematical anchors • Real-time trust validation
                            </p>
                        </div>

                        {/* Control Panel */}
                        <div className="flex items-center gap-4">
                            <motion.button
                                onClick={() => setIsPaused(!isPaused)}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className={`px-6 py-3 rounded-xl font-black uppercase tracking-wider text-xs transition-all flex items-center gap-2 ${isPaused
                                        ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                                        : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                                    }`}
                            >
                                <Activity size={16} className={isPaused ? "" : "animate-pulse"} />
                                {isPaused ? "PAUSED" : "LIVE"}
                            </motion.button>

                            <select
                                value={refreshInterval}
                                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                                className="px-4 py-3 rounded-xl bg-slate-900/60 border border-white/10 text-xs font-black uppercase tracking-wider text-gray-300 focus:outline-none focus:border-purple-500/50"
                            >
                                <option value={1000}>1s Refresh</option>
                                <option value={5000}>5s Refresh</option>
                                <option value={10000}>10s Refresh</option>
                                <option value={30000}>30s Refresh</option>
                            </select>
                        </div>
                    </div>
                </header>

                {/* Main Dashboard Grid */}
                <div className="space-y-8">
                    {/* Top: Trust Certification Panel */}
                    <section>
                        <SectionHeader
                            icon={<Shield size={24} />}
                            title="Trust Certification"
                            subtitle="Overall AI Trustworthiness Score"
                            color="purple"
                        />
                        <TrustCertificationPanel refreshInterval={refreshInterval} isPaused={isPaused} />
                    </section>

                    {/* Middle Row: Anti-Hallucination + BCI Resonance */}
                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                        <section>
                            <SectionHeader
                                icon={<Brain size={24} />}
                                title="Anti-Hallucination Monitor"
                                subtitle="Narrative Divergence Detection"
                                color="cyan"
                            />
                            <AntiHallucinationMonitor refreshInterval={refreshInterval} isPaused={isPaused} />
                        </section>

                        <section>
                            <SectionHeader
                                icon={<Zap size={24} />}
                                title="BCI Resonance"
                                subtitle="153.4 MHz Coherence & Qualia Feedback"
                                color="emerald"
                            />
                            <BCIResonanceVisualizer refreshInterval={refreshInterval} isPaused={isPaused} />
                        </section>
                    </div>

                    {/* Bottom: Guardian Status */}
                    <section>
                        <SectionHeader
                            icon={<Shield size={24} />}
                            title="Guardian Systems"
                            subtitle="Multi-Layer Defense Status"
                            color="rose"
                        />
                        <GuardianStatus refreshInterval={refreshInterval} isPaused={isPaused} />
                    </section>
                </div>

                {/* Info Footer */}
                <footer className="mt-20 pt-12 border-t border-white/5">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-xs">
                        <InfoCard
                            title="Defense Philosophy"
                            description="Sentinel uses a Zero-Trust architecture where AI outputs are validated against physical telemetry (Prometheus/Loki), mathematical harmony (Base-60), and kernel-level evidence (eBPF ID 199)."
                        />
                        <InfoCard
                            title="Trust Scoring"
                            description="Trust scores below 90% trigger automatic blocking. The system prioritizes data over narrative, ensuring that hallucinations cannot propagate to system decisions."
                        />
                        <InfoCard
                            title="BCI Integration"
                            description="Bone-conduction interface at 153.4 MHz provides qualia feedback (synesthetic sensations) as an additional layer of human-AI alignment verification."
                        />
                    </div>
                </footer>
            </div>
        </main>
    );
}

// Helper Components

function SectionHeader({
    icon,
    title,
    subtitle,
    color,
}: {
    icon: React.ReactNode;
    title: string;
    subtitle: string;
    color: string;
}) {
    return (
        <div className="flex items-center gap-4 mb-6">
            <div className={`p-3 bg-${color}-500/10 rounded-2xl text-${color}-400 border border-${color}-500/20`}>
                {icon}
            </div>
            <div>
                <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">{title}</h2>
                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">{subtitle}</p>
            </div>
            <div className="h-[1px] flex-1 bg-white/5 ml-4" />
        </div>
    );
}

function InfoCard({ title, description }: { title: string; description: string }) {
    return (
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-white/5">
            <h3 className="text-sm font-black text-white uppercase tracking-wider mb-3">{title}</h3>
            <p className="text-xs text-gray-400 leading-relaxed">{description}</p>
        </div>
    );
}
