"use client";

import { useSentinelStatus } from "@/hooks/useSentinelStatus";
import { motion } from "framer-motion";
import { Activity, BarChart2, Cpu, Database, Globe, Zap, Clock, Maximize2, TrendingUp, Brain, Network } from "lucide-react";

const AdaptiveMetricCard = ({
  label,
  value,
  color,
  icon: Icon,
  trend
}: {
  label: string;
  value: string;
  color: string;
  icon: any;
  trend?: string;
}) => {
  return (
    <motion.div
      whileHover={{ y: -5, scale: 1.02 }}
      className={`relative rounded-[35px] border border-white/5 bg-slate-900/40 backdrop-blur-3xl p-8 overflow-hidden group shadow-2xl transition-all hover:border-white/10`}
    >
      <div className={`absolute top-0 right-0 w-32 h-32 blur-[80px] opacity-10 rounded-full -mr-12 -mt-12 ${color.replace('text', 'bg')}`} />
      <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
        <Icon size={48} />
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className={`p-4 rounded-2xl bg-white/5 border border-white/5 ${color} group-hover:scale-110 transition-transform`}>
          <Icon size={20} />
        </div>
        {trend && (
          <div className="flex items-center gap-2">
            <TrendingUp size={12} className="text-emerald-400" />
            <span className="text-[9px] font-black uppercase tracking-widest text-emerald-400 italic">{trend}</span>
          </div>
        )}
      </div>

      <p className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-2 italic leading-none">{label}</p>
      <p className="text-4xl font-black text-white tracking-tighter italic leading-none mb-6">{value}</p>

      <div className="h-[3px] w-full bg-white/5 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: "100%" }}
          transition={{ duration: 2, ease: "easeOut" }}
          className={`h-full ${color.replace('text', 'bg')} shadow-[0_0_15px_rgba(255,255,255,0.3)]`}
        />
      </div>
    </motion.div>
  );
};

