import "server-only";
import { NextResponse } from "next/server";
import { CSRF_COOKIE, SESSION_COOKIE, readCookie } from "./security";
import { sentinelBackendUrl } from "./backend";

export { CSRF_COOKIE, SESSION_COOKIE, hasValidCsrf, isSameOrigin, readCookie } from "./security";
export const SESSION_TTL_SECONDS = 600;

export function sessionCookieOptions() {
  return {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/",
    maxAge: SESSION_TTL_SECONDS,
  };
}

export function csrfCookieOptions() {
  return {
    httpOnly: false,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/",
    maxAge: SESSION_TTL_SECONDS,
  };
}

export function noStore(response: NextResponse): NextResponse {
  response.headers.set("Cache-Control", "private, no-store, max-age=0");
  response.headers.set("Pragma", "no-cache");
  return response;
}

export function sessionError(status = 401): NextResponse {
  return noStore(NextResponse.json(
    { error: status === 401 ? "Sesión no válida" : "Servicio de autenticación no disponible" },
    { status },
  ));
}

export async function fetchAuthMe(token: string): Promise<Response> {
  const endpoint = new URL("/api/v1/auth/me", `${sentinelBackendUrl()}/`);
  return fetch(endpoint, {
    headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
    cache: "no-store",
    redirect: "manual",
  });
}

export async function validateSession(request: Request): Promise<
  | { ok: true; token: string; identity: unknown }
  | { ok: false; status: 401 | 503 }
> {
  const token = readCookie(request, SESSION_COOKIE);
  if (!token) return { ok: false, status: 401 };
  try {
    const response = await fetchAuthMe(token);
    if (response.status === 401 || response.status === 403) return { ok: false, status: 401 };
    if (!response.ok) return { ok: false, status: 503 };
    return { ok: true, token, identity: await response.json() };
  } catch {
    return { ok: false, status: 503 };
  }
}

export function clearSessionCookies(response: NextResponse): NextResponse {
  response.cookies.set(SESSION_COOKIE, "", { ...sessionCookieOptions(), maxAge: 0 });
  response.cookies.set(CSRF_COOKIE, "", { ...csrfCookieOptions(), maxAge: 0 });
  return noStore(response);
}
