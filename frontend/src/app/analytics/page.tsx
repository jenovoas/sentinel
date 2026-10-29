"use client";

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
  const { history, metricsAvailable, anomalies, anomaliesAvailable, storage, loading } = useAnalytics();

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
    labels: history.cpu.map((sample) => new Date(sample.timestamp).toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'CPU Cortex',
        data: history.cpu.map((sample) => sample.value),
        borderColor: '#22d3ee',
        backgroundColor: 'rgba(34, 211, 238, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const memoryData = {
    labels: history.memory.map((sample) => new Date(sample.timestamp).toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'Memoria Cortex',
        data: history.memory.map((sample) => sample.value),
        borderColor: '#34d399',
        backgroundColor: 'rgba(52, 211, 153, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const gpuData = {
    labels: history.gpu.map((sample) => new Date(sample.timestamp).toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'GPU Cortex',
        data: history.gpu.map((sample) => sample.value),
        borderColor: '#a78bfa',
        backgroundColor: 'rgba(167, 139, 250, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const summarize = (values: number[]) => ({
    current: values.length ? values[values.length - 1] : null,
    avg: values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null,
    max: values.length ? Math.max(...values) : null,
  });
  const stats = {
    cpu: summarize(history.cpu.map((sample) => sample.value)),
    memory: summarize(history.memory.map((sample) => sample.value)),
    gpu: summarize(history.gpu.map((sample) => sample.value)),
    wifi: { current: null, avg: null, max: null, ssid: "No disponible" },
  };
  const formatPercent = (value: number | null) =>
    value === null ? "No disponible" : `${value.toFixed(1)}%`;

  if (loading) {
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
            Historial de CPU y RAM recolectado por Cortex; GPU, WiFi y logs externos no disponibles en este contrato.
          </p>
        </header>

        {/* Stats Cards */}
        <section className="grid gap-4 md:grid-cols-4 mb-8">
          <StatCard
            label="CPU Actual"
            value={formatPercent(stats.cpu.current)}
            stats={[
              { label: "Promedio", value: formatPercent(stats.cpu.avg) },
              { label: "Máximo", value: formatPercent(stats.cpu.max) },
            ]}
            color="cyan"
          />
          <StatCard
            label="Memoria Actual"
            value={formatPercent(stats.memory.current)}
            stats={[
              { label: "Promedio", value: formatPercent(stats.memory.avg) },
              { label: "Máximo", value: formatPercent(stats.memory.max) },
            ]}
            color="emerald"
          />
          <StatCard
            label="GPU Actual"
            value={formatPercent(stats.gpu.current)}
            stats={[
              { label: "Promedio", value: formatPercent(stats.gpu.avg) },
              { label: "Máximo", value: formatPercent(stats.gpu.max) },
            ]}
            color="purple"
          />
          <StatCard
            label="WiFi"
            value={formatPercent(stats.wifi.current)}
            stats={[
              { label: "Promedio", value: formatPercent(stats.wifi.avg) },
              { label: "Red", value: stats.wifi.ssid },
            ]}
            color="orange"
          />
        </section>

        {/* Charts Grid */}
        <section className="grid gap-6 md:grid-cols-2">
          <ChartCard title="CPU" subtitle="Muestras del runtime Cortex">
            {history.cpu.length ? <Line data={cpuData} options={chartOptions} /> : <p className="text-sm text-gray-400">{metricsAvailable ? "Sin muestras disponibles" : "Fuente Cortex no disponible"}</p>}
          </ChartCard>
          <ChartCard title="Memoria" subtitle="Muestras del runtime Cortex">
            {history.memory.length ? <Line data={memoryData} options={chartOptions} /> : <p className="text-sm text-gray-400">{metricsAvailable ? "Sin muestras disponibles" : "Fuente Cortex no disponible"}</p>}
          </ChartCard>
          <ChartCard title="GPU" subtitle="No expuesta por Cortex">
            {history.gpu.length ? <Line data={gpuData} options={chartOptions} /> : <p className="text-sm text-gray-400">No disponible en Cortex</p>}
          </ChartCard>
          <ChartCard title="WiFi" subtitle="No expuesto por Cortex">
            <p className="text-sm text-gray-400">No disponible</p>
          </ChartCard>
        </section>

        {/* Anomalies & Storage */}
        <section className="mt-8 grid gap-6 md:grid-cols-2">
          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Anomalías Detectadas</h3>
            {!anomaliesAvailable ? (
              <p className="text-gray-400 text-sm">La fuente de métricas para anomalías no está disponible</p>
            ) : anomalies.length === 0 ? (
              <p className="text-gray-400 text-sm">No hay anomalías activas en la lectura actual de CPU/RAM</p>
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
            <h3 className="text-xl font-semibold text-white mb-4">Logs del sistema</h3>
            <p className="text-sm text-gray-400">
              Cortex no expone un feed de logs del host para esta vista. Los logs permanecen como no disponibles;
              la ausencia de feed no significa que no haya eventos.
            </p>
          </div>
        </section>

        {/* Storage Summary */}
        <section className="mt-6">
          <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Storage Summary</h3>
            {storage ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Muestras en memoria (no persistentes)</span>
                  <span className="text-2xl font-semibold text-cyan-400">{storage.metrics_count}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Anomalías totales</span>
                  <span className="text-2xl font-semibold text-rose-400">
                    {storage.anomalies_count ?? "No disponible"}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Última muestra</span>
                  <span className="text-sm text-gray-400">
                    {storage.latest_metric_at
                      ? new Date(storage.latest_metric_at).toLocaleString('es')
                      : "Sin muestras"}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Retención en memoria</span>
                  <span className="text-sm text-gray-400">
                    {storage.metrics_count} / {storage.retention_capacity} muestras
                  </span>
                </div>
                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-xs text-gray-400">
                    Almacenamiento: {storage.storage_type}; persistencia: {storage.persisted ? "activa" : "no persistente"}.
                    {storage.db_size_bytes == null ? " Tamaño de base de datos: no disponible." : ` Tamaño DB: ${storage.db_size_bytes} bytes.`}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-gray-400 text-sm">
                {loading ? "Cargando información de almacenamiento..." : "Resumen de almacenamiento no disponible"}
              </p>
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
