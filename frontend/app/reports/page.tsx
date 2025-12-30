"use client";

import { useEffect, useState } from "react";

type ReportItem = {
  name: string;
  path: string;
  type: "html" | "md" | "csv" | "other";
};

export default function ReportsPage() {
  const [items, setItems] = useState<ReportItem[]>([]);
  const [error, setError] = useState<string | undefined>();

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch("/api/reports", { cache: "no-store" });
        const json = await res.json();
        if (json?.ok) setItems(json.items || []);
        else setError(json?.error || "Error");
      } catch (e: any) {
        setError(e?.message || "Error");
      }
    };
    load();
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-semibold text-gray-200">Informes</h1>
      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-300">{error}</div>
      )}
      <div className="grid gap-3 md:grid-cols-2">
        {items.length === 0 && (
          <div className="rounded-xl border border-white/5 bg-white/5 p-4 text-sm text-gray-400">Sin informes</div>
        )}
        {items.map((it) => (
          <div key={it.path} className="rounded-xl border border-white/5 bg-white/5 p-4 flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-200">{it.name}</p>
              <p className="text-xs text-gray-500">{it.type.toUpperCase()}</p>
            </div>
            <div className="flex items-center gap-2">
              {it.type === "html" ? (
                <a className="px-3 py-2 rounded-lg bg-cyan-500/20 text-cyan-200 border border-cyan-400/30 text-sm hover:bg-cyan-500/30" href={`/api/reports/view?path=${encodeURIComponent(it.path)}`} target="_blank" rel="noopener noreferrer">Ver</a>
              ) : null}
              <a className="px-3 py-2 rounded-lg bg-white/10 text-gray-200 border border-white/20 text-sm hover:bg-white/20" href={`/api/reports/download?path=${encodeURIComponent(it.path)}`}>Descargar</a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
