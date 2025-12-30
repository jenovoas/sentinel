"use client";

import { useEffect, useMemo, useState } from "react";

const API_PATH = "/api/v1/dashboard/status";
const ANALYTICS_RECENT_PATH = "/api/v1/analytics/metrics/recent?limit=200";
const ANOMALIES_PATH = "/api/v1/analytics/anomalies?hours=24&limit=200";
const STORAGE_SUMMARY_PATH = "/api/v1/analytics/storage/summary";

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

type AnalyticsSample = {
  sampled_at: string;
  cpu_percent: number;
  memory_percent: number;
  memory_used_mb: number;
  gpu_percent: number | null;
  network_bytes_sent: number;
  network_bytes_recv: number;
  db_connections_active: number;
  db_locks: number;
};

type AnomalyPoint = {
  id: string;
  timestamp: number;
  severity: "info" | "warning" | "critical";
  title: string;
  type: string;
  metric: keyof HistoryState;
  metricValue?: number;
};

type StorageSummary = {
  metrics_count: number;
  anomalies_count: number;
  latest_metric_at: string | null;
  latest_anomaly_at: string | null;
  db_size_bytes: number;
  status: "healthy" | "no_data";
};

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

const CircularStat = ({ value, label, hint, color, onClick }: { value: number; label: string; hint?: string; color: string; onClick?: () => void }) => {
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
    <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${isHealthy ? "bg-emerald-500/10 text-emerald-200" : "bg-rose-500/10 text-rose-200"}`}>
      <span className={`h-2 w-2 rounded-full ${isHealthy ? "bg-emerald-400" : "bg-rose-400"}`} />
      {isHealthy ? "Healthy" : "Unhealthy"}
    </span>
  );
};

const computeIssues = (data?: DashboardData) => {
  if (!data) return [] as string[];
  const issues: string[] = [];
  if (data.db_health.status !== "healthy") issues.push("DB reporta unhealthy (ver logs y conexión).");
  if (data.system.cpu_percent > data.thresholds.cpu_percent) issues.push(`CPU > umbral (${data.system.cpu_percent.toFixed(1)}%).`);
  if (data.system.mem_percent > data.thresholds.mem_percent) issues.push(`Memoria > umbral (${data.system.mem_percent.toFixed(1)}%).`);
  if (data.db_stats.connections_total > data.thresholds.connections) issues.push(`Conexiones totales altas (${data.db_stats.connections_total}).`);
  if (data.db_stats.locks > 5) issues.push(`Locks detectados (${data.db_stats.locks}); revisar bloqueos.`);
  if ((data.db_activity?.length ?? 0) > 0) {
    const longRunning = data.db_activity.find((q) => q.duration_seconds > 60);
    if (longRunning) issues.push("Hay queries activas (>60s); revisar qué bloquean.");
  }
  return issues;
};

const API_REFRESH_MS = 15000;
const HISTORY_SIZE = 60; // Keep last 60 samples (15min at 15s intervals)

type MetricHistory = {
  timestamp: number;
  value: number;
}[];

type HistoryState = {
  cpu: MetricHistory;
  memory: MetricHistory;
  gpu: MetricHistory;
  network: MetricHistory;
};

const severityColor: Record<AnomalyPoint["severity"], string> = {
  info: "#38bdf8",
  warning: "#fbbf24",
  critical: "#f87171",
};

const LineChart = ({ data, color, label: _label, unit = "%", anomalies = [] }: { data: MetricHistory; color: string; label: string; unit?: string; anomalies?: AnomalyPoint[] }) => {
  if (data.length === 0) return <p className="text-gray-400 text-sm">Sin datos históricos</p>;

  const max = Math.max(...data.map((d) => d.value), 100);
  const min = 0;
  const width = 600;
  const height = 200;
  const padding = 40;

  const xScale = (index: number) => padding + (index / (data.length - 1 || 1)) * (width - padding * 2);
  const yScale = (value: number) => height - padding - ((value - min) / (max - min || 1)) * (height - padding * 2);

  const pathData = data.map((d, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(d.value)}`).join(" ");

  const current = data[data.length - 1]?.value ?? 0;
  const avg = data.reduce((sum, d) => sum + d.value, 0) / data.length;
  const maxVal = Math.max(...data.map((d) => d.value));

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <p className="text-gray-400">Actual</p>
          <p className="text-xl font-bold" style={{ color }}>{current.toFixed(1)}{unit}</p>
        </div>
        <div>
          <p className="text-gray-400">Promedio</p>
          <p className="text-xl font-bold text-gray-200">{avg.toFixed(1)}{unit}</p>
        </div>
        <div>
          <p className="text-gray-400">Máximo</p>
          <p className="text-xl font-bold text-gray-200">{maxVal.toFixed(1)}{unit}</p>
        </div>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="w-full border border-white/10 rounded-lg bg-black/40">
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map((tick) => (
          <g key={tick}>
            <line
              x1={padding}
              y1={yScale(tick)}
              x2={width - padding}
              y2={yScale(tick)}
              stroke="rgba(255,255,255,0.05)"
              strokeWidth="1"
            />
            <text x={10} y={yScale(tick) + 4} fill="rgba(255,255,255,0.4)" fontSize="10">
              {tick}{unit}
            </text>
          </g>
        ))}

        {/* Area fill */}
        <path
          d={`${pathData} L ${xScale(data.length - 1)} ${height - padding} L ${padding} ${height - padding} Z`}
          fill={`${color}20`}
          stroke="none"
        />

        {/* Line */}
        <path d={pathData} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />

        {/* Points */}
        {data.map((d, i) => (
          <circle key={i} cx={xScale(i)} cy={yScale(d.value)} r="2" fill={color} />
        ))}

        {/* Anomaly markers */}
        {anomalies.map((a) => {
          const closest = data.reduce(
            (best, point, idx) => {
              const distance = Math.abs(point.timestamp - a.timestamp);
              return distance < best.distance ? { idx, distance } : best;
            },
            { idx: data.length - 1, distance: Number.MAX_SAFE_INTEGER }
          ).idx;

          const x = xScale(closest);
          return (
            <g key={a.id}>
              <line
                x1={x}
                y1={padding}
                x2={x}
                y2={height - padding}
                stroke={severityColor[a.severity]}
                strokeWidth="1"
                strokeDasharray="4 3"
                opacity={0.6}
              />
              <circle
                cx={x}
                cy={padding + 6}
                r="4"
                fill={severityColor[a.severity]}
              >
                <title>{`${a.title} (${a.severity})`}</title>
              </circle>
            </g>
          );
        })}
      </svg>

      <p className="text-xs text-gray-400 text-center">
        Últimas {data.length} muestras (~{Math.round((data.length * API_REFRESH_MS) / 60000)}min)
      </p>
    </div>
  );
};

