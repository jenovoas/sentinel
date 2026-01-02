"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Terminal, Cpu, FileText, Monitor, Shield, LayoutDashboard, Brain } from "lucide-react";

type CommandItem = {
    id: string;
    icon: React.ReactNode;
    label: string;
    action: () => void;
    shortcut?: string;
    group: "Navigation" | "System" | "AI";
};

export function CommandPalette() {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState("");
    const router = useRouter();

    // Toggle with Ctrl+K
    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setIsOpen((open) => !open);
            }
        };
        document.addEventListener("keydown", down);
        return () => document.removeEventListener("keydown", down);
    }, []);

    // Commands Definition
    const commands: CommandItem[] = [
        // Navigation
        { id: "nav-home", icon: <LayoutDashboard size={16} />, label: "Go to Dashboard", group: "Navigation", action: () => router.push("/") },
        { id: "nav-ops", icon: <Monitor size={16} />, label: "Ops Center", group: "Navigation", action: () => router.push("/dash-op") },
        { id: "nav-browser", icon: <Shield size={16} />, label: "Secure Browser", group: "Navigation", action: () => router.push("/dashboard") },
        { id: "nav-watchdog", icon: <Shield size={16} />, label: "Watchdog Monitor", group: "Navigation", action: () => router.push("/watchdog") },
        { id: "nav-mon", icon: <Cpu size={16} />, label: "Live Monitoring", group: "Navigation", action: () => router.push("/monitoring") },
        { id: "nav-docs", icon: <FileText size={16} />, label: "Documentation", group: "Navigation", action: () => router.push("/reports") },

        // AI Actions
        { id: "ai-analyze", icon: <Brain size={16} />, label: "Ask Cortex to analyze system status", group: "AI", action: () => console.log("AI Analyze Triggered") },

        // System
        { id: "sys-clear", icon: <Terminal size={16} />, label: "Clear Local Cache", group: "System", action: () => window.localStorage.clear() },
    ];

    const filteredCommands = commands.filter((cmd) =>
        cmd.label.toLowerCase().includes(query.toLowerCase())
    );

    // Grouping for display
    const grouped = filteredCommands.reduce((acc, cmd) => {
        if (!acc[cmd.group]) acc[cmd.group] = [];
        acc[cmd.group].push(cmd);
        return acc;
    }, {} as Record<string, CommandItem[]>);

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] px-4">
                {/* Backdrop */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={() => setIsOpen(false)}
                    className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                />

                {/* Modal */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -20 }}
                    className="relative w-full max-w-2xl overflow-hidden rounded-xl border border-white/10 bg-slate-900/90 shadow-2xl backdrop-blur-xl ring-1 ring-white/10"
                >
                    {/* Header / Input */}
                    <div className="flex items-center gap-3 border-b border-white/5 px-4 py-3">
                        <Search className="h-5 w-5 text-slate-400" />
                        <input
                            autoFocus
                            className="flex-1 bg-transparent text-lg text-white placeholder:text-slate-500 focus:outline-none font-medium"
                            placeholder="Type a command or search..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && filteredCommands.length > 0) {
                                    filteredCommands[0].action();
                                    setIsOpen(false);
                                }
                                if (e.key === "Escape") setIsOpen(false);
                            }}
                        />
                        <div className="flex items-center gap-1 rounded bg-white/10 px-2 py-0.5 text-xs text-slate-400 font-mono">
                            ESC
                        </div>
                    </div>

                    {/* List */}
                    <div className="max-h-[60vh] overflow-y-auto p-2 custom-scrollbar">
                        {Object.keys(grouped).length === 0 ? (
                            <div className="p-4 text-center text-sm text-slate-500">No results found.</div>
                        ) : (
                            Object.entries(grouped).map(([group, items]) => (
                                <div key={group} className="mb-2">
                                    <div className="px-2 py-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                                        {group}
                                    </div>
                                    {items.map((cmd) => (
                                        <button
                                            key={cmd.id}
                                            onClick={() => {
                                                cmd.action();
                                                setIsOpen(false);
                                            }}
                                            className="w-full flex items-center gap-3 rounded-lg px-2 py-2.5 text-left text-sm text-slate-300 hover:bg-white/10 hover:text-white transition-colors group"
                                        >
                                            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-white/5 text-slate-400 ring-1 ring-white/5 group-hover:bg-white/10 group-hover:text-white group-hover:ring-white/10 transition-all">
                                                {cmd.icon}
                                            </div>
                                            <span className="flex-1">{cmd.label}</span>
                                            {cmd.shortcut && (
                                                <span className="text-xs text-slate-500 font-mono">{cmd.shortcut}</span>
                                            )}
                                        </button>
                                    ))}
                                </div>
                            ))
                        )}
                    </div>

                    {/* Footer */}
                    <div className="border-t border-white/5 bg-white/5 px-4 py-2 text-xs text-slate-500 flex justify-between">
                        <span>Sentinel Cortex v2.0</span>
                        <span>Press <span className="text-white">Ctrl+K</span> to close</span>
                    </div>

                </motion.div>
            </div>
        </AnimatePresence>
    );
}