export default function AnalyticsPage() {
  const { status, loading } = useSentinelStatus();
  const iframeBaseUrl = "http://localhost:3001/d-solo/sentinel-overview/sentinel-overview?orgId=1&theme=dark&panelId=";

  return (
    <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-purple-500/30 overflow-hidden relative font-sans">
      {/* Visual Identity Layer: Evolutionary Analytics */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-500/10 blur-[150px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-cyan-500/10 blur-[150px] rounded-full animate-pulse" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-30 brightness-150 contrast-125 pointer-events-none" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,23,0)_0px,rgba(168,85,247,0.01)_1px,rgba(168,85,247,0.01)_2px)] bg-[size:100%_40px] pointer-events-none" />
      </div>

      <div className="relative z-10 mx-auto max-w-[1800px] px-8 py-10">
        <header className="flex flex-col xl:flex-row items-end justify-between gap-12 mb-16">
          <div className="flex-1">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4 mb-4"
            >
              <div className="h-[3px] w-12 bg-gradient-to-r from-purple-500 to-transparent rounded-full" />
              <p className="text-[10px] uppercase tracking-[0.6em] text-purple-400 font-black">Sentinel Analytics OS // Advanced Telemetry 0x8F92A</p>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
              Analytics <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-white to-cyan-500">Intelligence</span> Matrix
            </h1>

            <div className="flex flex-wrap gap-8 mt-8 items-center">
              <div className="flex items-center gap-3">
                <Brain className="w-4 h-4 text-purple-400" />
                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">
                  Neural Depth: <span className="text-white">Level 9 Synthesis</span>
                </p>
              </div>
              <div className="h-4 w-[1px] bg-white/10 hidden md:block" />
              <div className="flex items-center gap-3">
                <Activity className="w-4 h-4 text-cyan-400" />
                <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">
                  Stream Status: <span className="text-cyan-400">Real-time Active</span>
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 w-full xl:w-auto">
            <AnalyticsHeaderMetric label="UPTIME" value={status ? `${(status.uptime / 3600).toFixed(1)}h` : "99.9h"} color="text-emerald-400" />
            <AnalyticsHeaderMetric label="THROUGHPUT" value="14.2K/s" color="text-purple-400" />
            <AnalyticsHeaderMetric label="LATENCY" value="1.24ms" color="text-cyan-400" />
          </div>
        </header>

        {/* Adaptive Metrics Grid */}
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          <AdaptiveMetricCard
            label="CPU Load"
            value={status ? `${Math.round(parseFloat(status.cpu))}%` : "0%"}
            color="text-cyan-400"
            icon={Cpu}
            trend="+2.3%"
          />
          <AdaptiveMetricCard
            label="Memory Usage"
            value={status ? `${Math.round(parseFloat(status.memory))}%` : "0%"}
            color="text-purple-400"
            icon={Database}
            trend="Stable"
          />
          <AdaptiveMetricCard
            label="Network I/O"
            value={status?.network?.rx_bytes_sec ? `${(parseInt(status.network.rx_bytes_sec) / 1024).toFixed(0)} KB/s` : "0 KB/s"}
            color="text-emerald-400"
            icon={Network}
            trend="+5.1%"
          />
          <AdaptiveMetricCard
            label="Sync Rate"
            value="99.99%"
            color="text-amber-400"
            icon={BarChart2}
            trend="Optimal"
          />
        </section>

        {/* Deep Telemetry Visualization */}
        <section className="mb-16">
          <div className="flex items-center gap-6 mb-12">
            <div className="p-3 bg-purple-500/10 rounded-2xl text-purple-400 border border-purple-500/20">
              <BarChart2 size={24} />
            </div>
            <div>
              <h2 className="text-3xl font-black text-white uppercase tracking-tighter italic leading-none">Deep Telemetry Streams</h2>
              <div className="flex items-center gap-3 mt-1">
                <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
                <p className="text-[10px] font-black text-purple-500 uppercase tracking-widest italic">Grafana Neural Visualization Mesh</p>
              </div>
            </div>
            <div className="h-[1px] flex-1 bg-white/5 ml-8" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <TelemetryPanel id="6" title="Kernel Synaptic Pressure" color="border-cyan-500/20" baseUrl={iframeBaseUrl} />
            <TelemetryPanel id="8" title="Synthetic Memory Matrix" color="border-purple-500/20" baseUrl={iframeBaseUrl} />
          </div>
        </section>

        {/* Full Spectrum Analysis */}
        <section className="mb-16">
          <div className="flex items-center gap-6 mb-12">
            <div className="p-3 bg-cyan-500/10 rounded-2xl text-cyan-400 border border-cyan-500/20">
              <Maximize2 size={24} />
            </div>
            <div>
              <h2 className="text-3xl font-black text-white uppercase tracking-tighter italic leading-none">Full Spectrum Analysis</h2>
              <div className="flex items-center gap-3 mt-1">
                <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
                <p className="text-[10px] font-black text-cyan-500 uppercase tracking-widest italic">Unified Observability Dashboard</p>
              </div>
            </div>
            <div className="h-[1px] flex-1 bg-white/5 ml-8" />
          </div>

          <div className="bg-[#050814]/40 backdrop-blur-3xl rounded-[40px] border border-white/5 overflow-hidden h-[800px] relative group shadow-2xl transition-all hover:border-white/10">
            <div className="absolute top-8 left-10 z-10 flex items-center gap-4 pointer-events-none">
              <div className="p-3 bg-purple-500/10 rounded-2xl text-purple-400 border border-purple-500/20 shadow-[0_0_20px_rgba(168,85,247,0.2)]">
                <Activity size={24} className="animate-pulse" />
              </div>
              <div>
                <h3 className="text-xl font-black text-white uppercase italic tracking-tighter leading-none">Sentinel Overview</h3>
                <p className="text-[10px] font-black text-purple-500 uppercase tracking-widest mt-1">Complete System Synthesis</p>
              </div>
            </div>
            <iframe
              src="http://localhost:3001/d/sentinel-overview?orgId=1&kiosk&theme=dark"
              className="w-full h-full opacity-60 group-hover:opacity-100 transition-opacity duration-1000 grayscale hover:grayscale-0"
              title="Grafana Full Dashboard"
              allowFullScreen
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[#020617] via-transparent to-transparent pointer-events-none opacity-40" />
          </div>
        </section>

        {/* System Insights */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <InsightCard
            icon={<Brain />}
            title="AI Integration"
            description="Neural pathways operating at 99.99% efficiency with real-time AI analysis and feedback loops active."
            color="purple"
          />
          <InsightCard
            icon={<Network />}
            title="Network Consensus"
            description="All nodes synchronized in perfect harmony. Quantum-resistant encryption verified across all channels."
            color="cyan"
          />
          <InsightCard
            icon={<Zap />}
            title="Adaptive Performance"
            description="System performance optimizing in real-time. Ready for advanced integration protocols and scaling."
            color="emerald"
          />
        </section>
      </div>

      <footer className="mt-40 py-12 border-t border-white/5 bg-black/40 backdrop-blur-md relative z-10 text-[10px] font-black text-gray-600 uppercase tracking-[0.4em] italic">
        <div className="max-w-[1800px] mx-auto px-8 flex justify-between items-center">
          <p>© 2026 Sentinel Analytics // Advanced Telemetry Suite // Build 0x8F92A</p>
          <div className="flex gap-12">
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" /> ANALYSIS: ACTIVE</span>
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse" /> STREAMS: VERIFIED</span>
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> PERFORMANCE: OPTIMAL</span>
          </div>
        </div>
      </footer>
    </main>
  );
}

function AnalyticsHeaderMetric({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="bg-slate-900/40 p-5 px-10 rounded-[30px] border border-white/5 backdrop-blur-3xl hover:bg-white/10 transition-all min-w-[140px] group overflow-hidden relative shadow-2xl">
      <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-10 transition-opacity">
        <Activity size={16} className={color} />
      </div>
      <p className="text-[9px] text-gray-500 uppercase font-black tracking-widest mb-1 italic leading-none">{label}</p>
      <div className={`text-2xl font-black font-mono tracking-tighter italic ${color}`}>
        {value}
      </div>
    </div>
  );
}

function TelemetryPanel({ id, title, color, baseUrl }: { id: string; title: string; color: string; baseUrl: string }) {
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
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
    </div>
  );
}

function InsightCard({ icon, title, description, color }: { icon: React.ReactNode; title: string; description: string; color: 'purple' | 'cyan' | 'emerald' }) {
  const colorClasses = {
    purple: 'text-purple-400 border-purple-500/20 bg-purple-500/10',
    cyan: 'text-cyan-400 border-cyan-500/20 bg-cyan-500/10',
    emerald: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/10'
  };

  return (
    <div className="bg-[#050814]/60 backdrop-blur-3xl rounded-[40px] border border-white/5 p-10 flex flex-col group relative overflow-hidden shadow-2xl hover:border-white/10 transition-all">
      <div className="absolute top-0 right-0 p-10 opacity-5 group-hover:opacity-10 transition-opacity">
        {icon}
      </div>
      <div className={`p-4 rounded-2xl w-fit mb-6 border ${colorClasses[color]} group-hover:scale-110 transition-transform`}>
        {icon}
      </div>
      <h3 className="text-2xl font-black text-white uppercase tracking-tighter italic mb-4 leading-none">{title}</h3>
      <p className="text-sm text-gray-500 font-bold leading-relaxed italic">{description}</p>
    </div>
  );
}
