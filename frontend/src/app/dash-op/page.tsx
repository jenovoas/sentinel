"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSentinelStatus } from "@/hooks/useSentinelStatus";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Server, Zap, Globe, Database, Terminal, ShieldAlert, BarChart3, Clock, AlertCircle, Sparkles, BrainCircuit, Network, Cpu } from "lucide-react";

export default function OperationsMatrixPage() {
  const { status, loading } = useSentinelStatus();
  const [notes, setNotes] = useState("");
  const iframeBaseUrl = "http://localhost:3001/d-solo/sentinel-overview/sentinel-overview?orgId=1&theme=dark&panelId=";

  useEffect(() => {
    const saved = window.localStorage.getItem("sentinel-dashboard-notes");
    if (saved) setNotes(saved);
  }, []);

  const handleNoteChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNotes(e.target.value);
    window.localStorage.setItem("sentinel-dashboard-notes", e.target.value);
  }

  return (
    <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-emerald-500/30 overflow-hidden relative font-sans">
      {/* Visual Identity Layer - Sovereign Ops Matrix v2.1 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-emerald-500/10 blur-[150px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-cyan-500/10 blur-[150px] rounded-full animate-pulse" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-30 brightness-150 contrast-125 pointer-events-none" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,23,0)_0px,rgba(52,211,153,0.01)_1px,rgba(52,211,153,0.01)_2px)] bg-[size:100%_40px] pointer-events-none" />
      </div>

      <div className="relative z-10 mx-auto max-w-[1800px] px-8 py-10">
        <header className="flex flex-col xl:flex-row items-end justify-between gap-12 mb-16">
          <div className="flex-1">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4 mb-4"
            >
              <div className="h-[3px] w-12 bg-gradient-to-r from-emerald-500 to-transparent rounded-full" />
              <p className="text-[10px] uppercase tracking-[0.6em] text-emerald-400 font-black">Sentinel Operations OS // Control Node 0x8F92A</p>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
              Operational <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-white to-cyan-500">Ops Matrix</span>
            </h1>

            <div className="flex flex-wrap gap-8 mt-8 items-center">
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full animate-pulse ${status?.system === 'CRITICAL' ? 'bg-rose-500' : 'bg-emerald-500'}`} />
                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">
                  System Health: <span className={status?.system === 'CRITICAL' ? 'text-rose-400' : 'text-emerald-400'}>{status?.system || "STABLE"}</span>
                </p>
              </div>
              <div className="h-4 w-[1px] bg-white/10 hidden md:block" />
              <div className="flex items-center gap-3">
                <Clock className="w-4 h-4 text-cyan-400" />
                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">
                  Temporal Uptime: <span className="text-white">{status ? (status.uptime / 3600).toFixed(1) + "h" : "---"}</span>
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full xl:w-auto">
            <header-metric label="CPU PRESSURE" value={status ? `${Math.round(parseFloat(status.cpu))}%` : "-"} color="text-emerald-400" />
            <header-metric label="MEM LOAD" value={status ? `${Math.round(parseFloat(status.memory))}%` : "-"} color="text-cyan-400" />
            <header-metric label="NET RX" value={status ? `${(parseInt(status.network?.rx_bytes_sec || "0") / 1024).toFixed(0)} KB/s` : "-"} color="text-amber-400" />
            <header-metric label="NET TX" value={status ? `${(parseInt(status.network?.tx_bytes_sec || "0") / 1024).toFixed(0)} KB/s` : "-"} color="text-purple-400" />
          </div>
        </header>

        {/* Operational Statistics Grid */}
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          <OperationalCard label="CPU COMPUTE" value={status ? `${status.cpu}%` : "0%"} icon={<Cpu />} color="emerald" trend="Nominal" />
          <OperationalCard label="MEMORY MESH" value={status ? `${status.memory}%` : "0%"} icon={<Database />} color="cyan" trend="Synchronized" />
          <OperationalCard label="DATA INGRESS" value={status?.network?.rx_bytes_sec || "0"} icon={<Network />} color="amber" trend="High Flow" />
          <OperationalCard label="DATA EGRESS" value={status?.network?.tx_bytes_sec || "0"} icon={<Globe />} color="purple" trend="Authenticated" />
        </section>

        {/* Direct Telemetry Matrix (Grafana Integration) */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
          <GrafanaBox id="6" title="Infrastructure CPU History" color="border-emerald-500/20" baseUrl={iframeBaseUrl} />
          <GrafanaBox id="8" title="Resource Memory Matrix" color="border-cyan-500/20" baseUrl={iframeBaseUrl} />
        </section>

        {/* Real-time Diagnostics Stream */}
        <section className="mb-16 rounded-[40px] border border-white/5 bg-[#050814]/40 backdrop-blur-3xl overflow-hidden h-[650px] relative group shadow-2xl transition-all hover:border-white/10">
          <div className="absolute top-8 left-10 z-10 flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 rounded-2xl text-emerald-400 border border-emerald-500/20 shadow-[0_0_20px_rgba(52,211,153,0.2)]">
              <Activity size={24} className="animate-pulse" />
            </div>
            <div>
              <h3 className="text-xl font-black text-white uppercase italic tracking-tighter leading-none">Diagnostic Stream</h3>
              <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest mt-1">Loki Neural Log Pipeline // Ring-0 Capture</p>
            </div>
          </div>
          <iframe
            src={`${iframeBaseUrl}5`}
            width="100%"
            height="100%"
            frameBorder="0"
            className="opacity-70 group-hover:opacity-100 transition-opacity duration-1000 grayscale hover:grayscale-0"
          />
          <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-[#020617] via-transparent to-transparent opacity-40" />
        </section>

        {/* Commander Intelligence Layer */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 bg-slate-900/40 backdrop-blur-3xl rounded-[40px] border border-white/5 p-10 flex flex-col group relative overflow-hidden shadow-2xl">
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
              <Terminal size={64} />
            </div>
            <div className="flex items-center gap-4 mb-10">
              <div className="p-3 bg-emerald-500/10 rounded-2xl text-emerald-400 border border-emerald-500/20">
                <Terminal size={20} />
              </div>
              <div>
                <h3 className="text-sm font-black text-white uppercase italic tracking-widest leading-none">Command Notes</h3>
                <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mt-1">Encrypted Local Persistence</p>
              </div>
            </div>
            <textarea
              className="w-full h-64 bg-black/40 border border-white/5 rounded-3xl p-6 text-sm text-gray-300 focus:border-emerald-500/40 focus:outline-none resize-none font-mono placeholder:text-gray-800 transition-all selection:bg-emerald-500/30"
              placeholder="Capture cognitive operational insights..."
              value={notes}
              onChange={handleNoteChange}
            />
          </div>

          <div className="lg:col-span-2 bg-emerald-500/5 backdrop-blur-3xl rounded-[40px] border border-emerald-500/10 p-10 flex flex-col justify-center items-center text-center relative overflow-hidden group shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent pointer-events-none opacity-50" />
            <div className="p-6 bg-emerald-500/10 rounded-full mb-8 text-emerald-400 border border-emerald-400/20 shadow-[0_0_30px_rgba(52,211,153,0.3)] animate-pulse">
              <ShieldAlert size={48} />
            </div>
            <h3 className="text-4xl font-black text-white uppercase tracking-tighter italic mb-6">Operations Integrity: Verified</h3>
            <p className="text-gray-500 max-w-2xl leading-relaxed text-base font-bold italic">
              All infrastructure subsystems are currently oscillating in perfect synchronization with the Sovereign Core. Neural telemetry reports nominal latency across all ingress/egress vectors. Command consensus is maintained.
            </p>

            <div className="mt-12 flex flex-wrap justify-center gap-6">
              <SourceBadge label="Prometheus" color="emerald" />
              <SourceBadge label="Loki" color="cyan" />
              <SourceBadge label="Tempo" color="purple" />
              <SourceBadge label="TruthSync" color="amber" />
            </div>
          </div>
        </section>
      </div>

      <footer className="mt-20 py-12 border-t border-white/5 bg-black/40 backdrop-blur-md relative z-10 text-[10px] font-black text-gray-600 uppercase tracking-[0.4em] italic">
        <div className="max-w-[1800px] mx-auto px-8 flex justify-between items-center">
          <p>© 2026 Sentinel Operations // Enterprise Telemetry v2.1.2</p>
          <div className="flex gap-12">
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> INFRA: NOMINAL</span>
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-cyan-500" /> MESH: AUTHENTICATED</span>
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-purple-500" /> TRUTH: SYNC</span>
          </div>
        </div>
      </footer>
    </main>
  );
}

function OperationalCard({ label, value, icon, color, trend }: { label: string; value: string; icon: React.ReactNode; color: 'emerald' | 'cyan' | 'amber' | 'purple'; trend: string }) {
  const colors = {
    emerald: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/10',
    cyan: 'text-cyan-400 border-cyan-500/20 bg-cyan-500/10',
    amber: 'text-amber-400 border-amber-500/20 bg-amber-500/10',
    purple: 'text-purple-400 border-purple-500/20 bg-purple-500/10'
  };

  return (
    <div className="bg-slate-900/40 p-8 rounded-[35px] border border-white/5 backdrop-blur-3xl hover:bg-white/5 transition-all group overflow-hidden relative shadow-2xl hover:border-white/10">
      <div className="flex justify-between items-start mb-6">
        <div className={`p-4 rounded-2xl border ${colors[color]} group-hover:scale-110 transition-transform`}>
          {icon}
        </div>
        <div className={`text-[9px] font-black uppercase tracking-widest italic flex items-center gap-2 ${colors[color].split(' ')[0]}`}>
          <Activity size={10} /> {trend}
        </div>
      </div>
      <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-1 italic">{label}</p>
      <div className={`text-4xl font-black font-mono tracking-tighter italic text-white flex items-baseline gap-2`}>
        {value}
        <span className="text-xs text-gray-700 uppercase tracking-widest font-black">Live</span>
      </div>
      <div className="mt-6 flex gap-1">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className={`h-1 flex-1 rounded-full ${i < 8 ? colors[color].split(' ')[0].replace('text-', 'bg-') + ' opacity-50' : 'bg-white/5'}`} />
        ))}
      </div>
    </div>
  );
}

function SourceBadge({ label, color }: { label: string, color: 'emerald' | 'cyan' | 'purple' | 'amber' }) {
  const colors = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20'
  };
  return (
    <div className={`px-4 py-1.5 rounded-full border text-[10px] font-black uppercase tracking-widest italic ${colors[color]}`}>
      {label}
    </div>
  );
}

function GrafanaBox({ id, title, color, baseUrl }: { id: string; title: string; color: string; baseUrl: string }) {
  return (
    <div className={`rounded-[40px] border ${color} bg-[#050814]/40 overflow-hidden h-[450px] relative group transition-all hover:scale-[1.01] hover:border-white/20 shadow-2xl`}>
      <div className="absolute top-6 left-8 z-10 text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 bg-black/80 px-4 py-2 rounded-full backdrop-blur-md border border-white/5 italic">
        {title}
      </div>
      <iframe
        src={`${baseUrl}${id}`}
        width="100%"
        height="100%"
        frameBorder="0"
        className="opacity-60 group-hover:opacity-100 transition-opacity duration-700 grayscale hover:grayscale-0"
      />
    </div>
  );
}
