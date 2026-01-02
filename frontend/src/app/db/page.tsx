"use client";

import { useSentinelStatus } from "@/hooks/useSentinelStatus";
import { motion } from "framer-motion";
import { Database, Server, Zap, Shield, Activity, Terminal, Lock, RefreshCw, Cpu } from "lucide-react";

const StatCard = ({
  label,
  value,
  subtitle,
  color,
  icon: Icon,
}: {
  label: string;
  value: string;
  subtitle?: string;
  color: string;
  icon: any;
}) => {
  return (
    <motion.div
      whileHover={{ y: -5, scale: 1.02 }}
      className={`relative rounded-3xl border border-white/5 bg-slate-900/40 backdrop-blur-3xl p-6 overflow-hidden group shadow-2xl transition-all hover:border-white/10`}
    >
      <div className={`absolute top-0 right-0 w-24 h-24 blur-3xl opacity-10 rounded-full -mr-8 -mt-8 ${color.replace('text', 'bg')}`} />
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-2xl bg-white/5 border border-white/5 ${color}`}>
          <Icon size={18} />
        </div>
        <div className="flex flex-col items-end">
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 italic">Core Stream</span>
        </div>
      </div>
      <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1">{label}</p>
      <p className="text-3xl font-black text-white tracking-tighter italic leading-none">{value}</p>
      {subtitle && <p className="text-[9px] font-black text-gray-600 mt-2 uppercase tracking-widest italic">{subtitle}</p>}

      <div className="mt-6 h-[2.5px] w-full bg-white/5 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: "100%" }}
          transition={{ duration: 2, ease: "easeOut" }}
          className={`h-full ${color.replace('text', 'bg')} shadow-[0_0_10px_rgba(255,255,255,0.2)]`}
        />
      </div>
    </motion.div>
  );
};

export default function DatabasesPage() {
  const { status } = useSentinelStatus();
  const iframeBaseUrl = "http://localhost:3001/d-solo/sentinel-overview/sentinel-overview?orgId=1&theme=dark&panelId=";

  return (
    <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-cyan-500/30 overflow-hidden relative">
      {/* Background Aesthetic */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[30%] -left-[10%] w-[50%] h-[40%] bg-amber-500/5 blur-[150px] rounded-full animate-pulse" />
        <div className="absolute -bottom-[10%] right-[10%] w-[40%] h-[50%] bg-blue-500/5 blur-[150px] rounded-full animate-pulse" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 pointer-events-none" />
      </div>

      <div className="relative z-10 mx-auto max-w-[1700px] px-8 py-10">
        <header className="flex flex-col md:flex-row items-end justify-between gap-8 mb-16">
          <div className="flex-1">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4 mb-3"
            >
              <div className="h-[3px] w-12 bg-gradient-to-r from-amber-500 to-transparent rounded-full" />
              <p className="text-[10px] uppercase tracking-[0.6em] text-amber-500 font-black">Sentinel Data Ingress // Node v2.1</p>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
              Sovereign <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-white to-blue-500">Database Matrix</span>
            </h1>
            <p className="text-gray-500 mt-6 max-w-2xl font-bold uppercase tracking-widest text-[10px] italic">
              Real-time PostgreSQL transaction synchronization and Redis cache mesh orchestration.
            </p>
          </div>

          <div className="flex gap-4">
            <button className="px-6 py-3 rounded-2xl bg-white/5 border border-white/5 text-[10px] font-black uppercase tracking-widest hover:bg-white/10 transition-all flex items-center gap-3">
              <Terminal size={14} /> SQL Console
            </button>
            <button className="px-6 py-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[10px] font-black uppercase tracking-widest hover:bg-amber-500/20 transition-all flex items-center gap-3 shadow-[0_0_20px_rgba(245,158,11,0.1)]">
              <RefreshCw size={14} /> Full Optimization
            </button>
          </div>
        </header>

        <section className="grid gap-6 md:grid-cols-4 mb-12">
          <StatCard
            label="DB TRANSACTIONS"
            value={status ? `${status.db_transactions}` : "---"}
            color="text-amber-400"
            icon={Zap}
            subtitle="TPS / REAL-TIME FLOPS"
          />
          <StatCard
            label="INGRESS HEALTH"
            value={status ? status.system : "---"}
            color="text-emerald-400"
            icon={Shield}
            subtitle={status?.defense_level || "LEVEL 6 ALPHA"}
          />
          <StatCard
            label="ACTIVE THREATS"
            value={status ? `${status.active_threats}` : "---"}
            color="text-rose-500"
            icon={Lock}
            subtitle="ANOMALIES DETECTED"
          />
          <StatCard
            label="IO LATENCY"
            value={status ? status.ai_latency : "---"}
            color="text-purple-400"
            icon={Activity}
            subtitle="ENGINE RESPONSE TIME"
          />
        </section>

        <section className="grid gap-8 lg:grid-cols-12 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-12 group relative"
          >
            <div className="absolute -inset-[1px] bg-gradient-to-r from-amber-500/20 via-white/5 to-blue-500/20 rounded-[32px] blur-sm opacity-50 group-hover:opacity-100 transition-opacity" />
            <div className="relative rounded-[32px] border border-white/10 bg-black/80 overflow-hidden h-[600px] backdrop-blur-3xl shadow-2xl">
              <div className="absolute top-6 left-8 z-10 flex items-center gap-4">
                <div className="p-3 bg-amber-500/20 rounded-xl text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.3)]">
                  <Terminal size={18} />
                </div>
                <div>
                  <h3 className="text-xs font-black text-white uppercase tracking-widest italic">Infrastructure Logs Matrix</h3>
                  <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest italic">DB // REDIS // GRAFANA // LOKI STREAMS</p>
                </div>
              </div>
              <iframe
                src={`http://localhost:3001/explore?orgId=1&left=%7B%22datasource%22:%22Loki%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22%7Bcontainer%3D~%5C%22sentinel-truth.*%7Csentinel-grafana%7Csentinel-loki%5C%22%7D%22%7D%5D,%22range%22:%7B%22from%22:%22now-1h%22,%22to%22:%22now%22%7D%7D`}
                width="100%"
                height="100%"
                frameBorder="0"
                className="opacity-80 group-hover:opacity-100 transition-all duration-1000 brightness-110 saturate-150 contrast-125 invert-[0.05]"
              ></iframe>
            </div>
          </motion.div>
        </section>

        <section className="grid gap-8 md:grid-cols-2 lg:grid-cols-12 mb-12">
          {/* CPU Impact */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-6 group relative"
          >
            <div className="relative rounded-[32px] border border-white/5 bg-slate-900/40 overflow-hidden h-[400px] backdrop-blur-3xl p-8 shadow-2xl">
              <div className="flex items-center gap-4 mb-8">
                <div className="p-2 bg-pink-500/20 rounded-lg text-pink-500">
                  <Cpu size={16} />
                </div>
                <h3 className="text-[10px] font-black text-white uppercase tracking-widest italic">IO Processor Load</h3>
              </div>
              <iframe
                src={`${iframeBaseUrl}6&from=now-6h&to=now`}
                width="100%"
                height="280"
                frameBorder="0"
                className="opacity-70 group-hover:opacity-100 transition-all brightness-110"
              ></iframe>
            </div>
          </motion.div>

          {/* Memory Impact */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-6 group relative"
          >
            <div className="relative rounded-[32px] border border-white/5 bg-slate-900/40 overflow-hidden h-[400px] backdrop-blur-3xl p-8 shadow-2xl">
              <div className="flex items-center gap-4 mb-8">
                <div className="p-2 bg-blue-500/20 rounded-lg text-blue-500">
                  <Activity size={16} />
                </div>
                <h3 className="text-[10px] font-black text-white uppercase tracking-widest italic">Shared Pool Saturation</h3>
              </div>
              <iframe
                src={`${iframeBaseUrl}8&from=now-6h&to=now`}
                width="100%"
                height="280"
                frameBorder="0"
                className="opacity-70 group-hover:opacity-100 transition-all brightness-110"
              ></iframe>
            </div>
          </motion.div>
        </section>

        {/* Diagnostic Footer */}
        <section className="mt-12">
          <motion.div
            whileHover={{ scale: 1.01 }}
            className="rounded-[40px] border border-white/5 bg-white/2 backdrop-blur-3xl p-10 shadow-2xl relative overflow-hidden group"
          >
            <div className="absolute top-0 left-0 w-2 h-full bg-gradient-to-b from-amber-500 via-transparent to-blue-500" />
            <h3 className="text-2xl font-black text-white mb-8 flex items-center gap-4 italic uppercase tracking-tighter">
              <Server className="w-8 h-8 text-amber-500" />
              Sovereign Data Infrastructure
            </h3>
            <div className="grid md:grid-cols-3 gap-8">
              <InfrastructureItem icon={<Database className="text-blue-400" />} label="POSTGRES_CORE" value="truth-db.sentinel.internal:5432" status="SYNC" />
              <InfrastructureItem icon={<Zap className="text-amber-400" />} label="REDIS_L2_CACHE" value="truth-redis.sentinel.internal:6379" status="HOT" />
              <InfrastructureItem icon={<Shield className="text-emerald-400" />} label="VALT_MESH" value="mTLS Enforced // AES-256-GCM" status="SECURE" />
            </div>
          </motion.div>
        </section>
      </div>

      <footer className="mt-20 py-10 border-t border-white/5 bg-black/40 backdrop-blur-md relative z-10">
        <div className="max-w-[1700px] mx-auto px-8 flex justify-between items-center text-[10px] font-black text-gray-600 uppercase tracking-[0.4em] italic leading-none">
          <p>© 2026 Sentinel Data Systems // PostgreSQL v16.1 // Redis v7.2</p>
          <div className="flex gap-12">
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-amber-500" /> QUORUM: ACTIVE</span>
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" /> PERSISTENCE: DURABLE</span>
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> INTEGRITY: VERIFIED</span>
          </div>
        </div>
      </footer>
    </main>
  );
}

function InfrastructureItem({ icon, label, value, status }: { icon: React.ReactNode; label: string; value: string; status: string }) {
  return (
    <div className="bg-black/40 border border-white/5 rounded-3xl p-6 hover:border-white/20 transition-all">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="p-1.5 bg-white/5 rounded-lg">{icon}</span>
          <span className="text-[10px] font-black text-white tracking-widest">{label}</span>
        </div>
        <span className="text-[8px] font-black text-gray-500 uppercase tracking-[0.2em]">{status}</span>
      </div>
      <p className="text-xs font-mono text-gray-400 tracking-tighter truncate">{value}</p>
    </div>
  );
}
