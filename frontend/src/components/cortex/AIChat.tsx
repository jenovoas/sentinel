"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal, Cpu, Sparkles, BrainCircuit, Activity, Zap, ShieldCheck, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Interface representing a single chat message.
 */
interface Message {
    role: 'user' | 'ai';
    text: string;
    /** Optional evidence block (logs, metrics) to be displayed below the message */
    evidence?: string;
    timestamp: Date;
}

/**
 * Main AI Chat Interface Component (Sovereign Neural Uplink v2.1).
 * 
 * Displays a futuristic neural interface for interacting with the Cortex AI.
 * Features advanced animations, glassmorphism, and deep API integration.
 */
export const AIChat: React.FC = () => {
    const [input, setInput] = useState<string>('');
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'ai',
            text: 'Neural Link established. Sovereign Matrix v2.1 operational. Awaiting commander directives.',
            timestamp: new Date()
        }
    ]);
    const [isThinking, setIsThinking] = useState(false);
    const [neuralLatency, setNeuralLatency] = useState<number>(0);

    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isThinking]);

    /**
     * Handles sending a message and triggering the REAL AI response from Ollama.
     */
    const handleSend = async () => {
        if (!input.trim() || isThinking) return;

        const userMessage = input;
        const startTime = Date.now();
        setInput('');

        // Add user message
        setMessages(prev => [...prev, { role: 'user', text: userMessage, timestamp: new Date() }]);
        setIsThinking(true);

        try {
            const res = await fetch("/api/v1/ai/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt: userMessage,
                    max_tokens: 150,
                    temperature: 0.4
                })
            });

            const data = await res.json();
            const latency = Date.now() - startTime;
            setNeuralLatency(latency);

            if (res.ok) {
                setMessages(prev => [...prev, {
                    role: 'ai',
                    text: data.response || "No response data received.",
                    evidence: `[NEURAL_MODEL] ${data.model} | [STABILITY] 1.0 | [LATENCY] ${latency}ms`,
                    timestamp: new Date()
                }]);
            } else {
                setMessages(prev => [...prev, {
                    role: 'ai',
                    text: `SYSTEM ERROR: ${data.detail?.error || data.detail || 'Neural Link Error'}`,
                    evidence: `[ERROR] ${JSON.stringify(data.detail) || 'Connection failed'}`,
                    timestamp: new Date()
                }]);
            }

        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'ai',
                text: "CRITICAL FAILURE: Neural Link Severed.",
                evidence: `[EXCEPTION] ${String(error)}`,
                timestamp: new Date()
            }]);
        } finally {
            setIsThinking(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-[#0a0f1e]/60 backdrop-blur-2xl rounded-[30px] border border-white/10 overflow-hidden relative shadow-2xl group transition-all duration-500 hover:border-cyan-500/30">
            {/* Neural Background - Subtle Pulse */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-20">
                <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 blur-[100px] rounded-full animate-pulse" />
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 blur-[100px] rounded-full animate-pulse" />
            </div>

            {/* Header / Uplink Status */}
            <div className="bg-slate-900/40 border-b border-white/5 px-6 py-4 flex items-center justify-between relative z-10 backdrop-blur-md">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-xl border border-white/10 text-cyan-400">
                        <BrainCircuit size={18} className="animate-pulse" />
                    </div>
                    <div>
                        <h3 className="text-xs font-black text-white uppercase tracking-[0.2em] italic">Neural Uplink</h3>
                        <p className="text-[8px] font-black text-emerald-500 uppercase tracking-widest">Active Link // Secure</p>
                    </div>
                </div>

                <div className="flex items-center gap-6">
                    <div className="hidden md:flex flex-col items-end">
                        <span className="text-[8px] font-black text-gray-500 uppercase tracking-widest">Neural Latency</span>
                        <span className="text-[10px] font-bold text-cyan-400 italic">{neuralLatency > 0 ? `${neuralLatency}ms` : 'SYNCING...'}</span>
                    </div>
                    <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)] animate-pulse" />
                </div>
            </div>

            {/* Messages Matrix */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/5 scrollbar-track-transparent relative z-10" ref={scrollRef}>
                <AnimatePresence>
                    {messages.map((msg, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ type: "spring", stiffness: 100 }}
                            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                        >
                            <div className={`group relative max-w-[85%] rounded-[24px] p-5 shadow-xl transition-all ${msg.role === 'user'
                                    ? 'bg-gradient-to-br from-cyan-600/20 to-blue-600/10 border border-cyan-500/20 text-blue-50'
                                    : 'bg-slate-900/60 border border-white/5 text-emerald-50 backdrop-blur-md'
                                }`}>

                                <div className="flex items-center gap-2 mb-2 opacity-40 text-[9px] font-black uppercase tracking-widest italic">
                                    {msg.role === 'ai' ? <Cpu size={10} className="text-emerald-400" /> : <ShieldCheck size={10} className="text-cyan-400" />}
                                    <span>{msg.role === 'ai' ? 'CORTEX CORE' : 'COMMANDER'}</span>
                                    <span className="ml-auto opacity-30">{msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                </div>

                                <div className="text-sm font-bold leading-relaxed tracking-tight">
                                    {msg.text}
                                </div>

                                {msg.role === 'ai' && (
                                    <div className="absolute -left-2 top-4 w-[2px] h-[40%] bg-emerald-500 rounded-full opacity-50" />
                                )}
                            </div>

                            {msg.evidence && (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="mt-2 text-[9px] font-mono text-cyan-400/60 bg-black/40 px-3 py-2 rounded-xl border border-white/5 flex items-center gap-2 italic uppercase tracking-widest mx-2"
                                >
                                    <Activity size={10} className="text-cyan-500/40" />
                                    {msg.evidence}
                                </motion.div>
                            )}
                        </motion.div>
                    ))}

                    {isThinking && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex flex-col items-start"
                        >
                            <div className="bg-slate-900/40 border border-white/5 rounded-[20px] p-4 backdrop-blur-md">
                                <div className="flex items-center gap-3">
                                    <Loader2 size={16} className="animate-spin text-purple-400" />
                                    <span className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] italic">AI Cognitive Synthesis...</span>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Command Input Area */}
            <div className="p-6 bg-slate-950/40 border-t border-white/5 backdrop-blur-xl relative z-10">
                <div className={`flex items-center gap-4 bg-[#050814] rounded-[22px] px-5 py-2 border transition-all duration-300 ${isThinking ? 'border-purple-500/20' : 'border-white/5 focus-within:border-cyan-500/50 shadow-[0_0_20px_rgba(0,0,0,0.5)]'
                    }`}>
                    <div className="flex items-center gap-3 text-cyan-500">
                        <Terminal size={14} className={isThinking ? 'opacity-20' : 'animate-pulse'} />
                        <span className="text-xs font-black opacity-30 italic">{'>'}</span>
                    </div>

                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        disabled={isThinking}
                        className="flex-1 bg-transparent border-none outline-none text-white py-3 placeholder:text-slate-700 font-bold tracking-tight text-sm disabled:opacity-50"
                        placeholder={isThinking ? "Awaiting neural synthesis..." : "Enter neural command..."}
                    />

                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleSend}
                            disabled={isThinking || !input.trim()}
                            className={`p-2 rounded-xl transition-all ${isThinking || !input.trim()
                                    ? 'opacity-20 cursor-not-allowed'
                                    : 'bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 hover:scale-110 border border-cyan-500/20'
                                }`}
                        >
                            <Zap size={18} />
                        </button>
                    </div>
                </div>

                <div className="mt-4 flex items-center justify-between px-2">
                    <div className="flex gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-1 h-1 rounded-full bg-cyan-500" />
                            <span className="text-[8px] font-black text-gray-600 uppercase tracking-widest">TLS 1.3 Encryption</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-1 h-1 rounded-full bg-purple-500" />
                            <span className="text-[8px] font-black text-gray-600 uppercase tracking-widest">Ollama Cluster Native</span>
                        </div>
                    </div>
                    <span className="text-[8px] font-black text-gray-800 uppercase tracking-[0.3em]">Neural Interface v2.1.0-STABLE</span>
                </div>
            </div>
        </div>
    );
};
