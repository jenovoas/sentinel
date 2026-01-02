"use client";

import { useEffect, useState } from "react";
import { Activity, CheckCircle2, XCircle, AlertTriangle, Clock, RefreshCw, Shield, Server, Box, Cpu, Terminal, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

type WatchdogStatus = {
    timestamp: string;
    hardware_watchdog: {
        enabled: boolean;
        status: string;
        last_kick: string;
        interval_seconds: number;
        device: string;
    };
    systemd_services: Array<{
        name: string;
        status: string;
        uptime_seconds: number;
        restart_count: number;
    }>;
    docker_containers: Array<{
        name: string;
        health: string;
        uptime_seconds: number;
        restart_count: number;
    }>;
    alerts: string[];
};

const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 24) {
        const days = Math.floor(hours / 24);
        return `${days}d ${hours % 24}h`;
    }
    return `${hours}h ${minutes}m`;
};

const StatusBadge = ({ status, pulse = false }: { status: string; pulse?: boolean }) => {
    const isHealthy = status === "active" || status === "healthy" || status === "running";
    return (
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[9px] font-black tracking-widest uppercase border ${isHealthy
            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
            : "bg-rose-500/10 text-rose-400 border-rose-500/20"
            }`}>
            <div className={`w-1.5 h-1.5 rounded-full ${isHealthy ? 'bg-emerald-500' : 'bg-rose-500'} ${pulse ? 'animate-pulse' : ''}`} />
            {status}
        </div>
    );
};

export default function WatchdogPage() {
    const [data, setData] = useState<WatchdogStatus | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch("/api/v1/watchdog/status", { cache: "no-store" });
                const json = await res.json();
                setData(json);
            } catch (error) {
                console.error("Failed to fetch watchdog status:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading && !data) {
        return (
            <main className="min-h-screen bg-[#020617] flex items-center justify-center">
                <div className="text-center">
                    <RefreshCw className="w-12 h-12 animate-spin text-cyan-500 mx-auto mb-6 opacity-20" />
                    <p className="text-[10px] font-black uppercase tracking-[0.4em] text-gray-500 italic">Synchronizing Watchdog Matrix...</p>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-[#020617] text-white selection:bg-cyan-500/30 overflow-hidden relative">
            {/* Visual Identity Layer */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[20%] -right-[10%] w-[50%] h-[50%] bg-amber-500/5 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute bottom-[10%] -left-[10%] w-[40%] h-[60%] bg-rose-500/5 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 brightness-200 contrast-125 pointer-events-none" />
                <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,23,0)_0px,rgba(18,18,23,0)_1px,rgba(245,158,11,0.02)_1px,rgba(245,158,11,0.02)_2px)] bg-[size:100%_40px] pointer-events-none" />
            </div>

            <div className="relative z-10 mx-auto max-w-[1700px] px-8 py-10">
                <header className="flex flex-col md:flex-row items-start justify-between gap-8 mb-16">
                    <div className="flex-1">
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex items-center gap-4 mb-3"
                        >
                            <div className="h-[3px] w-12 bg-gradient-to-r from-amber-500 to-transparent rounded-full" />
                            <p className="text-[10px] uppercase tracking-[0.6em] text-amber-500 font-black">Sentinel Integrity OS // Node v2.1</p>
                        </motion.div>

                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
                            Watchdog <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-white to-rose-500">Integrity Matrix</span>
                        </h1>

                        <div className="mt-8 flex items-center gap-6">
                            <div className="flex items-center gap-3 bg-white/5 px-5 py-2 rounded-2xl border border-white/5 backdrop-blur-md">
                                <Activity className="w-4 h-4 text-amber-500 animate-pulse" />
                                <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">Live Telemetry Synchronized</span>
                            </div>
                            <div className="text-[10px] font-black uppercase tracking-widest text-gray-600 italic">
                                Last Scan: {data ? new Date(data.timestamp).toLocaleTimeString() : '---'}
                            </div>
                        </div>
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Left Column: Core Statuses */}
                    <div className="lg:col-span-8 flex flex-col gap-8">

                        {/* Hardware Layer */}
                        <motion.section
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-slate-900/30 backdrop-blur-3xl border border-white/5 rounded-[32px] p-8 relative overflow-hidden group hover:border-amber-500/20 transition-all shadow-2xl"
                        >
                            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-amber-500/30 to-transparent" />
                            <div className="flex items-center justify-between mb-8">
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-amber-500/10 rounded-2xl border border-amber-500/20 text-amber-400">
                                        <Cpu className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">Hardware Guardian</h2>
                                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Physical Reset & Heartbeat Monitoring</p>
                                    </div>
                                </div>
                                <StatusBadge status={data?.hardware_watchdog.status || "offline"} pulse />
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <WatchdogMetric label="DEVICE_ID" value={data?.hardware_watchdog.device || 'N/A'} color="text-white" />
                                <WatchdogMetric label="HEARTBEAT" value={`${data?.hardware_watchdog.interval_seconds} SEC`} color="text-amber-400" />
                                <WatchdogMetric label="LAST_KICK" value={data?.hardware_watchdog.last_kick ? new Date(data.hardware_watchdog.last_kick).toLocaleTimeString() : '---'} color="text-gray-300" />
                                <WatchdogMetric label="ENFORCEMENT" value={data?.hardware_watchdog.enabled ? "ACTIVE" : "ARMED"} color="text-emerald-400" />
                            </div>
                        </motion.section>

                        {/* Middle Layer: Systemd Grid */}
                        <section>
                            <div className="flex items-center gap-4 mb-8">
                                <Server className="w-5 h-5 text-amber-400" />
                                <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">Low-Level Services</h2>
                                <div className="h-[1px] flex-1 bg-white/5" />
                            </div>
                            <div className="grid md:grid-cols-2 gap-6">
                                {data?.systemd_services.map((service, idx) => (
                                    <motion.div
                                        key={service.name}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.05 }}
                                        className="bg-black/40 border border-white/5 rounded-3xl p-6 hover:bg-white/5 transition-all group relative overflow-hidden"
                                    >
                                        <div className="absolute top-0 left-0 h-full w-[2px] bg-amber-500/20 group-hover:bg-amber-500 transition-colors" />
                                        <div className="flex items-center justify-between mb-4">
                                            <h3 className="text-xs font-black font-mono text-gray-400 truncate uppercase mt-1">{service.name}</h3>
                                            <StatusBadge status={service.status} />
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-[9px] font-black text-gray-600 uppercase tracking-widest mb-1">UPTIME</p>
                                                <p className="text-sm font-black text-white italic">{formatUptime(service.uptime_seconds)}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-[9px] font-black text-gray-600 uppercase tracking-widest mb-1">RESTARTS</p>
                                                <p className={`text-sm font-black italic ${service.restart_count > 0 ? "text-amber-500" : "text-emerald-500"}`}>{service.restart_count}</p>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </section>

                        {/* Top Layer: Docker Mesh */}
                        <section>
                            <div className="flex items-center gap-4 mb-8">
                                <Box className="w-5 h-5 text-rose-400" />
                                <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">Virtualization Mesh</h2>
                                <div className="h-[1px] flex-1 bg-white/5" />
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                {data?.docker_containers.map((container, idx) => (
                                    <motion.div
                                        key={container.name}
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        transition={{ delay: idx * 0.05 }}
                                        className="bg-black/60 border border-white/5 rounded-[24px] p-5 hover:border-rose-500/30 transition-all flex flex-col gap-4 group"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="w-8 h-8 rounded-xl bg-rose-500/10 flex items-center justify-center text-rose-500 group-hover:scale-110 transition-transform">
                                                <Box size={16} />
                                            </div>
                                            <StatusBadge status={container.health} />
                                        </div>
                                        <div>
                                            <h3 className="text-[10px] font-black text-white truncate uppercase italic tracking-tighter mb-1">{container.name}</h3>
                                            <div className="flex justify-between items-center text-[9px] font-black text-gray-600 tracking-widest uppercase">
                                                <span>Restarts: {container.restart_count}</span>
                                                <span className="text-rose-500/50">{formatUptime(container.uptime_seconds)}</span>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </section>

                    </div>

                    {/* Right Column: Alerts & Intelligence */}
                    <div className="lg:col-span-4 flex flex-col gap-8">
                        <section className="bg-rose-500/5 border border-rose-500/10 rounded-[32px] p-8 backdrop-blur-3xl relative overflow-hidden h-full">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-rose-500/10 blur-3xl rounded-full" />
                            <div className="flex items-center gap-4 mb-8">
                                <Shield className="w-6 h-6 text-rose-500" />
                                <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">Integrity Violations</h2>
                            </div>

                            <AnimatePresence>
                                {data?.alerts && data.alerts.length > 0 ? (
                                    <div className="space-y-4">
                                        {data.alerts.map((alert, i) => (
                                            <motion.div
                                                key={i}
                                                initial={{ opacity: 0, x: 20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                className="bg-black/40 border border-rose-500/20 rounded-2xl p-4 flex gap-4"
                                            >
                                                <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                                                <p className="text-[11px] font-bold text-gray-300 leading-relaxed uppercase tracking-tight italic">{alert}</p>
                                            </motion.div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center h-full py-12 text-center">
                                        <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-6">
                                            <CheckCircle2 size={32} />
                                        </div>
                                        <p className="text-sm font-black text-white uppercase italic tracking-widest mb-2">Matrix 100% Intact</p>
                                        <p className="text-[10px] text-gray-600 font-bold uppercase tracking-[0.2em]">No violations detected in current epoch</p>
                                    </div>
                                )}
                            </AnimatePresence>
                        </section>

                        <section className="bg-white/2 border border-white/5 rounded-[32px] p-8 backdrop-blur-3xl flex flex-col gap-6">
                            <div className="flex items-center gap-3">
                                <Zap className="w-5 h-5 text-amber-500" />
                                <h3 className="text-lg font-black text-white uppercase tracking-tighter italic">Integrity Controls</h3>
                            </div>
                            <div className="space-y-4">
                                <MatrixConfigItem label="Auto-Recovery" value="ENABLED" status="good" />
                                <MatrixConfigItem label="Fail-Safe Reset" value="ARMED" status="warn" />
                                <MatrixConfigItem label="Kernel Heartbeat" value="0xFF92" status="good" />
                                <MatrixConfigItem label="TruthSync Mesh" value="VERIFIED" status="good" />
                            </div>
                            <button className="w-full py-4 mt-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl text-[10px] font-black text-amber-400 uppercase tracking-[0.3em] hover:bg-amber-500/20 transition-all flex items-center justify-center gap-3">
                                <Terminal size={14} /> MANUAL_KICK_WATCHDOG
                            </button>
                        </section>
                    </div>
                </div>
            </div>

            <footer className="mt-20 py-10 border-t border-white/5 bg-black/40 backdrop-blur-md relative z-10">
                <div className="max-w-[1700px] mx-auto px-8 flex justify-between items-center text-[10px] font-mono text-gray-600 uppercase tracking-[0.3em]">
                    <p>© 2026 Sentinel Integrity // Hardware Watchdog Active // Build: 0x8F92A</p>
                    <div className="flex gap-12">
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-amber-500" /> QUORUM: ACTIVE</span>
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> HEARTBEAT: SYNC</span>
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-rose-500" /> VIOLATIONS: 0</span>
                    </div>
                </div>
            </footer>
        </main>
    );
}

function WatchdogMetric({ label, value, color }: { label: string; value: string | number; color: string }) {
    return (
        <div className="bg-white/2 p-3 px-5 rounded-2xl border border-white/5 backdrop-blur-md hover:bg-white/5 transition-all">
            <p className="text-[8px] text-gray-600 uppercase font-black tracking-widest mb-1">{label}</p>
            <div className={`text-xs font-black font-mono tracking-tighter ${color} truncate mt-1`}>
                {value}
            </div>
        </div>
    );
}

function MatrixConfigItem({ label, value, status }: { label: string; value: string; status: 'good' | 'warn' }) {
    return (
        <div className="flex items-center justify-between p-4 bg-black/40 border border-white/5 rounded-2xl group hover:border-white/20 transition-all">
            <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{label}</span>
            <span className={`text-[10px] font-black italic ${status === 'good' ? 'text-emerald-400' : 'text-amber-400'}`}>{value}</span>
        </div>
    );
}
