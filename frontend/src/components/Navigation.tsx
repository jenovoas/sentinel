"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard, Hexagon, ScanSearch, ShieldAlert, BarChart3, LineChart,
  UserCheck, LogOut, Menu, X, ShieldCheck,
} from "lucide-react";
import { csrfTokenFromCookie } from "@/lib/session-client";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "Panel", href: "/dashboard", Icon: LayoutDashboard },
  { label: "Retículo S60", href: "/dashboard/lattice", Icon: Hexagon },
  { label: "Verificación", href: "/ai/playground", Icon: ScanSearch },
  { label: "Seguridad", href: "/security/watchdog", Icon: ShieldAlert },
  { label: "Métricas", href: "/metrics", Icon: BarChart3 },
  { label: "Analítica", href: "/analytics", Icon: LineChart },
];

export function Navigation({ isSuperuser = false }: { isSuperuser?: boolean }) {
  const pathname = usePathname();
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  const items = isSuperuser
    ? [...NAV_ITEMS, { label: "Gamma", href: "/security/gamma", Icon: UserCheck }]
    : NAV_ITEMS;

  useEffect(() => {
    let active = true;
    const check = async () => {
      try {
        const res = await fetch("/api/v1/dashboard/status", { cache: "no-store" });
        if (active) setBackendOk(res.ok);
      } catch {
        if (active) setBackendOk(false);
      }
    };
    void check();
    const id = setInterval(check, 30_000);
    return () => { active = false; clearInterval(id); };
  }, []);

  const handleLogout = async () => {
    await fetch("/api/auth/logout", {
      method: "POST",
      headers: { "x-csrf-token": csrfTokenFromCookie() },
      cache: "no-store",
    });
    router.replace("/login");
    router.refresh();
  };

  const isActive = (href: string) =>
    href === "/dashboard" ? pathname === "/" || pathname === "/dashboard" : pathname?.startsWith(href);

  return (
    <nav className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-slate-950/95 backdrop-blur-md" aria-label="Navegación principal">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between gap-4 px-6">
        <Link href="/dashboard" className="flex shrink-0 items-center gap-2.5" aria-label="Consola Sentinel — Inicio">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyan-400/30 bg-cyan-500/10">
            <ShieldCheck className="h-5 w-5 text-cyan-300" />
          </span>
          <span className="text-lg font-bold tracking-tight text-slate-100">
            Consola <span className="text-cyan-300">Sentinel</span>
          </span>
        </Link>

        <div className="hidden items-center gap-1 md:flex" role="menubar">
          {items.map(({ label, href, Icon }) => (
            <Link
              key={href}
              href={href}
              role="menuitem"
              className={cn(
                "flex items-center gap-2 whitespace-nowrap rounded-lg border px-3.5 py-2 text-sm font-medium transition-colors",
                isActive(href)
                  ? "border-cyan-400/20 bg-cyan-500/10 text-cyan-300"
                  : "border-transparent text-slate-400 hover:bg-white/5 hover:text-white",
              )}
            >
              <Icon className="h-4 w-4" /> {label}
            </Link>
          ))}
        </div>

        <div className="hidden shrink-0 items-center gap-3 md:flex">
          <span className="flex items-center gap-2 text-xs text-slate-400">
            <span
              aria-hidden
              className={cn(
                "inline-block h-2 w-2 rounded-full",
                backendOk === true ? "bg-emerald-400" : backendOk === false ? "bg-rose-400" : "bg-slate-500",
              )}
            />
            {backendOk === true ? "Backend conectado" : backendOk === false ? "Backend no disponible" : "Verificando…"}
          </span>
          <button
            type="button"
            onClick={() => void handleLogout()}
            className="flex items-center gap-1.5 rounded-lg border border-white/15 px-3 py-1.5 text-sm text-slate-300 transition-colors hover:bg-white/5"
          >
            <LogOut className="h-4 w-4" /> Salir
          </button>
        </div>

        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-slate-400 md:hidden"
          onClick={() => setMenuOpen((v) => !v)}
          aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"}
          aria-expanded={menuOpen}
        >
          {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {menuOpen && (
        <div className="border-t border-white/5 bg-slate-950/98 px-6 py-4 md:hidden" aria-label="Menú móvil">
          <div className="flex flex-col gap-1">
            {items.map(({ label, href, Icon }) => (
              <Link
                key={href}
                href={href}
                onClick={() => setMenuOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-4 py-3 text-base font-medium",
                  isActive(href) ? "bg-cyan-500/10 text-cyan-300" : "text-slate-400",
                )}
              >
                <Icon className="h-5 w-5" /> {label}
              </Link>
            ))}
            <button
              type="button"
              onClick={() => void handleLogout()}
              className="mt-2 flex items-center gap-3 rounded-lg border border-white/15 px-4 py-3 text-left text-slate-300"
            >
              <LogOut className="h-5 w-5" /> Cerrar sesión
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
