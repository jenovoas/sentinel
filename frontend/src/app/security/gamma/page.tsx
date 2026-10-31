"use client";

import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { csrfTokenFromCookie } from "@/lib/session-client";

type Decision = {
  id: number; guardian: string; type: string;
  context: Record<string, unknown>; evidence: Record<string, unknown>;
  confidence_s60_raw: number; created_at: string; timeout_at: string;
};

async function readResponse(response: Response): Promise<unknown> {
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const messages: Record<number, string> = {
      401: "Sesión caducada. Vuelva a iniciar sesión.",
      403: "Acceso denegado: se requiere superusuario de plataforma y una solicitud válida.",
      404: "La decisión ya no está pendiente o ha caducado. Actualice la cola.",
      422: "La justificación no es válida.",
      503: "Backend no disponible. No se ha confirmado ninguna acción.",
    };
    throw new Error(messages[response.status] ?? `Error upstream (${response.status}). No se ha confirmado ninguna acción.`);
  }
  return body;
}

export default function GammaReviewPage() {
  const [allowed, setAllowed] = useState(false);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [selected, setSelected] = useState<Decision | null>(null);
  const [feedback, setFeedback] = useState("");
  const [confirmation, setConfirmation] = useState<"approve" | "deny" | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    // Discard the old selection so a refreshed list always requires another review.
    setSelected(null);
    setConfirmation(null);
    setFeedback("");
    try {
      const identity = await readResponse(await fetch("/api/auth/me", { cache: "no-store" }));
      if (!identity || typeof identity !== "object" || !("is_superuser" in identity) || identity.is_superuser !== true) {
        setAllowed(false);
        setDecisions([]);
        throw new Error("Solo un superusuario de plataforma puede revisar la cola global Gamma. Un administrador de tenant no tiene acceso.");
      }
      setAllowed(true);
      const pending = await readResponse(await fetch("/api/v1/gamma/pending?limit=50", { cache: "no-store" }));
      if (!Array.isArray(pending)) throw new Error("Respuesta de cola no válida.");
      setDecisions(pending as Decision[]);
    } catch (cause) {
      setDecisions([]);
      setError(cause instanceof Error ? cause.message : "No se pudo consultar Gamma.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const review = async () => {
    if (!selected || !confirmation || !feedback.trim() || busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await readResponse(await fetch(`/api/v1/gamma/${confirmation}/${selected.id}`, {
        method: "POST", cache: "no-store",
        headers: { "Content-Type": "application/json", "x-csrf-token": csrfTokenFromCookie() },
        body: JSON.stringify({ feedback: feedback.trim() }),
      }));
      setNotice(`Decisión #${selected.id} ${confirmation === "approve" ? "aprobada" : "denegada"}. Revisión registrada con su identidad autenticada.`);
      await load();
    } catch (cause) {
      setConfirmation(null);
      setError(cause instanceof Error ? cause.message : "Resultado no confirmado. Consulte la cola antes de reintentar.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <header>
          <h1 className="text-3xl font-semibold">Guardian Gamma · revisión humana</h1>
          <p className="text-slate-300 mt-2">Cola global, solo superusuarios de plataforma. La revisión persiste el veredicto y su auditoría; no confirma ejecución ni habilita enforcement.</p>
          <Button className="mt-4" variant="outline" disabled={busy || loading} onClick={() => { setNotice(""); void load(); }}>Actualizar pendientes</Button>
        </header>
        {loading && <p role="status">Consultando identidad y cola…</p>}
        {error && <p role="alert" className="text-rose-300">{error}</p>}
        {notice && <p role="status" className="text-emerald-300">{notice}</p>}
        {allowed && !loading && (
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>Pendientes ({decisions.length}, máximo 50)</CardTitle></CardHeader>
              <CardContent>
                {!error && decisions.length === 0 && <p>No hay decisiones pendientes vigentes.</p>}
                <ul className="space-y-3">
                  {decisions.map((decision) => (
                    <li key={decision.id}>
                      <Button variant="outline" className="w-full justify-start" disabled={busy} onClick={() => { setSelected(decision); setFeedback(""); setConfirmation(null); setError(""); setNotice(""); }}>
                        #{decision.id} · {decision.guardian} · {decision.type}
                      </Button>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
            {selected && (
              <Card>
                <CardHeader><CardTitle>Revisión #{selected.id}</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                  <dl>
                    <dt>Origen / tipo</dt><dd>{selected.guardian} / {selected.type}</dd>
                    <dt>Confianza S60 (unidades base exactas)</dt><dd>{selected.confidence_s60_raw} / 12960000</dd>
                    <dt>Creación</dt><dd>{selected.created_at}</dd>
                    <dt>Caducidad</dt><dd>{selected.timeout_at}</dd>
                  </dl>
                  <p className="text-sm text-slate-400">Contexto y evidencia no confiables, mostrados como texto inerte. Secretos redactados y tamaños acotados por backend; las marcas TRUNCATED indican información omitida.</p>
                  <h2 className="font-semibold">Contexto</h2>
                  <pre className="whitespace-pre-wrap break-all max-h-64 overflow-auto text-sm">{JSON.stringify(selected.context, null, 2)}</pre>
                  <h2 className="font-semibold">Evidencia</h2>
                  <pre className="whitespace-pre-wrap break-all max-h-64 overflow-auto text-sm">{JSON.stringify(selected.evidence, null, 2)}</pre>
                  <label className="block" htmlFor="gamma-feedback">Justificación de la revisión (obligatoria, sin secretos)</label>
                  <textarea id="gamma-feedback" className="w-full border rounded p-2 bg-slate-900" value={feedback} maxLength={2000} disabled={busy} onChange={(event) => { setFeedback(event.target.value); setConfirmation(null); }} />
                  <div className="flex gap-3">
                    <Button disabled={busy || !feedback.trim()} onClick={() => setConfirmation("approve")}>Aprobar…</Button>
                    <Button variant="outline" disabled={busy || !feedback.trim()} onClick={() => setConfirmation("deny")}>Denegar…</Button>
                  </div>
                  {confirmation && <div role="group" aria-label="Confirmación del veredicto" className="border p-3 space-y-3">
                    <p>¿Confirmar {confirmation === "approve" ? "aprobación" : "denegación"} de #{selected.id}? Se registrará con su actor autenticado.</p>
                    <Button disabled={busy} onClick={() => void review()}>{busy ? "Registrando…" : "Confirmar veredicto"}</Button>
                    <Button variant="outline" disabled={busy} onClick={() => setConfirmation(null)}>Cancelar</Button>
                  </div>}
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
