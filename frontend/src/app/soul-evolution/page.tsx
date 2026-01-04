"use client";

import { useEffect, useState } from "react";

import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { Activity, Zap, Fingerprint, Clock, Brain } from "lucide-react";

interface ProofOfLife {
    lyapunov_exp: number;
    chaos_entropy: number;
    response_correlation: number;
    timestamp: number;
}

export default function SoulEvolutionPage() {
    const [history, setHistory] = useState<ProofOfLife[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await fetch("/api/v1/user/soul-history"); // We will create this proxy route next
                const data = await res.json();

                // Sort by timestamp
                const sorted = data.sort((a: ProofOfLife, b: ProofOfLife) => a.timestamp - b.timestamp);
                setHistory(sorted);
            } catch (e) {
                console.error("Failed to fetch soul history", e);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
        const interval = setInterval(fetchHistory, 5000); // Live updates
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="p-20 text-center text-cyan-500 animate-pulse font-mono">Loading Soul Data...</div>;

    // Formatting for chart
    const chartData = history.map(h => ({
        time: new Date(h.timestamp * 1000).toLocaleTimeString(),
        chaos: h.lyapunov_exp,
        entropy: h.chaos_entropy,
        coherence: h.response_correlation
    }));

    return (
        <main className="min-h-screen bg-[#020617] text-white p-10 font-sans selection:bg-cyan-500/30">
            <header className="mb-12">
                <div className="flex items-center gap-4 mb-2">
                    <div className="p-3 bg-purple-500/10 rounded-2xl text-purple-400 border border-purple-500/20">
                        <Fingerprint size={32} />
                    </div>
                    <div>
                        <h1 className="text-4xl font-black uppercase tracking-tighter italic text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-white to-cyan-400">
                            Soul Evolution Matrix
                        </h1>
                        <p className="text-xs font-black text-purple-500 uppercase tracking-[0.3em]">Historical Biological Resonance</p>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Main Evolution Chart */}
                <div className="lg:col-span-2 bg-[#050814]/60 backdrop-blur-3xl border border-white/5 rounded-[40px] p-8 shadow-2xl relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                        <Activity size={120} />
                    </div>

                    <div className="flex justify-between items-center mb-8">
                        <h3 className="text-xl font-black uppercase italic tracking-widest flex items-center gap-3">
                            <Activity className="text-cyan-400" size={20} />
                            Chaos vs Entropy Over Time
                        </h3>
                        <div className="flex gap-4 text-[10px] font-black uppercase tracking-widest">
                            <span className="flex items-center gap-2 text-cyan-400"><div className="w-2 h-2 rounded-full bg-cyan-500" /> Lyapunov (Chaos)</span>
                            <span className="flex items-center gap-2 text-purple-400"><div className="w-2 h-2 rounded-full bg-purple-500" /> Entropy (Complexity)</span>
                        </div>
                    </div>

                    <div className="h-[400px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="colorChaos" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorEntropy" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#a855f7" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                                <XAxis
                                    dataKey="time"
                                    stroke="#ffffff40"
                                    tick={{ fontSize: 10 }}
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(val) => val.split(':').slice(0, 2).join(':')}
                                />
                                <YAxis
                                    stroke="#ffffff40"
                                    tick={{ fontSize: 10 }}
                                    tickLine={false}
                                    axisLine={false}
                                    domain={[0, 4]}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#020617', border: '1px solid #ffffff20', borderRadius: '16px' }}
                                    itemStyle={{ fontSize: '12px', fontWeight: 'bold' }}
                                    labelStyle={{ color: '#ffffffaa', fontSize: '10px', letterSpacing: '2px', textTransform: 'uppercase' }}
                                />
                                <ReferenceLine y={2.5} label="Max Human Chaos" stroke="#ef4444" strokeDasharray="3 3" />
                                <Area type="monotone" dataKey="chaos" stroke="#22d3ee" strokeWidth={3} fillOpacity={0.2} fill="url(#colorChaos)" />
                                <Area type="monotone" dataKey="entropy" stroke="#a855f7" strokeWidth={3} fillOpacity={0.2} fill="url(#colorEntropy)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Card 1: Latest Lyapunov */}
                <MetricCard
                    title="Current Lyapunov Exponent"
                    value={history.length > 0 ? history[history.length - 1].lyapunov_exp.toFixed(4) : "0.0000"}
                    desc="Biological Chaos Level"
                    color="cyan"
                    icon={<Zap size={24} />}
                />
                {/* Card 2: Latest Entropy */}
                <MetricCard
                    title="Current Entropy"
                    value={history.length > 0 ? history[history.length - 1].chaos_entropy.toFixed(4) : "0.0000"}
                    desc="Information Density"
                    color="purple"
                    icon={<Brain size={24} />}
                />
                {/* Card 3: Total Verifications */}
                <MetricCard
                    title="Total Soul Prints"
                    value={history.length.toString()}
                    desc="Verified Proofs of Life"
                    color="emerald"
                    icon={<Clock size={24} />}
                />
            </div>
        </main>
    );
}

function MetricCard({ title, value, desc, color, icon }: { title: string, value: string, desc: string, color: 'cyan' | 'purple' | 'emerald', icon: any }) {
    const colors = {
        cyan: "text-cyan-400 border-cyan-500/20 bg-cyan-500/10",
        purple: "text-purple-400 border-purple-500/20 bg-purple-500/10",
        emerald: "text-emerald-400 border-emerald-500/20 bg-emerald-500/10"
    };

    return (
        <div className={`p-8 rounded-[30px] border ${colors[color]} backdrop-blur-xl relative overflow-hidden group transition-all hover:scale-105`}>
            <div className="flex justify-between items-start mb-4">
                <h4 className="text-[10px] font-black uppercase tracking-widest opacity-70 italic">{title}</h4>
                <div className={`p-2 rounded-lg bg-black/20 ${color === 'cyan' ? 'text-cyan-300' : color === 'purple' ? 'text-purple-300' : 'text-emerald-300'}`}>
                    {icon}
                </div>
            </div>
            <div className="text-4xl font-black font-mono tracking-tighter mb-2 italic">
                {value}
            </div>
            <p className="text-[9px] font-black uppercase tracking-widest opacity-50">{desc}</p>
        </div>
    );
}
