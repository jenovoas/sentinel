"use client";

import { Activity, Zap, Database, Lock, BarChart3, Brain, Terminal, ShieldAlert, Sparkles, BrainCircuit, Network, Cpu } from "lucide-react";
import { useSentinelStatus } from "@/hooks/useSentinelStatus";
import { SovereignSearchInput } from "@/components/SovereignSearchInput";
import { CognitiveProjection } from "@/components/sentinel/CognitiveProjection";
import { ResonanceRateCard } from "@/components/sentinel/ResonanceRateCard";
import { GoldTruthFeed } from "@/components/sentinel/GoldTruthFeed";
import { OracleConsole } from "@/components/sentinel/OracleConsole";
import { motion } from "framer-motion";
import { useState } from "react";
import { SoulGate } from "@/components/security/SoulGate";

export default function LandingPage() {
  const { status } = useSentinelStatus();
  const [authData, setAuthData] = useState<any>(null);
  const iframeBaseUrl = "http://localhost:3001/d-solo/sentinel-overview/sentinel-overview?orgId=1&theme=dark&panelId=";

  if (!authData) {
    return (
      <main className="min-h-screen bg-[#020617] flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none" />
        <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-cyan-500/5 blur-[180px] rounded-full animate-pulse pointer-events-none" />

        <div className="relative z-10 w-full">
          <SoulGate onAuthenticationComplete={(sig) => {
            setAuthData(sig);
            localStorage.setItem('sentinel_soul_role', sig.role);
            localStorage.setItem('sentinel_soul_id', sig.user_id);
          }} />
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-cyan-500/30 relative overflow-hidden font-sans">
      {/* Visual Identity Layer: Advanced Intelligence Matrix */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-cyan-500/10 blur-[180px] rounded-full animate-pulse" />
        <div className="absolute top-[20%] right-[-10%] w-[50%] h-[70%] bg-purple-500/10 blur-[180px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] left-[20%] w-[60%] h-[40%] bg-emerald-500/5 blur-[180px] rounded-full" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-30 brightness-150 contrast-125 pointer-events-none" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,23,0)_0px,rgba(34,211,238,0.01)_1px,rgba(34,211,238,0.01)_2px)] bg-[size:100%_40px] pointer-events-none" />
      </div>

      <div className="relative z-10 mx-auto max-w-[1800px] px-8 py-10">
        {/* Unified Command Header: Cognitive Intelligence Gateway */}
        <header className="flex flex-col xl:flex-row items-start justify-between gap-12 mb-20">
          <div className="flex-1">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <div className="h-[3px] w-12 bg-gradient-to-r from-cyan-500 via-purple-500 to-transparent rounded-full" />
              <p className="text-[10px] uppercase tracking-[0.6em] text-cyan-400 font-black">Sentinel Sovereign OS // Cognitive Intelligence v2.1.0</p>
            </motion.div>

            <h1 className="text-3xl md:text-5xl font-black tracking-tighter text-white uppercase italic leading-none select-none">
              Command <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-white to-purple-500">Tower</span> Matrix
            </h1>

            <div className="mt-10 w-full max-w-4xl relative group">
              <div className="absolute -inset-4 bg-cyan-500/5 blur-3xl rounded-[40px] opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
              <SovereignSearchInput />
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full xl:w-auto mt-8 xl:mt-0">
            <LandingHeaderMetric label="System Health" value={status?.system || "STABLE"} color="text-emerald-400" pulse />
            <LandingHeaderMetric label="Neural Depth" value="LEVEL 9" color="text-cyan-400" />
            <LandingHeaderMetric label="Uptime" value={`${status?.uptime ? (status.uptime / 3600).toFixed(1) : "99.9"}h`} color="text-white" />
            <LandingHeaderMetric label="Consensus" value="99.99%" color="text-purple-400" />
          </div>
        </header>

        {/* Global Intelligence Layer: Bidirectional Feedback */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-10 mb-20">

          {/* Main Projection Field: The Cognitive Sight */}
          <div className="lg:col-span-8 flex flex-col gap-10">
            <div className="relative rounded-[40px] border border-white/5 bg-[#050814]/40 backdrop-blur-3xl p-1 overflow-hidden group shadow-2xl transition-all hover:border-white/10">
              <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent" />
              <div className="p-8 pb-0 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-cyan-500/10 rounded-2xl text-cyan-400 border border-cyan-500/20">
                    <BrainCircuit size={24} />
                  </div>
                  <div>
                    <h3 className="text-xl font-black text-white uppercase italic tracking-tighter leading-none">Neural Projection</h3>
                    <p className="text-[10px] font-black text-cyan-500 uppercase tracking-widest mt-1">Real-time System Mapping</p>
                  </div>
                </div>
                <div className="hidden md:flex gap-4">
                  <StatusBadge label="SYNCING" color="emerald" />
                  <StatusBadge label="ENCRYPTED" color="cyan" />
                </div>
              </div>
              <CognitiveProjection />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
              <ResonanceRateCard />
              <div className="grid grid-cols-2 gap-4">
                <AdaptiveMetric icon={<Cpu size={20} />} label="CPU Load" value={`${status?.cpu || 0}%`} trend="nominal" color="text-cyan-400" />
                <AdaptiveMetric icon={<Activity size={20} />} label="Memory" value={`${status?.memory || 0}%`} trend="stable" color="text-emerald-400" />
                <AdaptiveMetric icon={<Database size={20} />} label="Transactions" value={status?.db_transactions || 0} trend="active" color="text-amber-400" />
                <AdaptiveMetric icon={<Network size={20} />} label="Network Nodes" value={status?.network_nodes || 128} trend="sync" color="text-purple-400" />
              </div>
            </div>
          </div>

          {/* Oracle Intelligence: Advanced Query Interface */}
          <div className="lg:col-span-4 flex flex-col gap-10 h-full">
            <div className="flex-1 min-h-[600px]">
              <OracleConsole />
            </div>

            <div className="bg-[#050814]/60 border border-white/5 rounded-[40px] p-10 backdrop-blur-3xl relative overflow-hidden group shadow-2xl transition-all hover:border-rose-500/20">
              <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                <ShieldAlert size={64} className="text-rose-500" />
              </div>
              <div className="flex items-center gap-4 mb-8">
                <div className="p-3 bg-rose-500/10 rounded-2xl text-rose-500 border border-rose-500/20">
                  <ShieldAlert size={20} />
                </div>
                <div>
                  <h3 className="text-sm font-black text-white uppercase italic tracking-widest leading-none">Active Mitigations</h3>
                  <p className="text-[9px] font-black text-rose-500/60 uppercase tracking-widest mt-1 italic">Real-time Shield Matrix</p>
                </div>
              </div>
              <div className="space-y-4">
                <MitigationProtocol pid="8821" process="synapse_ingress_protect" status="SHIELDED" />
                <MitigationProtocol pid="1009" process="unauth_neural_link" status="BLOCKED" />
                <MitigationProtocol pid="442" process="adaptive_drift_scan" status="STABLE" />
              </div>
            </div>
          </div>
        </section>

        {/* Neural Telemetry streams (Deep Observability) */}
        <section className="mb-20">
          <div className="flex items-center gap-6 mb-12">
            <div className="p-3 bg-orange-500/10 rounded-2xl text-orange-400 border border-orange-500/20">
              <Terminal size={24} />
            </div>
            <div>
              <h2 className="text-3xl font-black text-white uppercase tracking-tighter italic leading-none">Neural Streams</h2>
              <div className="flex items-center gap-3 mt-1">
                <div className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
                <p className="text-[10px] font-black text-orange-500 uppercase tracking-widest italic">Live Telemetry Visualization Mesh</p>
              </div>
            </div>
            <div className="h-[1px] flex-1 bg-white/5 ml-8" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
            <NeuralPanel id="6" title="Kernel Synaptic Pressure" color="border-cyan-500/20" baseUrl={iframeBaseUrl} />
            <NeuralPanel id="8" title="Synthetic Memory Matrix" color="border-purple-500/20" baseUrl={iframeBaseUrl} />
            <NeuralPanel id="5" title="Auditd Cognitive Log" color="border-orange-500/20" baseUrl={iframeBaseUrl} />
          </div>
        </section>

        {/* Truth Verification Matrix */}
        <section className="mb-20">
          <div className="flex items-center gap-6 mb-12">
            <div className="p-3 bg-emerald-500/10 rounded-2xl text-emerald-400 border border-emerald-500/20">
              <BarChart3 size={24} />
            </div>
            <div>
              <h2 className="text-3xl font-black text-white uppercase tracking-tighter italic leading-none">Truth Feed</h2>
              <div className="flex items-center gap-3 mt-1">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest italic">Verified Security Events</p>
              </div>
            </div>
            <div className="h-[1px] flex-1 bg-white/5 ml-8" />
          </div>
          <GoldTruthFeed />
        </section>

        {/* Ingress Portal Matrix */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          <PortalButton icon={<Lock />} title="Secure Workspace" desc="High-isolation secure environment v2.1" href="/dashboard" color="cyan" />
          <PortalButton icon={<Activity />} title="Ops Matrix" desc="Real-time Prometheus telemetry streams" href="/dash-op" color="emerald" />
          <PortalButton icon={<Brain />} title="Cortex Core" desc="Advanced AI Intelligence Engine" href="/cortex" color="purple" />
        </div>
      </div>

      <footer className="mt-40 py-16 border-t border-white/5 bg-black/40 backdrop-blur-md relative z-10 text-[10px] font-black text-gray-600 uppercase tracking-[0.4em] italic">
        <div className="max-w-[1800px] mx-auto px-8 flex justify-between items-center">
          <p>© 2026 Sentinel Sovereign // Cognitive Intelligence Platform // 0x8F92A</p>
          <div className="flex gap-16">
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> KERNEL: ACTIVE</span>
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse" /> SYNC: ESTABLISHED</span>
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" /> INTELLIGENCE: ONLINE</span>
          </div>
        </div>
      </footer>
    </main>
  );
}

function LandingHeaderMetric({ label, value, color, pulse = false }: { label: string; value: string | number; color: string; pulse?: boolean }) {
  return (
    <div className="bg-slate-900/40 p-6 px-10 rounded-[30px] border border-white/5 backdrop-blur-3xl hover:bg-white/10 transition-all group overflow-hidden relative shadow-2xl">
      <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-10 transition-opacity">
        <Sparkles size={16} className={color} />
      </div>
      <p className="text-[9px] text-gray-500 uppercase font-black tracking-widest mb-2 italic select-none">{label}</p>
      <div className={`text-3xl font-black font-mono tracking-tighter flex items-center gap-4 italic ${color}`}>
        {pulse && <span className="relative flex h-2.5 w-2.5">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${color.replace('text-', 'bg-')}`}></span>
          <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${color.replace('text-', 'bg-')}`}></span>
        </span>}
        {value}
      </div>
    </div>
  );
}

function AdaptiveMetric({ icon, label, value, trend, color }: { icon: React.ReactNode; label: string; value: string | number; trend: string; color: string }) {
  return (
    <div className="bg-[#050814]/60 backdrop-blur-3xl border border-white/5 rounded-[30px] p-8 hover:bg-white/5 hover:border-white/10 transition-all group relative overflow-hidden shadow-2xl">
      <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
        {icon}
      </div>
      <p className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-3 italic leading-none">{label}</p>
      <div className="text-4xl font-black font-mono text-white tracking-widest mb-3 italic">
        {value}
      </div>
      <div className={`text-[9px] font-black uppercase tracking-tighter flex items-center gap-2 italic ${color}`}>
        <Activity size={10} />
        {trend}
      </div>
    </div>
  );
}

function MitigationProtocol({ pid, process, status }: { pid: string; process: string; status: string }) {
  return (
    <div className="flex items-center justify-between p-4 rounded-2xl bg-black/40 border border-white/5 group hover:border-rose-500/30 transition-all shadow-inner">
      <div className="flex items-center gap-4 font-mono">
        <span className="text-[10px] text-gray-700 font-black">[{pid}]</span>
        <span className="text-xs text-white font-black uppercase tracking-tight italic">{process}</span>
      </div>
      <span className="text-[9px] font-black text-emerald-400 tracking-widest bg-emerald-500/5 px-2 py-1 rounded-full border border-emerald-500/10 italic">{status}</span>
    </div>
  );
}

function NeuralPanel({ id, title, color, baseUrl }: { id: string; title: string; color: string; baseUrl: string }) {
  return (
    <div className={`rounded-[40px] border ${color} bg-[#050814]/60 overflow-hidden h-[450px] relative group hover:scale-[1.02] transition-transform shadow-2xl`}>
      <div className="absolute top-6 left-8 z-10 text-[10px] font-black uppercase tracking-widest text-gray-600 bg-black/80 px-4 py-2 rounded-full backdrop-blur-md border border-white/10 italic">
        {title}
      </div>
      <iframe
        src={`${baseUrl}${id}`}
        width="100%"
        height="100%"
        frameBorder="0"
        className="opacity-50 group-hover:opacity-100 transition-opacity duration-1000 grayscale hover:grayscale-0"
      ></iframe>
      <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
    </div>
  );
}

function StatusBadge({ label, color }: { label: string, color: 'emerald' | 'cyan' }) {
  const colorClass = color === 'emerald' ? 'text-emerald-400 border-emerald-500/20 bg-emerald-500/10' : 'text-cyan-400 border-cyan-500/20 bg-cyan-500/10';
  return (
    <div className={`px-4 py-1 rounded-full border text-[9px] font-black uppercase tracking-widest italic leading-none flex items-center gap-2 ${colorClass}`}>
      <div className={`w-1 h-1 rounded-full animate-pulse ${color === 'emerald' ? 'bg-emerald-500' : 'bg-cyan-500'}`} />
      {label}
    </div>
  );
}

function PortalButton({ icon, title, desc, href, color }: { icon: React.ReactNode; title: string; desc: string; href: string, color: 'cyan' | 'emerald' | 'purple' }) {
  const accentColor = {
    cyan: 'text-cyan-400 border-cyan-500/20 bg-cyan-500/10 group-hover:bg-cyan-500/20',
    emerald: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/10 group-hover:bg-emerald-500/20',
    purple: 'text-purple-400 border-purple-500/20 bg-purple-500/10 group-hover:bg-purple-500/20'
  }[color];

  return (
    <a href={href} className="flex flex-col gap-6 p-10 rounded-[40px] border border-white/5 bg-[#050814]/40 backdrop-blur-3xl hover:bg-white/5 hover:border-white/10 transition-all group relative overflow-hidden shadow-2xl">
      <div className="absolute top-0 right-0 p-10 opacity-5 group-hover:opacity-10 transition-opacity">
        {icon}
      </div>
      <div className={`p-4 rounded-2xl w-fit transition-all group-hover:scale-110 border ${accentColor}`}>
        {icon}
      </div>
      <div>
        <h3 className="text-3xl font-black text-white uppercase tracking-tighter italic mb-2 leading-none">{title}</h3>
        <p className="text-[11px] text-gray-500 font-black uppercase tracking-widest leading-relaxed italic">{desc}</p>
      </div>
      <div className="mt-4 flex items-center gap-2 text-[9px] font-black text-cyan-500 uppercase tracking-widest italic opacity-0 group-hover:opacity-100 transition-opacity">
        <span>Establish neural link</span>
        <Zap size={10} className="animate-pulse" />
      </div>
    </a>
  );
}
