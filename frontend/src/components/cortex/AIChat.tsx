"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal, Cpu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Interface representing a single chat message.
 */
interface Message {
    role: 'user' | 'ai';
    text: string;
    /** Optional evidence block (logs, metrics) to be displayed below the message */
    evidence?: string;
}

/**
 * Main AI Chat Interface Component.
 * 
 * Displays a terminal-like chat window for interacting with the Cortex AI.
 * Includes simulated responses for the "Hollywood" demo effect.
 */
export const AIChat: React.FC = () => {
    const [input, setInput] = useState<string>('');
    const [messages, setMessages] = useState<Message[]>([
        { role: 'ai', text: 'Cortex v1.0.0 online. Waiting for instructions.' }
    ]);

    // Reference for auto-scrolling to the bottom of the chat
    const scrollRef = useRef<HTMLDivElement>(null);

    /**
     * Effect to auto-scroll to the latest message whenever the message list changes.
     */
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    /**
     * Handles sending a message and triggering the mock AI response.
     */
    const handleSend = () => {
        if (!input.trim()) return;

        // Add user message to state
        setMessages(prev => [...prev, { role: 'user', text: input }]);
        const currentInput = input;
        setInput('');

        // Mock AI Response (Simulating "Hollywood" interaction)
        // In a real implementation, this would call an API hook (e.g., useMutation)
        setTimeout(() => {
            let responseText = "Processing...";
            let evidence: string | undefined = undefined;

            // Simple pattern matching for demo purposes
            if (currentInput.toLowerCase().includes('attack')) {
                responseText = "Simulating DDoS attack pattern (SynFloods). Activating Shield Protocols.";
                evidence = "[LOG] 20:42:15 WARN SynFlood detected from 192.168.1.X\n[METRIC] cpu_usage > 85%";
            } else if (currentInput.toLowerCase().includes('status')) {
                responseText = "All systems nominal. Kernel integrity verified.";
                evidence = "[KERNEL] SHA256: 3a1f...e5b2 OK";
            } else {
                responseText = `Command '${currentInput}' acknowledged.`;
            }

            setMessages(prev => [...prev, { role: 'ai', text: responseText, evidence }]);
        }, 1000);
    };

    return (
        <div className="flex flex-col h-full bg-slate-950 rounded-xl border border-slate-800 overflow-hidden font-mono text-sm relative">
            {/* Header / Toolbar */}
            <div className="bg-slate-900 border-b border-white/5 p-2 flex items-center space-x-2 text-slate-400">
                <Terminal className="w-4 h-4" />
                <span className="text-xs uppercase tracking-widest">Cortex Command Uplink</span>
                <div className="flex-1" />
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                <AnimatePresence>
                    {messages.map((msg, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                        >
                            <div className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user'
                                ? 'bg-blue-600/20 border border-blue-500/30 text-blue-100'
                                : 'bg-slate-800/50 border border-slate-700/50 text-emerald-100'
                                }`}>
                                <div className="flex items-center space-x-2 mb-1 opacity-50 text-xs">
                                    {msg.role === 'ai' ? <Cpu className="w-3 h-3" /> : null}
                                    <span>{msg.role === 'ai' ? 'CORTEX' : 'COMMANDER'}</span>
                                </div>
                                {msg.text}
                            </div>
                            {msg.evidence && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    className="mt-1 ml-2 max-w-[80%] text-[10px] text-slate-500 bg-black/30 p-2 rounded border border-dashed border-slate-800 w-full"
                                >
                                    <pre>{msg.evidence}</pre>
                                </motion.div>
                            )}
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {/* Input Area */}
            <div className="p-3 bg-slate-900/50 border-t border-white/5">
                <div className="flex items-center space-x-2 bg-black/40 rounded-lg p-2 border border-slate-800 focus-within:border-emerald-500/50 transition-colors">
                    <span className="text-emerald-500">{'>'}</span>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        className="flex-1 bg-transparent border-none outline-none text-white placeholder-slate-600"
                        placeholder="Enter command..."
                        autoFocus
                    />
                    <button onClick={handleSend} className="p-1 hover:bg-white/10 rounded transition-colors">
                        <Send className="w-4 h-4 text-slate-400" />
                    </button>
                </div>
            </div>
        </div>
    );
};
