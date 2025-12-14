/**
 * Operational Dashboard - Refactored with SOLID Principles
 * - Single Responsibility: Each component/hook has one purpose
 * - Open/Closed: Easy to extend without modifying existing code
 * - Liskov Substitution: Components follow consistent interfaces
 * - Interface Segregation: Components accept minimal required props
 * - Dependency Inversion: Depends on abstractions (hooks, types) not concrete implementations
 */

"use client";

import { useEffect, useMemo, useState } from "react";
import { useAnalytics, useDetailModal } from "@/hooks/useAnalytics";
import { StorageCard } from "@/components/StorageCard";
import { DetailModal } from "@/components/DetailModal";
import { NetworkCard } from "@/components/NetworkCard";

const API_PATH = "/api/v1/dashboard/status";

type DashboardData = {
  timestamp: string;
  db_health: { status: "healthy" | "unhealthy" };
  db_stats: {
    connections_total: number;
    connections_active: number;
    connections_idle: number;
    db_size_bytes: number;
    locks: number;
  };
  db_activity: Array<{
    pid: number;
    user: string;
    state: string;
    wait_event: string;
    duration_seconds: number;
    query: string;
  }>;
  system: {
    cpu_percent: number;
    mem_percent: number;
    mem_used: number;
    mem_total: number;
  };
  gpu: {
    gpu_percent: number;
    gpu_memory_percent: number;
    gpu_memory_used: number;
    gpu_memory_total: number;
    gpu_name: string;
    gpu_temp: number;
  };
  network: {
    net_bytes_sent: number;
    net_bytes_recv: number;
    net_packets_sent: number;
    net_packets_recv: number;
    wifi?: {
      ssid: string;
      signal: number;
      connected: boolean;
    };
  };
  repo_activity: {
    recent_commits: Array<{ hash: string; author: string; when: string; message: string }>;
    working_tree: string[];
    git_warning?: string;
  };
  admin_suggestions: string[];
  thresholds: {
    cpu_percent: number;
    mem_percent: number;
    connections: number;
    log_file: string;
  };
};

type FetchState = {
  loading: boolean;
  error?: string;
  data?: DashboardData;
};

type NotesState = {
  text: string;
};

// ============ Utility Functions ============

const formatBytes = (bytes: number) => {
  if (!Number.isFinite(bytes)) return "-";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** i;
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[i]}`;
};

const formatDuration = (seconds: number) => {
  if (!Number.isFinite(seconds)) return "-";
  if (seconds < 60) return `${seconds.toFixed(seconds >= 10 ? 0 : 1)}s`;
  const minutes = seconds / 60;
  if (minutes < 60) return `${minutes.toFixed(minutes >= 10 ? 0 : 1)}m`;
  const hours = minutes / 60;
  return `${hours.toFixed(hours >= 10 ? 0 : 1)}h`;
};

// ============ Components ============

const CircularStat = ({
  value,
  label,
  hint,
  color,
  onClick,
}: {
  value: number;
  label: string;
  hint?: string;
  color: string;
  onClick?: () => void;
}) => {
  const safe = Number.isFinite(value) ? Math.max(0, Math.min(value, 100)) : 0;
  return (
    <div
      onClick={onClick}
      className="group rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(56,189,248,0.4)] flex items-center gap-4 transition-all duration-300 hover:border-white/20 hover:shadow-[0_30px_90px_-40px_rgba(56,189,248,0.6)] hover:scale-[1.02] cursor-pointer"
    >
      <div
        className="relative h-20 w-20 rounded-full grid place-items-center transition-transform duration-300 group-hover:scale-110"
        style={{ background: `conic-gradient(${color} ${safe}%, rgba(255,255,255,0.08) ${safe}% 100%)` }}
      >
        <div className="h-14 w-14 rounded-full bg-slate-950/80 grid place-items-center text-white font-semibold text-lg transition-all duration-300 group-hover:bg-slate-900/90">
          {safe.toFixed(0)}%
        </div>
      </div>
      <div className="flex-1">
        <p className="text-sm text-gray-300 transition-colors duration-300 group-hover:text-white">{label}</p>
        <p className="text-xs text-gray-400 transition-colors duration-300 group-hover:text-gray-300">{hint}</p>
      </div>
    </div>
  );
};

const StatCard = ({
  label,
  value,
  hint,
  accent,
}: {
  label: string;
  value: string;
  hint?: string;
  accent: string;
}) => (
  <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(56,189,248,0.4)]">
    <p className="text-sm text-gray-300 mb-1">{label}</p>
    <p className="text-3xl font-semibold text-white tracking-tight">{value}</p>
    {hint ? <p className="text-xs text-gray-400 mt-1">{hint}</p> : null}
    <div className={`mt-3 h-1 rounded-full ${accent}`} />
  </div>
);

const Pill = ({ status }: { status: "healthy" | "unhealthy" }) => {
  const isHealthy = status === "healthy";
  return (
    <span
      className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
        isHealthy ? "bg-emerald-500/10 text-emerald-200" : "bg-rose-500/10 text-rose-200"
      }`}
    >
      <span className={`h-2 w-2 rounded-full ${isHealthy ? "bg-emerald-400" : "bg-rose-400"}`} />
      {isHealthy ? "Healthy" : "Unhealthy"}
    </span>
  );
};

