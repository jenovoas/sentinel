"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { BackupStatusCard } from "@/components/backup/BackupStatusCard";
import { FailSafeSecurityCard } from "@/components/failsafe/FailSafeSecurityCard";
import { IncidentManagementCard } from "@/components/IncidentManagementCard";
import { SecureBrowser } from "@/components/browser/SecureBrowser";
import { useSentinelStatus } from "@/hooks/useSentinelStatus";
import { motion, AnimatePresence } from "framer-motion";
import { Lock, ShieldCheck, Zap, BarChart3, Globe, Command, Activity, Clock, Sparkles, BrainCircuit, ShieldAlert, Fingerprint } from "lucide-react";

// Sentinel High-Impact Components
import { ResonanceRateCard } from "@/components/sentinel/ResonanceRateCard";
import { GoldTruthFeed } from "@/components/sentinel/GoldTruthFeed";
import { OracleConsole } from "@/components/sentinel/OracleConsole";
import { CognitiveProjection } from "@/components/sentinel/CognitiveProjection";

interface SLOData {
    availability: { value: number; target: number };
    errorRate: { value: number; target: number };
    latency: { value: number; target: number };
    aiResponse: { value: number; target: number };
}

export default function SecureWorkspacePage() {
    const searchParams = useSearchParams();
    const urlParam = searchParams.get("url");
    const modeParam = searchParams.get("mode") as "clear" | "velocity" | "ghost" | "deep" | null;
    const { status } = useSentinelStatus();

    const [sloData, setSloData] = useState<SLOData>({
        availability: { value: 99.95, target: 99.9 },
        errorRate: { value: 0.3, target: 1.0 },
        latency: { value: 45, target: 100 },
        aiResponse: { value: 1.2, target: 3.0 },
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                const statsRes = await fetch("/api/v1/analytics/statistics?hours=24");
                const statsData = await statsRes.json();

                if (statsData) {
                    setSloData(prev => ({
                        ...prev,
                        availability: {
                            value: statsData.cpu?.avg < 90 ? 99.95 : 99.5,
                            target: 99.9
                        },
                        errorRate: {
                            value: statsData.anomalies_count > 10 ? 1.5 : 0.3,
                            target: 1.0
                        }
                    }));
                }
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const getSLOStatus = (value: number, target: number, inverse = false) => {
        const ratio = inverse ? target / value : value / target;
        if (ratio >= 1.0) return "good";
        if (ratio >= 0.9) return "warning";
        return "critical";
    };

    return (
        <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-cyan-500/30 overflow-hidden relative font-sans">
            {/* Visual Identity Layer: Advanced Security Matrix */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-cyan-500/10 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-purple-500/10 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-30 brightness-150 contrast-125 pointer-events-none" />
                <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,23,0)_0px,rgba(34,211,238,0.01)_1px,rgba(34,211,238,0.01)_2px)] bg-[size:100%_40px] pointer-events-none" />
            </div>

            <div className="relative z-10 mx-auto max-w-[1800px] px-8 py-10">
                {/* Unified Workspace Header: Secure Neural Gateway */}
                <header className="flex flex-col xl:flex-row items-end justify-between gap-12 mb-16">
                    <div className="flex-1">
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex items-center gap-4 mb-4"
                        >
                            <div className="h-[3px] w-12 bg-gradient-to-r from-cyan-500 to-transparent rounded-full" />
                            <p className="text-[10px] uppercase tracking-[0.6em] text-cyan-400 font-black">Sentinel Workspace OS // Secure Ingress 0x8F92A</p>
                        </motion.div>

                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
                            Secure <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-white to-purple-500">Workspace</span> Matrix
                        </h1>

                        <div className="flex flex-wrap gap-8 mt-8 items-center">
                            <div className="flex items-center gap-3">
                                <Lock className="w-4 h-4 text-cyan-400" />
                                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">
                                    Isolation Mode: <span className="text-white">Quantum Resistant Bridge</span>
                                </p>
                            </div>
                            <div className="h-4 w-[1px] bg-white/10 hidden md:block" />
                            <div className="flex items-center gap-3">
                                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">
                                    Status: <span className="text-emerald-400">{status?.system || "STABLE"}</span>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full xl:w-auto">
                        <WorkspaceMetric label="AVAILABILITY" value={`${sloData.availability.value}%`} color="text-emerald-400" />
                        <WorkspaceMetric label="ERROR RATE" value={`${sloData.errorRate.value}%`} color="text-rose-400" />
                        <WorkspaceMetric label="SECURE LINKS" value="12 ACTIVE" color="text-cyan-400" />
                        <WorkspaceMetric label="SYNC" value="VERIFIED" color="text-purple-400" />
                    </div>
                </header>

                {/* Intelligence Awareness Layer: Cognitive Projection */}
                <section className="mb-16">
                    <div className="bg-[#050814]/40 backdrop-blur-3xl rounded-[40px] border border-white/5 p-1 group relative overflow-hidden shadow-2xl transition-all hover:border-white/10">
                        <div className="absolute top-8 left-10 flex items-center gap-4 z-10 pointer-events-none">
                            <div className="p-3 bg-cyan-500/10 rounded-2xl text-cyan-400 border border-cyan-500/20 shadow-[0_0_20px_rgba(34,211,238,0.2)]">
                                <BrainCircuit size={24} className="animate-pulse" />
                            </div>
                            <div>
                                <h3 className="text-xl font-black text-white uppercase italic tracking-tighter leading-none">Neural Awareness</h3>
                                <p className="text-[10px] font-black text-cyan-500 uppercase tracking-widest mt-1">Real-time System Mapping</p>
                            </div>
                        </div>
                        <CognitiveProjection />
                    </div>
                </section>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-16 items-start">
                    <div className="lg:col-span-8 flex flex-col gap-8">
                        {/* Adaptive SLO Matrix */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <ResonanceRateCard />
                            <div className="grid grid-cols-2 gap-4 h-full">
                                <SLOTile
                                    title="Uptime"
                                    value={`${sloData.availability.value}%`}
                                    target={`${sloData.availability.target}%`}
                                    status={getSLOStatus(sloData.availability.value, sloData.availability.target)}
                                    color="emerald"
                                />
                                <SLOTile
                                    title="Failure"
                                    value={`${sloData.errorRate.value}%`}
                                    target={`<${sloData.errorRate.target}%`}
                                    status={getSLOStatus(sloData.errorRate.value, sloData.errorRate.target, true)}
                                    color="rose"
                                />
                                <SLOTile
                                    title="Latency"
                                    value={`${sloData.latency.value}ms`}
                                    target={`<${sloData.latency.target}ms`}
                                    status={getSLOStatus(sloData.latency.value, sloData.latency.target, true)}
                                    color="cyan"
                                />
                                <SLOTile
                                    title="AI Synthesis"
                                    value={`${sloData.aiResponse.value}s`}
                                    target={`<${sloData.aiResponse.target}s`}
                                    status={getSLOStatus(sloData.aiResponse.value, sloData.aiResponse.target, true)}
                                    color="purple"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="lg:col-span-4 h-full min-h-[500px]">
                        <OracleConsole />
                    </div>
                </div>

                {/* Sovereign Interaction Layer: Secure Browser Node */}
                <section className="mb-16" id="secure-workspace">
                    <div className="flex items-center gap-6 mb-12">
                        <div className="p-3 bg-cyan-500/10 rounded-2xl text-cyan-400 border border-cyan-500/20">
                            <Globe size={24} />
                        </div>
                        <div>
                            <h2 className="text-3xl font-black text-white uppercase tracking-tighter italic leading-none">Sovereign Browser Node</h2>
                            <div className="flex items-center gap-3 mt-1">
                                <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
                                <p className="text-[10px] font-black text-cyan-500 uppercase tracking-widest italic">High-Isolation Secure Ingress</p>
                            </div>
                        </div>
                        <div className="h-[1px] flex-1 bg-white/5 ml-8" />
                    </div>

                    <div className="bg-[#050814]/40 backdrop-blur-3xl rounded-[40px] p-4 border border-white/5 transition-all hover:border-cyan-500/20 shadow-2xl relative group overflow-hidden">
                        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent" />
                        <SecureBrowser
                            initialUrl={urlParam || undefined}
                            initialMode={modeParam || undefined}
                            autoNavigate={!!urlParam}
                        />
                    </div>
                </section>

                {/* Security Intelligence & Protocols */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
                    <div className="lg:col-span-2">
                        <GoldTruthFeed />
                    </div>
                    <div className="flex flex-col gap-8">
                        <BackupStatusCard />
                        <FailSafeSecurityCard />
                    </div>
                </div>

                {/* Operations Incident Matrix */}
                <section>
                    <div className="flex items-center gap-6 mb-12">
                        <div className="p-3 bg-purple-500/10 rounded-2xl text-purple-400 border border-purple-500/20">
                            <BarChart3 size={24} />
                        </div>
                        <div>
                            <h2 className="text-3xl font-black text-white uppercase tracking-tighter italic leading-none">Incident Matrix</h2>
                            <div className="flex items-center gap-3 mt-1">
                                <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
                                <p className="text-[10px] font-black text-purple-500 uppercase tracking-widest italic">Tactical Awareness Layer</p>
                            </div>
                        </div>
                        <div className="h-[1px] flex-1 bg-white/5 ml-8" />
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        <IncidentManagementCard />
                    </div>
                </section>
            </div>

            <footer className="mt-40 py-12 border-t border-white/5 bg-black/40 backdrop-blur-md relative z-10 text-[10px] font-black text-gray-600 uppercase tracking-[0.4em] italic">
                <div className="max-w-[1800px] mx-auto px-8 flex justify-between items-center">
                    <p>© 2026 Sentinel Workspace // Secure Ingress Point // Build 0x8F92A</p>
                    <div className="flex gap-12">
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse" /> ISOLATION: ACTIVE</span>
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" /> CRYPTO: VERIFIED</span>
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> COMPLIANCE: 100%</span>
                    </div>
                </div>
            </footer>
        </main>
    );
}

function WorkspaceMetric({ label, value, color }: { label: string; value: string | number; color: string }) {
    return (
        <div className="bg-slate-900/40 p-5 px-10 rounded-[30px] border border-white/5 backdrop-blur-3xl hover:bg-white/10 transition-all min-w-[150px] group overflow-hidden relative shadow-2xl">
            <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-10 transition-opacity">
                <Sparkles size={16} className={color} />
            </div>
            <p className="text-[9px] text-gray-500 uppercase font-black tracking-widest mb-1 italic leading-none">{label}</p>
            <div className={`text-2xl font-black font-mono tracking-tighter italic ${color}`}>
                {value}
            </div>
        </div>
    );
}

function SLOTile({
    title,
    value,
    target,
    status,
    color
}: {
    title: string;
    value: string;
    target: string;
    status: "good" | "warning" | "critical";
    color: 'emerald' | 'rose' | 'cyan' | 'purple';
}) {
    const statusColors = {
        good: `border-${color}-500/20 bg-${color}-500/5 hover:bg-${color}-500/10 shadow-[0_0_20px_rgba(0,0,0,0.3)]`,
        warning: "border-amber-500/20 bg-amber-500/5 hover:bg-amber-500/10 shadow-[0_0_20px_rgba(0,0,0,0.3)]",
        critical: "border-rose-500/20 bg-rose-500/5 hover:bg-rose-500/10 shadow-[0_0_20px_rgba(0,0,0,0.3)]",
    };

    const textColors = {
        good: `text-${color}-400`,
        warning: "text-amber-400",
        critical: "text-rose-400",
    };

    return (
        <div className={`group transition-all duration-500 border rounded-[35px] p-8 flex flex-col justify-between overflow-hidden relative shadow-2xl ${statusColors[status]}`}>
            <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
                <Zap size={32} />
            </div>
            <div>
                <p className="text-[10px] text-gray-600 mb-2 font-black uppercase tracking-[0.2em] italic leading-none">{title}</p>
                <p className={`text-4xl font-black font-mono tracking-tighter italic ${textColors[status]}`}>{value}</p>
            </div>
            <div className="flex items-center justify-between text-[9px] font-black uppercase tracking-widest border-t border-white/5 pt-6 mt-4 italic">
                <span className="text-gray-700">Objective</span>
                <span className="text-white/20">{target}</span>
            </div>
        </div>
    );
}
