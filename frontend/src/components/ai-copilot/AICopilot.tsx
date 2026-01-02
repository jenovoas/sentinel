"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence, useDragControls } from "framer-motion";
import { usePathname } from "next/navigation";
import {
    Brain, X, Maximize2, Minimize2, GripVertical,
    Shield, Sparkles, AlertTriangle, CheckCircle, XCircle,
    Zap, TrendingUp, MessageSquare, Activity, Eye, Cpu, Heart
} from "lucide-react";

type ViewMode = "minimized" | "panel" | "canvas";

interface AIRecommendation {
    id: string;
    type: "info" | "warning" | "action" | "insight";
    title: string;
    description: string;
    action?: { label: string; href?: string; onClick?: () => void };
    trustScore: number;
}

interface TrustMetrics {
    overall: number;
    dataSupport: number;
    base60Valid: boolean;
    hallucinationRate: number;
}

export function AICopilot() {
    const pathname = usePathname();
    const [viewMode, setViewMode] = useState<ViewMode>("panel");
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [trustMetrics, setTrustMetrics] = useState<TrustMetrics>({
        overall: 0,
        dataSupport: 0,
        base60Valid: false,
        hallucinationRate: 0,
    });
    const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
    const [userMessage, setUserMessage] = useState("");
    const [chatHistory, setChatHistory] = useState<Array<{ role: "user" | "ai"; content: string }>>([]);

    const dragControls = useDragControls();
    const constraintsRef = useRef(null);

    // Fetch trust metrics
    useEffect(() => {
        const fetchTrustMetrics = async () => {
            try {
                const response = await fetch("/api/v1/truthsync/stats");
                const data = await response.json();

                setTrustMetrics({
                    overall: calculateOverallScore(data),
                    dataSupport: data.data_support || 0,
                    base60Valid: data.base60_valid || false,
                    hallucinationRate: data.hallucination_rate || 0,
                });
            } catch (err) {
                console.error("Failed to fetch trust metrics:", err);
            }
        };

        fetchTrustMetrics();
        const interval = setInterval(fetchTrustMetrics, 10000);
        return () => clearInterval(interval);
    }, []);

    // Generate contextual recommendations
    useEffect(() => {
        const newRecommendations = generateRecommendations(pathname, trustMetrics);
        setRecommendations(newRecommendations);
    }, [pathname, trustMetrics]);

    const handleSendMessage = async () => {
        if (!userMessage.trim()) return;
        setChatHistory(prev => [...prev, { role: "user", content: userMessage }]);
        const aiResponse = await getAIResponse(userMessage, pathname, trustMetrics);
        setChatHistory(prev => [...prev, { role: "ai", content: aiResponse }]);
        setUserMessage("");
    };

    const trustStatus = getTrustStatus(trustMetrics.overall);

    // Minimized mode - floating button
    if (viewMode === "minimized") {
        return (
            <motion.button
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                onClick={() => setViewMode("panel")}
                className="fixed bottom-6 right-6 z-50 p-4 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 shadow-[0_0_40px_rgba(168,85,247,0.6)] hover:shadow-[0_0_60px_rgba(168,85,247,0.8)] transition-all"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
            >
                <Brain size={28} className="text-white" />
                {trustMetrics.overall < 90 && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 rounded-full animate-pulse" />
                )}
            </motion.button>
        );
    }

    // Canvas mode - large draggable floating panel
    if (viewMode === "canvas") {
        return (
            <div ref={constraintsRef} className="fixed inset-0 pointer-events-none z-50">
                <motion.div
                    drag
                    dragControls={dragControls}
                    dragConstraints={constraintsRef}
                    dragElastic={0.1}
                    dragMomentum={false}
                    initial={{
                        x: (window.innerWidth - 1200) / 2,
                        y: (window.innerHeight - 800) / 2
                    }}
                    className="absolute w-[1200px] h-[800px] flex flex-col bg-slate-900/98 backdrop-blur-3xl border-2 border-purple-500/30 rounded-3xl shadow-[0_0_80px_rgba(168,85,247,0.4)] overflow-hidden pointer-events-auto"
                >
                    {/* Draggable header */}
                    <div
                        onPointerDown={(e) => dragControls.start(e)}
                        className="p-4 border-b border-white/10 bg-gradient-to-r from-purple-500/10 to-cyan-500/10 cursor-move"
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <GripVertical size={20} className="text-gray-500" />
                                <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20 border border-purple-500/30">
                                    <Brain size={24} className="text-purple-400" />
                                </div>
                                <div>
                                    <h1 className="text-2xl font-black text-white uppercase tracking-tighter italic">
                                        Sentinel IA
                                    </h1>
                                    <p className="text-[10px] text-gray-500 uppercase tracking-wider">
                                        Asistente Cognitivo • Modo Canvas
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setViewMode("panel")}
                                    className="p-2 rounded-lg hover:bg-white/5 transition-colors"
                                >
                                    <Minimize2 size={18} className="text-gray-400" />
                                </button>
                                <button
                                    onClick={() => setViewMode("minimized")}
                                    className="p-2 rounded-lg hover:bg-white/5 transition-colors"
                                >
                                    <X size={18} className="text-gray-400" />
                                </button>
                            </div>
                        </div>

                        {/* Trust indicator */}
                        <div className={`flex items-center gap-4 p-4 rounded-xl border-2 ${trustStatus.borderClass} ${trustStatus.bgClass} mt-3`}>
                            {trustStatus.icon}
                            <div className="flex-1">
                                <div className={`text-base font-black uppercase ${trustStatus.textClass}`}>
                                    {trustStatus.label}
                                </div>
                                <div className="text-[10px] text-gray-500 uppercase tracking-wider">
                                    Trust: {Math.round(trustMetrics.overall)}% • Data: {Math.round(trustMetrics.dataSupport)}%
                                </div>
                            </div>
                            <div className={`text-4xl font-black font-mono ${trustStatus.textClass}`}>
                                {Math.round(trustMetrics.overall)}
                            </div>
                        </div>
                    </div>

                    {/* Canvas content */}
                    <div className="flex-1 grid grid-cols-3 gap-4 p-4 overflow-hidden">
                        {/* Left: Recommendations */}
                        <div className="space-y-3 overflow-y-auto custom-scrollbar">
                            <h2 className="text-base font-black text-white uppercase tracking-tight flex items-center gap-2 sticky top-0 bg-slate-900/95 pb-2">
                                <Sparkles size={18} className="text-cyan-400" />
                                Recommendations
                            </h2>
                            {recommendations.map((rec) => (
                                <RecommendationCard key={rec.id} recommendation={rec} />
                            ))}
                        </div>

                        {/* Center: Chat */}
                        <div className="flex flex-col bg-slate-900/60 backdrop-blur-xl border border-white/10 rounded-2xl p-4">
                            <h2 className="text-base font-black text-white uppercase tracking-tight mb-3 flex items-center gap-2">
                                <MessageSquare size={18} className="text-purple-400" />
                                Conversation
                            </h2>
                            <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 mb-3">
                                {chatHistory.length === 0 ? (
                                    <div className="flex items-center justify-center h-full text-gray-500 text-sm">
                                        Ask me anything about Sentinel...
                                    </div>
                                ) : (
                                    chatHistory.map((msg, idx) => (
                                        <div
                                            key={idx}
                                            className={`p-3 rounded-xl text-sm ${msg.role === "user"
                                                ? "bg-purple-500/10 border border-purple-500/30 ml-6"
                                                : "bg-cyan-500/10 border border-cyan-500/30 mr-6"
                                                }`}
                                        >
                                            <div className={`text-[10px] font-black uppercase mb-1 ${msg.role === "user" ? "text-purple-400" : "text-cyan-400"
                                                }`}>
                                                {msg.role === "user" ? "You" : "Sentinel AI"}
                                            </div>
                                            <div className="text-gray-300 leading-relaxed">{msg.content}</div>
                                        </div>
                                    ))
                                )}
                            </div>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={userMessage}
                                    onChange={(e) => setUserMessage(e.target.value)}
                                    onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                                    placeholder="Ask Sentinel AI..."
                                    className="flex-1 px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50"
                                />
                                <button
                                    onClick={handleSendMessage}
                                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-cyan-500 hover:shadow-[0_0_20px_rgba(168,85,247,0.6)] transition-all"
                                >
                                    <Zap size={18} className="text-white" />
                                </button>
                            </div>
                        </div>

                        {/* Right: System Status */}
                        <div className="space-y-3 overflow-y-auto custom-scrollbar">
                            <h2 className="text-base font-black text-white uppercase tracking-tight flex items-center gap-2 sticky top-0 bg-slate-900/95 pb-2">
                                <Activity size={18} className="text-emerald-400" />
                                System Status
                            </h2>
                            <SystemStatusCard icon={<Shield size={18} />} title="Guardian Alpha" status="active" value="98.3%" color="cyan" />
                            <SystemStatusCard icon={<Eye size={18} />} title="Guardian Beta" status="standby" value="97.1%" color="purple" />
                            <SystemStatusCard icon={<Heart size={18} />} title="TruthSync" status="healthy" value="1.69μs" color="emerald" />
                            <SystemStatusCard icon={<Cpu size={18} />} title="LSM Hook (ID 199)" status="active" value="280ns" color="rose" />
                        </div>
                    </div>
                </motion.div>
            </div>
        );
    }

    // Panel mode - draggable floating panel
    return (
        <div ref={constraintsRef} className="fixed inset-0 pointer-events-none z-50">
            <motion.div
                drag
                dragControls={dragControls}
                dragConstraints={constraintsRef}
                dragElastic={0.1}
                dragMomentum={false}
                initial={{ x: window.innerWidth - 450, y: 100 }}
                className="absolute w-[420px] max-h-[80vh] flex flex-col bg-slate-900/95 backdrop-blur-2xl border border-purple-500/30 rounded-3xl shadow-[0_0_60px_rgba(168,85,247,0.3)] overflow-hidden pointer-events-auto"
            >
                {/* Draggable header */}
                <div
                    onPointerDown={(e) => dragControls.start(e)}
                    className="p-4 border-b border-white/10 bg-gradient-to-r from-purple-500/10 to-cyan-500/10 cursor-move"
                >
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                            <GripVertical size={20} className="text-gray-500" />
                            <div className="p-2 rounded-xl bg-purple-500/20 border border-purple-500/30">
                                <Brain size={20} className="text-purple-400" />
                            </div>
                            <div>
                                <h3 className="text-sm font-black text-white uppercase tracking-tight">
                                    Sentinel AI
                                </h3>
                                <p className="text-[9px] text-gray-500 uppercase tracking-wider">
                                    Asistente Cognitivo
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setViewMode("canvas")}
                                className="p-2 rounded-lg hover:bg-white/5 transition-colors"
                            >
                                <Maximize2 size={16} className="text-gray-400" />
                            </button>
                            <button
                                onClick={() => setViewMode("minimized")}
                                className="p-2 rounded-lg hover:bg-white/5 transition-colors"
                            >
                                <X size={16} className="text-gray-400" />
                            </button>
                        </div>
                    </div>

                    {/* Trust indicator */}
                    <div className={`flex items-center gap-3 p-3 rounded-xl border-2 ${trustStatus.borderClass} ${trustStatus.bgClass}`}>
                        {trustStatus.icon}
                        <div className="flex-1 min-w-0">
                            <div className={`text-xs font-black uppercase ${trustStatus.textClass}`}>
                                {trustStatus.label}
                            </div>
                            <div className="text-[9px] text-gray-500 uppercase tracking-wider truncate">
                                Score: {Math.round(trustMetrics.overall)}%
                            </div>
                        </div>
                        <div className={`text-2xl font-black font-mono ${trustStatus.textClass}`}>
                            {Math.round(trustMetrics.overall)}
                        </div>
                    </div>
                </div>

                {/* Recommendations */}
                <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3">
                    <div className="flex items-center gap-2 mb-3">
                        <Sparkles size={14} className="text-cyan-400" />
                        <h4 className="text-xs font-black text-white uppercase tracking-wider">
                            Recommendations
                        </h4>
                    </div>
                    {recommendations.map((rec) => (
                        <RecommendationCard key={rec.id} recommendation={rec} />
                    ))}
                </div>

                {/* Chat input */}
                <div className="p-4 border-t border-white/10 bg-black/40">
                    <div className="flex items-center gap-2">
                        <input
                            type="text"
                            value={userMessage}
                            onChange={(e) => setUserMessage(e.target.value)}
                            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                            placeholder="Ask AI..."
                            className="flex-1 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50"
                        />
                        <button
                            onClick={handleSendMessage}
                            className="p-2 rounded-xl bg-gradient-to-r from-purple-500 to-cyan-500 hover:shadow-[0_0_20px_rgba(168,85,247,0.6)] transition-all"
                        >
                            <Zap size={18} className="text-white" />
                        </button>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}

