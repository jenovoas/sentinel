"use client";

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Ban, Activity, Skull, ShieldAlert, Crosshair, Zap, Eye } from 'lucide-react';

interface KillEvent {
    id: string;
    source: string;
    threat: string;
    timestamp: string;
    action: string;
}

interface KillBoardProps {
    kills: number; // Total kills
}

export const KillBoard: React.FC<KillBoardProps> = ({ kills }) => {
    const [events, setEvents] = useState<KillEvent[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Simulate incoming neural mitigations (Mock Data)
    useEffect(() => {
        const interval = setInterval(() => {
            const newEvent: KillEvent = {
                id: Math.random().toString(36).substr(2, 9),
                source: `IPV4: ${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
                threat: ['RING_0_WRITE', 'HEURISTIC_OVERFLOW', 'RCE_PATTERN', 'SYNC_FLOOD'][Math.floor(Math.random() * 4)],
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                action: 'NEUTRALIZED'
            };

            setEvents(prev => [newEvent, ...prev].slice(0, 15)); // Keep last 15
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col h-full bg-slate-950/40 backdrop-blur-2xl rounded-[30px] border border-white/5 overflow-hidden relative shadow-2xl group transition-all duration-500 hover:border-rose-500/20">
            {/* Header / Summary */}
            <div className="p-6 border-b border-white/5 bg-slate-900/40 relative z-10">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3 text-rose-500">
                        <Crosshair size={18} className="animate-pulse" />
                        <span className="font-black tracking-[0.2em] uppercase text-xs italic">Mitigation Matrix</span>
                    </div>
                </div>
                <div className="flex items-end justify-between">
                    <div>
                        <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest italic leading-none">Total Neural Blocked</p>
                        <h4 className="text-3xl font-black text-white italic tracking-tighter mt-1">{kills.toLocaleString()}</h4>
                    </div>
                    <div className="bg-rose-500/10 px-3 py-1 rounded-full border border-rose-500/20 flex items-center gap-2">
                        <div className="w-1 h-1 rounded-full bg-rose-500 animate-ping" />
                        <span className="text-[9px] font-black text-rose-400 uppercase tracking-widest leading-none">Live Interception</span>
                    </div>
                </div>
            </div>

            {/* Event Matrix List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar relative z-10" ref={scrollRef}>
                <AnimatePresence initial={false}>
                    {events.map((event, idx) => (
                        <motion.div
                            key={event.id}
                            initial={{ opacity: 0, x: 20, scale: 0.95 }}
                            animate={{ opacity: 1, x: 0, scale: 1 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ duration: 0.4 }}
                            className="bg-[#050814]/60 border border-white/5 rounded-2xl p-4 group/item hover:border-emerald-500/30 transition-all relative overflow-hidden"
                        >
                            <div className="absolute top-0 right-0 p-3 opacity-0 group-hover/item:opacity-20 transition-opacity">
                                <Zap size={14} className="text-emerald-400" />
                            </div>

                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-3">
                                    <span className="text-[9px] font-black text-gray-600 uppercase tracking-widest">{event.timestamp}</span>
                                    <span className="px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 text-[8px] font-black uppercase tracking-widest border border-rose-500/20">
                                        {event.threat}
                                    </span>
                                </div>
                                <span className="text-emerald-400 text-[8px] font-black uppercase tracking-widest flex items-center gap-2">
                                    <ShieldAlert size={10} /> {event.action}
                                </span>
                            </div>

                            <div className="flex items-center justify-between">
                                <span className="text-[10px] font-bold text-gray-400 flex items-center gap-2">
                                    <Eye size={10} className="text-gray-700" /> {event.source}
                                </span>
                                <div className="flex gap-1">
                                    <div className="w-1 h-1 rounded-full bg-emerald-500/50" />
                                    <div className="w-1 h-1 rounded-full bg-emerald-500/30" />
                                    <div className="w-1 h-1 rounded-full bg-emerald-500/10" />
                                </div>
                            </div>
                        </motion.div>
                    ))}
                    {events.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-center p-12 opacity-30">
                            <ShieldAlert size={48} className="text-gray-500 mb-4" />
                            <p className="text-[10px] font-black text-gray-600 uppercase tracking-widest italic">Awaiting threat ingestion...</p>
                        </div>
                    )}
                </AnimatePresence>
            </div>

            {/* Bottom Glow */}
            <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-slate-900 via-transparent to-transparent pointer-events-none opacity-80" />
        </div>
    );
};
