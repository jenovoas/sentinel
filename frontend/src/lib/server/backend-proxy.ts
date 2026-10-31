import "server-only";
import { NextResponse } from "next/server";
import { sentinelBackendUrl } from "@/lib/server/backend";
import {
  SESSION_COOKIE,
  clearSessionCookies,
  hasValidCsrf,
  isSameOrigin,
  noStore,
  readCookie,
  sessionError,
  validateSession,
} from "@/lib/server/session";

const BACKEND_ROUTES: Record<string, readonly [string, string][]> = {
  "analytics/anomalies": [["GET", "/api/v1/analytics/anomalies"]],
  "analytics/metrics/recent": [["GET", "/api/v1/analytics/metrics/recent"]],
  "analytics/statistics": [["GET", "/api/v1/analytics/statistics"]],
  "analytics/storage/summary": [["GET", "/api/v1/analytics/storage/summary"]],
  "ai/health": [["GET", "/api/v1/ai/health"]],
  "ai/query": [["POST", "/api/v1/ai/query"]],
  "backup/status": [["GET", "/api/v1/backup/status"]],
  "backup/trigger": [["POST", "/api/v1/backup/trigger"]],
  "dashboard/status": [["GET", "/api/v1/dashboard/status"]],
  "failsafe/status": [["GET", "/api/v1/failsafe/status"]],
  "lattice/hologram": [["GET", "/api/v1/lattice/hologram"]],
  "gamma/pending": [["GET", "/api/v1/gamma/pending"]],
};

export async function proxyBackend(request: Request, route: string): Promise<NextResponse> {
  // Only canonical numeric review IDs are accepted; creation/cleanup stay server-only.
  const review = /^gamma\/(approve|deny)\/([1-9]\d{0,9})$/.exec(route);
  const allowedRoute = BACKEND_ROUTES[route] ?? (review
    ? [["POST", `/api/v1/gamma/${review[1]}/${review[2]}`] as const]
    : undefined);
  const target = allowedRoute?.find(([method]) => method === request.method);
  if (!target) {
    return noStore(NextResponse.json(
      { error: allowedRoute ? "Método no permitido" : "Ruta no permitida" },
      { status: allowedRoute ? 405 : 404 },
    ));
  }

  const token = readCookie(request, SESSION_COOKIE);
  if (!token) return sessionError();
  if (request.method !== "GET" && request.method !== "HEAD") {
    if (!isSameOrigin(request) || !hasValidCsrf(request)) {
      return noStore(NextResponse.json({ error: "Solicitud no válida" }, { status: 403 }));
    }
    if (!request.headers.get("content-type")?.toLowerCase().startsWith("application/json")) {
      return noStore(NextResponse.json({ error: "Content-Type no permitido" }, { status: 415 }));
    }
  }

  if (route.startsWith("gamma/")) {
    const session = await validateSession(request);
    if (!session.ok) {
      const response = sessionError(session.status);
      return session.status === 401 ? clearSessionCookies(response) : response;
    }
    if (
      typeof session.identity !== "object" || session.identity === null ||
      !("is_superuser" in session.identity) || session.identity.is_superuser !== true
    ) {
      return noStore(NextResponse.json({ error: "Se requiere superusuario de plataforma" }, { status: 403 }));
    }
  }

  try {
    const endpoint = new URL(target[1], `${sentinelBackendUrl()}/`);
    endpoint.search = new URL(request.url).search;
    const upstream = await fetch(endpoint, {
      method: request.method,
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json",
        ...(request.method === "GET" || request.method === "HEAD" ? {} : { "Content-Type": "application/json" }),
      },
      body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.text(),
      cache: "no-store",
      redirect: "manual",
    });
    const response = new NextResponse(upstream.status === 204 || upstream.status === 304 ? null : upstream.body, {
      status: upstream.status,
      headers: {
        "Cache-Control": "private, no-store, max-age=0",
        Pragma: "no-cache",
        ...(upstream.headers.get("content-type") ? { "Content-Type": upstream.headers.get("content-type")! } : {}),
      },
    });
    return upstream.status === 401 ? clearSessionCookies(response) : response;
  } catch {
    return noStore(NextResponse.json({ error: "Backend no disponible" }, { status: 503 }));
  }
}