const DetailModal = ({
  isOpen,
  onClose,
  type,
  storage,
  anomalies,
}: {
  isOpen: boolean;
  onClose: () => void;
  type: "metrics" | "anomalies" | "database" | null;
  storage: StorageSummary | null;
  anomalies: AnomalyPoint[];
}) => {
  if (!isOpen || !type) return null;

  const getTitle = () => {
    switch (type) {
      case "metrics": return "Métricas Guardadas";
      case "anomalies": return "Anomalías Detectadas";
      case "database": return "Base de Datos";
      default: return "";
    }
  };

  const getColor = () => {
    switch (type) {
      case "metrics": return "#22d3ee";
      case "anomalies": return "#fbbf24";
      case "database": return "#10b981";
      default: return "#fff";
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div
        className="relative bg-slate-900 border border-white/10 rounded-2xl shadow-[0_40px_100px_-20px_rgba(0,0,0,0.8)] max-w-2xl w-full p-6 animate-[fadeIn_0.2s_ease-out]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white">{getTitle()}</h2>
            <p className="text-sm text-gray-400">Detalle completo del almacenamiento</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-4">
          {type === "metrics" && storage && (
            <>
              <div className="rounded-lg border border-white/5 bg-black/40 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Total de muestras guardadas</span>
                  <span className="text-2xl font-bold" style={{ color: getColor() }}>{storage.metrics_count}</span>
                </div>
              </div>
              <div className="rounded-lg border border-white/5 bg-black/40 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Última muestra</span>
                  <span className="text-sm text-gray-200">{storage.latest_metric_at ? new Date(storage.latest_metric_at).toLocaleString() : "N/A"}</span>
                </div>
              </div>
              <div className="rounded-lg border border-white/5 bg-black/40 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Estado</span>
                  <span className={`text-sm font-semibold ${storage.status === "healthy" ? "text-emerald-400" : "text-rose-400"}`}>
                    {storage.status === "healthy" ? "✓ Datos fluyendo" : "⚠ Sin datos"}
                  </span>
                </div>
              </div>
              <div className="rounded-lg border border-white/5 bg-black/40 p-4 text-xs text-gray-400 space-y-1">
                <p>• Las métricas se recopilan cada 15 segundos</p>
                <p>• Se mantienen 90 días de histórico</p>
                <p>• Incluye CPU, Memoria, GPU, Red y DB stats</p>
              </div>
            </>
          )}

          {type === "anomalies" && (
            <>
              <div className="rounded-lg border border-white/5 bg-black/40 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Total de anomalías detectadas</span>
                  <span className="text-2xl font-bold" style={{ color: getColor() }}>{storage?.anomalies_count ?? 0}</span>
                </div>
              </div>
              <div className="rounded-lg border border-white/5 bg-black/40 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Última anomalía</span>
                  <span className="text-sm text-gray-200">{storage?.latest_anomaly_at ? new Date(storage.latest_anomaly_at).toLocaleString() : "Sin eventos"}</span>
                </div>
              </div>
              <div className="rounded-lg border border-white/5 bg-black/40 p-4">
                <p className="text-gray-300 text-sm font-semibold mb-3">Últimas anomalías en este período:</p>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {anomalies.length === 0 ? (
                    <p className="text-xs text-gray-500">Sin anomalías registradas en las últimas 24 horas</p>
                  ) : (
                    anomalies.slice(0, 10).map((a) => (
                      <div key={a.id} className="text-xs border border-white/5 rounded p-2 flex items-center justify-between">
                        <span className="text-gray-200">{a.title}</span>
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${a.severity === "critical" ? "bg-rose-500/20 text-rose-300" :
                            a.severity === "warning" ? "bg-amber-500/20 text-amber-300" :
                              "bg-cyan-500/20 text-cyan-300"
                          }`}>{a.severity}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </>
          )}

          {type === "database" && storage && (
            <>
              <div className="rounded-lg border border-white/5 bg-black/40 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Tamaño total de la BD</span>
                  <span className="text-2xl font-bold" style={{ color: getColor() }}>{formatBytes(storage.db_size_bytes)}</span>
                </div>
              </div>
              <div className="rounded-lg border border-white/5 bg-black/40 p-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-400">Métricas en BD</p>
                    <p className="text-xl font-semibold text-cyan-400">{storage.metrics_count}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Anomalías en BD</p>
                    <p className="text-xl font-semibold text-amber-400">{storage.anomalies_count}</p>
                  </div>
                </div>
              </div>
              <div className="rounded-lg border border-white/5 bg-black/40 p-4 text-xs text-gray-400 space-y-1">
                <p>• PostgreSQL con tablas time-series optimizadas</p>
                <p>• Índices en timestamps para queries rápidas</p>
                <p>• Retención automática: 90 días</p>
                <p>• Compresión automática de datos antiguos</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

const MetricModal = ({
  isOpen,
  onClose,
  title,
  data,
  color,
  unit,
  anomalies,
}: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  data: MetricHistory;
  color: string;
  unit?: string;
  anomalies?: AnomalyPoint[];
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div
        className="relative bg-slate-900 border border-white/10 rounded-2xl shadow-[0_40px_100px_-20px_rgba(0,0,0,0.8)] max-w-3xl w-full p-6 animate-[fadeIn_0.2s_ease-out]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white">{title}</h2>
            <p className="text-sm text-gray-400">Histórico de métricas en tiempo real</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <LineChart data={data} color={color} label={title} unit={unit} anomalies={anomalies} />
      </div>
    </div>
  );
};

export default function DashboardPage() {
  const [state, setState] = useState<FetchState>({ loading: true });
  const [notes, setNotes] = useState<NotesState>({ text: "" });
  const [history, setHistory] = useState<HistoryState>({
    cpu: [],
    memory: [],
    gpu: [],
    network: [],
  });
  const [anomalies, setAnomalies] = useState<AnomalyPoint[]>([]);
  const [modal, setModal] = useState<{ type: keyof HistoryState; isOpen: boolean }>({ type: "cpu", isOpen: false });
  const [storage, setStorage] = useState<StorageSummary | null>(null);
  const [detailModal, setDetailModal] = useState<{ type: "metrics" | "anomalies" | "database" | null; isOpen: boolean }>({ type: null, isOpen: false });

  const normalizeNetworkPercent = (bytesSent: number, bytesRecv: number) => {
    const total = bytesSent + bytesRecv;
    const gb = total / (1024 * 1024 * 1024);
    return Math.min(gb * 10, 100);
  };

  const hydrateHistoryFromServer = async () => {
    try {
      const res = await fetch(ANALYTICS_RECENT_PATH, { cache: "no-store" });
      if (!res.ok) return;
      const json = (await res.json()) as { samples: AnalyticsSample[] };
      const sorted = (json.samples ?? []).sort((a, b) => new Date(a.sampled_at).getTime() - new Date(b.sampled_at).getTime());

      const toHistory = (selector: (s: AnalyticsSample) => number) =>
        sorted.map((s) => ({ timestamp: new Date(s.sampled_at).getTime(), value: selector(s) })).slice(-HISTORY_SIZE);

      setHistory((prev) => ({
        ...prev,
        cpu: toHistory((s) => s.cpu_percent),
        memory: toHistory((s) => s.memory_percent),
        gpu: toHistory((s) => s.gpu_percent ?? 0),
        network: toHistory((s) => normalizeNetworkPercent(s.network_bytes_sent, s.network_bytes_recv)),
      }));
    } catch (err) {
      console.error("hydrateHistoryFromServer error", err);
    }
  };

  const loadAnomalies = async () => {
    try {
      const res = await fetch(ANOMALIES_PATH, { cache: "no-store" });
      if (!res.ok) return;
      const json = (await res.json()) as { anomalies: Array<{ id: string; detected_at: string; severity: AnomalyPoint["severity"]; title: string; type: string; metric_value?: number }> };
      const mapMetric = (type: string): keyof HistoryState => {
        switch (type) {
          case "cpu_spike":
            return "cpu";
          case "memory_spike":
            return "memory";
          case "gpu_overheat":
            return "gpu";
          case "network_spike":
          case "conn_surge":
          case "lock_detected":
          case "query_slow":
            return "network";
          default:
            return "cpu";
        }
      };

      const mapped = (json.anomalies ?? []).map((a) => ({
        id: a.id,
        timestamp: new Date(a.detected_at).getTime(),
        severity: a.severity,
        title: a.title,
        type: a.type,
        metric: mapMetric(a.type),
        metricValue: a.metric_value,
      }));
      setAnomalies(mapped);
    } catch (err) {
      console.error("loadAnomalies error", err);
    }
  };

  const loadStorageSummary = async () => {
    try {
      const res = await fetch(STORAGE_SUMMARY_PATH, { cache: "no-store" });
      if (!res.ok) return;
      const json = (await res.json()) as StorageSummary;
      setStorage(json);
    } catch (err) {
      console.error("loadStorageSummary error", err);
    }
  };

  const load = async () => {
    try {
      setState((s) => ({ ...s, loading: true, error: undefined }));
      const res = await fetch(API_PATH, { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as DashboardData;
      setState({ loading: false, data: json });

      // Update history
      const timestamp = Date.now();
      setHistory((prev) => {
        const addSample = (arr: MetricHistory, value: number) => {
          const updated = [...arr, { timestamp, value }];
          return updated.slice(-HISTORY_SIZE);
        };

        return {
          cpu: addSample(prev.cpu, json.system.cpu_percent),
          memory: addSample(prev.memory, json.system.mem_percent),
          gpu: addSample(prev.gpu, json.gpu.gpu_percent),
          network: addSample(prev.network, normalizeNetworkPercent(json.network.net_bytes_sent, json.network.net_bytes_recv)),
        };
      });
    } catch (err) {
      setState({ loading: false, error: err instanceof Error ? err.message : "Error" });
    }
  };

  useEffect(() => {
    hydrateHistoryFromServer();
    loadAnomalies();
    loadStorageSummary();
    load();
    const id = setInterval(load, API_REFRESH_MS);
    const anomaliesId = setInterval(loadAnomalies, 60000);
    const storageId = setInterval(loadStorageSummary, 30000);
    return () => {
      clearInterval(id);
      clearInterval(anomaliesId);
      clearInterval(storageId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
  const issues = computeIssues(data);
  const anomaliesByMetric = useMemo(() => {
    return anomalies.reduce<Record<keyof HistoryState, AnomalyPoint[]>>(
      (acc, a) => {
        acc[a.metric] = [...acc[a.metric], a];
        return acc;
      },
      { cpu: [], memory: [], gpu: [], network: [] }
    );
  }, [anomalies]);

  const ratio = useMemo(() => {
    if (!data) return 0;
    return Math.min(
      (data.db_stats.connections_active / (data.thresholds.connections || 1)) * 100,
      999
    );
  }, [data]);

  return (
    <main className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100">
      <div className="absolute inset-0 opacity-50 blur-3xl bg-[radial-gradient(circle_at_20%_20%,rgba(34,211,238,0.12),transparent_35%),radial-gradient(circle_at_80%_0%,rgba(16,185,129,0.12),transparent_30%),radial-gradient(circle_at_70%_80%,rgba(59,130,246,0.12),transparent_25%)]" aria-hidden />
      <div className="relative mx-auto max-w-6xl px-6 py-10">
        <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-cyan-200/70">Sentinel</p>
            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white">Operational Dashboard (Dev)</h1>
            <p className="text-gray-300 mt-2 max-w-2xl">Salud de base de datos, sistema y sugerencias rápidas para mantenimiento.</p>
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

        <section className="grid gap-4 md:grid-cols-3 lg:grid-cols-5">
          <CircularStat
            value={data?.system.cpu_percent ?? 0}
            label="CPU"
            hint={`Umbral ${data?.thresholds.cpu_percent ?? 0}%`}
            color="#22d3ee"
            onClick={() => setModal({ type: "cpu", isOpen: true })}
          />
          <CircularStat
            value={data?.system.mem_percent ?? 0}
            label="Memoria"
            hint={`${formatBytes(data?.system.mem_used ?? 0)} / ${formatBytes(data?.system.mem_total ?? 0)}`}
            color="#34d399"
            onClick={() => setModal({ type: "memory", isOpen: true })}
          />
          <CircularStat
            value={data?.gpu.gpu_percent ?? 0}
            label="GPU"
            hint={data?.gpu.gpu_name !== "N/A" ? `${data?.gpu.gpu_name} • ${data?.gpu.gpu_temp ?? 0}°C` : "No detectada"}
            color="#a78bfa"
            onClick={() => setModal({ type: "gpu", isOpen: true })}
          />
          <CircularStat
            value={(() => {
              if (!data?.network) return 0;
              const total = data.network.net_bytes_sent + data.network.net_bytes_recv;
              const gb = total / (1024 * 1024 * 1024);
              return Math.min(gb * 10, 100);
            })()}
            label="Red (total)"
            hint={`↑ ${formatBytes(data?.network.net_bytes_sent ?? 0)} ↓ ${formatBytes(data?.network.net_bytes_recv ?? 0)}`}
            color="#fb923c"
            onClick={() => setModal({ type: "network", isOpen: true })}
          />
          <StatCard label="Conexiones" value={`${data?.db_stats.connections_active ?? 0} / ${data?.thresholds.connections ?? 0}`} hint={`Totales: ${data?.db_stats.connections_total ?? 0} • Locks: ${data?.db_stats.locks ?? 0}`} accent="bg-gradient-to-r from-fuchsia-400 to-cyan-400" />
        </section>

        <section className="mt-6 grid gap-4 md:grid-cols-3">
          <div
            onClick={() => setDetailModal({ type: "metrics", isOpen: true })}
            className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(56,189,248,0.2)] transition-all duration-300 hover:border-cyan-400/50 hover:bg-white/10 hover:shadow-[0_30px_90px_-40px_rgba(56,189,248,0.6)] hover:scale-[1.02] cursor-pointer">
            <p className="text-sm text-gray-300 mb-1 transition-colors duration-300 group-hover:text-cyan-200">Métricas guardadas</p>
            <p className="text-3xl font-semibold text-white">{storage?.metrics_count ?? 0}</p>
            <p className="text-xs text-gray-400 mt-2 transition-colors duration-300 hover:text-cyan-300">{storage?.latest_metric_at ? `Última: ${new Date(storage.latest_metric_at).toLocaleTimeString()}` : "Sin datos"}</p>
            <div className="mt-3 h-1 rounded-full bg-gradient-to-r from-cyan-400 to-blue-400 transition-opacity duration-300 hover:opacity-100 opacity-80" />
          </div>
          <div
            onClick={() => setDetailModal({ type: "anomalies", isOpen: true })}
            className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(251,191,36,0.2)] transition-all duration-300 hover:border-amber-400/50 hover:bg-white/10 hover:shadow-[0_30px_90px_-40px_rgba(251,191,36,0.6)] hover:scale-[1.02] cursor-pointer">
            <p className="text-sm text-gray-300 mb-1 transition-colors duration-300 hover:text-amber-200">Anomalías detectadas</p>
            <p className="text-3xl font-semibold text-white">{storage?.anomalies_count ?? 0}</p>
            <p className="text-xs text-gray-400 mt-2 transition-colors duration-300 hover:text-amber-300">{storage?.latest_anomaly_at ? `Última: ${new Date(storage.latest_anomaly_at).toLocaleTimeString()}` : "Sin eventos"}</p>
            <div className="mt-3 h-1 rounded-full bg-gradient-to-r from-amber-400 to-orange-400 transition-opacity duration-300 hover:opacity-100 opacity-80" />
          </div>
          <div
            onClick={() => setDetailModal({ type: "database", isOpen: true })}
            className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(16,185,129,0.2)] transition-all duration-300 hover:border-emerald-400/50 hover:bg-white/10 hover:shadow-[0_30px_90px_-40px_rgba(16,185,129,0.6)] hover:scale-[1.02] cursor-pointer">
            <p className="text-sm text-gray-300 mb-1 transition-colors duration-300 hover:text-emerald-200">Base de datos (tamaño)</p>
            <p className="text-3xl font-semibold text-white">{formatBytes(storage?.db_size_bytes ?? 0)}</p>
            <p className="text-xs text-gray-400 mt-2 transition-colors duration-300 hover:text-emerald-300">Estado: {storage?.status === "healthy" ? "✓ Datos fluyen" : "⚠ Sin datos"}</p>
            <div className="mt-3 h-1 rounded-full bg-gradient-to-r from-emerald-400 to-teal-400 transition-opacity duration-300 hover:opacity-100 opacity-80" />
          </div>
        </section>

        <MetricModal
          isOpen={modal.isOpen && modal.type === "cpu"}
          onClose={() => setModal({ ...modal, isOpen: false })}
          title="CPU Usage"
          data={history.cpu}
          color="#22d3ee"
          unit="%"
          anomalies={anomaliesByMetric.cpu}
        />
        <MetricModal
          isOpen={modal.isOpen && modal.type === "memory"}
          onClose={() => setModal({ ...modal, isOpen: false })}
          title="Memory Usage"
          data={history.memory}
          color="#34d399"
          unit="%"
          anomalies={anomaliesByMetric.memory}
        />
        <MetricModal
          isOpen={modal.isOpen && modal.type === "gpu"}
          onClose={() => setModal({ ...modal, isOpen: false })}
          title="GPU Usage"
          data={history.gpu}
          color="#a78bfa"
          unit="%"
          anomalies={anomaliesByMetric.gpu}
        />
        <MetricModal
          isOpen={modal.isOpen && modal.type === "network"}
          onClose={() => setModal({ ...modal, isOpen: false })}
          title="Network Traffic"
          data={history.network}
          color="#fb923c"
          unit="%"
          anomalies={anomaliesByMetric.network}
        />

        <DetailModal
          isOpen={detailModal.isOpen}
          onClose={() => setDetailModal({ type: null, isOpen: false })}
          type={detailModal.type}
          storage={storage}
          anomalies={anomalies}
        />

        <section className="mt-6 grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6 shadow-[0_30px_80px_-50px_rgba(14,165,233,0.45)]">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-400">Tamaño de base</p>
                <p className="text-2xl font-semibold text-white">{formatBytes(data?.db_stats.db_size_bytes ?? 0)}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-400">Última muestra</p>
                <p className="text-sm font-semibold text-cyan-200">{data ? new Date(data.timestamp).toLocaleString() : "-"}</p>
              </div>
            </div>
            <div className="mt-6 rounded-xl bg-black/40 border border-white/5 p-5">
              <div className="flex items-center justify-between text-sm mb-2 text-gray-300">
                <span>Uso de conexiones</span>
                <span>{ratio.toFixed(0)}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-white/5 overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400" style={{ width: `${Math.min(ratio, 100)}%` }} />
              </div>
              <p className="text-xs text-gray-400 mt-3">Umbral configurado: {data?.thresholds.connections ?? 0} conexiones.</p>
            </div>
          </div>

          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6 space-y-4">
            <h3 className="text-lg font-semibold text-white mb-3">Sugerencias rápidas</h3>
            <ul className="space-y-3 text-sm text-gray-200">
              {(data?.admin_suggestions ?? ["Ejecuta VACUUM en ventana de mantenimiento", "Revisa bloqueos prolongados", "Termina conexiones idle > 15m"]).map((s, idx) => (
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

        <section className="mt-6 grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-white">Actividad de base de datos</h3>
              <span className="text-xs rounded-full bg-white/10 px-3 py-1 text-gray-200 border border-white/10">
                {activeQueries.length} activas
              </span>
            </div>
            <div className="space-y-3">
              {activeQueries.length === 0 ? (
                <div className="rounded-lg border border-white/5 bg-black/30 text-sm text-gray-300 px-4 py-3">
                  Sin queries activas ahora mismo.
                </div>
              ) : (
                activeQueries.map((q, idx) => (
                  <div key={`${q.pid}-${idx}`} className="rounded-lg border border-white/5 bg-black/40 p-4">
                    <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between text-sm">
                      <div className="flex flex-wrap items-center gap-2 text-cyan-100">
                        <span className="font-semibold">{q.user}</span>
                        <span className="text-xs text-gray-400">PID {q.pid}</span>
                      </div>
                      <div className="flex flex-wrap items-center gap-2 text-xs">
                        <span className="rounded-full bg-white/10 px-2 py-1 text-gray-200 border border-white/10">{q.state}</span>
                        <span className="text-gray-300">{formatDuration(q.duration_seconds)}</span>
                        <span className="text-gray-400">{q.wait_event || "sin espera"}</span>
                      </div>
                    </div>
                    <pre className="mt-3 text-xs text-gray-100 bg-white/5 border border-white/5 rounded-md p-3 overflow-x-auto whitespace-pre-wrap break-words">
                      {q.query}
                    </pre>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-3">Anomalías recientes (24h)</h3>
            <div className="space-y-3">
              {anomalies.length === 0 ? (
                <div className="rounded-lg border border-white/5 bg-black/30 text-sm text-gray-300 px-4 py-3">
                  Sin anomalías registradas.
                </div>
              ) : null}
              {anomalies.map((a) => (
                <div key={a.id} className="rounded-lg border border-white/5 bg-black/40 p-4 flex flex-col gap-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white font-semibold">{a.title}</span>
                    <span className={`text-xs px-2 py-1 rounded-full border ${a.severity === "critical"
                        ? "border-rose-400 text-rose-200"
                        : a.severity === "warning"
                          ? "border-amber-400 text-amber-200"
                          : "border-cyan-400 text-cyan-200"
                      }`}>
                      {a.severity}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400 flex flex-wrap gap-3">
                    <span>{new Date(a.timestamp).toLocaleString()}</span>
                    <span className="uppercase tracking-wide">{a.type}</span>
                    {Number.isFinite(a.metricValue) ? <span>Valor: {a.metricValue}</span> : null}
                  </div>
                  <div className="text-xs text-gray-300">Métrica: {a.metric}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-3">Actividad de código</h3>
            <div className="mb-4">
              <p className="text-sm text-gray-300 mb-2">Commits recientes</p>
              <ul className="space-y-2 text-sm text-gray-100">
                {(repo?.recent_commits ?? []).map((c) => (
                  <li key={c.hash} className="rounded-lg border border-white/5 bg-black/30 px-3 py-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-cyan-200 text-xs">{c.hash}</span>
                      <span className="text-xs text-gray-400">{c.when}</span>
                    </div>
                    <div className="text-gray-200 text-sm">{c.message}</div>
                    <div className="text-xs text-gray-400">por {c.author}</div>
                  </li>
                ))}
                {(repo?.recent_commits?.length ?? 0) === 0 ? (
                  <li className="text-sm text-gray-300">No hay commits recientes disponibles.</li>
                ) : null}
              </ul>
            </div>

            <div>
              <p className="text-sm text-gray-300 mb-2">Working tree</p>
              <div className="space-y-1 text-sm text-gray-100">
                {(repo?.working_tree ?? []).map((line, idx) => (
                  <div key={idx} className="rounded border border-white/5 bg-black/30 px-2 py-1 font-mono text-xs">{line}</div>
                ))}
                {(repo?.working_tree?.length ?? 0) === 0 ? (
                  <div className="text-sm text-gray-300">Sin cambios locales.</div>
                ) : null}
              </div>
            </div>

            {repo?.git_warning ? (
              <div className="mt-3 text-xs text-amber-200 bg-amber-500/10 border border-amber-500/30 rounded px-3 py-2">
                Aviso Git: {repo.git_warning}
              </div>
            ) : null}

            <div>
              <p className="text-sm text-gray-300 mb-2">Notas / tareas pendientes</p>
              <textarea
                value={notes.text}
                onChange={(e) => setNotes({ text: e.target.value })}
                className="w-full rounded-xl border border-white/10 bg-black/30 text-sm text-gray-100 p-3 min-h-[140px] focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                placeholder="Escribe tareas rápidas o recordatorios..."
              />
              <p className="text-xs text-gray-400 mt-1">Se guarda localmente en este navegador para tu sesión.</p>
            </div>
          </div>
        </section>

        {error ? (
          <div className="mt-6 rounded-xl border border-rose-500/40 bg-rose-500/10 text-rose-100 px-4 py-3 text-sm">
            Error al cargar el dashboard: {error}
          </div>
        ) : null}

        {loading ? (
          <div className="mt-6 text-sm text-gray-300">Cargando métricas…</div>
        ) : null}
      </div>
    </main>
  );
}
