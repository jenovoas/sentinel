"use client";

/**
 * NetworkCard Component (Enhanced)
 * Displays network statistics with WiFi info
 * Supports both server-side (Docker) and client-side (Browser API) WiFi detection
 * Uses client WiFi when available (more accurate)
 */

import React from "react";
import type { ClientNetworkInfo } from "@/hooks/useNetworkInfo";
import { MiniChart } from "./MiniChart";

export interface NetworkInfo {
  net_bytes_sent: number;
  net_bytes_recv: number;
  net_packets_sent: number;
  net_packets_recv: number;
  wifi?: {
    ssid: string;
    signal: number;
    connected: boolean;
  };
}

interface NetworkCardProps {
  network?: NetworkInfo;
  clientNetwork?: ClientNetworkInfo;
  history?: Array<{ timestamp: number; value: number }>;
}

const formatBytes = (bytes: number): string => {
  if (!Number.isFinite(bytes)) return "-";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** i;
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[i]}`;
};

export const NetworkCard: React.FC<NetworkCardProps> = ({ network, clientNetwork, history }) => {
  // Prefer client WiFi info (browser API) over server info (Docker container)
  const effectiveWifi = clientNetwork?.wifi?.connected ? clientNetwork.wifi : network?.wifi;

  if (!network && !clientNetwork) {
    return (
      <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(249,115,22,0.2)] hover:shadow-[0_20px_60px_-20px_rgba(249,115,22,0.3)] transition-all duration-300">
        <p className="text-sm text-gray-400">Sin datos de red</p>
      </div>
    );
  }

  const totalBytes = (network?.net_bytes_sent ?? 0) + (network?.net_bytes_recv ?? 0);
  const totalGB = totalBytes / (1024 * 1024 * 1024);

  // WiFi signal color psychology
  const getWiFiSignalColor = () => {
    if (!effectiveWifi?.connected)
      return { color: "text-gray-500", bg: "bg-gray-500/10", label: "Desconectado" };
    const signal = effectiveWifi.signal ?? (effectiveWifi as any).signalStrength ?? 0;
    if (signal >= 75) return { color: "text-emerald-400", bg: "bg-emerald-400/10", label: "Excelente" };
    if (signal >= 50) return { color: "text-cyan-400", bg: "bg-cyan-400/10", label: "Bueno" };
    if (signal >= 25) return { color: "text-amber-400", bg: "bg-amber-400/10", label: "Moderado" };
    return { color: "text-rose-400", bg: "bg-rose-400/10", label: "Débil" };
  };

  const wifiState = getWiFiSignalColor();

  // Render WiFi signal bars
  const renderSignalBars = () => {
    if (!effectiveWifi?.connected) {
      return (
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="w-1 h-4 bg-gray-600 rounded-sm opacity-30"
            />
          ))}
        </div>
      );
    }

    const signal = (effectiveWifi.signal ?? (effectiveWifi as any).signalStrength ?? 0) as number;
    const bars = Math.ceil((signal / 100) * 4);
    return (
      <div className="flex items-end gap-1">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`w-1 rounded-sm transition-all duration-300 ${i <= bars ? `${wifiState.color} h-${4 + i}` : "bg-gray-600/30 h-2"
              }`}
            style={{
              height: i <= bars ? `${4 + i * 2}px` : "8px",
            }}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(249,115,22,0.2)] hover:shadow-[0_20px_60px_-20px_rgba(249,115,22,0.3)] transition-all duration-300 group hover:bg-white/[0.08]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-orange-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" />
          </svg>
          <h3 className="text-sm font-semibold text-gray-200 group-hover:text-orange-300 transition-colors">Red</h3>
        </div>
        <div className="text-xs px-2 py-1 rounded-full bg-orange-400/10 text-orange-300">
          {totalGB.toFixed(1)} GB
        </div>
      </div>

      {/* Network Stats Grid */}
      {network && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-white/5 rounded-lg p-2.5 hover:bg-white/10 transition-colors">
            <p className="text-xs text-gray-400 mb-1">↑ Enviados</p>
            <p className="text-sm font-mono text-orange-300">
              {formatBytes(network.net_bytes_sent)}
            </p>
          </div>
          <div className="bg-white/5 rounded-lg p-2.5 hover:bg-white/10 transition-colors">
            <p className="text-xs text-gray-400 mb-1">↓ Recibidos</p>
            <p className="text-sm font-mono text-orange-300">
              {formatBytes(network.net_bytes_recv)}
            </p>
          </div>
          <div className="bg-white/5 rounded-lg p-2.5 hover:bg-white/10 transition-colors">
            <p className="text-xs text-gray-400 mb-1">📤 Paquetes</p>
            <p className="text-sm font-mono text-orange-300">
              {(network.net_packets_sent / 1000).toFixed(1)}k
            </p>
          </div>
          <div className="bg-white/5 rounded-lg p-2.5 hover:bg-white/10 transition-colors">
            <p className="text-xs text-gray-400 mb-1">📥 Paquetes</p>
            <p className="text-sm font-mono text-orange-300">
              {(network.net_packets_recv / 1000).toFixed(1)}k
            </p>
          </div>
        </div>
      )}

      {/* WiFi Section */}
      {effectiveWifi && (
        <div className={`rounded-lg p-3 border border-white/5 ${wifiState.bg}`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <svg className={`w-4 h-4 ${wifiState.color}`} fill="currentColor" viewBox="0 0 24 24">
                <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z" />
              </svg>
              <span className="text-xs font-medium text-gray-300">
                {effectiveWifi.connected
                  ? effectiveWifi.ssid || (effectiveWifi as any).frequency ? "Conectado" : "Conectado"
                  : "Desconectado"}
              </span>
            </div>
            {renderSignalBars()}
          </div>

          {effectiveWifi.connected && (
            <div className="flex items-center justify-between text-xs mb-2">
              <span className={`${wifiState.color} font-semibold`}>{wifiState.label}</span>
              <span className="text-gray-400">
                {(effectiveWifi.signal ?? (effectiveWifi as any).signalStrength ?? 0)}%
              </span>
            </div>
          )}

          {/* History Chart */}
          {history && history.length > 0 && (
            <div className="mt-2 h-10">
              <MiniChart data={history} color={wifiState.color.replace('text-', '#')} height={40} />
            </div>
          )}

          {/* Show source of WiFi info */}
          <p className="text-xs text-gray-500 mt-2">
            {clientNetwork?.wifi?.connected ? "WiFi del navegador" : "WiFi del servidor"}
          </p>
        </div>
      )}
    </div>
  );
};
