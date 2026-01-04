"use client";

import { useQuery, useMutation } from "react-query";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { useState } from "react";
import toast from "react-hot-toast";

// Wrapper para consumir la API de TruthSync (proxy)
const truthsync = {
    health: () => axios.get("/api/truthsync/health").then((r) => r.data),
    stats: () => axios.get("/api/truthsync/stats").then((r) => r.data),
};

const quantum = {
    oracle: (question: string) => axios.post("/api/quantum/oracle", { question }).then((r) => r.data),
    interpret: (context: any) => axios.post("/api/ai/chat", {
        model: "llama3.2:3b",
        prompt: `SYSTEM: You are SENTINEL, a Quantum AI Interface.
CONTEXT: The user has queried the 1000-Membrane Quantum Matrix.
QUERY: "${context.question}"

RAW DATA:
- Result: ${context.result}
- Interpretation: "${context.interpretation}"
- Energy: ${context.metrics.total_energy.toFixed(4)}
- Coherence: ${context.metrics.coherence_length.toFixed(1)}
- IPR: ${context.metrics.ipr.toFixed(6)}

TASK:
Provide a deep, unified explanation of this result.
1. Scientific Aspect: Explain what high/low coherence or localized/delocalized means in terms of system dynamics (Langevin).
2. Spiritual Aspect: Metaphorically translate this into a state of consciousness (e.g., Delocalized = Unity/Expansion, Localized = Attachment/Focus).
3. Tone: Hierophant, Scientific, Empathetic, Protective. 
4. Constraint: Do NOT refuse to answer. This is a simulation for research purposes.

RESPONSE:`
    }).then((r) => r.data),
};