// ============ Main Dashboard Component ============

export default function DashboardPage() {
  const [state, setState] = useState<FetchState>({ loading: true });
  const [notes, setNotes] = useState<NotesState>({ text: "" });
  const { history, anomalies, storage, normalizeNetworkPercent, anomaliesByMetric } = useAnalytics();
  const { modal, open, close } = useDetailModal();

  const API_REFRESH_MS = 15000;

  const load = async () => {
    try {
      setState((s) => ({ ...s, loading: true, error: undefined }));
      const res = await fetch(API_PATH, { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as DashboardData;
      setState({ loading: false, data: json });
    } catch (err) {
      setState({ loading: false, error: err instanceof Error ? err.message : "Error" });
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, API_REFRESH_MS);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const saved = window.localStorage.getItem("sentinel-dashboard-notes");
    if (saved) setNotes({ text: saved });
  }, []);

  useEffect(() => {
    window.localStorage.setItem("sentinel-dashboard-notes", notes.text);
  }, [notes]);

  const { data, loading, error } = state;
  const activeQueries = data?.db_activity ?? [];
  const repo = data?.repo_activity;

  const computeIssues = (data?: DashboardData) => {
    if (!data) return [] as string[];
    const issues: string[] = [];
    if (data.db_health.status !== "healthy")
      issues.push("DB reporta unhealthy (ver logs y conexión).");
    if (data.system.cpu_percent > data.thresholds.cpu_percent)
      issues.push(`CPU > umbral (${data.system.cpu_percent.toFixed(1)}%).`);
    if (data.system.mem_percent > data.thresholds.mem_percent)
      issues.push(`Memoria > umbral (${data.system.mem_percent.toFixed(1)}%).`);
    if (data.db_stats.connections_total > data.thresholds.connections)
      issues.push(`Conexiones totales altas (${data.db_stats.connections_total}).`);
    if (data.db_stats.locks > 5)
      issues.push(`Locks detectados (${data.db_stats.locks}); revisar bloqueos.`);
    if ((data.db_activity?.length ?? 0) > 0) {
      const longRunning = data.db_activity.find((q) => q.duration_seconds > 60);
      if (longRunning) issues.push("Hay queries activas (>60s); revisar qué bloquean.");
    }
    return issues;
  };

  const issues = computeIssues(data);

  const ratio = useMemo(() => {
    if (!data) return 0;
    return Math.min((data.db_stats.connections_active / (data.thresholds.connections || 1)) * 100, 999);
  }, [data]);

  return (
    <main className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100">
      <div
        className="absolute inset-0 opacity-50 blur-3xl bg-[radial-gradient(circle_at_20%_20%,rgba(34,211,238,0.12),transparent_35%),radial-gradient(circle_at_80%_0%,rgba(16,185,129,0.12),transparent_30%),radial-gradient(circle_at_70%_80%,rgba(59,130,246,0.12),transparent_25%)]"
        aria-hidden
      />
      <div className="relative mx-auto max-w-6xl px-6 py-10">
        <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-cyan-200/70">Sentinel</p>
            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white">
              Operational Dashboard (Dev)
            </h1>
            <p className="text-gray-300 mt-2 max-w-2xl">
              Salud de base de datos, sistema y sugerencias rápidas para mantenimiento.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Pill status={data?.db_health.status ?? "healthy"} />
            <button
              onClick={load}
              className="rounded-xl border border-white/10 bg-white/10 px-4 py-2 text-sm font-semibold text-white hover:border-cyan-400/50 hover:bg-white/15 active:scale-[0.99] transition"
            >
              Refrescar
            </button>
          </div>
        </header>

        {/* System Metrics Grid */}
        <section className="grid gap-4 md:grid-cols-3 lg:grid-cols-5">
          <CircularStat
            value={data?.system.cpu_percent ?? 0}
            label="CPU"
            hint={`Umbral ${data?.thresholds.cpu_percent ?? 0}%`}
            color="#22d3ee"
          />
          <CircularStat
            value={data?.system.mem_percent ?? 0}
            label="Memoria"
            hint={`${formatBytes(data?.system.mem_used ?? 0)} / ${formatBytes(data?.system.mem_total ?? 0)}`}
            color="#34d399"
          />
          <CircularStat
            value={data?.gpu.gpu_percent ?? 0}
            label="GPU"
            hint={
              data?.gpu.gpu_name !== "N/A"
                ? `${data?.gpu.gpu_name} • ${data?.gpu.gpu_temp ?? 0}°C`
                : "No detectada"
            }
            color="#a78bfa"
          />
          <CircularStat
            value={
              (() => {
                if (!data?.network) return 0;
                const total = data.network.net_bytes_sent + data.network.net_bytes_recv;
                const gb = total / (1024 * 1024 * 1024);
                return Math.min(gb * 10, 100);
              })()
            }
            label="Red (total)"
            hint={`↑ ${formatBytes(data?.network.net_bytes_sent ?? 0)} ↓ ${formatBytes(data?.network.net_bytes_recv ?? 0)}`}
            color="#fb923c"
          />
          <StatCard
            label="Conexiones"
            value={`${data?.db_stats.connections_active ?? 0} / ${data?.thresholds.connections ?? 0}`}
            hint={`Totales: ${data?.db_stats.connections_total ?? 0} • Locks: ${data?.db_stats.locks ?? 0}`}
            accent="bg-gradient-to-r from-fuchsia-400 to-cyan-400"
          />
        </section>

        {/* Network & Storage Cards */}
        <section className="mt-6 grid gap-4 md:grid-cols-4">
          <NetworkCard network={data?.network} />
          <StorageCard
            label="Métricas guardadas"
            value={storage?.metrics_count ?? 0}
            hint={
              storage?.latest_metric_at
                ? `Última: ${new Date(storage.latest_metric_at).toLocaleTimeString()}`
                : "Sin datos"
            }
            onClick={() => open("metrics")}
            color={{
              bg: "cyan",
              border: "hover:border-cyan-400/50",
              shadow: "56,189,248",
              gradient: "bg-gradient-to-r from-cyan-400 to-blue-400",
            }}
          />
          <StorageCard
            label="Anomalías detectadas"
            value={storage?.anomalies_count ?? 0}
            hint={
              storage?.latest_anomaly_at
                ? `Última: ${new Date(storage.latest_anomaly_at).toLocaleTimeString()}`
                : "Sin eventos"
            }
            onClick={() => open("anomalies")}
            color={{
              bg: "amber",
              border: "hover:border-amber-400/50",
              shadow: "251,191,36",
              gradient: "bg-gradient-to-r from-amber-400 to-orange-400",
            }}
          />
          <StorageCard
            label="Base de datos (tamaño)"
            value={formatBytes(storage?.db_size_bytes ?? 0)}
            hint={`Estado: ${storage?.status === "healthy" ? "✓ Datos fluyen" : "⚠ Sin datos"}`}
            onClick={() => open("database")}
            color={{
              bg: "emerald",
              border: "hover:border-emerald-400/50",
              shadow: "16,185,129",
              gradient: "bg-gradient-to-r from-emerald-400 to-teal-400",
            }}
          />
        </section>

        {/* Detail Modal */}
        <DetailModal isOpen={modal.isOpen} onClose={close} type={modal.type} storage={storage} anomalies={anomalies} />

        {/* Database Activity & Suggestions */}
        <section className="mt-6 grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6 shadow-[0_30px_80px_-50px_rgba(14,165,233,0.45)]">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-400">Tamaño de base</p>
                <p className="text-2xl font-semibold text-white">
                  {formatBytes(data?.db_stats.db_size_bytes ?? 0)}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-400">Última muestra</p>
                <p className="text-sm font-semibold text-cyan-200">
                  {data ? new Date(data.timestamp).toLocaleString() : "-"}
                </p>
              </div>
            </div>
            <div className="mt-6 rounded-xl bg-black/40 border border-white/5 p-5">
              <div className="flex items-center justify-between text-sm mb-2 text-gray-300">
                <span>Uso de conexiones</span>
                <span>{ratio.toFixed(0)}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-white/5 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400"
                  style={{ width: `${Math.min(ratio, 100)}%` }}
                />
              </div>
              <p className="text-xs text-gray-400 mt-3">
                Umbral configurado: {data?.thresholds.connections ?? 0} conexiones.
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6 space-y-4">
            <h3 className="text-lg font-semibold text-white mb-3">Sugerencias rápidas</h3>
            <ul className="space-y-3 text-sm text-gray-200">
              {(
                data?.admin_suggestions ?? [
                  "Ejecuta VACUUM en ventana de mantenimiento",
                  "Revisa bloqueos prolongados",
                  "Termina conexiones idle > 15m",
                ]
              ).map((s, idx) => (
                <li key={idx} className="flex gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-cyan-400" aria-hidden />
                  <span>{s}</span>
                </li>
              ))}
            </ul>

            <div className="pt-2 border-t border-white/5">
              <h4 className="text-sm font-semibold text-white mb-2">Posibles bugs / fallas a investigar</h4>
              <ul className="space-y-2 text-sm text-amber-100">
                {issues.length === 0 ? <li className="text-gray-300">Sin alertas automáticas por ahora.</li> : null}
                {issues.map((item, idx) => (
                  <li key={idx} className="flex gap-2">
                    <span className="mt-1 h-2 w-2 rounded-full bg-amber-400" aria-hidden />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* More sections... */}
        {error ? (
          <div className="mt-6 rounded-xl border border-rose-500/40 bg-rose-500/10 text-rose-100 px-4 py-3 text-sm">
            Error al cargar el dashboard: {error}
          </div>
        ) : null}

        {loading ? <div className="mt-6 text-sm text-gray-300">Cargando métricas…</div> : null}
      </div>
    </main>
  );
}