// Helper Components

function RecommendationCard({ recommendation }: { recommendation: AIRecommendation }) {
    const typeConfig = {
        info: { icon: <Sparkles size={16} />, bgClass: "bg-cyan-500/10", borderClass: "border-cyan-500/30", textClass: "text-cyan-400" },
        warning: { icon: <AlertTriangle size={16} />, bgClass: "bg-amber-500/10", borderClass: "border-amber-500/30", textClass: "text-amber-400" },
        action: { icon: <Zap size={16} />, bgClass: "bg-purple-500/10", borderClass: "border-purple-500/30", textClass: "text-purple-400" },
        insight: { icon: <TrendingUp size={16} />, bgClass: "bg-emerald-500/10", borderClass: "border-emerald-500/30", textClass: "text-emerald-400" },
    };

    const config = typeConfig[recommendation.type];

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-3 rounded-xl border ${config.borderClass} ${config.bgClass}`}
        >
            <div className="flex items-start gap-3">
                <div className={config.textClass}>{config.icon}</div>
                <div className="flex-1 min-w-0">
                    <div className={`text-xs font-black uppercase ${config.textClass} mb-1`}>
                        {recommendation.title}
                    </div>
                    <p className="text-[10px] text-gray-400 leading-relaxed mb-2">
                        {recommendation.description}
                    </p>
                    {recommendation.action && (
                        <a
                            href={recommendation.action.href}
                            className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg text-[10px] font-black uppercase ${config.textClass} ${config.bgClass} border ${config.borderClass} hover:brightness-125 transition-all`}
                        >
                            {recommendation.action.label}
                            <Zap size={10} />
                        </a>
                    )}
                </div>
            </div>
        </motion.div>
    );
}

