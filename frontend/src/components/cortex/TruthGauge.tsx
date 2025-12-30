"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Shield, ShieldAlert, CheckCircle } from 'lucide-react';

interface TruthGaugeProps {
    integrity: number; // 0 to 100
}

export const TruthGauge: React.FC<TruthGaugeProps> = ({ integrity }) => {
    const isArmorMode = integrity < 95;
    const statusColor = isArmorMode ? 'text-red-500' : 'text-emerald-500';
    const ringColor = isArmorMode ? '#ef4444' : '#10b981'; // Tailwind red-500 / emerald-500

    return (
        <div className="flex flex-col items-center justify-center p-6 bg-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-800 shadow-2xl relative overflow-hidden">
            {/* Background Pulse Effect in Armor Mode */}
            {isArmorMode && (
                <motion.div
                    animate={{ opacity: [0.1, 0.3, 0.1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                    className="absolute inset-0 bg-red-900/20 z-0"
                />
            )}

            <div className="relative z-10 w-64 h-64 flex items-center justify-center">
                {/* Outer Ring */}
                <svg className="w-full h-full transform -rotate-90">
                    <circle
                        cx="128"
                        cy="128"
                        r="120"
                        stroke="#1e293b"
                        strokeWidth="12"
                        fill="transparent"
                    />
                    <motion.circle
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: integrity / 100 }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                        cx="128"
                        cy="128"
                        r="120"
                        stroke={ringColor}
                        strokeWidth="12"
                        fill="transparent"
                        strokeDasharray="1 1" // This is actually pathLength relative, handled by motion
                        strokeLinecap="round"
                    />
                </svg>

                {/* Center Content */}
                <div className="absolute flex flex-col items-center">
                    <motion.div
                        animate={isArmorMode ? { scale: [1, 1.1, 1] } : {}}
                        transition={{ duration: 0.5, repeat: isArmorMode ? Infinity : 0, repeatDelay: 1 }}
                    >
                        {isArmorMode ? (
                            <ShieldAlert className="w-16 h-16 text-red-500 mb-2" />
                        ) : (
                            <Shield className="w-16 h-16 text-emerald-500 mb-2" />
                        )}
                    </motion.div>

                    <span className={`text-5xl font-bold font-mono tracking-tighter ${statusColor}`}>
                        {integrity}%
                    </span>
                    <span className="text-xs text-slate-400 uppercase tracking-widest mt-1">
                        Truth Integrity
                    </span>
                </div>
            </div>

            {/* Status Label */}
            <motion.div
                className={`mt-4 px-4 py-1 rounded-full text-sm font-bold tracking-widest border ${isArmorMode
                        ? 'bg-red-500/10 border-red-500/50 text-red-500'
                        : 'bg-emerald-500/10 border-emerald-500/50 text-emerald-500'
                    }`}
                animate={isArmorMode ? { opacity: [1, 0.5, 1] } : {}}
                transition={{ duration: 1, repeat: Infinity }}
            >
                {isArmorMode ? '⚠️ ARMOR MODE ACTIVE' : 'SYSTEM NOMINAL'}
            </motion.div>
        </div>
    );
};
