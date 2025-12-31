"use client";

import React, { useState, useEffect } from 'react';
import MandalaUI from '@/components/cortex/MandalaUI';
import { KillBoard } from '@/components/cortex/KillBoard';
import { MetricsGrid } from '@/components/cortex/MetricsGrid';
import { AIChat } from '@/components/cortex/AIChat';
import { motion } from 'framer-motion';

export default function CortexDashboard() {
    // const [integrity, setIntegrity] = useState(100);
    const [kills, setKills] = useState(15689);

    // Simulación de "Armor Mode" y actividad para la demo
    useEffect(() => {
        const interval = setInterval(() => {
            // Randomly dip integrity to show effects (Deprecated for Mandala)
            // if (Math.random() > 0.8) {
            //    setIntegrity(prev => Math.max(90, prev - 5));
            // } else {
            //    setIntegrity(prev => Math.min(100, prev + 1));
            // }

            // Increment kills
            setKills(prev => prev + Math.floor(Math.random() * 5));
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    return (
        <main className="min-h-screen bg-slate-950 text-white p-6 font-sans overflow-hidden bg-[url('/grid-pattern.svg')]">
            {/* Top Bar */}
            <header className="flex justify-between items-center mb-6 border-b border-white/10 pb-4">
                <div className="flex items-center space-x-4">
                    <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
                    <h1 className="text-2xl font-bold tracking-[0.2em] uppercase text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-500">
                        Sentinel Headquarters
                    </h1>
                </div>
                <div className="flex space-x-6 text-xs font-mono text-slate-400">
                    <span>UPTIME: 99.999%</span>
                    <span>KERNEL: 6.8.9-SENTINEL-HARDENED</span>
                    <span>DEFCON: 5</span>
                </div>
            </header>

            {/* Main Grid Layout (Single Pane of Glass) */}
            <div className="grid grid-cols-12 gap-6 h-[calc(100vh-140px)]">

                {/* Left Column: Metrics (20%) - Span 3 */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5 }}
                    className="col-span-3 h-full"
                >
                    <MetricsGrid />
                </motion.div>

                {/* Center Column: Truth & Chat (50%) - Span 6 */}
                <div className="col-span-6 flex flex-col gap-6 h-full">
                    {/* Upper Center: Truth Gauge */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.7 }}
                        className="flex-1 flex items-center justify-center p-6"
                    >
                        <div className="scale-100">
                            <MandalaUI />
                        </div>
                    </motion.div>

                    {/* Lower Center: AI Command Chat */}
                    <motion.div
                        initial={{ opacity: 0, y: 50 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="h-1/3"
                    >
                        <AIChat />
                    </motion.div>
                </div>

                {/* Right Column: Kill Board (30%) - Span 3 */}
                <motion.div
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="col-span-3 h-full"
                >
                    <KillBoard kills={kills} />
                </motion.div>

            </div>
        </main>
    );
}
