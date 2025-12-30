'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Terminal, Shield, AlertTriangle, CheckCircle, Activity } from 'lucide-react';

interface AttackEvent {
    id: number;
    decision_type: 'block' | 'allow' | 'escalate';
    confidence: number;
    patterns: string[];
    process: string;
    timestamp: string;
    latency_ms: number;
}

export default function AttackStream() {
    const [events, setEvents] = React.useState<AttackEvent[]>([]);
    const [connected, setConnected] = React.useState(false);
    const wsRef = React.useRef<WebSocket | null>(null);

    React.useEffect(() => {
        // Connect to WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host || 'localhost:3000';
        // Ensure we point to backend port 8000 for WS if on dev, or use proxy
        const wsUrl = `ws://localhost:8000/ws`;

        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
            console.log('✅ Connected to Cortex Neural Stream');
            setConnected(true);
        };

        wsRef.current.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                if (message.type === 'decision') {
                    setEvents(prev => [message.data, ...prev].slice(0, 50)); // Keep last 50
                }
            } catch (e) {
                console.error('Error parsing WS message:', e);
            }
        };

        wsRef.current.onclose = () => setConnected(false);

        // Cleanup
        return () => {
            wsRef.current?.close();
        };
    }, []);

    const getIcon = (type: string) => {
        switch (type) {
            case 'block': return <Shield className="text-red-500" size={16} />;
            case 'escalate': return <AlertTriangle className="text-orange-500" size={16} />;
            default: return <CheckCircle className="text-emerald-500" size={16} />;
        }
    };

    return (
        <Card className="h-[600px] flex flex-col border-none bg-slate-950 text-slate-200 shadow-2xl font-mono text-sm">
            <CardHeader className="border-b border-slate-800 py-3 bg-slate-900/50">
                <div className="flex justify-between items-center">
                    <CardTitle className="flex items-center gap-2 text-sm uppercase tracking-wider">
                        <Terminal size={14} className="text-blue-400" />
                        Cortex Neural Stream
                    </CardTitle>
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] opacity-50">{events.length} EVENTS CAPTURED</span>
                        <div className={`h-2 w-2 rounded-full ${connected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                    </div>
                </div>
            </CardHeader>
            <CardContent className="flex-1 p-0 overflow-hidden relative">
                <ScrollArea className="h-full w-full p-4">
                    <div className="space-y-2">
                        {events.length === 0 && (
                            <div className="text-center opacity-30 mt-20">
                                <Activity className="mx-auto mb-2" size={32} />
                                <p>WAITING FOR NEURAL ACTIVITY...</p>
                            </div>
                        )}
                        {events.map((evt) => (
                            <div
                                key={evt.id}
                                className={`
                                    p-3 rounded border-l-2 flex flex-col gap-2 transition-all hover:bg-white/5
                                    ${evt.decision_type === 'block' ? 'border-red-500 bg-red-950/10' :
                                        evt.decision_type === 'escalate' ? 'border-orange-500 bg-orange-950/10' :
                                            'border-emerald-500 bg-emerald-950/10'}
                                `}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex items-center gap-2">
                                        {getIcon(evt.decision_type)}
                                        <span className={`font-bold uppercase ${evt.decision_type === 'block' ? 'text-red-400' :
                                                evt.decision_type === 'escalate' ? 'text-orange-400' :
                                                    'text-emerald-400'
                                            }`}>
                                            {evt.decision_type}
                                        </span>
                                        <span className="opacity-50 text-xs">ID::{evt.id.toString().padStart(6, '0')}</span>
                                    </div>
                                    <span className="text-xs opacity-40">{new Date(evt.timestamp).toLocaleTimeString()}</span>
                                </div>

                                <div className="flex justify-between text-xs">
                                    <span className="text-blue-300 truncate max-w-[200px]">{evt.process || 'unknown'}</span>
                                    <div className="flex items-center gap-2">
                                        <Badge variant="outline" className="border-slate-700 text-[10px] h-5">
                                            {(evt.confidence * 100).toFixed(0)}% CONF
                                        </Badge>
                                        <span className="text-slate-500">{evt.latency_ms?.toFixed(2)}ms</span>
                                    </div>
                                </div>

                                {evt.patterns && evt.patterns.length > 0 && (
                                    <div className="flex flex-wrap gap-1 mt-1">
                                        {evt.patterns.map((p, i) => (
                                            <span key={i} className="text-[10px] px-1.5 py-0.5 bg-slate-800 rounded text-slate-400">
                                                {p}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </ScrollArea>

                {/* CRT Scanline Effect */}
                <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-10 bg-[length:100%_2px,3px_100%] opacity-20" />
            </CardContent>
        </Card>
    );
}