function SystemStatusCard({ icon, title, status, value, color }: any) {
    return (
        <div className={`p-4 rounded-2xl border border-${color}-500/20 bg-${color}-500/5`}>
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <div className={`text-${color}-400`}>{icon}</div>
                    <span className="text-xs font-black text-white uppercase">{title}</span>
                </div>
                <CheckCircle size={14} className={`text-${color}-400`} />
            </div>
            <div className={`text-lg font-black font-mono text-${color}-400`}>{value}</div>
            <div className="text-[9px] text-gray-500 uppercase">{status}</div>
        </div>
    );
}

// Helper Functions

function getTrustStatus(score: number) {
    if (score >= 95) {
        return { label: "CERTIFIED", textClass: "text-emerald-400", bgClass: "bg-emerald-500/10", borderClass: "border-emerald-500/30", icon: <CheckCircle size={20} className="text-emerald-400" /> };
    } else if (score >= 90) {
        return { label: "TRUSTED", textClass: "text-cyan-400", bgClass: "bg-cyan-500/10", borderClass: "border-cyan-500/30", icon: <Shield size={20} className="text-cyan-400" /> };
    } else if (score >= 70) {
        return { label: "CAUTION", textClass: "text-amber-400", bgClass: "bg-amber-500/10", borderClass: "border-amber-500/30", icon: <AlertTriangle size={20} className="text-amber-400" /> };
    } else {
        return { label: "UNTRUSTED", textClass: "text-rose-400", bgClass: "bg-rose-500/10", borderClass: "border-rose-500/30", icon: <XCircle size={20} className="text-rose-400" /> };
    }
}

