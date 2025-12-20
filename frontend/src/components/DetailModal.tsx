/**
 * DetailModal Component
 * Modal displaying detailed info for storage metrics
 * Follows Open/Closed Principle - open for extension via content variants
 */

import React from "react";
import { StorageSummary, AnomalyPoint } from "@/lib/types";

interface DetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: "metrics" | "anomalies" | "database" | null;
  storage: StorageSummary | null;
  anomalies: AnomalyPoint[];
}

const formatBytes = (bytes: number) => {
  if (!Number.isFinite(bytes)) return "-";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** i;
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[i]}`;
};

const DetailContent: React.FC<{
  type: "metrics" | "anomalies" | "database";
  storage: StorageSummary | null;
  anomalies: AnomalyPoint[];
}> = ({ type, storage, anomalies }) => {
  switch (type) {
    case "metrics":
      return (
        <>
          <div className="rounded-lg border border-white/5 bg-black/40 p-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Total de muestras guardadas</span>
              <span className="text-2xl font-bold text-cyan-400">{storage?.metrics_count ?? 0}</span>
            </div>
          </div>
          <div className="rounded-lg border border-white/5 bg-black/40 p-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Última muestra</span>
              <span className="text-sm text-gray-200">
                {storage?.latest_metric_at ? new Date(storage.latest_metric_at).toLocaleString() : "N/A"}
              </span>
            </div>
          </div>
          <div className="rounded-lg border border-white/5 bg-black/40 p-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Estado</span>
              <span className={`text-sm font-semibold ${storage?.status === "healthy" ? "text-emerald-400" : "text-rose-400"}`}>
                {storage?.status === "healthy" ? "✓ Datos fluyendo" : "⚠ Sin datos"}
              </span>
            </div>
          </div>
          <div className="rounded-lg border border-white/5 bg-black/40 p-4 text-xs text-gray-400 space-y-1">
            <p>• Las métricas se recopilan cada 15 segundos</p>
            <p>• Se mantienen 90 días de histórico</p>
            <p>• Incluye CPU, Memoria, GPU, Red y DB stats</p>
          </div>
        </>
      );

    case "anomalies":
      return (
        <>
          <div className="rounded-lg border border-white/5 bg-black/40 p-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Total de anomalías detectadas</span>
              <span className="text-2xl font-bold text-amber-400">{anomalies.length ?? 0}</span>
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
                    <span
                      className={`px-2 py-1 rounded text-xs font-semibold ${a.severity === "critical"
                          ? "bg-rose-500/20 text-rose-300"
                          : a.severity === "warning"
                            ? "bg-amber-500/20 text-amber-300"
                            : "bg-cyan-500/20 text-cyan-300"
                        }`}
                    >
                      {a.severity}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      );

    case "database":
      return (
        <>
          <div className="rounded-lg border border-white/5 bg-black/40 p-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Tamaño total de la BD</span>
              <span className="text-2xl font-bold text-emerald-400">
                {formatBytes(storage?.db_size_bytes ?? 0)}
              </span>
            </div>
          </div>
          <div className="rounded-lg border border-white/5 bg-black/40 p-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-400">Métricas en BD</p>
                <p className="text-xl font-semibold text-cyan-400">{storage?.metrics_count ?? 0}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Anomalías en BD</p>
                <p className="text-xl font-semibold text-amber-400">{storage?.anomalies_count ?? 0}</p>
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
      );
  }
};

const getTitleAndColor = (
  type: "metrics" | "anomalies" | "database"
): { title: string; color: string } => {
  switch (type) {
    case "metrics":
      return { title: "Métricas Guardadas", color: "#22d3ee" };
    case "anomalies":
      return { title: "Anomalías Detectadas", color: "#fbbf24" };
    case "database":
      return { title: "Base de Datos", color: "#10b981" };
  }
};

export const DetailModal: React.FC<DetailModalProps> = ({
  isOpen,
  onClose,
  type,
  storage,
  anomalies,
}) => {
  if (!isOpen || !type) return null;

  const { title } = getTitleAndColor(type);

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
            <h2 className="text-2xl font-bold text-white">{title}</h2>
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
          <DetailContent type={type} storage={storage} anomalies={anomalies} />
        </div>
      </div>
    </div>
  );
};
