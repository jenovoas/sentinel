import "server-only";
import { NextResponse } from "next/server";
import {
  SESSION_COOKIE,
  clearSessionCookies,
  hasValidCsrf,
  isSameOrigin,
  noStore,
  readCookie,
  sessionError,
} from "@/lib/server/session";

const CORTEX_INTERNAL_URL = process.env.CORTEX_INTERNAL_URL || "http://backend:8000";
const CORTEX_ROUTES: Record<string, readonly [string, string][]> = {
  "analytics/anomalies": [["GET", "/api/v1/analytics/anomalies"]],
  "analytics/metrics/recent": [["GET", "/api/v1/analytics/metrics/recent"]],
  "analytics/storage/summary": [["GET", "/api/v1/analytics/storage/summary"]],
  "ai/health": [["GET", "/api/v1/ai/health"]],
  "ai/query": [["POST", "/api/v1/ai/query"]],
  "backup/status": [["GET", "/api/v1/backup/status"]],
  "dashboard/status": [["GET", "/api/v1/dashboard/status"]],
  "failsafe/status": [["GET", "/api/v1/failsafe/status"]],
  "lattice/hologram": [["GET", "/api/v1/lattice/hologram"]],
};

export async function proxyCortex(request: Request, route: string): Promise<NextResponse> {
  const target = CORTEX_ROUTES[route]?.find(([method]) => method === request.method);
  if (!target) {
    const allowedRoute = CORTEX_ROUTES[route];
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

  const endpoint = new URL(target[1], `${CORTEX_INTERNAL_URL.replace(/\/+$/, "")}/`);
  endpoint.search = new URL(request.url).search;

  try {
    const upstream = await fetch(endpoint, {
      method: request.method,
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json",
        ...(request.method === "GET" || request.method === "HEAD"
          ? {}
          : { "Content-Type": "application/json" }),
      },
      body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.text(),
      cache: "no-store",
      redirect: "manual",
    });

    const response = new NextResponse(
      upstream.status === 204 || upstream.status === 304 ? null : upstream.body,
      {
        status: upstream.status,
        headers: {
          "Cache-Control": "private, no-store, max-age=0",
          Pragma: "no-cache",
          ...(upstream.headers.get("content-type")
            ? { "Content-Type": upstream.headers.get("content-type")! }
            : {}),
        },
      },
    );
    return upstream.status === 401 ? clearSessionCookies(response) : response;
  } catch {
    return noStore(NextResponse.json({ error: "Cortex no disponible" }, { status: 503 }));
  }
}
