"use client";

import React from 'react';
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';
import { Cpu, Server, Wifi, Activity } from 'lucide-react';

interface MetricCardProps {
    title: string;
    value: string;
    unit: string;
    icon: React.ReactNode;
    data: { time: number; value: number }[];
    color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, unit, icon, data, color }) => (
    <div className="bg-slate-900/50 backdrop-blur-sm p-4 rounded-xl border border-slate-800 flex flex-col justify-between overflow-hidden relative">
        <div className="flex justify-between items-start z-10 mb-2">
            <div>
                <h3 className="text-xs font-medium text-slate-400 uppercase tracking-widest">{title}</h3>
                <div className="flex items-baseline mt-1 space-x-1">
                    <span className="text-2xl font-bold font-mono text-white">{value}</span>
                    <span className="text-xs text-slate-500 font-mono">{unit}</span>
                </div>
            </div>
            <div className={`p-2 rounded-lg bg-opacity-10 ${color.replace('text-', 'bg-')}`}>
                {icon}
            </div>
        </div>

        <div className="h-16 w-full absolute bottom-0 left-0 right-0 opacity-50">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id={`gradient-${title}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="currentColor" stopOpacity={0.3} className={color} />
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
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    </div>
);

export const MetricsGrid = () => {
    // Mock Data Generator
    const generateData = () => Array.from({ length: 20 }, (_, i) => ({
        time: i,
        value: Math.floor(Math.random() * 50) + 20
    }));

    return (
        <div className="grid grid-cols-2 gap-4 h-full">
            <MetricCard
                title="Latency P99"
                value="1.2"
                unit="ms"
                icon={<Activity className="w-4 h-4 text-emerald-500" />}
                data={generateData()}
                color="text-emerald-500"
            />
            <MetricCard
                title="Requests"
                value="14.5"
                unit="k/rps"
                icon={<Wifi className="w-4 h-4 text-blue-500" />}
                data={generateData()}
                color="text-blue-500"
            />
            <MetricCard
                title="CPU Kernel"
                value="12"
                unit="%"
                icon={<Cpu className="w-4 h-4 text-purple-500" />}
                data={generateData()}
                color="text-purple-500"
            />
            <MetricCard
                title="Mem Usage"
                value="2.4"
                unit="GB"
                icon={<Server className="w-4 h-4 text-orange-500" />}
                data={generateData()}
                color="text-orange-500"
            />
        </div>
    );
};
