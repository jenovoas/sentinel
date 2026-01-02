"use client";

import { useState, useEffect } from "react";
import { Search, Globe, ShieldCheck, Zap, Loader2, Sparkles, BrainCircuit, ShieldAlert } from "lucide-react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

export function SovereignSearchInput({ className = "" }: { className?: string }) {
    const [query, setQuery] = useState("");
    const [isFocused, setIsFocused] = useState(false);
    const [isVerifying, setIsVerifying] = useState(false);
    const [verificationStatus, setVerificationStatus] = useState<'idle' | 'verifying' | 'verified' | 'failed'>('idle');
    const router = useRouter();

    const handleSearch = async () => {
        if (!query.trim() || isVerifying) return;

        setIsVerifying(true);
        setVerificationStatus('verifying');

        try {
            // 🌐 TruthSync Verification Protocol
            const response = await fetch("/api/v1/truthsync/verify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: query,
                    metadata: { source: "sovereign_terminal", layer: "neural_ingress" }
                }),
            });

            const result = await response.json();

            // Artificial delay for "Cognitive Processing" feel
            await new Promise(resolve => setTimeout(resolve, 800));

            if (result.confidence > 0.7) {
                setVerificationStatus('verified');
                const searchEngineUrl = `http://localhost:8080/search?q=${encodeURIComponent(query)}`;
                // Add a small delay to show the "Verified" state before navigation
                setTimeout(() => {
                    router.push(`/dashboard?url=${encodeURIComponent(searchEngineUrl)}&mode=velocity&verified=true#secure-workspace`);
                }, 400);
            } else {
                setVerificationStatus('failed');
                // Even if verification is low, we might still allow it but with a warning, 
                // or just proceed to the dashboard where the browser will handle it.
                // For now, let's navigate but pass the low confidence.
                const searchEngineUrl = `http://localhost:8080/search?q=${encodeURIComponent(query)}`;
                setTimeout(() => {
                    router.push(`/dashboard?url=${encodeURIComponent(searchEngineUrl)}&mode=secure&risk=high#secure-workspace`);
                }, 1000);
            }
        } catch (error) {
            console.error("TruthSync Verification Error:", error);
            setVerificationStatus('failed');
            // Fallback navigation
            router.push(`/dashboard?q=${encodeURIComponent(query)}&mode=failsafe#secure-workspace`);
        } finally {
            setIsVerifying(false);
        }
    };

    return (
        <div className={`relative group ${className}`}>
            {/* Neural Background Aura */}
            <div
                className={`absolute -inset-1 bg-gradient-to-r from-cyan-500/30 via-purple-500/30 to-blue-500/30 rounded-[28px] opacity-75 blur-2xl transition-all duration-1000 group-hover:opacity-100 group-hover:blur-3xl ${isFocused || isVerifying ? 'opacity-100 blur-3xl scale-[1.05]' : 'opacity-20'}`}
            ></div>

            <div className="relative flex flex-col gap-2">
                <div className={`relative flex items-center bg-slate-950/80 backdrop-blur-3xl rounded-[24px] p-2 border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)] transition-all duration-500 ${isFocused ? 'border-cyan-500/50 ring-1 ring-cyan-500/20' : 'group-hover:border-white/20'}`}>

                    {/* Visual Pulse for Verification */}
                    <AnimatePresence>
                        {isVerifying && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="absolute inset-0 rounded-[24px] overflow-hidden pointer-events-none"
                            >
                                <motion.div
                                    animate={{ x: ['-100%', '100%'] }}
                                    transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                                    className="h-full w-1/3 bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent skew-x-12"
                                />
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <div className="p-3 border-r border-white/5 text-cyan-400 group-hover:scale-110 transition-transform flex items-center justify-center min-w-[56px]">
                        {isVerifying ? (
                            <Loader2 size={20} className="animate-spin text-purple-400" />
                        ) : verificationStatus === 'verified' ? (
                            <ShieldCheck size={20} className="text-emerald-400" />
                        ) : verificationStatus === 'failed' ? (
                            <ShieldAlert size={20} className="text-rose-400" />
                        ) : (
                            <Globe size={20} className="group-hover:rotate-12 transition-transform" />
                        )}
                    </div>

                    <input
                        type="text"
                        disabled={isVerifying}
                        className="flex-1 bg-transparent border-none outline-none text-white px-5 py-4 placeholder:text-slate-700 font-bold tracking-tight text-xl selection:bg-cyan-500/30 disabled:opacity-50"
                        placeholder={isVerifying ? "Verifying Claim via TruthSync..." : "Query the Sovereign Matrix..."}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    />

                    <button
                        onClick={handleSearch}
                        disabled={isVerifying}
                        className={`px-8 py-3 rounded-2xl transition-all flex items-center gap-3 font-black uppercase tracking-[0.2em] text-xs border active:scale-95 disabled:opacity-50 ${isVerifying
                                ? 'bg-purple-500/10 border-purple-500/20 text-purple-400'
                                : 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 hover:shadow-[0_0_30px_rgba(34,211,238,0.2)]'
                            }`}
                    >
                        {isVerifying ? (
                            <>
                                <BrainCircuit size={16} className="animate-pulse" />
                                ANALYZING
                            </>
                        ) : (
                            <>
                                <Zap size={16} className="text-amber-400" />
                                EXECUTE
                            </>
                        )}
                    </button>
                </div>

                {/* Status Indicator Bar */}
                <div className="flex items-center justify-between px-4">
                    <div className="flex items-center gap-6 text-[9px] font-black uppercase tracking-[0.3em] text-gray-600 italic">
                        <div className={`flex items-center gap-2 transition-colors ${verificationStatus === 'verified' ? 'text-emerald-500' : 'hover:text-cyan-400'}`}>
                            <ShieldCheck size={12} className={verificationStatus === 'verified' ? 'text-emerald-500' : 'text-gray-700'} />
                            <span>Neural Ingress: {verificationStatus === 'verified' ? 'TRUSTED' : 'ENCRYPTED'}</span>
                        </div>
                        <div className={`flex items-center gap-2 transition-colors ${isVerifying ? 'text-purple-400 animate-pulse' : 'hover:text-cyan-400'}`}>
                            <BrainCircuit size={12} className={isVerifying ? 'text-purple-400' : 'text-gray-700'} />
                            <span>TruthSync {isVerifying ? 'Active' : 'Standby'}</span>
                        </div>
                        <div className="flex items-center gap-2 hover:text-cyan-400 transition-colors">
                            <Sparkles size={12} className="text-amber-500/50" />
                            <span>Sovereign Link v2.1</span>
                        </div>
                    </div>

                    <div className="text-[9px] font-black text-gray-700 tracking-widest uppercase">
                        Latency: <span className="text-cyan-900">12ms</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
