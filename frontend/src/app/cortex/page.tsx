"use client";

import React, { useState, useEffect } from 'react';
import MandalaUI from '@/components/cortex/MandalaUI';
import { KillBoard } from '@/components/cortex/KillBoard';
import { MetricsGrid } from '@/components/cortex/MetricsGrid';
import { AIChat } from '@/components/cortex/AIChat';
import { motion, AnimatePresence } from 'framer-motion';
import { useSentinelStatus } from '@/hooks/useSentinelStatus';
import { Brain, Activity, ShieldCheck, Zap, Sparkles, BrainCircuit, Network, Cpu, Database } from 'lucide-react';

export default function CortexDashboard() {
    const { status } = useSentinelStatus();
    const [kills, setKills] = useState(15689);
    const [cognitiveSync, setCognitiveSync] = useState(94.2);
    const [activeLinks, setActiveLinks] = useState(1);

    useEffect(() => {
        const interval = setInterval(() => {
            setKills(prev => prev + Math.floor(Math.random() * 5));
            setCognitiveSync(prev => {
                const next = prev + (Math.random() * 0.2 - 0.1);
                return Math.min(100, Math.max(90, next));
            });
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-cyan-500/30 overflow-hidden relative font-sans">
            {/* Visual Identity Layer - Sovereign Matrix v2.1 */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-500/10 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-cyan-500/10 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-30 brightness-150 contrast-125 pointer-events-none" />
                <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,23,0)_0px,rgba(34,211,238,0.01)_1px,rgba(34,211,238,0.01)_2px)] bg-[size:100%_40px] pointer-events-none" />
            </div>

            <div className="relative z-10 mx-auto max-w-[1800px] px-8 py-10">
                {/* Specialized Cortex Header: Neural Command Center */}
                <header className="flex flex-col xl:flex-row items-end justify-between gap-12 mb-16">
                    <div className="flex-1">
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex items-center gap-4 mb-4"
                        >
                            <div className="h-[3px] w-12 bg-gradient-to-r from-purple-500 to-transparent rounded-full" />
                            <p className="text-[10px] uppercase tracking-[0.6em] text-purple-400 font-black">Sentinel Neural Core // Ingress 0x8F92A</p>
                        </motion.div>

                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
                            Sovereign <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-white to-purple-500">Cortex</span> Matrix
                        </h1>

                        <div className="flex flex-wrap gap-8 mt-8 items-center">
                            <div className="flex items-center gap-3">
                                <BrainCircuit className="w-4 h-4 text-cyan-400 animate-pulse" />
                                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">
                                    Link Type: <span className="text-white">Neural Synchronous</span>
                                </p>
                            </div>
                            <div className="h-4 w-[1px] bg-white/10 hidden md:block" />
                            <div className="flex items-center gap-3">
                                <Activity className="w-4 h-4 text-emerald-400" />
                                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">
                                    Resonance Mode: <span className="text-white">Active Feedback Loop</span>
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* High-Impact Status Tiles */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full xl:w-auto">
                        <CortexMetricTile label="SYNC RATE" value={`${cognitiveSync.toFixed(1)}%`} color="text-purple-400" />
                        <CortexMetricTile label="THREATS" value={status?.active_threats || 0} color="text-rose-400" />
                        <CortexMetricTile label="LATENCY" value="12ms" color="text-cyan-400" />
                        <CortexMetricTile label="NODES" value={status?.network_nodes || 128} color="text-emerald-400" />
                    </div>
                </header>

                {/* AI Intelligence Operational Interface */}
                <div className="grid grid-cols-12 gap-8 min-h-[750px] items-stretch">

                    {/* Left Intelligence Stack: Performance & Telemetry (Span 3) */}
                    <motion.div
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="col-span-12 lg:col-span-3 flex flex-col gap-8"
                    >
                        <IntelligenceCard
                            icon={<Activity size={20} className="text-cyan-400" />}
                            title="Neural Telemetry"
                            subtitle="Kernel Performance Streams"
                        >
                            <MetricsGrid />
                        </IntelligenceCard>

                        <IntelligenceCard
                            icon={<Database size={20} className="text-purple-400" />}
                            title="Memory Fragments"
                            subtitle="Sovereign Truth Validation"
                        >
                            <div className="space-y-4">
                                <ResourceRow label="L1 Cache" value="0.4ms" status="nominal" />
                                <ResourceRow label="Vector Index" value="99.9%" status="shield" />
                                <ResourceRow label="BCI Link" value="STABLE" status="sync" />
                            </div>
                        </IntelligenceCard>
                    </motion.div>

                    {/* Central Core: Mandala & Neural Uplink (Span 6) */}
                    <div className="col-span-12 lg:col-span-6 flex flex-col gap-8">
                        {/* Upper Core: Akasha Resonance Engine */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="flex-1 bg-slate-900/40 backdrop-blur-3xl rounded-[40px] border border-white/5 relative group p-1 shadow-2xl overflow-hidden"
                        >
                            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" />
                            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(168,85,247,0.05)_0%,transparent_70%)] pointer-events-none" />

                            <div className="h-full w-full flex flex-col items-center justify-center relative z-10 p-8">
                                <div className="absolute top-8 left-10 flex items-center gap-4">
                                    <div className="p-3 bg-purple-500/10 rounded-2xl text-purple-400 border border-purple-500/20 shadow-[0_0_20px_rgba(168,85,247,0.2)]">
                                        <Sparkles size={24} className="animate-pulse" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-black text-white uppercase italic tracking-tighter leading-none">Akasha Core</h3>
                                        <p className="text-[10px] font-black text-purple-500 uppercase tracking-widest mt-1">Sovereign Resonance Filter</p>
                                    </div>
                                </div>

                                <div className="scale-[1.3] xl:scale-[1.6]">
                                    <MandalaUI />
                                </div>
                            </div>
                        </motion.div>

                        {/* Lower Core: Neural Uplink Console */}
                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="h-[400px]"
                        >
                            <AIChat />
                        </motion.div>
                    </div>

                    {/* Right Threat Stack: Kill Board & Activity (Span 3) */}
                    <motion.div
                        initial={{ opacity: 0, x: 30 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="col-span-12 lg:col-span-3 flex flex-col gap-8"
                    >
                        <IntelligenceCard
                            icon={<ShieldCheck size={20} className="text-emerald-400" />}
                            title="Mitigation Stream"
                            subtitle="Neutralized Threat Matrix"
                        >
                            <KillBoard kills={kills} />
                        </IntelligenceCard>

                        <div className="bg-rose-500/5 border border-rose-500/10 rounded-[40px] p-8 backdrop-blur-3xl relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
                                <ShieldCheck size={64} />
                            </div>
                            <h4 className="text-xs font-black text-rose-400 uppercase tracking-[0.2em] italic mb-6">Threat Intelligence</h4>
                            <div className="space-y-6">
                                <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">RCE Injection</span>
                                    <span className="text-[10px] font-black text-emerald-400 italic">BLOCKED</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Buffer Overflow</span>
                                    <span className="text-[10px] font-black text-emerald-400 italic">MITIGATED</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Zero-Day Search</span>
                                    <span className="text-[10px] font-black text-cyan-400 italic">OBSERVING</span>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>

            <footer className="mt-20 py-12 border-t border-white/5 bg-black/40 backdrop-blur-md relative z-10 text-[10px] font-black text-gray-600 uppercase tracking-[0.4em] italic">
                <div className="max-w-[1800px] mx-auto px-8 flex justify-between items-center">
                    <p>© 2026 Sentinel Intelligence // Neural Link 1.0.4-STABLE</p>
                    <div className="flex gap-12">
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> COGNITIVE_SYNC: {cognitiveSync.toFixed(2)}%</span>
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-cyan-500" /> BCI_PHASE: 0.1</span>
                    </div>
                </div>
            </footer>
        </main>
    );
}

function CortexMetricTile({ label, value, color }: { label: string; value: string | number; color: string }) {
    return (
        <div className="bg-slate-900/40 p-4 px-8 rounded-3xl border border-white/5 backdrop-blur-3xl hover:bg-white/5 transition-all min-w-[140px] group overflow-hidden relative shadow-2xl">
            <div className="absolute top-0 right-0 w-8 h-8 opacity-5 group-hover:opacity-10 transition-opacity">
                <Zap size={32} />
            </div>
            <p className="text-[9px] text-gray-500 uppercase font-black tracking-widest mb-1 italic">{label}</p>
            <div className={`text-2xl font-black font-mono tracking-tighter italic ${color}`}>
                {value}
            </div>
        </div>
    );
}

function IntelligenceCard({ icon, title, subtitle, children }: { icon: React.ReactNode; title: string; subtitle: string; children: React.ReactNode }) {
    return (
        <div className="bg-slate-900/40 backdrop-blur-3xl rounded-[40px] border border-white/5 p-8 flex flex-col group relative overflow-hidden transition-all hover:border-white/10 shadow-2xl">
            <div className="flex items-center gap-4 mb-8">
                <div className="p-3 bg-white/5 rounded-2xl text-gray-400 group-hover:scale-110 group-hover:bg-white/10 transition-all border border-white/5">
                    {icon}
                </div>
                <div>
                    <h3 className="text-sm font-black text-white uppercase italic tracking-widest leading-none">{title}</h3>
                    <p className="text-[9px] font-bold text-gray-600 uppercase tracking-widest mt-1 italic">{subtitle}</p>
                </div>
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {children}
            </div>
        </div>
    );
}

function ResourceRow({ label, value, status }: { label: string; value: string; status: 'nominal' | 'shield' | 'sync' }) {
    const statusColor = {
        nominal: 'text-emerald-400',
        shield: 'text-cyan-400',
        sync: 'text-purple-400'
    }[status];

    return (
        <div className="flex items-center justify-between p-4 bg-black/40 border border-white/5 rounded-2xl group hover:border-white/10 transition-all">
            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">{label}</span>
            <span className={`text-[10px] font-black italic tracking-widest ${statusColor}`}>{value}</span>
        </div>
    );
}
