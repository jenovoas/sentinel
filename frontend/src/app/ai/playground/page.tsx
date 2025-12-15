"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

export default function AIPlaygroundPage() {
    const [prompt, setPrompt] = useState("");
    const [model, setModel] = useState("phi3:mini");
    const [maxTokens, setMaxTokens] = useState(100);
    const [temperature, setTemperature] = useState(0.3);
    const [response, setResponse] = useState("");
    const [loading, setLoading] = useState(false);
    const [history, setHistory] = useState<Array<{
        prompt: string;
        response: string;
        timestamp: Date;
        model: string;
    }>>([]);

    const examplePrompts = [
        "Why is CPU usage high right now?",
        "Analyze the memory spike at 2 PM",
        "What caused the latency increase?",
        "Recommend optimizations for database performance",
        "Explain the recent anomaly detection",
        "What are common causes of memory leaks in Node.js?",
    ];

    const handleQuery = async () => {
        if (!prompt.trim()) return;

        setLoading(true);
        setResponse("");

        try {
            const res = await fetch("/api/v1/ai/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt,
                    max_tokens: maxTokens,
                    temperature,
                }),
            });

            const data = await res.json();

            if (data.response) {
                setResponse(data.response);

                // Add to history
                setHistory([
                    {
                        prompt,
                        response: data.response,
                        timestamp: new Date(),
                        model: data.model || model,
                    },
                    ...history,
                ]);
            } else {
                setResponse("Error: No response from AI");
            }
        } catch (error) {
            console.error("AI query error:", error);
            setResponse("Error: Failed to connect to AI service");
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
                            <p className="text-sm uppercase tracking-[0.25em] text-purple-200/70">Sentinel AI</p>
                            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white">
                                AI Playground
                            </h1>
                            <p className="text-gray-300 mt-2 max-w-2xl">
                                Interact with local AI (Ollama + phi3:mini) for system insights and analysis
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
                                    Query Input
                                </CardTitle>
                                <CardDescription>Ask questions about your system metrics and anomalies</CardDescription>
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

                                <div className="grid gap-4 md:grid-cols-3">
                                    <div>
                                        <label className="text-sm text-gray-400 mb-2 block">Model</label>
                                        <select
                                            value={model}
                                            onChange={(e) => setModel(e.target.value)}
                                            className="w-full rounded-lg bg-slate-900/50 border border-white/10 p-2 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                                        >
                                            <option value="phi3:mini">phi3:mini (1.3B)</option>
                                            <option value="llama3.2:1b">llama3.2:1b</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="text-sm text-gray-400 mb-2 block">
                                            Max Tokens: {maxTokens}
                                        </label>
                                        <input
                                            type="range"
                                            min="10"
                                            max="500"
                                            step="10"
                                            value={maxTokens}
                                            onChange={(e) => setMaxTokens(Number(e.target.value))}
                                            className="w-full"
                                        />
                                    </div>

                                    <div>
                                        <label className="text-sm text-gray-400 mb-2 block">
                                            Temperature: {temperature.toFixed(1)}
                                        </label>
                                        <input
                                            type="range"
                                            min="0"
                                            max="1"
                                            step="0.1"
                                            value={temperature}
                                            onChange={(e) => setTemperature(Number(e.target.value))}
                                            className="w-full"
                                        />
                                    </div>
                                </div>

                                <Button
                                    onClick={handleQuery}
                                    disabled={!prompt.trim() || loading}
                                    className="w-full bg-purple-600 hover:bg-purple-700"
                                >
                                    {loading ? (
                                        <>
                                            <span className="animate-spin mr-2">⏳</span>
                                            Generating...
                                        </>
                                    ) : (
                                        <>
                                            <span className="mr-2">🤖</span>
                                            Generate Response
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
                                            AI Response
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
                                                        {item.model}
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
                            <p className="text-purple-400 font-semibold mb-1">Local AI Processing</p>
                            <p className="text-sm text-gray-300">
                                All queries are processed locally using Ollama with phi3:mini model.
                                Your data never leaves your infrastructure. First query may take 7-10s
                                (model loading), subsequent queries ~1-2s.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
