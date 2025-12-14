/**
 * StorageCard Component
 * Reusable card for storage stats with consistent styling
 */

import React from "react";

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
}

export const StorageCard: React.FC<StorageCardProps> = ({
  label,
  value,
  hint,
  onClick,
  color,
}) => {
  return (
    <div
      onClick={onClick}
      className={`rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl p-4 shadow-[0_20px_60px_-30px_rgba(${color.shadow},0.2)] transition-all duration-300 ${color.border} hover:bg-white/10 hover:shadow-[0_30px_90px_-40px_rgba(${color.shadow},0.6)] hover:scale-[1.02] cursor-pointer`}
    >
      <p className="text-sm text-gray-300 mb-1 transition-colors duration-300">
        {label}
      </p>
      <p className="text-3xl font-semibold text-white">{value}</p>
      <p className="text-xs text-gray-400 mt-2 transition-colors duration-300">
        {hint}
      </p>
      <div className={`mt-3 h-1 rounded-full ${color.gradient} transition-opacity duration-300 hover:opacity-100 opacity-80`} />
    </div>
  );
};
