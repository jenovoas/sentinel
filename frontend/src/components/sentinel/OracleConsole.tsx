"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Loader2, Database, History, Sparkles, BrainCircuit, Activity, Zap, ShieldCheck } from "lucide-react";

interface Message {
    role: "user" | "oracle";
    content: string;
    timestamp: Date;
    verified?: boolean;
}

export const OracleConsole = () => {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "oracle",
            content: "Sentinel Oracle online. Neural pathways connected. Accessing ChromaDB memory index. How can I assist you with system insights today?",
            timestamp: new Date(),
        },
    ]);
    const [loading, setLoading] = useState(false);
    const [neuralDepth, setNeuralDepth] = useState(88.4);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, loading]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage: Message = {
            role: "user",
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setLoading(true);

        try {
            // Simulate TruthSync verification for the prompt
            const verRes = await fetch("/api/v1/truthsync/verify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: input })
            });
            const verData = await verRes.json();

            const res = await fetch("/api/v1/ai/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt: input,
                    max_tokens: 200,
                    temperature: 0.3
                }),
            });
            const data = await res.json();

            const oracleMessage: Message = {
                role: "oracle",
                content: data.response || "I couldn't retrieve that information from the memory index.",
                timestamp: new Date(),
                verified: verData.confidence > 0.8
            };
            setMessages(prev => [...prev, oracleMessage]);
            setNeuralDepth(prev => Math.min(99.9, prev + (Math.random() * 2)));
        } catch (error) {
            console.error("Oracle Query error:", error);
            setMessages(prev => [...prev, {
                role: "oracle",
                content: "Communication interruption. Neural link unstable.",
                timestamp: new Date(),
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-[#050814]/60 backdrop-blur-3xl border border-purple-500/20 rounded-[40px] shadow-[0_0_50px_rgba(168,85,247,0.1)] h-full flex flex-col overflow-hidden relative group">
            {/* Visual Identity Layer */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-30">
                <div className="absolute top-0 right-0 w-48 h-48 bg-purple-500/10 blur-[80px] rounded-full animate-pulse" />
                <div className="absolute bottom-0 left-0 w-48 h-48 bg-cyan-500/10 blur-[80px] rounded-full animate-pulse" />
            </div>

            {/* Oracle Header */}
            <div className="px-8 py-6 border-b border-white/5 flex items-center justify-between relative z-10 bg-slate-900/40">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20 border border-purple-500/30 flex items-center justify-center text-purple-400 shadow-[0_0_20px_rgba(168,85,247,0.2)]">
                        <BrainCircuit size={24} className="animate-pulse" />
                    </div>
                    <div>
                        <h2 className="text-sm font-black text-white uppercase tracking-[0.2em] italic">Sovereign Oracle</h2>
                        <div className="flex items-center gap-2 mt-0.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-[10px] font-black text-purple-400/70 uppercase tracking-widest italic leading-none">Inference Engine v2.1</span>
                        </div>
                    </div>
                </div>
                <div className="flex flex-col items-end">
                    <span className="text-[9px] font-black text-gray-600 uppercase tracking-widest leading-none mb-1">Neural Depth</span>
                    <span className="text-sm font-black text-white italic tracking-tighter leading-none">{neuralDepth.toFixed(1)}%</span>
                </div>
            </div>

            {/* Neural Chat Matrix */}
            <div className="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-hide relative z-10" ref={scrollRef}>
                <AnimatePresence mode="popLayout">
                    {messages.map((msg, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            transition={{ type: "spring", stiffness: 100 }}
                            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                            <div className={`relative max-w-[85%] p-5 rounded-[28px] border shadow-2xl transition-all hover:scale-[1.01] ${msg.role === "user"
                                ? "bg-gradient-to-br from-purple-600/20 to-blue-600/10 border-purple-500/30 text-white"
                                : "bg-black/40 border-white/5 text-purple-50"
                                }`}>

                                <div className="flex items-center gap-2 mb-3 opacity-40 text-[9px] font-black uppercase tracking-[0.2em] italic">
                                    {msg.role === "user" ? <User size={10} /> : <Bot size={10} />}
                                    <span>{msg.role === "user" ? "Authorized Commander" : "Oracle Insight"}</span>
                                    {msg.verified && <span className="ml-auto text-emerald-400 flex items-center gap-1"><ShieldCheck size={10} /> TRUTHSYNC_OK</span>}
                                </div>

                                <p className="text-[13px] font-bold leading-relaxed tracking-tight italic">
                                    {msg.content}
                                </p>

                                <div className={`absolute top-4 ${msg.role === 'user' ? '-right-1' : '-left-1'} w-[4px] h-[30%] bg-purple-500 rounded-full opacity-50 shadow-[0_0_10px_rgba(168,85,247,0.5)]`} />
                            </div>
                        </motion.div>
                    ))}
                    {loading && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex justify-start"
                        >
                            <div className="bg-white/5 border border-white/5 p-4 rounded-[24px] flex items-center gap-4">
                                <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                                <div className="flex flex-col">
                                    <span className="text-[10px] text-purple-300 font-black uppercase tracking-[0.2em] italic">Synthesizing Insight...</span>
                                    <div className="w-32 h-1 bg-white/5 rounded-full mt-2 overflow-hidden">
                                        <motion.div
                                            animate={{ x: ['-100%', '100%'] }}
                                            transition={{ duration: 1, repeat: Infinity }}
                                            className="w-1/2 h-full bg-purple-500"
                                        />
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Neural Input Uplink */}
            <div className="p-8 bg-slate-900/40 border-t border-white/5 backdrop-blur-xl relative z-10">
                <div className={`relative flex items-center bg-black/60 rounded-[22px] px-6 py-2 border transition-all duration-500 shadow-inner group-focus-within:border-purple-500/50 ${loading ? 'border-purple-500/20' : 'border-white/5'
                    }`}>
                    <div className="flex items-center gap-4 text-purple-500 opacity-40 group-focus-within:opacity-100 transition-opacity">
                        <Database size={16} />
                        <span className="text-xs font-black italic">{'>'}</span>
                    </div>

                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSend()}
                        disabled={loading}
                        className="flex-1 bg-transparent border-none outline-none text-white py-4 px-4 placeholder:text-slate-800 font-bold tracking-tight text-sm disabled:opacity-50 selection:bg-purple-500/30"
                        placeholder={loading ? "Inference protocol active..." : "Query the Oracle Memory..."}
                    />

                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                        className={`p-2.5 rounded-xl transition-all shadow-lg active:scale-95 ${!input.trim() || loading
                                ? 'opacity-20 cursor-not-allowed bg-white/5'
                                : 'bg-gradient-to-br from-purple-600 to-purple-800 text-white hover:shadow-[0_0_20px_rgba(168,85,247,0.4)] hover:scale-105 border border-purple-400/30'
                            }`}
                    >
                        {loading ? <Loader2 size={18} className="animate-spin" /> : <Zap size={18} />}
                    </button>
                </div>

                <div className="mt-4 flex items-center justify-between px-2">
                    <div className="flex gap-6">
                        <button className="text-[10px] font-black text-gray-700 hover:text-purple-400 transition-colors flex items-center gap-2 uppercase tracking-widest italic group">
                            <History size={12} className="group-hover:rotate-[-45deg] transition-transform" />
                            <span>Flush Index</span>
                        </button>
                        <div className="h-4 w-[1px] bg-white/5" />
                        <p className="text-[10px] font-black text-gray-700 uppercase tracking-widest italic">
                            Memory: <span className="text-purple-900">CHROMA_VECTORS</span>
                        </p>
                    </div>
                    <span className="text-[10px] font-black text-gray-800 tracking-[0.4em] uppercase">Oracle Uplink v2.4</span>
                </div>
            </div>
        </div>
    );
};
