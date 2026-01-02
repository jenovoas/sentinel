"use client";

import React from 'react';
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';
import { Cpu, Server, Wifi, Activity, Zap, BrainCircuit, Network, Database } from 'lucide-react';

interface MetricCardProps {
    title: string;
    value: string;
    unit: string;
    icon: React.ReactNode;
    data: { time: number; value: number }[];
    color: string;
    description: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, unit, icon, data, color, description }) => (
    <div className="bg-slate-950/40 backdrop-blur-md p-5 rounded-[28px] border border-white/5 flex flex-col h-full overflow-hidden relative group hover:border-white/10 transition-all shadow-xl">
        <div className="flex justify-between items-start z-10 mb-4">
            <div className="flex gap-4">
                <div className={`p-3 rounded-2xl bg-white/5 border border-white/5 group-hover:scale-110 transition-transform ${color}`}>
                    {icon}
                </div>
                <div>
                    <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] italic mb-1">{title}</h3>
                    <div className="flex items-baseline gap-2">
                        <span className="text-2xl font-black font-mono text-white italic tracking-tighter">{value}</span>
                        <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest">{unit}</span>
                    </div>
                </div>
            </div>
        </div>

        <div className="mt-2 flex-1 relative min-h-[60px]">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id={`gradient-${title}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="currentColor" stopOpacity={0.4} className={color} />
                            <stop offset="95%" stopColor="currentColor" stopOpacity={0} className={color} />
                        </linearGradient>
                    </defs>
                    <Area
                        type="monotone"
                        dataKey="value"
                        stroke="currentColor"
                        fill={`url(#gradient-${title})`}
                        strokeWidth={2}
                        className={color}
                        animationDuration={2000}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>

        <p className="mt-4 text-[8px] font-bold text-gray-700 uppercase tracking-widest leading-none italic">
            STATUS: {description}
        </p>
    </div>
);

export const MetricsGrid = () => {
    // Neural Data Generator
    const generateData = (seed: number) => Array.from({ length: 20 }, (_, i) => ({
        time: i,
        value: Math.floor(Math.random() * 20) + seed
    }));

    return (
        <div className="grid grid-cols-1 gap-4 w-full">
            <MetricCard
                title="Neural Latency"
                value="1.24"
                unit="ms"
                icon={<Activity size={18} />}
                data={generateData(10)}
                color="text-cyan-400"
                description="Synchronous Stability"
            />
            <MetricCard
                title="Cortex Load"
                value="14.5"
                unit="TFLOPs"
                icon={<BrainCircuit size={18} />}
                data={generateData(30)}
                color="text-purple-400"
                description="Neural synthesis throughput"
            />
            <MetricCard
                title="Kernel Cycles"
                value="12.2"
                unit="M/s"
                icon={<Cpu size={18} />}
                data={generateData(15)}
                color="text-emerald-400"
                description="eBPF Ringbuf Integrity"
            />
            <MetricCard
                title="Memory Index"
                value="2.4"
                unit="GB"
                icon={<Database size={18} />}
                data={generateData(50)}
                color="text-amber-400"
                description="Vector storage allocation"
            />
        </div>
    );
};
