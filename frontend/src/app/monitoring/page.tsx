"use client";

import React, { useState } from "react";
import { Activity, ExternalLink, RefreshCw, AlertTriangle, Terminal, Layers } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

export default function MonitoringPage() {
    const [grafanaUrl, setGrafanaUrl] = useState("http://localhost:3001");

    return (
        <main className="h-screen bg-[#020617] text-white flex flex-col overflow-hidden relative">
            {/* Visual Identity Layer */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[10%] -left-[10%] w-[40%] h-[40%] bg-orange-500/10 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 brightness-150 contrast-125 pointer-events-none" />
            </div>

            <header className="px-8 py-6 flex items-center justify-between border-b border-white/5 bg-slate-950/80 backdrop-blur-2xl z-10">
                <div className="flex items-center gap-6">
                    <div className="flex flex-col">
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex items-center gap-3 mb-1"
                        >
                            <div className="h-[2px] w-8 bg-orange-500 rounded-full" />
                            <p className="text-[9px] uppercase tracking-[0.5em] text-orange-400 font-black">Sentinel Monitoring OS // v2.1</p>
                        </motion.div>
                        <h1 className="text-3xl font-black text-white uppercase tracking-tighter italic flex items-center gap-3">
                            Sovereign <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-white">Telemetry</span> Matrix
                        </h1>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className="hidden lg:flex items-center gap-6 mr-8 px-6 py-2 bg-white/5 rounded-full border border-white/5">
                        <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">Prometheus: Active</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">Loki: Active</span>
                        </div>
                    </div>

                    <Button
                        variant="outline"
                        size="sm"
                        className="gap-2 border-white/10 hover:bg-white/5 text-gray-400 hover:text-white transition-all rounded-xl h-10 px-5"
                        onClick={() => window.location.reload()}
                    >
                        <RefreshCw className="w-4 h-4" /> REFRESH MATRIX
                    </Button>
                    <a href={grafanaUrl} target="_blank" rel="noopener noreferrer">
                        <Button size="sm" className="gap-2 bg-orange-600 hover:bg-orange-500 text-white font-black tracking-tighter rounded-xl h-10 px-5 shadow-[0_0_20px_rgba(234,88,12,0.3)]">
                            <ExternalLink className="w-4 h-4" /> FULL CONSOLE
                        </Button>
                    </a>
                </div>
            </header>

            <div className="flex-1 relative bg-black w-full z-0">
                {/* Diagnostics Overlay */}
                <div className="absolute top-4 left-1/2 -translate-x-1/2 px-6 py-2 bg-black/60 backdrop-blur-xl border border-white/10 rounded-full z-10 flex items-center justify-center gap-4 text-[10px] font-black uppercase tracking-widest text-gray-500 opacity-0 hover:opacity-100 transition-opacity duration-500 cursor-default">
                    <Terminal className="w-3 h-3 text-orange-400" />
                    <span>Telemetry Ingress Status:</span>
                    <span className="text-emerald-400 italic">verified_active</span>
                    <div className="w-[1px] h-3 bg-white/10 mx-2" />
                    <Layers className="w-3 h-3 text-cyan-400" />
                    <span>Mesh Consensus:</span>
                    <span className="text-cyan-400 italic">synchronized</span>
                </div>

                <iframe
                    src={`${grafanaUrl}/d/sentinel-overview?orgId=1&kiosk&theme=dark`}
                    className="w-full h-full border-none opacity-80 hover:opacity-100 transition-opacity duration-700"
                    onError={(e) => console.error("Grafana load error", e)}
                    title="Grafana Dashboard"
                    allowFullScreen
                />

                {/* Decorative Bottom Bar */}
                <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-orange-500/20 to-transparent" />
            </div>
        </main>
    );
}
