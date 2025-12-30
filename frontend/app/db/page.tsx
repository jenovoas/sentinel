"use client";

import { useEffect, useState } from "react";

type DbStats = {
  connections_total: number;
  connections_active: number;
  connections_idle: number;
  db_size_bytes: number;
  locks: number;
};

type ActiveQuery = {
  pid: number;
  user: string;
  state: string;
  wait_event: string;
  duration_seconds: number;
  query: string;
};

type DashboardData = {
  db_health: { status: "healthy" | "unhealthy" };
  db_stats: DbStats;
  db_activity: ActiveQuery[];
};

const API_PATH = "/api/v1/dashboard/status";

const formatBytes = (bytes: number) => {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let i = 0;
  let v = bytes;
  while (v > 1024 && i < units.length - 1) {
    v /= 1024;
    i++;
  }
  return `${v.toFixed(v >= 10 ? 0 : 1)} ${units[i]}`;
};

export default function DatabasesPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();
  const [filterUser, setFilterUser] = useState<string>("");
  const [sortByDuration, setSortByDuration] = useState<boolean>(true);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const res = await fetch(API_PATH, { cache: "no-store" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as DashboardData;
        setData(json);
        setError(undefined);
      } catch (e: any) {
        setError(e?.message || "Error");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-semibold text-gray-200">Bases de Datos</h1>
      {/* Controles */}
      <div className="flex flex-wrap items-center gap-3">
        <input
          value={filterUser}
          onChange={(e) => setFilterUser(e.target.value)}
          placeholder="Filtrar por usuario"
          className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-gray-200 placeholder:text-gray-500"
        />
        <label className="flex items-center gap-2 text-sm text-gray-300">
          <input type="checkbox" checked={sortByDuration} onChange={(e) => setSortByDuration(e.target.checked)} />
          Ordenar por duración
        </label>
        <button
          onClick={() => {
            if (!data) return;
            const rows = data.db_activity.map((q) => ({
              pid: q.pid,
              user: q.user,
              state: q.state,
              wait_event: q.wait_event,
              duration_seconds: q.duration_seconds,
              query: q.query.replace(/\n/g, " "),
            }));
            const header = Object.keys(rows[0] || { pid: "", user: "", state: "", wait_event: "", duration_seconds: 0, query: "" });
            const csv = [header.join(","), ...rows.map((r) => header.map((h) => String((r as any)[h]).replace(/","/g, "\"\,\"")).join(","))].join("\n");
            const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `db_activity_${Date.now()}.csv`;
            a.click();
            URL.revokeObjectURL(url);
          }}
          className="px-3 py-2 rounded-lg bg-cyan-500/20 text-cyan-200 border border-cyan-400/30 text-sm hover:bg-cyan-500/30"
        >
          Exportar CSV
        </button>
      </div>
      {loading && (
        <div className="rounded-xl border border-white/5 bg-white/5 p-4">Cargando…</div>
      )}
      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-300">
          {error}
        </div>
      )}

      {data && (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Estado e instancia actual */}
          <div className="rounded-xl border border-white/5 bg-white/5 p-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium text-gray-300">Instancia</h2>
              <span
                className={`text-xs px-2 py-1 rounded-full ${data.db_health.status === "healthy"
                    ? "bg-emerald-500/15 text-emerald-300"
                    : "bg-rose-500/15 text-rose-300"
                  }`}
              >
                {data.db_health.status}
              </span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-gray-400">Conexiones activas</p>
                <p className="font-mono text-orange-300">{data.db_stats.connections_active}</p>
              </div>
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-gray-400">Conexiones totales</p>
                <p className="font-mono text-orange-300">{data.db_stats.connections_total}</p>
              </div>
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-gray-400">Locks</p>
                <p className="font-mono text-orange-300">{data.db_stats.locks}</p>
              </div>
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-gray-400">Tamaño DB</p>
                <p className="font-mono text-orange-300">{formatBytes(data.db_stats.db_size_bytes)}</p>
              </div>
            </div>
          </div>

          {/* Consultas activas */}
          <div className="rounded-xl border border-white/5 bg-white/5 p-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium text-gray-300">Consultas activas</h2>
              <span className="text-xs text-gray-400">{data.db_activity.length}</span>
            </div>
            <div className="mt-3 space-y-3">
              {data.db_activity.length === 0 && (
                <p className="text-sm text-gray-500">Sin consultas activas</p>
              )}
              {data && (
                (data.db_activity
                  .filter((q) => (filterUser ? q.user.toLowerCase().includes(filterUser.toLowerCase()) : true))
                  .sort((a, b) => (sortByDuration ? b.duration_seconds - a.duration_seconds : 0))
                ).map((q) => (
                  <div key={q.pid} className="rounded-lg bg-white/5 p-3">
                    <div className="flex items-center justify-between">
                      <div className="text-xs text-gray-300">
                        <span className="font-mono">PID {q.pid}</span> · {q.user} · {q.state}
                      </div>
                      <div className="text-xs text-gray-400">{Math.round(q.duration_seconds)}s</div>
                    </div>
                    {q.wait_event && (
                      <p className="mt-1 text-xs text-amber-300">{q.wait_event}</p>
                    )}
                    <pre className="mt-2 whitespace-pre-wrap break-words text-xs text-gray-400">{q.query}</pre>
                  </div>
                )))
              }
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
