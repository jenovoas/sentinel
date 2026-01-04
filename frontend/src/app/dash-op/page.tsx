'use client';

import { useState, useEffect } from "react";
import { ShieldAlert, Terminal, Lock, Eye, AlertTriangle, Radio } from "lucide-react";
import { motion } from "framer-motion";

interface AlertItem {
  type: string;
  hash: string;
  ip: string;
  timestamp: number;
  severity: string;
}

interface CombinedEvent {
  id: string;
  timestamp: number;
  type: 'SUCCESS' | 'ALERT';
  hash: string;
  details: any;
}

export default function DashOpPage() {
  const [events, setEvents] = useState<CombinedEvent[]>([]);

  const fetchData = async () => {
    try {
      // Fetch History (Successes)
      const histRes = await fetch('/api/v1/user/soul-history');
      const history: any[] = histRes.ok ? await histRes.json() : [];

      // Fetch Alerts (Failures)
      const alertRes = await fetch('/api/v1/sentinel/alerts');
      const alerts: AlertItem[] = alertRes.ok ? await alertRes.json() : [];

      const combined: CombinedEvent[] = [
        ...history.map((h, i) => ({
          id: `h-${i}-${h.timestamp}`,
          timestamp: h.timestamp,
          type: 'SUCCESS' as const,
          hash: h.role === 'Sovereign' ? 'jnovoas' : 'Family Member',
          details: h
        })),
        ...alerts.map((a, i) => ({
          id: `a-${i}-${a.timestamp}`,
          timestamp: a.timestamp,
          type: 'ALERT' as const,
          hash: a.hash,
          details: a
        }))
      ].sort((a, b) => b.timestamp - a.timestamp); // Newest first

      setEvents(combined);
    } catch (e) {
      console.error("Failed to sync ops dashboard", e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (ts: number) => {
    const date = new Date(ts * 1000);
    return date.toLocaleTimeString();
  };

  return (
    <main className="min-h-screen bg-[#020617] text-cyan-50 font-mono p-4 md:p-8">
      <header className="mb-8 flex items-center gap-4 border-b border-cyan-900/50 pb-4">
        <div className="p-3 bg-red-950/30 rounded-lg border border-red-500/20">
          <ShieldAlert className="w-8 h-8 text-red-500" />
        </div>
        <div>
          <h1 className="text-2xl md:text-3xl font-black uppercase tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-amber-500">
            Sentinel Ops Center
          </h1>
          <div className="flex items-center gap-2 text-xs text-red-400/60 uppercase tracking-widest">
            <Radio className="w-3 h-3 animate-pulse" />
            Live Security Feed
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Feed */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-bold text-cyan-700 uppercase tracking-widest flex items-center gap-2">
            <Terminal className="w-4 h-4" />
            Event Log
          </h2>

          <div className="space-y-2">
            {events.length === 0 && (
              <div className="text-cyan-900 italic text-center py-10">No biological signatures detected...</div>
            )}

            {events.map((event) => (
              <motion.div
                key={event.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`p-4 rounded border flex items-center gap-4 ${event.type === 'ALERT'
                  ? 'bg-red-950/10 border-red-900/50 text-red-100'
                  : 'bg-cyan-950/10 border-cyan-900/50 text-cyan-100'
                  }`}
              >
                <div className="text-xs opacity-50 w-20 shrink-0 font-mono">
                  {formatTime(event.timestamp)}
                </div>

                <div className="p-2 rounded-full bg-black/20 shrink-0">
                  {event.type === 'ALERT' && <AlertTriangle className="w-5 h-5 text-red-500" />}
                  {event.type === 'SUCCESS' && event.details.role === 'Sovereign' && <Lock className="w-5 h-5 text-amber-400" />}
                  {event.type === 'SUCCESS' && event.details.role !== 'Sovereign' && <Eye className="w-5 h-5 text-cyan-400" />}
                </div>

                <div className="flex-1">
                  <div className="flex items-baseline gap-2">
                    <span className="font-bold">
                      {event.type === 'SUCCESS' && event.details.role === 'Sovereign' && '👑 SOVEREIGN'}
                      {event.type === 'SUCCESS' && event.details.role !== 'Sovereign' && '👁️ MONITORED'}
                      {event.type === 'ALERT' && '⛔ BLOCKED'}
                    </span>
                    <span className="text-xs uppercase tracking-wider opacity-70">
                      {event.hash}
                    </span>
                  </div>
                  <div className="text-xs opacity-60 mt-1">
                    {event.type === 'ALERT' && `IP: ${event.details.ip} | L: ${event.details.lyapunov.toFixed(2)} | E: ${event.details.entropy.toFixed(2)} | SEV: ${event.details.severity}`}
                    {event.type === 'SUCCESS' && `Lyapunov: ${event.details.lyapunov_exp.toFixed(4)} | Entropy: ${event.details.chaos_entropy.toFixed(4)}`}
                  </div>
                </div>

                {event.type === 'ALERT' && (
                  <div className="px-2 py-1 bg-red-500/20 text-red-300 text-[10px] uppercase rounded border border-red-500/30">
                    Intrusion
                  </div>
                )}
                {event.type === 'SUCCESS' && (
                  <div className="px-2 py-1 bg-green-500/20 text-green-300 text-[10px] uppercase rounded border border-green-500/30">
                    Authorized
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        {/* Sidebar Stats */}
        <div className="space-y-6">
          <div className="p-6 bg-black/40 border border-cyan-900/30 rounded-xl space-y-4">
            <h3 className="text-xs font-bold text-cyan-600 uppercase">System Status</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-cyan-950/20 rounded border border-cyan-900/20 text-center">
                <div className="text-2xl font-black text-cyan-400">
                  {events.filter(e => e.type === 'SUCCESS').length}
                </div>
                <div className="text-[10px] uppercase text-cyan-700 mt-1">Authentications</div>
              </div>
              <div className="p-4 bg-red-950/20 rounded border border-red-900/20 text-center">
                <div className="text-2xl font-black text-red-500">
                  {events.filter(e => e.type === 'ALERT').length}
                </div>
                <div className="text-[10px] uppercase text-red-700 mt-1">Intrusions</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
