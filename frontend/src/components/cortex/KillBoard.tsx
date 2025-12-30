"use client";

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Ban, Activity, Skull } from 'lucide-react';

interface KillEvent {
    id: string;
    ip: string;
    threat: string;
    timestamp: string;
}

interface KillBoardProps {
    kills: number; // Total kills
}

export const KillBoard: React.FC<KillBoardProps> = ({ kills }) => {
    const [events, setEvents] = useState<KillEvent[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Simulate incoming events for the demo (Mock Data)
    useEffect(() => {
        const interval = setInterval(() => {
            const newEvent: KillEvent = {
                id: Math.random().toString(36).substr(2, 9),
                ip: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
                threat: ['XDP_DROP', 'SQL_INJECTION', 'RCE_ATTEMPT', 'BAD_REP'][Math.floor(Math.random() * 4)],
                timestamp: new Date().toLocaleTimeString(),
            };

            setEvents(prev => [newEvent, ...prev].slice(0, 10)); // Keep last 10
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col h-full bg-slate-900/50 backdrop-blur-sm rounded-xl border border-red-900/30 overflow-hidden relative">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-red-500 to-transparent opacity-50" />

            {/* Header */}
            <div className="p-4 border-b border-white/5 flex justify-between items-center bg-black/20">
                <div className="flex items-center space-x-2 text-red-500">
                    <Skull className="w-5 h-5" />
                    <span className="font-bold tracking-widest uppercase text-sm">Kill Board</span>
                </div>
                <div className="flex items-center space-x-2">
                    <span className="text-xs text-red-400/70 uppercase">Total Neutralized</span>
                    <span className="text-xl font-mono font-bold text-red-500 bg-red-500/10 px-2 rounded">
                        {kills.toLocaleString()}
                    </span>
                </div>
            </div>

            {/* Event List */}
            <div className="flex-1 overflow-hidden p-2 space-y-2 font-mono text-xs relative" ref={scrollRef}>
                <AnimatePresence initial={false}>
                    {events.map((event) => (
                        <motion.div
                            key={event.id}
                            initial={{ opacity: 0, x: 20, height: 0 }}
                            animate={{ opacity: 1, x: 0, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3 }}
                            className="flex items-center justify-between p-2 bg-red-950/20 border-l-2 border-red-600/50 rounded-r"
                        >
                            <span className="text-slate-400">{event.timestamp}</span>
                            <span className="text-red-200 font-bold">{event.threat}</span>
                            <span className="text-slate-500">{event.ip}</span>
                            <Ban className="w-3 h-3 text-red-500" />
                        </motion.div>
                    ))}
                </AnimatePresence>

                {/* Gradient Mask at bottom */}
                <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-slate-900/50 to-transparent pointer-events-none" />
            </div>
        </div>
    );
};
