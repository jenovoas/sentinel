"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

export default function AIPlaygroundPage() {
    const [prompt, setPrompt] = useState("");
    const [response, setResponse] = useState("");
    const [loading, setLoading] = useState(false);
    const [history, setHistory] = useState<Array<{
        prompt: string;
        response: string;
        timestamp: Date;
    }>>([]);

    const examplePrompts = [
        "¿Qué es una anomalía de CPU?",
        "Explica qué es Prometheus en 10 palabras",
        "¿Cómo optimizar una base de datos?",
        "¿Qué causa un memory leak?",
        "Explica qué es latencia",
        "¿Cómo funciona Redis?",
    ];

    const handleQuery = async () => {
        if (!prompt.trim()) return;

        setLoading(true);
        setResponse("");

        try {
            const res = await fetch("/api/v1/ai/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: prompt }),
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.error || `HTTP ${res.status}`);
            }

            const verification = JSON.stringify(data, null, 2);
            setResponse(verification);
            setHistory((previous) => [
                { prompt, response: verification, timestamp: new Date() },
                ...previous,
            ]);
        } catch (error) {
            console.error("AI query error:", error);
            setResponse(`No se pudo verificar la consulta: ${error instanceof Error ? error.message : "error de conexión"}`);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && e.ctrlKey) {
            handleQuery();
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100">
            <div
                className="absolute inset-0 opacity-50 blur-3xl bg-[radial-gradient(circle_at_20%_20%,rgba(139,92,246,0.12),transparent_35%),radial-gradient(circle_at_80%_0%,rgba(34,211,238,0.12),transparent_30%)]"
                aria-hidden
            />

            <div className="relative mx-auto max-w-7xl px-6 py-10">
                {/* Header */}
                <header className="mb-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm uppercase tracking-[0.25em] text-purple-200/70">Sentinel · TruthSync</p>
                            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white">
                                Verificación de consultas
                            </h1>
                            <p className="text-gray-300 mt-2 max-w-2xl">
                                TruthSync verifica el texto enviado; Cortex no tiene conectado un generador de respuestas IA.
                            </p>
                        </div>
                        <Link href="/dashboard">
                            <Button variant="outline">← Back to Dashboard</Button>
                        </Link>
                    </div>
                </header>

                <div className="grid gap-6 lg:grid-cols-3">
                    {/* Left: Query Interface (2 columns) */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Query Input */}
                        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <span className="text-purple-400">💬</span>
                                    Texto para verificar
                                </CardTitle>
                                <CardDescription>La verificación no genera ni responde preguntas.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <textarea
                                        placeholder="Enter your prompt here... (Ctrl+Enter to submit)"
                                        value={prompt}
                                        onChange={(e) => setPrompt(e.target.value)}
                                        onKeyDown={handleKeyPress}
                                        rows={6}
                                        className="w-full resize-none rounded-lg bg-slate-900/50 border border-white/10 p-4 text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                                    />
                                </div>

                                <p className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3 text-sm text-amber-200/80">
                                    El contrato actual acepta solo el texto de consulta y devuelve resultados de verificación TruthSync; no hay selección de modelo ni parámetros de generación.
                                </p>

                                <Button
                                    onClick={handleQuery}
                                    disabled={!prompt.trim() || loading}
                                    className="w-full bg-purple-600 hover:bg-purple-700"
                                >
                                    {loading ? (
                                        <>
                                            <span className="animate-spin mr-2">⏳</span>
                                            Verificando…
                                        </>
                                    ) : (
                                        <>
                                            <span className="mr-2">🤖</span>
                                            Verificar consulta
                                        </>
                                    )}
                                </Button>
                            </CardContent>
                        </Card>

                        {/* Response */}
                        {response && (
                            <Card className="bg-white/5 backdrop-blur-xl border-purple-500/20">
                                <CardHeader>
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="flex items-center gap-2">
                                            <span className="text-purple-400">✨</span>
                                            Resultado de verificación TruthSync
                                        </CardTitle>
                                        <div className="flex gap-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => copyToClipboard(response)}
                                            >
                                                📋 Copy
                                            </Button>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="bg-slate-900/50 rounded-lg p-4 font-mono text-sm whitespace-pre-wrap text-gray-300 border border-white/10">
                                        {response}
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </div>

                    {/* Right: Examples & History */}
                    <div className="space-y-6">
                        {/* Example Prompts */}
                        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <span className="text-cyan-400">💡</span>
                                    Example Prompts
                                </CardTitle>
                                <CardDescription>Click to use</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-2">
                                {examplePrompts.map((example, i) => (
                                    <button
                                        key={i}
                                        onClick={() => setPrompt(example)}
                                        className="w-full text-left bg-slate-900/50 hover:bg-slate-800/50 border border-white/10 rounded-lg p-3 text-sm text-gray-300 transition-colors"
                                    >
                                        {example}
                                    </button>
                                ))}
                            </CardContent>
                        </Card>

                        {/* Query History */}
                        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <CardTitle className="flex items-center gap-2">
                                        <span className="text-emerald-400">📜</span>
                                        Query History
                                    </CardTitle>
                                    {history.length > 0 && (
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => setHistory([])}
                                        >
                                            Clear
                                        </Button>
                                    )}
                                </div>
                            </CardHeader>
                            <CardContent>
                                {history.length === 0 ? (
                                    <p className="text-sm text-gray-400">No queries yet</p>
                                ) : (
                                    <div className="space-y-3 max-h-96 overflow-y-auto">
                                        {history.map((item, i) => (
                                            <div
                                                key={i}
                                                className="bg-slate-900/50 rounded-lg p-3 border border-white/10 cursor-pointer hover:border-purple-500/30 transition-colors"
                                                onClick={() => setPrompt(item.prompt)}
                                            >
                                                <div className="flex items-center justify-between mb-2">
                                                    <p className="text-xs text-gray-400">
                                                        {item.timestamp.toLocaleTimeString()}
                                                    </p>
                                                    <Badge variant="outline" className="text-xs">
                                                        TruthSync
                                                    </Badge>
                                                </div>
                                                <p className="text-sm font-medium text-purple-400 mb-2 line-clamp-2">
                                                    {item.prompt}
                                                </p>
                                                <p className="text-xs text-gray-300 line-clamp-3">
                                                    {item.response}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </div>

                {/* Info Footer */}
                <div className="mt-8 bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                        <span className="text-2xl">ℹ️</span>
                        <div>
                            <p className="text-purple-400 font-semibold mb-1">Verificación local de TruthSync</p>
                            <p className="text-sm text-gray-300">
                                La ruta de Cortex valida la consulta y devuelve campos de verificación. No genera respuestas de texto ni expone modelo, latencia estimada o garantías sobre el procesamiento de red.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
