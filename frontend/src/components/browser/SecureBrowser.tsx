"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Shield, Globe, Lock, Eye, EyeOff, Search, RotateCcw, ShieldCheck, ShieldAlert } from "lucide-react";

type BrowseMode = "clear" | "velocity" | "ghost" | "deep";

interface BrowserResponse {
    success: boolean;
    url?: string;
    title?: string;
    content?: string; // HTML string
    text_only?: string;
    error?: string;
    mode: BrowseMode;
    verification?: any;
    proxy_error?: boolean;
}

interface SecureBrowserProps {
    initialUrl?: string;
    initialMode?: BrowseMode;
    autoNavigate?: boolean;
}

export function SecureBrowser({ initialUrl, initialMode, autoNavigate = false }: SecureBrowserProps = {}) {
    const [url, setUrl] = useState(initialUrl || "https://example.com");
    const [mode, setMode] = useState<BrowseMode>(initialMode || "clear");
    const [isLoading, setIsLoading] = useState(false);
    const [response, setResponse] = useState<BrowserResponse | null>(null);
    const [history, setHistory] = useState<string[]>([]);

    // Auto-navigate when initialUrl or initialMode changes (e.g. via parent state/params)
    useEffect(() => {
        if (autoNavigate && initialUrl) {
            setUrl(initialUrl);
            const targetMode = initialMode || mode;
            if (initialMode) setMode(initialMode);
            handleBrowse(initialUrl, targetMode);
        }
    }, [initialUrl, initialMode, autoNavigate]);

    const handleBrowse = async (overrideUrl?: string, overrideMode?: BrowseMode) => {
        let targetUrl = (overrideUrl || url).trim();
        const targetMode = overrideMode || mode;

        if (!targetUrl) return;

        // Search detection: If not a URL, treat as query
        if (!targetUrl.startsWith('http') && !targetUrl.includes('.')) {
            targetUrl = `http://localhost:8080/search?q=${encodeURIComponent(targetUrl)}`;
            setUrl(targetUrl);
        }

        setIsLoading(true);
        setResponse(null);

        try {
            // Add to history if unique
            if (!history.includes(targetUrl)) {
                setHistory(prev => [targetUrl, ...prev].slice(0, 10));
            }

            const res = await fetch("http://localhost:8000/browser/browse", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ url: targetUrl, mode: targetMode }),
            });

            const data = await res.json();
            setResponse(data);
        } catch (error) {
            setResponse({
                success: false,
                mode: targetMode,
                error: "Failed to connect to backend service."
            });
        } finally {
            setIsLoading(false);
        }
    };

    const getModeColor = (m: BrowseMode) => {
        switch (m) {
            case "clear": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
            case "velocity": return "text-cyan-400 bg-cyan-500/10 border-cyan-500/20";
            case "ghost": return "text-purple-400 bg-purple-500/10 border-purple-500/20";
            case "deep": return "text-rose-400 bg-rose-500/10 border-rose-500/20";
        }
    };

    const getModeIcon = (m: BrowseMode) => {
        switch (m) {
            case "clear": return <Globe className="w-4 h-4" />;
            case "velocity": return <Shield className="w-4 h-4" />; // Tor
            case "ghost": return <EyeOff className="w-4 h-4" />; // Nym
            case "deep": return <Lock className="w-4 h-4" />; // I2P
        }
    };

    return (
        <div className="space-y-6">
            {/* Control Bar */}
            <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                <CardContent className="p-4">
                    <div className="flex gap-4">
                        {/* Mode Selector */}
                        <div className="w-40">
                            <Select value={mode} onValueChange={(v: BrowseMode) => setMode(v)}>
                                <SelectTrigger className="bg-slate-900/50 border-white/10">
                                    <SelectValue placeholder="Mode" />
                                </SelectTrigger>
                                <SelectContent className="bg-slate-900 border-white/10 text-gray-200">
                                    <SelectItem value="clear">
                                        <div className="flex items-center gap-2">
                                            <Globe className="w-3 h-3 text-emerald-400" /> Clear
                                        </div>
                                    </SelectItem>
                                    <SelectItem value="velocity">
                                        <div className="flex items-center gap-2">
                                            <Shield className="w-3 h-3 text-cyan-400" /> Velocity
                                        </div>
                                    </SelectItem>
                                    <SelectItem value="ghost">
                                        <div className="flex items-center gap-2">
                                            <EyeOff className="w-3 h-3 text-purple-400" /> Ghost
                                        </div>
                                    </SelectItem>
                                    <SelectItem value="deep">
                                        <div className="flex items-center gap-2">
                                            <Lock className="w-3 h-3 text-rose-400" /> Deep
                                        </div>
                                    </SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        {/* URL Input */}
                        <div className="flex-1 flex gap-2">
                            <Input
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="Enter URL (e.g., https://example.com)"
                                className="bg-slate-900/50 border-white/10 text-gray-200"
                                onKeyDown={(e) => e.key === 'Enter' && handleBrowse()}
                            />
                            <Button
                                onClick={() => handleBrowse()}
                                disabled={isLoading}
                                className="bg-cyan-500 hover:bg-cyan-600 text-white"
                            >
                                {isLoading ? <RotateCcw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Browser Content Area */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

                {/* Main Viewport */}
                <div className="lg:col-span-3">
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10 min-h-[600px] flex flex-col">
                        <CardHeader className="border-b border-white/10 py-3">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <Badge variant="outline" className={`${getModeColor(mode)} flex items-center gap-1`}>
                                        {getModeIcon(mode)} {mode.toUpperCase()} MODE
                                    </Badge>
                                    {response?.success && (
                                        <span className="text-sm text-gray-400 truncate max-w-md">
                                            {response.title}
                                        </span>
                                    )}
                                </div>
                                <div className="text-xs text-gray-500">
                                    {isLoading ? "Fetching..." : response ? `Status: ${response.status_code || 200}` : "Ready"}
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent className="p-0 flex-1 relative overflow-hidden bg-white/90">
                            {isLoading ? (
                                <div className="absolute inset-0 flex items-center justify-center bg-slate-900/10 backdrop-blur-sm">
                                    <div className="flex flex-col items-center gap-4">
                                        <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
                                        <p className="text-slate-800 font-medium animate-pulse">
                                            Routing through {mode === 'clear' ? 'Direct Connection' : 'Anonymity Network'}...
                                        </p>
                                    </div>
                                </div>
                            ) : response ? (
                                response.success ? (
                                    <div
                                        className="w-full h-full overflow-auto p-8 prose max-w-none dark:prose-invert text-gray-200"
                                        onClick={(e) => {
                                            const target = (e.target as HTMLElement).closest('a');
                                            if (target && target.href) {
                                                e.preventDefault();
                                                const clickedUrl = target.href;
                                                setUrl(clickedUrl);
                                                handleBrowse(clickedUrl);
                                            }
                                        }}
                                    >
                                        {/* Render Sanitized HTML */}
                                        <div dangerouslySetInnerHTML={{ __html: response.content || "" }} />
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center h-full text-center p-8 bg-slate-100">
                                        <Shield className="w-16 h-16 text-rose-500 mb-4" />
                                        <h3 className="text-xl font-bold text-rose-600 mb-2">Connection Blocked / Failed</h3>
                                        <p className="text-slate-600 max-w-md">
                                            {response.error}
                                        </p>
                                        {response.proxy_error && (
                                            <div className="mt-4 p-4 bg-amber-50 text-amber-800 rounded-lg text-sm max-w-md">
                                                <strong>Tip:</strong> Ensure your Tor/Nym proxy is running on the configured port.
                                            </div>
                                        )}
                                    </div>
                                )
                            ) : (
                                <div className="flex flex-col items-center justify-center h-full text-center text-slate-500">
                                    <Globe className="w-12 h-12 mb-4 opacity-20" />
                                    <p>Enter a URL to begin secure browsing</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Sidebar Info */}
                <div className="space-y-6">
                    {/* TruthSync Verification */}
                    <Card className="bg-slate-900/50 backdrop-blur-2xl border-white/10 overflow-hidden relative">
                        <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-cyan-500 to-blue-600"></div>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-xs font-bold uppercase tracking-widest text-cyan-400 flex items-center gap-2">
                                <ShieldCheck className="w-4 h-4" />
                                TruthSync AI
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            {response?.verification ? (
                                <div className="space-y-4">
                                    <div className="flex flex-col gap-1">
                                        <div className="flex items-center justify-between text-xs text-gray-400">
                                            <span>VERDICT</span>
                                            <span className="font-mono text-[10px]">{response.verification.verdict}</span>
                                        </div>
                                        <div className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                                            {response.verification.score}%
                                            <span className="text-sm font-medium text-gray-500">Confidence</span>
                                        </div>
                                        <div className="w-full h-1.5 bg-white/5 rounded-full mt-1 overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${response.verification.score}%` }}
                                                className={`h-full rounded-full ${response.verification.score > 80 ? "bg-emerald-500" :
                                                    response.verification.score > 50 ? "bg-amber-500" : "bg-rose-500"
                                                    }`}
                                            />
                                        </div>
                                    </div>

                                    <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                                        <p className="text-[11px] leading-relaxed text-gray-300 italic">
                                            "{response.verification.reasoning}"
                                        </p>
                                    </div>

                                    {response.verification.flags && response.verification.flags.length > 0 && (
                                        <div className="space-y-2">
                                            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-tighter">AI DETECTIONS</p>
                                            <div className="flex flex-wrap gap-1">
                                                {response.verification.flags.map((flag: string, i: number) => (
                                                    <span key={i} className="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 text-[9px] border border-rose-500/20">
                                                        {flag}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <Button
                                        onClick={() => handleBrowse()}
                                        variant="outline"
                                        className="w-full mt-2 h-7 text-[10px] border-white/10 hover:bg-white/5 text-gray-400"
                                    >
                                        <RotateCcw className="w-3 h-3 mr-2" />
                                        REFRESH ANALYSIS
                                    </Button>
                                </div>
                            ) : (
                                <div className="py-8 flex flex-col items-center justify-center text-center opacity-40">
                                    <ShieldAlert className="w-8 h-8 mb-2 text-gray-600" />
                                    <p className="text-[10px] text-gray-500">STANDBY FOR NEURAL ANALYSIS</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Connection Details */}
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardHeader>
                            <CardTitle className="text-sm font-medium text-gray-300">
                                Circuit Details
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <div className="text-xs">
                                <span className="text-gray-500 block">Protocol</span>
                                <span className="text-gray-300 font-mono">{mode === 'clear' ? 'HTTPS/Direct' : 'SOCKS5/Tunnel'}</span>
                            </div>
                            <div className="text-xs">
                                <span className="text-gray-500 block">Encryption</span>
                                <span className="text-emerald-400 font-mono">AES-256-GCM (Local)</span>
                            </div>
                            <div className="text-xs">
                                <span className="text-gray-500 block">Sanitization</span>
                                <span className="text-emerald-400 font-mono">Active (Scripts Blocked)</span>
                            </div>
                        </CardContent>
                    </Card>
                </div>

            </div>
        </div>
    );
}
