"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, Mail, Lock, LogIn, ShieldCheck, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [organizationSlug, setOrganizationSlug] = useState("default");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ organizationSlug, email, password }),
        cache: "no-store",
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "No se pudo iniciar sesión");
      router.replace("/dashboard");
      router.refresh();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo iniciar sesión");
    } finally {
      setLoading(false);
    }
  }

  const inputClass =
    "w-full rounded-lg border border-white/10 bg-slate-950 py-3 pl-11 pr-4 text-slate-100 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20";

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-5 py-12 text-slate-100">
      <section className="w-full max-w-md rounded-2xl border border-white/10 bg-slate-900/80 p-8 shadow-2xl shadow-cyan-950/20">
        <div className="mb-8 flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-400/30 bg-cyan-500/10">
            <ShieldCheck className="h-6 w-6 text-cyan-300" />
          </span>
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.22em] text-cyan-300">Consola Sentinel</p>
            <h1 className="text-2xl font-semibold tracking-tight">Iniciar sesión</h1>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="organization" className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-400">
              Organización
            </label>
            <div className="relative">
              <Building2 className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
              <input
                id="organization" name="organizationSlug" autoComplete="organization" required maxLength={100}
                value={organizationSlug} onChange={(event) => setOrganizationSlug(event.target.value)}
                className={inputClass}
              />
            </div>
          </div>
          <div>
            <label htmlFor="email" className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-400">
              Correo electrónico
            </label>
            <div className="relative">
              <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
              <input
                id="email" name="email" type="email" autoComplete="username" required maxLength={254}
                value={email} onChange={(event) => setEmail(event.target.value)}
                className={inputClass} placeholder="usuario@pinguinoseguro.cl"
              />
            </div>
          </div>
          <div>
            <label htmlFor="password" className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-400">
              Contraseña
            </label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
              <input
                id="password" name="password" type="password" autoComplete="current-password" required maxLength={1024}
                value={password} onChange={(event) => setPassword(event.target.value)}
                className={inputClass}
              />
            </div>
          </div>
          {error && (
            <p role="alert" className="flex items-start gap-2 rounded-lg border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" /> {error}
            </p>
          )}
          <button
            type="submit" disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-cyan-500 px-4 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-wait disabled:opacity-60"
          >
            <LogIn className="h-5 w-5" /> {loading ? "Verificando…" : "Entrar"}
          </button>
        </form>
        <p className="mt-6 text-center text-xs text-slate-500">Consola interna · autenticación contra directorio corporativo</p>
      </section>
    </main>
  );
}
