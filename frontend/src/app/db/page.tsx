"use client";

import { useEffect, useState } from "react";

type StorageSummary = {
  available: boolean;
  storage_type: string;
  persisted: boolean;
  metrics_count: number;
  anomalies_count: number | null;
  latest_metric_at: string | null;
  latest_anomaly_at: string | null;
  db_size_bytes: number | null;
  retention_capacity: number;
  status: string;
};

const API_PATH = "/api/v1/analytics/storage/summary";

const formatBytes = (bytes: number) => {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let i = 0;
  let value = bytes;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i++;
  }
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[i]}`;
};

export default function DatabasesPage() {
  const [data, setData] = useState<StorageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const response = await fetch(API_PATH, { cache: "no-store" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const summary = (await response.json()) as StorageSummary;
        if (!active) return;
        setData(summary);
        setError(null);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Error al consultar Cortex");
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();
    const intervalId = window.setInterval(() => void load(), 15_000);
    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const storageStatus = data?.status === "healthy"
    ? "Disponible"
    : data?.status === "no_data"
      ? "Sin muestras"
      : data?.status === "unavailable"
        ? "No disponible"
        : "N/D";

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-gray-200">Bases de Datos</h1>
        <p className="mt-1 text-sm text-gray-400">
          Cortex expone el resumen de su almacenamiento de métricas, pero no publica telemetría de instancias de base de datos.
        </p>
      </div>

      {loading && !data && (
        <div className="rounded-xl border border-white/5 bg-white/5 p-4 text-gray-300">Cargando resumen de Cortex…</div>
      )}
      {error && (
        <div role="status" className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-300">
          No se pudo actualizar Cortex ({error}).{data ? " Se conserva la última respuesta válida." : ""}
        </div>
      )}

      {data && (
        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-xl border border-white/5 bg-white/5 p-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-sm font-medium text-gray-300">Almacenamiento de métricas Cortex</h2>
              <span className={`rounded-full px-2 py-1 text-xs ${data.available ? "bg-cyan-500/15 text-cyan-300" : "bg-gray-500/15 text-gray-300"}`}>
                {storageStatus}
              </span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-gray-400">Tipo</p>
                <p className="font-mono text-cyan-300">{data.storage_type || "N/D"}</p>
              </div>
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-gray-400">Persistencia</p>
                <p className="font-mono text-cyan-300">{data.persisted ? "Persistente" : "Solo memoria"}</p>
              </div>
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-gray-400">Muestras actuales</p>
                <p className="font-mono text-cyan-300">{data.metrics_count.toLocaleString()}</p>
              </div>
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-gray-400">Capacidad de retención</p>
                <p className="font-mono text-cyan-300">{data.retention_capacity.toLocaleString()}</p>
              </div>
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-gray-400">Última muestra</p>
                <p className="font-mono text-cyan-300">{data.latest_metric_at ? new Date(data.latest_metric_at).toLocaleString() : "N/D"}</p>
              </div>
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-gray-400">Tamaño de base de datos</p>
                <p className="font-mono text-gray-400">{data.db_size_bytes == null ? "N/D" : formatBytes(data.db_size_bytes)}</p>
              </div>
            </div>
          </section>

          <section className="rounded-xl border border-white/5 bg-white/5 p-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium text-gray-300">Telemetría de base de datos</h2>
              <span className="rounded-full bg-gray-500/15 px-2 py-1 text-xs text-gray-300">No disponible</span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
              {["Conexiones activas", "Conexiones totales", "Locks", "Consultas activas"].map((label) => (
                <div key={label} className="rounded-lg bg-white/5 p-3">
                  <p className="text-gray-400">{label}</p>
                  <p className="font-mono text-gray-400">N/D</p>
                </div>
              ))}
            </div>
            <p className="mt-4 text-sm text-gray-500">
              La API actual de Cortex no proporciona salud de la base de datos, conexiones ni un feed de consultas activas.
            </p>
          </section>
        </div>
      )}
    </div>
  );
}
