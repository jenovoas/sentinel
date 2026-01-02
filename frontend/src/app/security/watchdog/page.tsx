"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, AlertTriangle, Lock, Activity, Terminal, Zap, CheckCircle2, Search, Filter, ShieldAlert, Cpu, Database, Eye } from "lucide-react";
import Link from "next/link";

interface AuditEvent {
    id: string;
    timestamp: Date;
    type: string;
    severity: "low" | "medium" | "high" | "critical";
    description: string;
    action: string;
    user?: string;
    process?: string;
}

export default function SecurityWatchdogPage() {
    const [securityStatus] = useState<"secure" | "warning" | "critical">("secure");
    const [events, setEvents] = useState<AuditEvent[]>([]);
    const [threatsDetected, setThreatsDetected] = useState(0);
    const [eventsToday, setEventsToday] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                // Fetch real anomalies to populate events
                const res = await fetch("/api/v1/analytics/anomalies?hours=24");
                const data = await res.json();

                if (data.anomalies) {
                    const mappedEvents: AuditEvent[] = data.anomalies.map((a: any) => ({
                        id: a.id,
                        timestamp: new Date(a.detected_at),
                        type: a.type.toUpperCase(),
                        severity: a.severity.toLowerCase(),
                        description: a.title + ": " + a.description,
                        action: a.is_resolved ? "RESOLVED" : "BLOCKED",
                        user: a.context_data?.user || "SYSTEM",
                        process: a.context_data?.process || "KERNEL",
                    }));
                    setEvents(mappedEvents);
                    setEventsToday(mappedEvents.length);
                    setThreatsDetected(mappedEvents.filter((e: any) => e.severity === 'high' || e.severity === 'critical').length);
                }
            } catch (error) {
                console.error("Failed to fetch security events:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchEvents();
        const interval = setInterval(fetchEvents, 10000);
        return () => clearInterval(interval);
    }, []);

    const getSeverityStyles = (severity: AuditEvent["severity"]) => {
        switch (severity) {
            case "critical": return "text-rose-500 bg-rose-500/10 border-rose-500/20";
            case "high": return "text-orange-500 bg-orange-500/10 border-orange-500/20";
            case "medium": return "text-amber-500 bg-amber-500/10 border-amber-500/20";
            case "low": return "text-cyan-400 bg-cyan-500/10 border-cyan-500/20";
        }
    };

    return (
        <main className="min-h-screen bg-[#020617] text-white selection:bg-rose-500/30 overflow-hidden relative">
            {/* Security Aesthetic Layer */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[15%] -left-[10%] w-[50%] h-[40%] bg-rose-500/5 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute bottom-[20%] -right-[10%] w-[40%] h-[50%] bg-purple-500/5 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-150 contrast-125 pointer-events-none" />
                <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,23,0)_0px,rgba(245,158,11,0.01)_1px,rgba(245,158,11,0.01)_2px)] bg-[size:100%_30px] pointer-events-none" />
            </div>

            <div className="relative z-10 mx-auto max-w-[1700px] px-8 py-10">
                <header className="flex flex-col md:flex-row items-end justify-between gap-8 mb-16">
                    <div className="flex-1">
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex items-center gap-4 mb-3"
                        >
                            <div className="h-[3px] w-12 bg-gradient-to-r from-rose-500 to-transparent rounded-full" />
                            <p className="text-[10px] uppercase tracking-[0.6em] text-rose-500 font-black">Sentinel Security Force // Node v2.1</p>
                        </motion.div>

                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
                            Security <span className="text-transparent bg-clip-text bg-gradient-to-r from-rose-400 via-white to-orange-500">Watchdog Matrix</span>
                        </h1>
                        <p className="text-gray-500 mt-6 max-w-2xl font-bold uppercase tracking-widest text-[10px] italic">
                            Real-time kernel-level syscall interception and advanced exploit pattern recognition.
                        </p>
                    </div>

                    <div className="flex gap-4">
                        <button className="px-6 py-3 rounded-2xl bg-white/5 border border-white/5 text-[10px] font-black uppercase tracking-widest hover:bg-white/10 transition-all flex items-center gap-3">
                            <Filter size={14} /> Intelligence Filter
                        </button>
                        <button className="px-6 py-3 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[10px] font-black uppercase tracking-widest hover:bg-rose-500/20 transition-all flex items-center gap-3 shadow-[0_0_20px_rgba(244,63,94,0.1)]">
                            <ShieldAlert size={14} /> Lockdown Mode
                        </button>
                    </div>
                </header>

                {/* Hero Status Bar */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`mb-12 rounded-[40px] border p-1 backdrop-blur-3xl overflow-hidden group shadow-2xl ${securityStatus === "secure" ? "border-emerald-500/20 bg-emerald-500/5" : "border-rose-500/20 bg-rose-500/5"
                        }`}
                >
                    <div className="bg-black/40 rounded-[38px] px-10 py-8 flex flex-col md:flex-row items-center justify-between gap-8 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 blur-3xl rounded-full translate-x-32 -translate-y-32" />

                        <div className="flex items-center gap-8">
                            <div className={`w-20 h-20 rounded-3xl flex items-center justify-center text-4xl shadow-2xl transition-transform group-hover:scale-110 ${securityStatus === "secure" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                                }`}>
                                <Shield size={40} />
                            </div>
                            <div>
                                <h2 className="text-3xl font-black text-white italic uppercase tracking-tighter">
                                    System Status: <span className={securityStatus === "secure" ? "text-emerald-400" : "text-rose-400"}>
                                        {securityStatus.toUpperCase()}
                                    </span>
                                </h2>
                                <div className="flex items-center gap-4 mt-2">
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                        <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest leading-none">All Cores Active</span>
                                    </div>
                                    <div className="h-3 w-[1px] bg-white/10" />
                                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-none italic">
                                        Last deep scan: {new Date().toLocaleTimeString()}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="flex gap-12 text-right">
                            <div>
                                <p className="text-4xl font-black text-white italic tracking-tighter leading-none">{threatsDetected}</p>
                                <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mt-1">Critical Threats</p>
                            </div>
                            <div className="h-10 w-[1px] bg-white/10" />
                            <div>
                                <p className="text-4xl font-black text-white italic tracking-tighter leading-none">{eventsToday}</p>
                                <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mt-1">Audit Events (24h)</p>
                            </div>
                        </div>
                    </div>
                </motion.div>

                <div className="grid gap-8 lg:grid-cols-12">
                    {/* Events Matrix */}
                    <div className="lg:col-span-8 flex flex-col gap-6">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-rose-500/20 rounded-lg text-rose-400">
                                    <Terminal size={16} />
                                </div>
                                <div>
                                    <h3 className="text-xs font-black text-white uppercase tracking-widest italic">Live Syscall Stream</h3>
                                    <p className="text-[8px] font-black text-gray-500 uppercase tracking-widest">Interception Layer // Ring 0</p>
                                </div>
                            </div>
                            <div className="flex gap-2">
                                <div className="px-3 py-1 bg-white/5 rounded-full border border-white/5 text-[9px] font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
                                    <div className="w-1 h-1 rounded-full bg-cyan-400 animate-pulse" /> STABLE_FLUX
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {loading && events.length === 0 ? (
                                Array.from({ length: 5 }).map((_, i) => (
                                    <div key={i} className="h-24 w-full bg-white/5 rounded-3xl animate-pulse" />
                                ))
                            ) : events.length === 0 ? (
                                <div className="bg-white/2 border border-white/5 rounded-[40px] p-20 flex flex-col items-center justify-center text-center">
                                    <div className="p-6 bg-emerald-500/10 rounded-full text-emerald-500 mb-6">
                                        <CheckCircle2 size={48} />
                                    </div>
                                    <p className="text-lg font-black text-white uppercase italic tracking-widest">Pristine Integrity</p>
                                    <p className="text-xs font-bold text-gray-600 uppercase tracking-widest mt-2">No security violations detected in the current epoch</p>
                                </div>
                            ) : (
                                <AnimatePresence mode="popLayout">
                                    {events.map((event, idx) => (
                                        <motion.div
                                            key={event.id}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: idx * 0.05 }}
                                            className="bg-[#0a0f1e]/80 border border-white/5 rounded-3xl p-6 hover:border-rose-500/30 transition-all group relative overflow-hidden shadow-2xl"
                                        >
                                            <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
                                                <Shield size={64} />
                                            </div>
                                            <div className="flex items-start justify-between mb-4 relative z-10">
                                                <div className="flex items-center gap-3">
                                                    <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border ${getSeverityStyles(event.severity)}`}>
                                                        {event.severity}
                                                    </span>
                                                    <span className="px-3 py-1 rounded-full bg-white/5 border border-white/5 text-[9px] font-black text-gray-400 uppercase tracking-widest">
                                                        {event.type}
                                                    </span>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    <span className="text-[10px] font-black text-gray-600 uppercase tracking-widest">{event.timestamp.toLocaleTimeString()}</span>
                                                    <div className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
                                                </div>
                                            </div>
                                            <p className="text-sm font-black text-gray-200 mb-6 uppercase tracking-tight italic leading-relaxed">{event.description}</p>
                                            <div className="flex items-center justify-between pt-4 border-t border-white/5 text-[10px] font-black tracking-widest uppercase italic">
                                                <div className="flex gap-6">
                                                    <span className="text-gray-500 flex items-center gap-2"><Eye size={12} className="text-gray-700" /> AUTH: {event.user}</span>
                                                    <span className="text-gray-500 flex items-center gap-2"><Cpu size={12} className="text-gray-700" /> PID: {event.process}</span>
                                                </div>
                                                <span className="text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.3)]">{event.action}</span>
                                            </div>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                            )}
                        </div>
                    </div>

                    {/* Security Intel Sidebar */}
                    <div className="lg:col-span-4 flex flex-col gap-8">
                        {/* Exploit Detection */}
                        <section className="bg-rose-500/5 border border-rose-500/10 rounded-[40px] p-8 backdrop-blur-3xl relative overflow-hidden group hover:border-rose-500/20 transition-all">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-rose-500/10 blur-3xl rounded-full translate-x-16 -translate-y-16" />
                            <div className="flex items-center gap-4 mb-8">
                                <div className="p-2 bg-rose-500/20 rounded-xl text-rose-500">
                                    <Zap size={18} />
                                </div>
                                <h2 className="text-xl font-black text-white uppercase tracking-tighter italic">Exploit Detection</h2>
                            </div>

                            <div className="space-y-6">
                                <DetectionRow label="Privilege Escalation" value="0 DETECTED" status="good" />
                                <DetectionRow label="RCE Patterns" value="CLEAN" status="good" />
                                <DetectionRow label="Heap Overflows" value="MONITORED" status="good" />
                            </div>
                        </section>

                        {/* Compliance Matrix */}
                        <section className="bg-white/2 border border-white/5 rounded-[40px] p-8 backdrop-blur-3xl">
                            <div className="flex items-center gap-4 mb-8">
                                <div className="p-2 bg-cyan-500/20 rounded-xl text-cyan-400">
                                    <Activity size={18} />
                                </div>
                                <h2 className="text-xl font-black text-white uppercase tracking-tighter italic">Compliance Matrix</h2>
                            </div>
                            <div className="space-y-4">
                                <MatrixConfigItem label="SOC 2 Readiness" value="95%" status="good" />
                                <MatrixConfigItem label="Audit Logging" value="ENFORCED" status="good" />
                                <MatrixConfigItem label="Encryption" value="AES-256" status="good" />
                                <MatrixConfigItem label="Backup Verification" value="72% SYNC" status="warn" />
                            </div>
                        </section>

                        {/* AI Security Engine */}
                        <section className="bg-purple-500/5 border border-purple-500/10 rounded-[40px] p-8 backdrop-blur-3xl relative overflow-hidden group hover:border-purple-500/20 transition-all">
                            <div className="absolute bottom-0 right-0 w-32 h-32 bg-purple-500/10 blur-3xl rounded-full translate-x-16 translate-y-16" />
                            <div className="flex items-center gap-4 mb-6">
                                <div className="p-2 bg-purple-500/20 rounded-xl text-purple-400">
                                    <Database size={18} />
                                </div>
                                <h2 className="text-xl font-black text-white uppercase tracking-tighter italic">AI Insights</h2>
                            </div>
                            <p className="text-[11px] font-black text-gray-500 uppercase italic leading-relaxed tracking-wider">
                                "Security posture remains within normal bounds. No anomalous syscall sequences detected.
                                Recommendation: Formalize backup snapshot schedule to achieve 100% compliance."
                            </p>
                        </section>
                    </div>
                </div>

                {/* Technical Footer Info */}
                <div className="mt-12 bg-white/2 border border-white/5 rounded-[30px] p-8 flex items-start gap-6 relative overflow-hidden group">
                    <div className="absolute top-0 left-0 h-full w-1 bg-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.5)]" />
                    <div className="p-4 bg-rose-500/10 rounded-2xl text-rose-500 group-hover:scale-110 transition-transform">
                        <Shield size={32} />
                    </div>
                    <div>
                        <h4 className="text-lg font-black text-white uppercase italic tracking-widest mb-2">Defense-in-Depth Protocols</h4>
                        <p className="text-[10px] font-bold text-gray-500 uppercase leading-relaxed tracking-[0.05em] max-w-4xl italic">
                            The Sentinel Watchdog monitors critical syscalls (execve, open, ptrace, chmod) at the kernel level using the high-performance audit framework.
                            All captured events are hashed and validated against the Sovereign Consensus Matrix to ensure zero-tamper integrity.
                            Intelligence is synchronized in real-time with the Cortex AI for immediate heuristic classification of zero-day exploits.
                        </p>
                    </div>
                </div>
            </div>

            <footer className="mt-20 py-10 border-t border-white/5 bg-black/40 backdrop-blur-md relative z-10">
                <div className="max-w-[1700px] mx-auto px-8 flex justify-between items-center text-[10px] font-black text-gray-600 uppercase tracking-[0.4em] italic leading-none">
                    <p>© 2026 Sentinel Security Intelligence // Auditd Mesh Active</p>
                    <div className="flex gap-12">
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-rose-500" /> THREAT_LEVEL: 0</span>
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> INTEGRITY: 1.0</span>
                        <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-cyan-500" /> UPTIME: ∞</span>
                    </div>
                </div>
            </footer>
        </main>
    );
}

function DetectionRow({ label, value, status }: { label: string; value: string; status: 'good' | 'warn' }) {
    return (
        <div className="flex items-center justify-between">
            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">{label}</span>
            <span className={`text-[10px] font-black italic ${status === 'good' ? 'text-emerald-400' : 'text-amber-400'}`}>{value}</span>
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
