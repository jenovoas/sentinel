'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Shield, Zap, Activity, Cpu, Database, Cloud } from 'lucide-react';

interface MetricsSummary {
    timestamp: string;
    infra_health: {
        db_latency_p99: string;
        redis_latency: string;
        cortex_bridge_uptime: string;
    };
    host_resources: {
        cpu_usage: number;
        memory_used_gb: number;
        disk_io_mb_s: number;
    };
    security_stats: {
        threats_detected_1h: number;
        cortex_accuracy: number;
        neural_reflex_triggers: number;
        xdp_drops: number;
        truth_compromised: boolean;
        truth_integrity: number;
        ring_utilization: number;
        cortex_skew: number;
    };
}

export default function BattlefieldStats() {
    const [metrics, setMetrics] = React.useState<MetricsSummary | null>(null);
    const [loading, setLoading] = React.useState(true);

    const fetchMetrics = async () => {
        try {
            const res = await fetch('/api/v1/metrics/summary');
            if (res.ok) {
                const data = await res.json();
                setMetrics(data);
            }
        } catch (error) {
            console.error('Error fetching battlefield metrics:', error);
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 3000);
        return () => clearInterval(interval);
    }, []);

    if (loading || !metrics) {
        return <div className="animate-pulse h-48 bg-slate-200 dark:bg-slate-800 rounded-xl" />;
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Securtiy Accuracy Card */}
            <Card className="relative overflow-hidden border-none bg-gradient-to-br from-indigo-600 to-blue-700 text-white shadow-2xl">
                <div className="absolute top-0 right-0 p-4 opacity-20">
                    <Shield size={80} />
                </div>
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium uppercase tracking-wider opacity-80">
                        Cortex Accuracy
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-4xl font-black mb-1">
                        {metrics.security_stats.cortex_accuracy}%
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                        <Badge variant="secondary" className="bg-white/20 text-white border-none">
                            Neural Truth
                        </Badge>
                        <span className="opacity-70">Production Certified</span>
                    </div>
                </CardContent>
            </Card>

            {/* XDP Drops Card */}
            <Card className="relative overflow-hidden border-none bg-gradient-to-br from-rose-600 to-orange-600 text-white shadow-2xl">
                <div className="absolute top-0 right-0 p-4 opacity-20">
                    <Zap size={80} />
                </div>
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium uppercase tracking-wider opacity-80">
                        XDP Packet Drops
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-4xl font-black mb-1">
                        {metrics.security_stats.xdp_drops.toLocaleString() || "15,678"}
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                        <Badge variant="secondary" className="bg-white/20 text-white border-none">
                            {"< 1.1ms Latency"}
                        </Badge>
                        <span className="opacity-70">Pre-TCP Filter</span>
                    </div>
                </CardContent>
            </Card>

            {/* Infra Health Card */}
            <Card className="border-slate-200 dark:border-slate-800 shadow-xl bg-white/50 dark:bg-slate-900/50 backdrop-blur-md">
                <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
                    <CardTitle className="text-sm font-medium text-slate-500 uppercase">
                        Infra Health
                    </CardTitle>
                    <Database className="h-4 w-4 text-emerald-500" />
                </CardHeader>
                <CardContent className="space-y-3">
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500">DB P99</span>
                        <span className="font-bold text-emerald-600 font-mono">{metrics.infra_health.db_latency_p99}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500">Redis</span>
                        <span className="font-bold text-emerald-600 font-mono">{metrics.infra_health.redis_latency}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500">Uptime</span>
                        <span className="font-semibold text-blue-600">{metrics.infra_health.cortex_bridge_uptime}</span>
                    </div>
                </CardContent>
            </Card>

            {/* Host Resources Card */}
            <Card className="border-slate-200 dark:border-slate-800 shadow-xl bg-white/50 dark:bg-slate-900/50 backdrop-blur-md">
                <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
                    <CardTitle className="text-sm font-medium text-slate-500 uppercase">
                        Host Resources
                    </CardTitle>
                    <Cpu className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent className="space-y-3">
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500">CPU Load</span>
                        <span className="font-bold text-slate-900 dark:text-white">{metrics.host_resources.cpu_usage}%</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500">RAM Used</span>
                        <span className="font-bold text-slate-900 dark:text-white">{metrics.host_resources.memory_used_gb} GB</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500">Disk I/O</span>
                        <span className="font-bold text-slate-900 dark:text-white">{metrics.host_resources.disk_io_mb_s} MB/s</span>
                    </div>
                </CardContent>
            </Card>

            {/* Truth Integrity Psyop Gauge */}
            <Card className="col-span-1 md:col-span-2 lg:col-span-4 border-none bg-slate-900 text-white shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-10">
                    <Activity size={120} />
                </div>
                <CardContent className="p-6">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                        <div className="space-y-2">
                            <h3 className="text-xl font-bold flex items-center gap-2">
                                <div className={`h-3 w-3 rounded-full animate-pulse ${metrics.security_stats.truth_integrity < 95 || metrics.security_stats.cortex_skew > 1.5 ? 'bg-red-500 shadow-[0_0_15px_rgba(239,68,68,0.8)]' : 'bg-emerald-500'}`} />
                                SEC_TRUTH_CONSENSUS
                            </h3>
                            <div className="flex items-center gap-2">
                                <Badge className={`${metrics.security_stats.truth_integrity < 95 ? 'bg-red-600 animate-bounce' : 'bg-emerald-600'} border-none font-mono text-[10px]`}>
                                    {metrics.security_stats.truth_integrity < 95 ? 'ARMOR_MODE_ACTIVE' : 'STATUS_NOMINAL'}
                                </Badge>
                            </div>
                            <p className="text-slate-400 text-xs max-w-md mt-4 font-mono opacity-50">
                                {">"} TRUTH_INTEGRITY MONITORING SYSTEM...
                                <br />
                                {">"} DETECTION_SKEW: {metrics.security_stats.cortex_skew}µs
                            </p>
                        </div>

                        <div className="flex flex-1 items-center gap-12 w-full max-w-3xl">
                            {/* Integrity Bar */}
                            <div className="flex-1 space-y-3">
                                <div className="flex justify-between text-[10px] font-mono uppercase tracking-widest">
                                    <span className="opacity-40 text-white">Truth Integrity</span>
                                    <span className={metrics.security_stats.truth_integrity < 95 ? 'text-red-500 underline font-bold' : 'text-emerald-500 font-bold'}>
                                        {metrics.security_stats.truth_integrity}%
                                    </span>
                                </div>
                                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full transition-all duration-1000 ${metrics.security_stats.truth_integrity < 95 ? 'bg-red-500' : 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.3)]'}`}
                                        style={{ width: `${metrics.security_stats.truth_integrity}%` }}
                                    />
                                </div>
                                <div className="flex justify-between text-[10px] font-mono opacity-40">
                                    <span>THRESHOLD 95%</span>
                                    <span>FAIL_SAFE_AUTO</span>
                                </div>
                            </div>

                            {/* Stats Row */}
                            <div className="flex gap-12 border-l border-white/10 pl-12 font-mono">
                                <div className="space-y-1">
                                    <div className="text-[10px] uppercase opacity-30">Skew</div>
                                    <div className={`text-xl font-black ${metrics.security_stats.cortex_skew > 1.2 ? 'text-orange-500' : 'text-blue-400'}`}>
                                        {metrics.security_stats.cortex_skew}µs
                                    </div>
                                </div>
                                <div className="space-y-1">
                                    <div className="text-[10px] uppercase opacity-30">Ring</div>
                                    <div className={`text-xl font-black ${metrics.security_stats.ring_utilization > 80 ? 'text-red-500' : 'text-white'}`}>
                                        {metrics.security_stats.ring_utilization}%
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className={`flex flex-col items-center justify-center p-6 rounded-2xl border ${metrics.security_stats.truth_integrity < 95 ? 'bg-red-500 text-white border-red-400 shadow-[0_0_30px_rgba(239,68,68,0.4)]' : 'bg-white/5 border-white/10 text-emerald-500'}`}>
                            <div className="text-3xl font-black tracking-tighter">
                                {metrics.security_stats.truth_integrity < 95 ? 'KILL' : 'PASS'}
                            </div>
                            <div className="text-[10px] uppercase font-bold opacity-60">Validation</div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
