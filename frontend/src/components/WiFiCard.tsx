/**
 * WiFiCard Component
 * Displays WiFi network info with signal strength indicator
 */

import React from "react";

export interface WiFiInfo {
  ssid: string;
  signal: number;
  connected: boolean;
}

interface WiFiCardProps {
  wifi?: WiFiInfo;
}

export const WiFiCard: React.FC<WiFiCardProps> = ({ wifi }) => {
  if (!wifi || !wifi.connected) {
    return (
      <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(139,92,246,0.2)]">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-300 mb-1">WiFi</p>
            <p className="text-lg font-semibold text-gray-400">Desconectado</p>
          </div>
          <svg
            className="w-8 h-8 text-gray-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"
            />
          </svg>
        </div>
      </div>
    );
  }

  // Determine signal color and bars
  const getSignalColor = () => {
    if (wifi.signal >= 75) return "text-emerald-400";
    if (wifi.signal >= 50) return "text-cyan-400";
    if (wifi.signal >= 25) return "text-amber-400";
    return "text-rose-400";
  };

  const getSignalLabel = () => {
    if (wifi.signal >= 75) return "Excelente";
    if (wifi.signal >= 50) return "Bueno";
    if (wifi.signal >= 25) return "Regular";
    return "Débil";
  };

  return (
    <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(139,92,246,0.2)] hover:shadow-[0_30px_90px_-40px_rgba(139,92,246,0.6)] transition-all duration-300">
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-sm text-gray-300 mb-1">WiFi</p>
          <p className="text-base font-semibold text-white truncate max-w-[200px]">
            {wifi.ssid}
          </p>
        </div>
        <svg
          className={`w-8 h-8 ${getSignalColor()}`}
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z" />
        </svg>
      </div>

      <div className="space-y-2">
        {/* Signal bars */}
        <div className="flex items-end gap-1">
          {[0, 1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className={`transition-opacity duration-300 ${
                wifi.signal > i * 20
                  ? getSignalColor().replace("text-", "bg-")
                  : "bg-white/10"
              }`}
              style={{
                height: `${8 + i * 3}px`,
                width: "4px",
                borderRadius: "2px",
              }}
            />
          ))}
        </div>

        {/* Signal info */}
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400">{getSignalLabel()}</span>
          <span className={`font-semibold ${getSignalColor()}`}>{wifi.signal}%</span>
        </div>
      </div>

      <div className="mt-3 h-1 rounded-full bg-gradient-to-r from-violet-400 to-purple-400 opacity-80" />
    </div>
  );
};
