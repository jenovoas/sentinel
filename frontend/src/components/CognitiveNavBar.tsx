"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Shield,
  Bell,
  User,
  ChevronDown,
  Settings,
  LogOut,
  Lock,
  Brain,
  ShieldAlert,
  Activity,
  Zap,
  Globe,
  Terminal,
  Server,
  ChevronRight
} from "lucide-react";

interface NavItem {
  label: string;
  href?: string;
  icon: React.ReactNode;
  color: string;
  glow: string;
  description: string;
  children?: NavItem[];
}

const MAIN_NAV_ITEMS: NavItem[] = [
  {
    label: "HOME",
    href: "/",
    icon: <Globe className="w-4 h-4" />,
    color: "text-cyan-400",
    glow: "bg-cyan-400/20",
    description: "Command Tower Root",
  },
  {
    label: "COGNITIVE",
    href: "/cognitive",
    icon: <Zap className="w-4 h-4" />,
    color: "text-purple-400",
    glow: "bg-purple-400/20",
    description: "Merkabah Dimensional Interface",
  },
  {
    label: "INTELLIGENCE",
    icon: <Brain className="w-4 h-4" />,
    color: "text-purple-400",
    glow: "bg-purple-400/20",
    description: "AI & Cognitive Systems",
    children: [
      {
        label: "Cortex AI",
        href: "/cortex",
        icon: <Brain className="w-4 h-4" />,
        color: "text-purple-400",
        glow: "bg-purple-400/20",
        description: "Neural Inference Matrix",
      },
      {
        label: "Workspace",
        href: "/dashboard",
        icon: <Lock className="w-4 h-4" />,
        color: "text-cyan-400",
        glow: "bg-cyan-400/20",
        description: "Secure Browser & Environment",
      },
      {
        label: "AI Trust",
        href: "/ai-trust",
        icon: <Shield className="w-4 h-4" />,
        color: "text-emerald-400",
        glow: "bg-emerald-400/20",
        description: "AI Trust Certification & Hallucination Defense",
      },
    ],
  },
  {
    label: "OPERATIONS",
    icon: <Server className="w-4 h-4" />,
    color: "text-emerald-400",
    glow: "bg-emerald-400/20",
    description: "System Operations & Monitoring",
    children: [
      {
        label: "Ops Matrix",
        href: "/dash-op",
        icon: <LayoutDashboard className="w-4 h-4" />,
        color: "text-emerald-400",
        glow: "bg-emerald-400/20",
        description: "Operational Dashboard",
      },
      {
        label: "Watchdog",
        href: "/watchdog",
        icon: <ShieldAlert className="w-4 h-4" />,
        color: "text-orange-400",
        glow: "bg-orange-400/20",
        description: "System Health Monitor",
      },
      {
        label: "Telemetry",
        href: "/monitoring",
        icon: <Activity className="w-4 h-4" />,
        color: "text-pink-400",
        glow: "bg-pink-400/20",
        description: "Grafana Metrics",
      },
      {
        label: "DevOps",
        href: "/devops",
        icon: <Server className="w-4 h-4" />,
        color: "text-emerald-400",
        glow: "bg-emerald-400/20",
        description: "Infrastructure Console",
      },
      {
        label: "DevTools",
        href: "/devtools",
        icon: <Terminal className="w-4 h-4" />,
        color: "text-purple-400",
        glow: "bg-purple-400/20",
        description: "Developer Testing Suite",
      },
    ],
  },
];

