/**
 * StorageCard Component
 * Reusable card for storage stats with consistent styling
 */

import React from "react";
import { MiniChart } from "./MiniChart";

export interface StorageCardProps {
  label: string;
  value: React.ReactNode;
  hint: string;
  onClick: () => void;
  color: {
    bg: string; // bg color class
    border: string; // border hover class
    shadow: string; // shadow rgb values
    gradient: string; // gradient class
  };
  history?: Array<{ timestamp: number; value: number }>;
}

export const StorageCard: React.FC<StorageCardProps> = ({
  label,
  value,
  hint,
  onClick,
  color,
  history,
}) => {
  return (
    <div
      onClick={onClick}
      className={`rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(${color.shadow},0.2)] transition-all duration-300 ${color.border} hover:bg-white/10 hover:shadow-[0_30px_90px_-40px_rgba(${color.shadow},0.6)] hover:scale-[1.02] cursor-pointer flex flex-col gap-3`}
    >
      <div>
        <p className="text-sm text-gray-300 mb-1 transition-colors duration-300">
          {label}
        </p>
        <p className="text-3xl font-semibold text-white">{value}</p>
        <p className="text-xs text-gray-400 mt-2 transition-colors duration-300">
          {hint}
        </p>
      </div>
      {history && history.length > 0 && (
        <div className="h-10">
          <MiniChart data={history} color={`rgb(${color.shadow})`} height={40} />
        </div>
      )}
      <div className={`h-1 rounded-full ${color.gradient} transition-opacity duration-300 hover:opacity-100 opacity-80`} />
    </div>
  );
};
