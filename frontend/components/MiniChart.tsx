"use client";

import React from "react";

type DataPoint = {
  timestamp: number;
  value: number;
};

type MiniChartProps = {
  data: DataPoint[];
  color?: string;
  height?: number;
  showDots?: boolean;
};

export const MiniChart: React.FC<MiniChartProps> = ({
  data,
  color = "#3b82f6",
  height = 40,
  showDots = false,
}) => {
  if (!data || data.length === 0) {
    return (
      <div
        style={{ height }}
        className="w-full flex items-center justify-center text-gray-500 text-xs"
      >
        Sin datos
      </div>
    );
  }

  const values = data.map((d) => d.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const width = 100; // porcentaje
  const points = data.map((point, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((point.value - min) / range) * height;
    return { x, y };
  });

  const pathD = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
    .join(" ");

  const gradientId = `gradient-${Math.random().toString(36).slice(2, 9)}`;

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="none"
      className="w-full"
      style={{ height }}
    >
      <defs>
        <linearGradient id={gradientId} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0.05" />
        </linearGradient>
      </defs>
      {/* Área bajo la línea */}
      <path
        d={`${pathD} L ${width} ${height} L 0 ${height} Z`}
        fill={`url(#${gradientId})`}
      />
      {/* Línea */}
      <path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
      {/* Puntos opcionales */}
      {showDots &&
        points.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="2"
            fill={color}
            vectorEffect="non-scaling-stroke"
          />
        ))}
    </svg>
  );
};