export const CognitiveNavBar: React.FC<{ userEmail?: string; onLogout?: () => void }> = ({
  userEmail,
  onLogout,
}) => {
  const pathname = usePathname();
  const [openSubmenu, setOpenSubmenu] = useState<string | null>(null);

  const isItemActive = (item: NavItem): boolean => {
    if (item.href) return pathname === item.href;
    if (item.children) {
      return item.children.some(child => pathname === child.href);
    }
    return false;
  };

  return (
    <nav className="sticky top-0 z-[100] w-full border-b border-white/5 bg-slate-950/40 backdrop-blur-3xl shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
      <div className="max-w-[1700px] mx-auto px-8 py-3">
        <div className="flex items-center justify-between gap-10">
          {/* Logo Section */}
          <Link
            href="/"
            className="flex items-center gap-4 group transition-all duration-500"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-400/30 rounded-xl blur-md opacity-20 group-hover:opacity-60 transition-opacity" />
              <div className="relative bg-slate-900 border border-white/10 rounded-xl p-2.5 shadow-2xl transition-transform group-hover:rotate-12">
                <Shield className="w-6 h-6 text-cyan-400" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-black text-white italic tracking-tighter leading-none">SENTINEL</span>
              <span className="text-[8px] font-black tracking-[0.4em] text-cyan-500 uppercase">Sovereign OS</span>
            </div>
          </Link>

          {/* Main Navigation */}
          <div className="hidden lg:flex items-center gap-1 bg-white/2 p-1 rounded-2xl border border-white/5">
            {MAIN_NAV_ITEMS.map((item) => {
              const isActive = isItemActive(item);
              const hasSubmenu = item.children && item.children.length > 0;

              return (
                <div
                  key={item.label}
                  className="relative"
                  onMouseEnter={() => hasSubmenu && setOpenSubmenu(item.label)}
                  onMouseLeave={() => hasSubmenu && setOpenSubmenu(null)}
                >
                  {hasSubmenu ? (
                    // Menu item with submenu
                    <button
                      className={`relative flex items-center gap-3 px-5 py-2.5 rounded-[14px] transition-all duration-500 group overflow-hidden`}
                    >
                      {isActive && (
                        <motion.div
                          layoutId="nav-bg"
                          className="absolute inset-0 bg-white/5 border border-white/10 shadow-[inset_0_0_10px_rgba(255,255,255,0.05)] rounded-[14px]"
                          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                        />
                      )}

                      <span className={`relative z-10 transition-colors duration-500 ${isActive ? item.color : "text-gray-500 group-hover:text-gray-300"}`}>
                        {item.icon}
                      </span>
                      <span className={`relative z-10 text-[10px] font-black uppercase tracking-[0.2em] transition-colors duration-500 ${isActive ? 'text-white' : 'text-gray-500 group-hover:text-gray-300'}`}>
                        {item.label}
                      </span>
                      <ChevronDown className={`relative z-10 w-3 h-3 transition-all duration-300 ${openSubmenu === item.label ? 'rotate-180' : ''} ${isActive ? 'text-white' : 'text-gray-500'}`} />

                      {isActive && (
                        <motion.div
                          layoutId="nav-underline"
                          className={`absolute bottom-1.5 left-5 right-5 h-[1.5px] ${item.color.replace('text', 'bg')} rounded-full shadow-[0_0_10px_rgba(255,255,255,0.5)]`}
                        />
                      )}
                    </button>
                  ) : (
                    // Regular menu item
                    <Link
                      href={item.href!}
                      className={`relative flex items-center gap-3 px-5 py-2.5 rounded-[14px] transition-all duration-500 group overflow-hidden`}
                    >
                      {isActive && (
                        <motion.div
                          layoutId="nav-bg"
                          className="absolute inset-0 bg-white/5 border border-white/10 shadow-[inset_0_0_10px_rgba(255,255,255,0.05)] rounded-[14px]"
                          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                        />
                      )}

                      <span className={`relative z-10 transition-colors duration-500 ${isActive ? item.color : "text-gray-500 group-hover:text-gray-300"}`}>
                        {item.icon}
                      </span>
                      <span className={`relative z-10 text-[10px] font-black uppercase tracking-[0.2em] transition-colors duration-500 ${isActive ? 'text-white' : 'text-gray-500 group-hover:text-gray-300'}`}>
                        {item.label}
                      </span>

                      {isActive && (
                        <motion.div
                          layoutId="nav-underline"
                          className={`absolute bottom-1.5 left-5 right-5 h-[1.5px] ${item.color.replace('text', 'bg')} rounded-full shadow-[0_0_10px_rgba(255,255,255,0.5)]`}
                        />
                      )}

                      {/* Tooltip */}
                      <div className="absolute top-[calc(100%+10px)] left-1/2 -translate-x-1/2 px-3 py-1.5 rounded-lg bg-black/90 border border-white/10 text-[9px] font-black text-white opacity-0 group-hover:opacity-100 transition-all pointer-events-none whitespace-nowrap tracking-widest translate-y-2 group-hover:translate-y-0 z-[110]">
                        {item.description}
                      </div>
                    </Link>
                  )}

                  {/* Submenu Dropdown */}
                  <AnimatePresence>
                    {hasSubmenu && openSubmenu === item.label && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                        className="absolute top-[calc(100%+10px)] left-0 min-w-[240px] bg-slate-950/95 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-2xl py-2 z-[110]"
                      >
                        {item.children!.map((child) => {
                          const isChildActive = pathname === child.href;
                          return (
                            <Link
                              key={child.label}
                              href={child.href!}
                              className={`flex items-center gap-3 px-4 py-3 transition-all ${isChildActive
                                ? 'bg-white/10 text-white'
                                : 'text-gray-400 hover:text-white hover:bg-white/5'
                                }`}
                            >
                              <span className={isChildActive ? child.color : 'text-gray-500'}>
                                {child.icon}
                              </span>
                              <div className="flex-1">
                                <p className="text-[10px] font-black uppercase tracking-wider">
                                  {child.label}
                                </p>
                                <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">
                                  {child.description}
                                </p>
                              </div>
                              {isChildActive && (
                                <ChevronRight className="w-3 h-3 text-cyan-400" />
                              )}
                            </Link>
                          );
                        })}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-6">
            <div className="hidden xl:flex items-center gap-3 px-4 py-1.5 bg-black/40 rounded-full border border-white/5 text-[9px] font-black tracking-widest text-gray-500">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              TRUTH_SYNC: ACTIVE
            </div>

            <button className="relative p-2.5 text-gray-400 hover:text-white transition-all duration-300 hover:bg-white/5 rounded-xl border border-transparent hover:border-white/10">
              <Bell className="w-5 h-5" />
              <span className="absolute top-2.5 right-2.5 h-1.5 w-1.5 bg-rose-500 rounded-full shadow-[0_0_10px_rgba(244,63,94,0.5)]" />
            </button>

            <div className="relative group p-1 bg-white/2 rounded-2xl border border-white/5">
              <button className="flex items-center gap-3 px-3 py-2 rounded-[14px] text-gray-400 hover:text-white transition-all duration-500 hover:bg-white/5">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-400 via-blue-500 to-purple-600 flex items-center justify-center text-xs font-black text-white shadow-lg border border-white/20">
                  {userEmail?.charAt(0).toUpperCase() || "S"}
                </div>
                <div className="flex flex-col items-start leading-tight">
                  <span className="text-[10px] font-black uppercase tracking-widest text-white">
                    {userEmail?.split("@")[0] || "Operator"}
                  </span>
                  <span className="text-[8px] font-black text-gray-500 uppercase tracking-widest">Level 7 Clear</span>
                </div>
                <ChevronDown className="w-3 h-3 transition-transform duration-500 group-hover:rotate-180" />
              </button>

              <div className="absolute right-0 top-[calc(100%+10px)] w-56 bg-slate-950/95 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-500 py-3 z-[110] translate-y-2 group-hover:translate-y-0">
                <DropdownItem icon={<User className="w-4 h-4" />} label="Sovereign Profile" />
                <DropdownItem icon={<Settings className="w-4 h-4" />} label="Node Settings" />
                <DropdownItem icon={<Terminal className="w-4 h-4" />} label="Shell Access" />
                <div className="my-2 border-t border-white/5" />
                <button
                  onClick={onLogout}
                  className="w-full text-left px-4 py-2 text-xs font-black text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors flex items-center uppercase tracking-widest"
                >
                  <LogOut className="w-4 h-4 mr-3" /> Terminate Session
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

function DropdownItem({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <button className="w-full text-left px-5 py-2.5 text-[10px] font-black text-gray-400 hover:text-white hover:bg-white/5 transition-all flex items-center uppercase tracking-widest uppercase italic">
      <span className="mr-3 text-cyan-500">{icon}</span>
      {label}
    </button>
  );
}