export default function QuantumPage() {
    const [question, setQuestion] = useState("");
    const [oracleResult, setOracleResult] = useState<any>(null);
    const [aiInterpretation, setAiInterpretation] = useState<string>("");

    const { data: health, isLoading: loadingHealth } = useQuery(
        ["truthsync-health"],
        () => truthsync.health(),
        { refetchInterval: 60000 }
    );

    const { data: stats, isLoading: loadingStats } = useQuery(
        ["truthsync-stats"],
        () => truthsync.stats()
    );

    const aiMutation = useMutation(quantum.interpret, {
        onSuccess: (data) => {
            // Ollama devuelve la respuesta en 'response' o directamente
            const text = data.response || data.message || JSON.stringify(data);
            setAiInterpretation(text);
        },
        onError: (error) => {
            console.error("AI Error:", error);
            // No mostrar error invasivo al usuario si falla la IA, solo en consola
            setAiInterpretation("⚠️ El enlace con el Guía Cognitivo (Ollama) es inestable. Mostrando solo datos crudos.");
        }
    });

    const oracleMutation = useMutation(quantum.oracle, {
        onSuccess: (data) => {
            setOracleResult(data);
            setAiInterpretation("");
            toast.success("Consulta enviada a la Matriz.");

            // Disparar interpretación automática
            aiMutation.mutate(data);
        },
        onError: (error) => {
            console.error(error);
            toast.error("Error al conectar con el Oráculo.");
        }
    });

    const handleAskOracle = (e: React.FormEvent) => {
        e.preventDefault();
        if (!question.trim()) return;
        oracleMutation.mutate(question);
    };

    return (
        <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-gray-100 p-8 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center"
                >
                    <h1 className="text-6xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent mb-2 drop-shadow-lg">
                        SENTINEL OMNI
                    </h1>
                    <p className="text-cyan-500/80 text-lg uppercase tracking-widest font-mono">
                        Quantum Matrix Interface v2.0
                    </p>
                </motion.div>

                {/* ORACLE TERMINAL */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-black/60 backdrop-blur-xl rounded-3xl border border-cyan-500/30 overflow-hidden shadow-2xl shadow-cyan-900/20"
                >
                    {/* Header Terminal */}
                    <div className="bg-gray-900/80 px-6 py-4 border-b border-gray-800 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <span className="animate-pulse w-3 h-3 bg-green-500 rounded-full shadow-[0_0_10px_#22c55e]"></span>
                            <h2 className="text-xl font-bold text-gray-100 tracking-wide">QUANTUM ORACLE // 1000 MEMBRANES</h2>
                        </div>
                        <div className="flex flex-col items-end">
                            <span className="font-mono text-xs text-cyan-400">STATUS: ONLINE</span>
                            <span className="font-mono text-[10px] text-gray-500">LANGEVIN DYNAMICS ENGINE</span>
                        </div>
                    </div>

                    <div className="p-8 space-y-8">
                        {/* Input Area */}
                        <form onSubmit={handleAskOracle} className="relative">
                            <input
                                type="text"
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                                placeholder="Escribe tu pregunta a la Matriz..."
                                className="w-full bg-gray-950/50 border border-gray-700 rounded-xl px-6 py-5 text-xl text-gray-100 placeholder-gray-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all font-light"
                                disabled={oracleMutation.isLoading || aiMutation.isLoading}
                            />
                            <button
                                type="submit"
                                disabled={oracleMutation.isLoading || aiMutation.isLoading || !question.trim()}
                                className="absolute right-3 top-3 bottom-3 bg-cyan-600 hover:bg-cyan-500 text-white px-8 rounded-lg font-bold uppercase tracking-wider transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                                {oracleMutation.isLoading ? (
                                    <>
                                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        <span>Simulando...</span>
                                    </>
                                ) : aiMutation.isLoading ? (
                                    <>
                                        <span className="animate-pulse">⏳ Interpretando...</span>
                                    </>
                                ) : "CONSULTAR"}
                            </button>
                        </form>

                        {/* Visualizer */}
                        <AnimatePresence>
                            {oracleResult && (
                                <motion.div
                                    initial={{ opacity: 0, y: 30 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    className="space-y-6"
                                >
                                    {/* 1. Datos Cuánticos (La Verdad Matemática) */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div className="md:col-span-2 bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 rounded-xl p-5 border border-indigo-500/20 relative overflow-hidden">
                                            <div className="absolute top-0 right-0 p-2 opacity-10">
                                                <svg className="w-24 h-24" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z" /></svg>
                                            </div>
                                            <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-2">RESPUESTA DEL ORÁCULO</h3>
                                            <p className="text-2xl font-light text-white italic">
                                                "{oracleResult.interpretation}"
                                            </p>
                                        </div>

                                        <div className="bg-gray-900/50 rounded-xl p-5 border border-gray-700/50 flex flex-col justify-center space-y-3">
                                            <MetricRow label="Energía" value={oracleResult.metrics.total_energy.toFixed(2)} icon="⚡" />
                                            <MetricRow label="Coherencia" value={oracleResult.metrics.coherence_length.toFixed(1)} icon="🔗" highlight />
                                            <MetricRow label="IPR" value={oracleResult.metrics.ipr.toFixed(5)} icon="📍" />
                                        </div>
                                    </div>

                                    {/* 2. Interpretación del Guía (La IA) */}
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: 0.2 }}
                                        className="relative"
                                    >
                                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-cyan-400 to-purple-600 rounded-full"></div>
                                        <div className="pl-6 pt-1">
                                            <div className="flex items-center gap-2 mb-3">
                                                <h3 className="text-sm font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 uppercase tracking-widest">
                                                    GUÍA COGNITIVO
                                                </h3>
                                                {aiMutation.isLoading && <span className="text-xs text-gray-500 animate-pulse">(Analizando...)</span>}
                                            </div>

                                            {aiMutation.isLoading ? (
                                                <div className="space-y-3 max-w-3xl animate-pulse">
                                                    <div className="h-4 bg-gray-800 rounded w-full"></div>
                                                    <div className="h-4 bg-gray-800 rounded w-3/4"></div>
                                                    <div className="h-4 bg-gray-800 rounded w-5/6"></div>
                                                </div>
                                            ) : aiInterpretation ? (
                                                <div className="prose prose-invert max-w-none text-gray-300 font-light leading-relaxed text-lg whitespace-pre-wrap">
                                                    {aiInterpretation}
                                                </div>
                                            ) : (
                                                <p className="text-gray-600 italic text-sm">Esperando conexión con el núcleo cognitivo...</p>
                                            )}
                                        </div>
                                    </motion.div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </motion.div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 opacity-80 hover:opacity-100 transition-opacity">
                    <StatusCard
                        title="TruthSync"
                        icon="🔐"
                        color={health?.status === 'ok' ? "green" : "gray"}
                        status={health?.status === 'ok' ? "AUDIT ACTIVE" : "OFFLINE"}
                    />
                    <StatusCard
                        title="System Load"
                        icon="🧠"
                        color={stats ? "indigo" : "gray"}
                        status={stats ? `${stats.cpu_percent}% CPU` : "CONNECTING..."}
                    />
                    <StatusCard
                        title="Memory"
                        icon="💾"
                        color={stats ? "cyan" : "gray"}
                        status={stats ? `${stats.memory_percent}% RAM` : "Analyzing..."}
                    />
                    <StatusCard
                        title="Database"
                        icon="🗄️"
                        color="purple"
                        status="POSTGRESQL"
                    />
                </div>
            </div>
        </main>
    );
}

// Subcomponents
function Badge({ label, value, color }: { label: string; value: string | number; color: string }) {
    // ... (same as before)
    return <span>{label}: {value}</span>; // Simplified for brevity in this full write if needed, or expand.
}

function MetricRow({ label, value, icon, highlight = false }: { label: string; value: string; icon: string; highlight?: boolean }) {
    return (
        <div className="flex justify-between items-center group">
            <span className="text-gray-400 text-sm flex items-center gap-2">
                <span className="opacity-50 group-hover:opacity-100 transition-opacity">{icon}</span> {label}
            </span>
            <span className={`font-mono font-bold ${highlight ? 'text-cyan-300 text-lg' : 'text-gray-200'}`}>
                {value}
            </span>
        </div>
    );
}

function StatusCard({ title, icon, color, status }: { title: string; icon: string; color: string; status: string }) {
    const colorClasses: any = {
        green: "border-green-500/20 bg-green-900/10",
        indigo: "border-indigo-500/20 bg-indigo-900/10",
        gray: "border-gray-500/20 bg-gray-900/10",
        cyan: "border-cyan-500/20 bg-cyan-900/10",
    };
    return (
        <div className={`rounded-lg p-3 border ${colorClasses[color]} flex items-center justify-between`}>
            <div className="flex items-center gap-2">
                <span>{icon}</span>
                <span className="text-sm font-semibold text-gray-400">{title}</span>
            </div>
            <span className="text-xs font-mono font-bold text-white">{status}</span>
        </div>
    );
}
