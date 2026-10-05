/**
 * Operational Dashboard - Refactored with SOLID Principles
 * - Single Responsibility: Each component/hook has one purpose
 * - Open/Closed: Easy to extend without modifying existing code
 * - Liskov Substitution: Components follow consistent interfaces
 * - Interface Segregation: Components accept minimal required props
 * - Dependency Inversion: Depends on abstractions (hooks, types) not concrete implementations
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAnalytics, useDetailModal } from "@/hooks/useAnalytics";
import { AnalyticsAPI } from "@/lib/api";
import { StorageCard } from "@/components/StorageCard";
import { DetailModal } from "@/components/DetailModal";
import { NetworkCard } from "@/components/NetworkCard";
import { useNetworkInfo } from "@/hooks/useNetworkInfo";
import { MiniChart } from "@/components/MiniChart";

type DashboardData = {
  sampled_at: string;
  cpu_percent: number | null;
  memory_percent: number | null;
  memory_used_mb: number | null;
  gpu_percent: number | null;
  network_bytes_sent: number | null;
  network_bytes_recv: number | null;
};

type RuntimeHealth = {
  available: boolean;
  status: string;
  subsystems?: Record<string, string>;
};

type FetchState = {
  loading: boolean;
  data?: DashboardData;
  runtime?: RuntimeHealth;
};

// ============ Utility Functions ============

const formatBytes = (bytes: number | null | undefined) => {
  if (bytes == null || !Number.isFinite(bytes)) return "No disponible";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** i;
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[i]}`;
};



// ============ Components ============

const CircularStat = ({
  value,
  label,
  hint,
  color,
  onClick,
  history,
}: {
  value: number | null;
  label: string;
  hint?: string;
  color: string;
  onClick?: () => void;
  history?: Array<{ timestamp: number; value: number }>;
}) => {
  const safe = value !== null && Number.isFinite(value) ? Math.max(0, Math.min(value, 100)) : null;
  return (
    <div
      onClick={onClick}
      className="group rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(56,189,248,0.4)] flex flex-col gap-3 transition-all duration-300 hover:border-white/20 hover:shadow-[0_30px_90px_-40px_rgba(56,189,248,0.6)] hover:scale-[1.02] cursor-pointer"
    >
      <div className="flex items-center gap-4">
        <div
          className="relative h-20 w-20 rounded-full grid place-items-center transition-transform duration-300 group-hover:scale-110"
          style={{ background: safe === null ? "rgba(255,255,255,0.08)" : `conic-gradient(${color} ${safe}%, rgba(255,255,255,0.08) ${safe}% 100%)` }}
        >
          <div className="h-14 w-14 rounded-full bg-slate-950/80 grid place-items-center text-white font-semibold text-lg transition-all duration-300 group-hover:bg-slate-900/90">
            {safe === null ? "N/D" : `${safe.toFixed(0)}%`}
          </div>
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-300 transition-colors duration-300 group-hover:text-white">{label}</p>
          <p className="text-xs text-gray-400 transition-colors duration-300 group-hover:text-gray-300">{hint}</p>
        </div>
      </div>
      {history && history.length > 0 && (
        <div className="h-10">
          <MiniChart data={history} color={color} height={40} />
        </div>
      )}
    </div>
  );
};

const StatCard = ({
  label,
  value,
  hint,
  accent,
  history,
}: {
  label: string;
  value: string;
  hint?: string;
  accent: string;
  history?: Array<{ timestamp: number; value: number }>;
}) => (
  <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(56,189,248,0.4)] flex flex-col gap-3">
    <div>
      <p className="text-sm text-gray-300 mb-1">{label}</p>
      <p className="text-3xl font-semibold text-white tracking-tight">{value}</p>
      {hint ? <p className="text-xs text-gray-400 mt-1">{hint}</p> : null}
    </div>
    {history && history.length > 0 && (
      <div className="h-10">
        <MiniChart data={history} color="#c084fc" height={40} />
      </div>
    )}
    <div className={`h-1 rounded-full ${accent}`} />
  </div>
);

const Pill = ({ status }: { status: string }) => {
  const isHealthy = status === "healthy";
  const label = isHealthy ? "Operativo" : status === "degraded" ? "Degradado" : "No disponible";
  return (
    <span
      className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
        isHealthy ? "bg-emerald-500/10 text-emerald-200" : "bg-amber-500/10 text-amber-200"
      }`}
    >
      <span className={`h-2 w-2 rounded-full ${isHealthy ? "bg-emerald-400" : "bg-amber-400"}`} />
      {label}
    </span>
  );
};

// ============ Main Dashboard Component ============

export default function DashboardPage() {
  const router = useRouter();
  const [state, setState] = useState<FetchState>({ loading: true });
  const { anomalies, anomaliesAvailable, storage } = useAnalytics();
  const { modal, open, close } = useDetailModal();

  const API_REFRESH_MS = 15000;
    const clientNetwork = useNetworkInfo();
  const [hostSample, setHostSample] = useState<any>(null);

  const load = async () => {
    setState((current) => ({ ...current, loading: true }));
    const [samples, runtime] = await Promise.all([
      AnalyticsAPI.getRecentMetrics(1),
      fetch("/api/v1/ai/health", { cache: "no-store" })
        .then(async (response) => {
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          return (await response.json()) as RuntimeHealth;
        })
        .catch((): RuntimeHealth => ({ available: false, status: "unavailable" })),
    ]);
    const latest = samples[samples.length - 1];
    const data: DashboardData | undefined = latest
      ? {
          sampled_at: latest.sampled_at,
          cpu_percent: latest.cpu_percent,
          memory_percent: latest.memory_percent,
          memory_used_mb: latest.memory_used_mb,
          gpu_percent: latest.gpu_percent,
          network_bytes_sent: latest.network_bytes_sent,
          network_bytes_recv: latest.network_bytes_recv,
        }
      : undefined;
    setState({ loading: false, data, runtime });
  };

  useEffect(() => {
    load();
    const id = setInterval(load, API_REFRESH_MS);
    return () => clearInterval(id);
  }, []);

  // Load last host-metrics sample from CSV via API
  useEffect(() => {
    const fetchHostHistory = async () => {
      try {
        const res = await fetch("/api/host-metrics?limit=60", { cache: "no-store" });
        const json = await res.json();
        setHostSample(res.ok && json?.ok && Array.isArray(json.history) ? json.history : []);
      } catch {
        setHostSample([]);
      }
    };
    fetchHostHistory();
    const id = setInterval(fetchHostHistory, 60000);
    return () => clearInterval(id);
  }, []);

  const { data, loading, runtime } = state;
  const latestHostSample = hostSample?.[hostSample.length - 1];
  const cpuValue = latestHostSample?.cpu_percent ?? data?.cpu_percent ?? null;
  const memoryValue = latestHostSample?.mem_percent ?? data?.memory_percent ?? null;
  const gpuValue = latestHostSample?.gpu_percent ?? data?.gpu_percent ?? null;
  const networkInfo = latestHostSample?.network;
  const issues = [
    ...(cpuValue !== null && cpuValue > 85 ? [`CPU sobre el umbral de 85% (${cpuValue.toFixed(1)}%).`] : []),
    ...(memoryValue !== null && memoryValue > 85 ? [`RAM sobre el umbral de 85% (${memoryValue.toFixed(1)}%).`] : []),
  ];

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
              Dashboard Operacional
            </h1>
            <p className="text-gray-300 mt-2 max-w-2xl">
              Métricas actuales del runtime Rust y sensores de host con fuente identificada.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Pill status={runtime?.available ? runtime.status : "unavailable"} />
            <button
              onClick={load}
              className="rounded-xl border border-white/10 bg-white/10 px-4 py-2 text-sm font-semibold text-white hover:border-cyan-400/50 hover:bg-white/15 active:scale-[0.99] transition"
            >
              Refrescar
            </button>
          </div>
        </header>

        {/* Métricas con fuente confirmada */}
        <section className="grid gap-4 md:grid-cols-3 lg:grid-cols-5">
          <CircularStat
            value={cpuValue}
            label="CPU"
            hint={latestHostSample?.cpu_percent != null ? "Fuente: historial del host" : "Fuente: Cortex"}
            color="#22d3ee"
            history={hostSample?.flatMap((sample: any) =>
              typeof sample.cpu_percent === "number"
                ? [{ timestamp: new Date(sample.timestamp).getTime(), value: sample.cpu_percent }]
                : []
            )}
          />
          <CircularStat
            value={memoryValue}
            label="Memoria"
            hint={`Uso detectado: ${formatBytes(data?.memory_used_mb == null ? null : data.memory_used_mb * 1024 * 1024)}`}
            color="#34d399"
            history={hostSample?.flatMap((sample: any) =>
              typeof sample.mem_percent === "number"
                ? [{ timestamp: new Date(sample.timestamp).getTime(), value: sample.mem_percent }]
                : []
            )}
          />
          <CircularStat
            value={gpuValue}
            label="GPU"
            hint={gpuValue === null ? "No hay fuente GPU disponible" : "Fuente: historial del host"}
            color="#a78bfa"
            history={hostSample?.flatMap((sample: any) =>
              typeof sample.gpu_percent === "number"
                ? [{ timestamp: new Date(sample.timestamp).getTime(), value: sample.gpu_percent }]
                : []
            )}
          />
          <StatCard
            label="Tráfico desde la última muestra"
            value={`↑ ${formatBytes(data?.network_bytes_sent)} / ↓ ${formatBytes(data?.network_bytes_recv)}`}
            hint="Delta de contadores de red del runtime entre muestras (~15 s)"
            accent="bg-gradient-to-r from-orange-400 to-amber-400"
          />
          <StatCard
            label="Estado del runtime"
            value={runtime?.available ? runtime.status : "No disponible"}
            hint={data ? `Última muestra: ${new Date(data.sampled_at).toLocaleTimeString()}` : "Esperando primera muestra"}
            accent="bg-gradient-to-r from-cyan-400 to-emerald-400"
          />
        </section>

        {/* Network & Storage Cards */}
        <section className="mt-6 grid gap-4 md:grid-cols-4">
          <NetworkCard
            network={
              typeof networkInfo?.net_bytes_sent === "number" &&
              typeof networkInfo?.net_bytes_recv === "number"
                ? networkInfo
                : undefined
            }
            clientNetwork={clientNetwork}
            history={hostSample?.flatMap((sample: any) =>
              typeof sample.network?.wifi?.signal === "number"
                ? [{ timestamp: new Date(sample.timestamp).getTime(), value: sample.network.wifi.signal }]
                : []
            )}
          />
          <StorageCard
            label="Muestras en memoria"
            value={storage?.metrics_count ?? "No disponible"}
            hint={
              storage?.latest_metric_at
                ? `No persistentes • última: ${new Date(storage.latest_metric_at).toLocaleTimeString()}`
                : "Sin muestras disponibles"
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
            label="Alertas de CPU/RAM activas"
            value={anomaliesAvailable ? anomalies.length : "No disponible"}
            hint={anomaliesAvailable ? "Lectura actual; no es historial persistido" : "Fuente de métricas no disponible"}
            onClick={() => open("anomalies")}
            color={{
              bg: "amber",
              border: "hover:border-amber-400/50",
              shadow: "251,191,36",
              gradient: "bg-gradient-to-r from-amber-400 to-orange-400",
            }}
          />
          <StorageCard
            label="Base de datos"
            value="No disponible"
            hint="El runtime Cortex no entrega métricas de base de datos"
            onClick={() => router.push("/db")}
            color={{
              bg: "emerald",
              border: "hover:border-emerald-400/50",
              shadow: "16,185,129",
              gradient: "bg-gradient-to-r from-emerald-400 to-teal-400",
            }}
          />
        </section>

        {/* Detail Modal */}
        <DetailModal
          isOpen={modal.isOpen}
          onClose={close}
          type={modal.type}
          storage={storage}
          anomalies={anomalies}
          anomaliesAvailable={anomaliesAvailable}
        />

        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Estado del runtime</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between gap-4">
                <span className="text-gray-400">Última muestra</span>
                <span className="text-cyan-200">
                  {data ? new Date(data.sampled_at).toLocaleString() : "No disponible"}
                </span>
              </div>
              <div className="flex justify-between gap-4">
                <span className="text-gray-400">Almacenamiento de métricas</span>
                <span className="text-gray-200">
                  {storage ? `${storage.storage_type}; ${storage.persisted ? "persistente" : "solo memoria"}` : "No disponible"}
                </span>
              </div>
              {runtime?.subsystems && Object.entries(runtime.subsystems).map(([name, status]) => (
                <div className="flex justify-between gap-4" key={name}>
                  <span className="text-gray-400">{name}</span>
                  <span className="text-gray-200">{status}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-3">Presión del sistema</h3>
            {!anomaliesAvailable ? (
              <p className="text-sm text-gray-400">La fuente de métricas no está disponible.</p>
            ) : issues.length === 0 ? (
              <p className="text-sm text-gray-300">Sin superaciones de umbral en la lectura actual.</p>
            ) : (
              <ul className="space-y-2 text-sm text-amber-100">
                {issues.map((issue) => <li key={issue}>{issue}</li>)}
              </ul>
            )}
          </div>
        </section>

        {loading ? <div className="mt-6 text-sm text-gray-300">Cargando métricas…</div> : null}
      </div>
    </main>
  );
}
