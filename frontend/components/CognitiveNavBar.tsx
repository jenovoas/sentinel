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
import {
  LayoutDashboard,
  BarChart2,
  AlertTriangle,
  Database,
  FileText,
  Shield,
  Bell,
  User,
  ChevronDown,
  Settings,
  LogOut
} from "lucide-react";

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
    icon: <LayoutDashboard className="w-5 h-5" />,
    color: "cyan",
    description: "Monitoreo en tiempo real",
  },
  {
    label: "Analytics",
    href: "/analytics",
    icon: <BarChart2 className="w-5 h-5" />,
    color: "green",
    description: "Análisis históricos y tendencias",
  },
  {
    label: "Alertas",
    href: "/alerts",
    icon: <AlertTriangle className="w-5 h-5" />,
    color: "amber",
    description: "Anomalías y eventos críticos",
  },
  {
    label: "Bases de Datos",
    href: "/db",
    icon: <Database className="w-5 h-5" />,
    color: "amber",
    description: "Instancias y consultas activas",
  },
  {
    label: "Reportes",
    href: "/reports",
    icon: <FileText className="w-5 h-5" />,
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
                <Shield className="w-6 h-6 text-white" />
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
              <Bell className="w-5 h-5" />
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
                <ChevronDown className="w-4 h-4 transition-transform duration-300 group-hover:rotate-180" />
              </button>

              {/* Dropdown Menu - Escondido por defecto */}
              <div className="absolute right-0 top-full mt-0 w-48 bg-slate-900 border border-white/10 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 py-2">
                <button className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 transition-colors flex items-center">
                  <Settings className="w-4 h-4 mr-2" /> Preferencias
                </button>
                <button className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 transition-colors flex items-center">
                  <User className="w-4 h-4 mr-2" /> Mi Perfil
                </button>
                <hr className="my-2 border-white/10" />
                <button
                  onClick={onLogout}
                  className="w-full text-left px-4 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors flex items-center"
                >
                  <LogOut className="w-4 h-4 mr-2" /> Logout
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
