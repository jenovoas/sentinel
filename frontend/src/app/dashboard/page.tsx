"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  Activity, AlertTriangle, CheckCircle2, XCircle, Cpu, MemoryStick,
  HardDrive, Database, ShieldCheck, FileText, BarChart3, Lock, RefreshCw,
} from "lucide-react";
import { BackupStatusCard } from "@/components/backup/BackupStatusCard";
import { FailSafeSecurityCard } from "@/components/failsafe/FailSafeSecurityCard";

interface Snapshot {
  timestamp: string;
  db_health: { status: string };
  db_stats: { connections_total: number; connections_active: number; locks: number };
  system: { cpu_percent: number; mem_percent: number; disk_percent: number };
  gpu: { available: boolean };
}

type Health = "healthy" | "warning" | "critical" | "unknown";

export default function DashboardPage() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [checkedAt, setCheckedAt] = useState<string | null>(null);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const res = await fetch("/api/v1/dashboard/status", { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setSnapshot(await res.json());
      setCheckedAt(new Date().toLocaleTimeString());
      setError("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Sin conexión al backend");
    }
  };

  useEffect(() => {
    void load();
    const interval = setInterval(() => void load(), 30000);
    return () => clearInterval(interval);
  }, []);

  const health: Health = !snapshot
    ? "unknown"
    : snapshot.db_health.status !== "healthy"
      ? "critical"
      : snapshot.system.cpu_percent > 80 || snapshot.system.mem_percent > 80
        ? "warning"
        : "healthy";

  const heroStyle: Record<Health, string> = {
    healthy: "border-emerald-500/20 bg-emerald-500/10 text-emerald-300",
    warning: "border-amber-500/20 bg-amber-500/10 text-amber-300",
    critical: "border-rose-500/20 bg-rose-500/10 text-rose-300",
    unknown: "border-white/10 bg-white/5 text-slate-300",
  };

  const HeroIcon = health === "healthy" ? CheckCircle2 : health === "unknown" ? Activity : health === "warning" ? AlertTriangle : XCircle;

  const metrics = [
    { icon: Cpu, label: "CPU", value: snapshot ? `${snapshot.system.cpu_percent.toFixed(1)}%` : "N/D" },
    { icon: MemoryStick, label: "Memoria", value: snapshot ? `${snapshot.system.mem_percent.toFixed(1)}%` : "N/D" },
    { icon: HardDrive, label: "Disco", value: snapshot ? `${snapshot.system.disk_percent.toFixed(0)}%` : "N/D" },
    { icon: Database, label: "Conexiones DB", value: snapshot ? `${snapshot.db_stats.connections_active}/${snapshot.db_stats.connections_total}` : "N/D" },
  ];

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <header className="mb-8 flex items-end justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-cyan-300/70">Consola Sentinel</p>
            <h1 className="text-4xl font-semibold tracking-tight">Estado del sistema</h1>
            <p className="mt-2 text-sm text-slate-400">
              Métricas en vivo del backend Fenix{checkedAt ? ` · actualizado ${checkedAt}` : ""}.
            </p>
          </div>
          <Button variant="outline" onClick={() => void load()}>
            <RefreshCw className="mr-2 h-4 w-4" /> Actualizar
          </Button>
        </header>

        {error && (
          <p role="alert" className="mb-6 rounded-lg border border-rose-500/20 bg-rose-500/10 p-3 text-sm text-rose-300">
            Sin conexión al backend ({error}). Se conserva la última lectura.
          </p>
        )}

        <div className={`mb-8 flex items-center gap-4 rounded-2xl border p-6 ${heroStyle[health]}`}>
          <HeroIcon className="h-10 w-10 shrink-0" />
          <div>
            <h2 className="text-xl font-semibold text-white">
              {health === "healthy" && "Sistema operativo"}
              {health === "warning" && "Carga elevada de recursos"}
              {health === "critical" && "Base de datos no saludable"}
              {health === "unknown" && "Conectando con el backend…"}
            </h2>
            <p className="text-sm opacity-80">
              {snapshot
                ? `Base de datos ${snapshot.db_health.status} · ${snapshot.db_stats.locks} bloqueos · GPU ${snapshot.gpu.available ? "disponible" : "no disponible en este host"}`
                : "Esperando primera lectura."}
            </p>
          </div>
        </div>

        <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {metrics.map(({ icon: Icon, label, value }) => (
            <Card key={label} className="border-white/10 bg-white/5 backdrop-blur-xl">
              <CardContent className="flex items-center gap-4 p-5">
                <Icon className="h-8 w-8 shrink-0 text-cyan-300" />
                <div>
                  <p className="text-2xl font-semibold text-white">{value}</p>
                  <p className="text-xs text-slate-400">{label}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </section>

        <section className="mb-8 grid gap-6 md:grid-cols-2">
          <BackupStatusCard />
          <FailSafeSecurityCard />
        </section>

        <section>
          <h2 className="mb-4 text-xl font-semibold">Acciones</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { href: "/security/gamma", icon: ShieldCheck, title: "Revisión Gamma", desc: "Cola de decisiones humanas" },
              { href: "/metrics", icon: BarChart3, title: "Métricas", desc: "Historial del runtime" },
              { href: "/analytics", icon: Activity, title: "Analítica", desc: "Eventos y anomalías" },
              { href: "/reports", icon: FileText, title: "Informes", desc: "Reportes del sistema" },
            ].map(({ href, icon: Icon, title, desc }) => (
              <Link key={href} href={href}>
                <Card className="border-white/10 bg-white/5 backdrop-blur-xl transition-colors hover:border-cyan-400/30 hover:bg-white/10">
                  <CardContent className="p-5 text-center">
                    <Icon className="mx-auto mb-2 h-8 w-8 text-cyan-300" />
                    <p className="font-semibold">{title}</p>
                    <p className="mt-1 text-xs text-slate-400">{desc}</p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </section>

        <p className="mt-8 flex items-center gap-2 text-xs text-slate-500">
          <Lock className="h-3 w-3" /> Consola interna Sentinel · Fenix primario, Marte en espera.
        </p>
      </div>
    </main>
  );
}
