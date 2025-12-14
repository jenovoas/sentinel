"use client";

/**
 * CognitiveNavBar Component
 * 
 * Principios de Diseño Cognitivo Aplicados:
 * 
 * 1. JERARQUÍA VISUAL CLARA
 *    - Logo/Branding en izquierda (primario, familiar)
 *    - Items principales en centro (acceso rápido)
 *    - Usuario/Acciones en derecha (secundario)
 * 
 * 2. AGRUPACIÓN POR AFINIDAD (Law of Proximity)
 *    - Dashboard y Analytics juntos (monitoreo)
 *    - Settings y Logout juntos (configuración personal)
 * 
 * 3. FEEDBACK VISUAL INMEDIATO
 *    - Hover: elevación (shadow), brillo aumenta
 *    - Active: indicador visual persistente (underline color)
 *    - Micro-transiciones smooth (300ms)
 * 
 * 4. PSICOLOGÍA DEL COLOR
 *    - CYAN (#22d3ee): Confianza, claridad mental, tech
 *    - VERDE (#10b981): Éxito, datos healthy, go
 *    - ÁMBAR (#f59e0b): Alerta, requiere atención
 *    - ROJO (#ef4444): Peligro, error
 * 
 * 5. AFFORDANCIA
 *    - Cursor: pointer en items clickeables
 *    - Iconos + texto = reconocimiento inmediato
 *    - Espaciado generoso (breathing room)
 * 
 * 6. CONSISTENCIA
 *    - Mismo estilo que dashboard (rounded, backdrop-blur)
 *    - Colores y transiciones consistentes
 *    - Tamaños y tipografía predecibles
 */

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  color: "cyan" | "green" | "amber" | "purple";
  description?: string; // Tooltip cognitivo
}

const MAIN_NAV_ITEMS: NavItem[] = [
  {
    label: "Dashboard",
    href: "/dash-op",
    icon: (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      </svg>
    ),
    color: "cyan",
    description: "Monitoreo en tiempo real",
  },
  {
    label: "Analytics",
    href: "/analytics",
    icon: (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      </svg>
    ),
    color: "green",
    description: "Análisis históricos y tendencias",
  },
  {
    label: "Alertas",
    href: "/alerts",
    icon: (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
    ),
    color: "amber",
    description: "Anomalías y eventos críticos",
  },
  {
    label: "Reportes",
    href: "/reports",
    icon: (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
    ),
    color: "purple",
    description: "Reportes y documentación",
  },
];

interface CognitiveNavBarProps {
  userEmail?: string;
  onLogout?: () => void;
}

const getColorClasses = (color: string, isActive: boolean) => {
  const baseClasses =
    "transition-all duration-300 relative group text-gray-300 hover:text-white";

  if (isActive) {
    switch (color) {
      case "cyan":
        return `${baseClasses} text-cyan-400 after:absolute after:bottom-[-8px] after:left-0 after:right-0 after:h-1 after:bg-cyan-400 after:rounded-full`;
      case "green":
        return `${baseClasses} text-green-400 after:absolute after:bottom-[-8px] after:left-0 after:right-0 after:h-1 after:bg-green-400 after:rounded-full`;
      case "amber":
        return `${baseClasses} text-amber-400 after:absolute after:bottom-[-8px] after:left-0 after:right-0 after:h-1 after:bg-amber-400 after:rounded-full`;
      case "purple":
        return `${baseClasses} text-purple-400 after:absolute after:bottom-[-8px] after:left-0 after:right-0 after:h-1 after:bg-purple-400 after:rounded-full`;
      default:
        return baseClasses;
    }
  }

  switch (color) {
    case "cyan":
      return `${baseClasses} hover:text-cyan-300`;
    case "green":
      return `${baseClasses} hover:text-green-300`;
    case "amber":
      return `${baseClasses} hover:text-amber-300`;
    case "purple":
      return `${baseClasses} hover:text-purple-300`;
    default:
      return baseClasses;
  }
};

export const CognitiveNavBar: React.FC<CognitiveNavBarProps> = ({
  userEmail,
  onLogout,
}) => {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-40 w-full border-b border-white/5 bg-slate-950/80 backdrop-blur-xl shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between gap-8">
          {/* Logo / Branding - Primario (izquierda) */}
          <Link
            href="/"
            className="flex items-center gap-2 group transition-all duration-300 hover:scale-105"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-400 rounded-lg blur opacity-20 group-hover:opacity-40 transition-opacity" />
              <div className="relative bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg p-2">
                <svg
                  className="w-6 h-6 text-white"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
                </svg>
              </div>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent hidden sm:inline">
              Sentinel
            </span>
          </Link>

          {/* Main Navigation - Centro */}
          <div className="hidden md:flex items-center gap-1">
            {MAIN_NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-300 ${getColorClasses(item.color, isActive)} hover:bg-white/5`}
                  title={item.description}
                >
                  {item.icon}
                  <span className="text-sm font-medium">{item.label}</span>

                  {/* Tooltip Cognitivo (aparece en hover) */}
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1 rounded-md bg-slate-900/95 text-xs text-gray-200 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap border border-white/10">
                    {item.description}
                  </div>
                </Link>
              );
            })}
          </div>

          {/* Right Actions - Derecha */}
          <div className="flex items-center gap-4">
            {/* Notifications Badge - Psicología: rojo capta atención */}
            <button className="relative p-2 text-gray-300 hover:text-white transition-colors duration-300 hover:bg-white/5 rounded-lg group">
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                />
              </svg>
              <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full animate-pulse" />
            </button>

            {/* User Menu - Psicología: dropdown pattern familiar */}
            <div className="relative group">
              <button className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-white/5 transition-all duration-300">
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center text-xs font-bold text-white">
                  {userEmail?.charAt(0).toUpperCase() || "U"}
                </div>
                <span className="text-sm font-medium hidden sm:inline">
                  {userEmail?.split("@")[0] || "User"}
                </span>
                <svg
                  className="w-4 h-4 transition-transform duration-300 group-hover:rotate-180"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 14l-7 7m0 0l-7-7m7 7V3"
                  />
                </svg>
              </button>

              {/* Dropdown Menu - Escondido por defecto */}
              <div className="absolute right-0 top-full mt-0 w-48 bg-slate-900 border border-white/10 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 py-2">
                <button className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 transition-colors">
                  ⚙️ Preferencias
                </button>
                <button className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 transition-colors">
                  👤 Mi Perfil
                </button>
                <hr className="my-2 border-white/10" />
                <button
                  onClick={onLogout}
                  className="w-full text-left px-4 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
                >
                  🚪 Logout
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Navigation - Responsivo */}
        <div className="md:hidden mt-4 flex items-center gap-1 overflow-x-auto pb-2">
          {MAIN_NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-1 px-3 py-2 rounded-lg whitespace-nowrap transition-all duration-300 ${getColorClasses(item.color, isActive)} hover:bg-white/5`}
              >
                {item.icon}
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};
