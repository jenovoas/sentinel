"use client";

import { useEffect, useState } from "react";
import { useAnalytics } from "@/hooks/useAnalytics";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function AnalyticsPage() {
  const { history, anomalies, storage, loading } = useAnalytics();
  const [hostHistory, setHostHistory] = useState<any[]>([]);
  const [systemLogs, setSystemLogs] = useState<any>({ logs: [], summary: null });

  // Cargar historial completo del host
  useEffect(() => {
    const fetchHostHistory = async () => {
      try {
        const res = await fetch("/api/host-metrics?limit=100", { cache: "no-store" });
        const json = await res.json();
        if (json?.ok && json.history) {
          setHostHistory(json.history);
        }
      } catch { }
    };
    fetchHostHistory();
    const id = setInterval(fetchHostHistory, 60000);
    return () => clearInterval(id);
  }, []);

  // Cargar logs del sistema
  useEffect(() => {
    const fetchSystemLogs = async () => {
      try {
        const res = await fetch("/api/system-logs?limit=50", { cache: "no-store" });
        const json = await res.json();
        if (json?.ok) {
          setSystemLogs({ logs: json.logs, summary: json.summary });
        }
      } catch { }
    };
    fetchSystemLogs();
    const id = setInterval(fetchSystemLogs, 60000);
    return () => clearInterval(id);
  }, []);

  // Preparar datos para gráficos
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#e5e7eb',
          font: { size: 12 },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleColor: '#e5e7eb',
        bodyColor: '#e5e7eb',
        borderColor: 'rgba(56, 189, 248, 0.3)',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#9ca3af' },
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#9ca3af' },
        beginAtZero: true,
        max: 100,
      },
    },
  };

  const cpuData = {
    labels: hostHistory.map((s) => new Date(s.timestamp).toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'CPU Host',
        data: hostHistory.map((s) => s.cpu_percent),
        borderColor: '#22d3ee',
        backgroundColor: 'rgba(34, 211, 238, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'CPU Docker',
        data: history.cpu.map((s) => s.value),
        borderColor: '#06b6d4',
        backgroundColor: 'rgba(6, 182, 212, 0.1)',
        fill: true,
        tension: 0.4,
        borderDash: [5, 5],
      },
    ],
  };

  const memoryData = {
    labels: hostHistory.map((s) => new Date(s.timestamp).toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'Memoria Host',
        data: hostHistory.map((s) => s.mem_percent),
        borderColor: '#34d399',
        backgroundColor: 'rgba(52, 211, 153, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Memoria Docker',
        data: history.memory.map((s) => s.value),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
        borderDash: [5, 5],
      },
    ],
  };

  const gpuData = {
    labels: hostHistory.map((s) => new Date(s.timestamp).toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'GPU Host',
        data: hostHistory.map((s) => s.gpu_percent),
        borderColor: '#a78bfa',
        backgroundColor: 'rgba(167, 139, 250, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'GPU Docker',
        data: history.gpu.map((s) => s.value),
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        fill: true,
        tension: 0.4,
        borderDash: [5, 5],
      },
    ],
  };

  const wifiData = {
    labels: hostHistory.map((s) => new Date(s.timestamp).toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'Señal WiFi (%)',
        data: hostHistory.map((s) => s.network?.wifi?.signal ?? 0),
        borderColor: '#fb923c',
        backgroundColor: 'rgba(251, 146, 60, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const stats = {
    cpu: {
      current: hostHistory[hostHistory.length - 1]?.cpu_percent ?? 0,
      avg: hostHistory.reduce((sum, s) => sum + s.cpu_percent, 0) / (hostHistory.length || 1),
      max: Math.max(...hostHistory.map((s) => s.cpu_percent), 0),
      min: Math.min(...hostHistory.map((s) => s.cpu_percent), 100),
    },
    memory: {
      current: hostHistory[hostHistory.length - 1]?.mem_percent ?? 0,
      avg: hostHistory.reduce((sum, s) => sum + s.mem_percent, 0) / (hostHistory.length || 1),
      max: Math.max(...hostHistory.map((s) => s.mem_percent), 0),
      min: Math.min(...hostHistory.map((s) => s.mem_percent), 100),
    },
    gpu: {
      current: hostHistory[hostHistory.length - 1]?.gpu_percent ?? 0,
      avg: hostHistory.reduce((sum, s) => sum + s.gpu_percent, 0) / (hostHistory.length || 1),
      max: Math.max(...hostHistory.map((s) => s.gpu_percent), 0),
    },
    wifi: {
      current: hostHistory[hostHistory.length - 1]?.network?.wifi?.signal ?? 0,
      avg: hostHistory.reduce((sum, s) => sum + (s.network?.wifi?.signal ?? 0), 0) / (hostHistory.length || 1),
      ssid: hostHistory[hostHistory.length - 1]?.network?.wifi?.ssid ?? "N/A",
    },
  };

  if (loading && hostHistory.length === 0) {
    return (
      <main className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100">
        <div className="relative mx-auto max-w-7xl px-6 py-10">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-gray-400">Cargando analytics...</p>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100">
      <div
        className="absolute inset-0 opacity-50 blur-3xl bg-[radial-gradient(circle_at_20%_20%,rgba(34,211,238,0.12),transparent_35%),radial-gradient(circle_at_80%_0%,rgba(16,185,129,0.12),transparent_30%),radial-gradient(circle_at_70%_80%,rgba(59,130,246,0.12),transparent_25%)]"
        aria-hidden
      />
      <div className="relative mx-auto max-w-7xl px-6 py-10">
        {/* Header */}
        <header className="mb-8">
          <p className="text-sm uppercase tracking-[0.25em] text-cyan-200/70">Sentinel</p>
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white">
            Analytics Dashboard
          </h1>
          <p className="text-gray-300 mt-2 max-w-2xl">
            Análisis comparativo de métricas del host vs contenedores Docker
          </p>
        </header>

        {/* Stats Cards */}
        <section className="grid gap-4 md:grid-cols-4 mb-8">
          <StatCard
            label="CPU Actual"
            value={`${stats.cpu.current.toFixed(1)}%`}
            stats={[
              { label: "Promedio", value: `${stats.cpu.avg.toFixed(1)}%` },
              { label: "Máximo", value: `${stats.cpu.max.toFixed(1)}%` },
            ]}
            color="cyan"
          />
          <StatCard
            label="Memoria Actual"
            value={`${stats.memory.current.toFixed(1)}%`}
            stats={[
              { label: "Promedio", value: `${stats.memory.avg.toFixed(1)}%` },
              { label: "Máximo", value: `${stats.memory.max.toFixed(1)}%` },
            ]}
            color="emerald"
          />
          <StatCard
            label="GPU Actual"
            value={`${stats.gpu.current.toFixed(1)}%`}
            stats={[
              { label: "Promedio", value: `${stats.gpu.avg.toFixed(1)}%` },
              { label: "Máximo", value: `${stats.gpu.max.toFixed(1)}%` },
            ]}
            color="purple"
          />
          <StatCard
            label="WiFi"
            value={`${stats.wifi.current}%`}
            stats={[
              { label: "Promedio", value: `${stats.wifi.avg.toFixed(1)}%` },
              { label: "Red", value: stats.wifi.ssid },
            ]}
            color="orange"
          />
        </section>

        {/* Charts Grid */}
        <section className="grid gap-6 md:grid-cols-2">
          <ChartCard title="CPU Usage" subtitle="Host vs Docker">
            <Line data={cpuData} options={chartOptions} />
          </ChartCard>
          <ChartCard title="Memory Usage" subtitle="Host vs Docker">
            <Line data={memoryData} options={chartOptions} />
          </ChartCard>
          <ChartCard title="GPU Usage" subtitle="Host vs Docker">
            <Line data={gpuData} options={chartOptions} />
          </ChartCard>
          <ChartCard title="WiFi Signal" subtitle="Señal en tiempo real">
            <Line data={wifiData} options={chartOptions} />
          </ChartCard>
        </section>

        {/* Anomalies & Storage */}
        <section className="mt-8 grid gap-6 md:grid-cols-2">
          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Anomalías Detectadas</h3>
            {anomalies.length === 0 ? (
              <p className="text-gray-400 text-sm">No se detectaron anomalías en las últimas 24h</p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {anomalies.slice(0, 5).map((a, i) => (
                  <div key={i} className="bg-white/5 rounded-lg p-3 border border-rose-500/20">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-rose-300">{a.metric}</span>
                      <span className="text-xs text-gray-400">
                        {new Date(a.timestamp).toLocaleString('es')}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400">
                      Valor: {a.metricValue != null ? a.metricValue.toFixed(2) : 'N/A'}%
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4">System Logs</h3>
            {systemLogs.summary && (
              <div className="grid grid-cols-3 gap-2 mb-4">
                <div className="bg-rose-500/10 border border-rose-500/20 rounded-lg p-2 text-center">
                  <p className="text-2xl font-bold text-rose-400">{systemLogs.summary.critical_count}</p>
                  <p className="text-xs text-gray-400">Critical</p>
                </div>
                <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-2 text-center">
                  <p className="text-2xl font-bold text-amber-400">{systemLogs.summary.error_count}</p>
                  <p className="text-xs text-gray-400">Errors</p>
                </div>
                <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-2 text-center">
                  <p className="text-2xl font-bold text-orange-400">{systemLogs.summary.warning_count}</p>
                  <p className="text-xs text-gray-400">Warnings</p>
                </div>
              </div>
            )}
            {systemLogs.logs.length === 0 ? (
              <p className="text-gray-400 text-sm">Sin logs recientes</p>
            ) : (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {systemLogs.logs.slice(0, 10).map((log: any, i: number) => (
                  <div
                    key={i}
                    className={`bg-white/5 rounded-lg p-2 border text-xs ${log.level === 'CRITICAL' ? 'border-rose-500/30' :
                      log.level === 'ERROR' ? 'border-amber-500/30' :
                        'border-orange-500/20'
                      }`}
                  >
                    <div className="flex items-start gap-2 mb-1">
                      <span className={`font-semibold whitespace-nowrap ${log.level === 'CRITICAL' ? 'text-rose-400' :
                        log.level === 'ERROR' ? 'text-amber-400' :
                          'text-orange-400'
                        }`}>
                        {log.level}
                      </span>
                      <span className="text-gray-500 text-xs whitespace-nowrap">
                        {new Date(log.timestamp).toLocaleTimeString('es')}
                      </span>
                      <span className="text-cyan-400 text-xs">{log.unit}</span>
                    </div>
                    <p className="text-gray-300 text-xs truncate">{log.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Storage Summary */}
        <section className="mt-6">
          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Storage Summary</h3>
            {storage ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Métricas guardadas</span>
                  <span className="text-2xl font-semibold text-cyan-400">{storage.metrics_count}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Anomalías totales</span>
                  <span className="text-2xl font-semibold text-rose-400">{storage.anomalies_count}</span>
                </div>
                {storage.latest_metric_at && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Última métrica</span>
                    <span className="text-sm text-gray-400">
                      {new Date(storage.latest_metric_at).toLocaleString('es')}
                    </span>
                  </div>
                )}
                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-xs text-gray-400">
                    {hostHistory.length} muestras del host cargadas
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-gray-400 text-sm">Cargando información de almacenamiento...</p>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

const StatCard = ({
  label,
  value,
  stats,
  color,
}: {
  label: string;
  value: string;
  stats: Array<{ label: string; value: string }>;
  color: string;
}) => {
  const colors: Record<string, { border: string; text: string; bg: string }> = {
    cyan: { border: 'border-cyan-500/20', text: 'text-cyan-400', bg: 'bg-cyan-500/10' },
    emerald: { border: 'border-emerald-500/20', text: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    purple: { border: 'border-purple-500/20', text: 'text-purple-400', bg: 'bg-purple-500/10' },
    orange: { border: 'border-orange-500/20', text: 'text-orange-400', bg: 'bg-orange-500/10' },
  };
  const c = colors[color];

  return (
    <div className={`rounded-2xl border ${c.border} bg-white/5 backdrop-blur-xl p-4`}>
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className={`text-3xl font-semibold ${c.text} mb-3`}>{value}</p>
      <div className="space-y-1">
        {stats.map((s, i) => (
          <div key={i} className="flex justify-between text-xs">
            <span className="text-gray-400">{s.label}</span>
            <span className="text-gray-300">{s.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const ChartCard = ({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) => (
  <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
    <div className="mb-4">
      <h3 className="text-xl font-semibold text-white">{title}</h3>
      <p className="text-sm text-gray-400">{subtitle}</p>
    </div>
    <div className="h-64">{children}</div>
  </div>
);