function calculateOverallScore(data: any): number {
    const weights = { dataSupport: 0.4, base60: 0.3, hallucination: 0.3 };
    let score = 0;
    score += (data.data_support || 0) * weights.dataSupport;
    score += (data.base60_valid ? 100 : 0) * weights.base60;
    score += (100 - (data.hallucination_rate || 0) * 100) * weights.hallucination;
    return Math.min(100, Math.max(0, score));
}

function generateRecommendations(pathname: string, trustMetrics: TrustMetrics): AIRecommendation[] {
    const recommendations: AIRecommendation[] = [];

    if (pathname === "/") {
        recommendations.push({
            id: "home-1",
            type: "info",
            title: "System Operational",
            description: "All Guardian systems active. Trust score is optimal.",
            trustScore: trustMetrics.overall,
        });
    }

    if (pathname === "/cognitive") {
        recommendations.push({
            id: "cog-1",
            type: "insight",
            title: "Merkabah Active",
            description: "Cognitive interface showing optimal resonance patterns.",
            trustScore: 96,
        });
    }

    if (trustMetrics.overall < 90) {
        recommendations.push({
            id: "trust-warn",
            type: "warning",
            title: "Trust Score Low",
            description: `Current score: ${Math.round(trustMetrics.overall)}%. Verify AI outputs manually.`,
            action: { label: "View Details", href: "/ai-trust" },
            trustScore: trustMetrics.overall,
        });
    }

    if (!trustMetrics.base60Valid) {
        recommendations.push({
            id: "base60-warn",
            type: "warning",
            title: "Base-60 Failed",
            description: "Mathematical harmony check failed. AI may be unreliable.",
            action: { label: "Check Anchors", href: "/ai-trust" },
            trustScore: 45,
        });
    }

    if (recommendations.length === 0) {
        recommendations.push({
            id: "explore-1",
            type: "insight",
            title: "Explore AI Trust",
            description: "View comprehensive AI trust metrics and hallucination detection.",
            action: { label: "Open Dashboard", href: "/ai-trust" },
            trustScore: 95,
        });
    }

    return recommendations;
}

async function getAIResponse(message: string, pathname: string, trustMetrics: TrustMetrics): Promise<string> {
    try {
        const response = await fetch("/api/v1/ai/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: message,
                context: {
                    pathname,
                    trustScore: trustMetrics.overall,
                    dataSupport: trustMetrics.dataSupport,
                    base60Valid: trustMetrics.base60Valid,
                    hallucinationRate: trustMetrics.hallucinationRate,
                },
            }),
        });

        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }

        const data = await response.json();
        return data.response || "I'm having trouble processing that request.";
    } catch (error) {
        console.error("AI response error:", error);

        // Fallback to simple responses if backend is unavailable
        if (message.toLowerCase().includes("trust") || message.toLowerCase().includes("confianza")) {
            return `Your current trust score is ${Math.round(trustMetrics.overall)}%. ${trustMetrics.overall >= 90
                ? "The system is operating within safe parameters."
                : "I recommend verifying AI outputs manually until trust score improves."
                }`;
        }

        if (message.toLowerCase().includes("help") || message.toLowerCase().includes("ayuda")) {
            return `I can help you with: System status, Navigation guidance, Security recommendations, AI output verification. What would you like to know?`;
        }

        return `I'm currently offline. Please check that the AI backend is running.`;
    }
}
