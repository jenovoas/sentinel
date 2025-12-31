'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowRight, Clock, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function LatencyComparison() {
    return (
        <Card className="border-none bg-gradient-to-br from-slate-900 to-slate-800 text-white shadow-2xl overflow-hidden">
            <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg font-mono tracking-widest uppercase">
                    <Clock className="text-blue-400" />
                    Latency Superiority
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-8">
                {/* Legacy Flow */}
                <div className="space-y-2 opacity-50 hover:opacity-100 transition-opacity">
                    <div className="flex justify-between items-center text-xs font-mono uppercase tracking-widest text-slate-400">
                        <span>Legacy EDR / Cloud SIEM</span>
                        <span className="text-red-400">SLOW (&gt; 5.0s)</span>
                    </div>
                    <div className="relative h-12 bg-white/5 rounded-lg flex items-center px-4 overflow-hidden border border-white/10">
                        <div className="absolute left-0 top-0 bottom-0 bg-red-500/10 w-full animate-pulse" style={{ animationDuration: '5s' }} />
                        <div className="z-10 flex items-center gap-4 w-full justify-between">
                            <Badge variant="outline" className="border-red-500/50 text-red-500 text-[10px]">Log</Badge>
                            <ArrowRight size={14} className="text-slate-600" />
                            <Badge variant="outline" className="border-red-500/50 text-red-500 text-[10px]">Ingest</Badge>
                            <ArrowRight size={14} className="text-slate-600" />
                            <Badge variant="outline" className="border-red-500/50 text-red-500 text-[10px]">Query</Badge>
                            <ArrowRight size={14} className="text-slate-600" />
                            <div className="flex items-center gap-1 text-red-500 font-bold">
                                <ShieldAlert size={16} />
                                <span>FAIL</span>
                            </div>
                        </div>
                    </div>
                    <div className="text-[10px] text-right font-mono text-red-400">
                        Avg Latency: 5,240ms (Attack Succeeded)
                    </div>
                </div>

                {/* Sentinel Flow */}
                <div className="space-y-2">
                    <div className="flex justify-between items-center text-xs font-mono uppercase tracking-widest text-emerald-400">
                        <span>Sentinel Cortex (eBPF)</span>
                        <span className="animate-pulse">INSTANT (&lt; 1ms)</span>
                    </div>
                    <div className="relative h-14 bg-emerald-950/30 rounded-lg flex items-center px-4 overflow-hidden border border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.1)]">
                        <div className="absolute left-0 top-0 bottom-0 bg-emerald-500/20 w-full" />
                        <div className="z-10 flex items-center gap-4 w-full justify-between">
                            <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50 text-[10px] font-mono">KERNEL</Badge>
                            <div className="h-0.5 flex-1 bg-gradient-to-r from-emerald-500/50 to-emerald-500" />
                            <div className="flex items-center gap-2 text-emerald-400 font-black tracking-tighter text-lg">
                                <Zap size={18} fill="currentColor" />
                                <span>BLOCK</span>
                            </div>
                        </div>
                    </div>
                    <div className="flex justify-between items-center">
                        <div className="flex gap-2">
                            <Badge variant="secondary" className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px]">Pre-Execution</Badge>
                            <Badge variant="secondary" className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px]">Zero-Copy</Badge>
                        </div>
                        <div className="text-xs font-mono text-emerald-400 font-bold">
                            Avg Latency: 0.045ms (Attack Neutralized)
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

function Zap({ size, fill, className }: { size?: number, fill?: string, className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width={size || 24}
            height={size || 24}
            viewBox="0 0 24 24"
            fill={fill || "none"}
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
    )
}
