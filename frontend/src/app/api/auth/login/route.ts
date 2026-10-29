import { randomBytes } from "node:crypto";
import { NextResponse } from "next/server";
import {
  CSRF_COOKIE,
  SESSION_COOKIE,
  csrfCookieOptions,
  isSameOrigin,
  noStore,
  sessionCookieOptions,
} from "@/lib/server/session";
import { sentinelBackendUrl } from "@/lib/server/backend";

type Credentials = { organizationSlug?: unknown; email?: unknown; password?: unknown };

export async function POST(request: Request) {
  if (!isSameOrigin(request)) {
    return noStore(NextResponse.json({ error: "Solicitud no válida" }, { status: 403 }));
  }
  let credentials: Credentials;
  try {
    credentials = await request.json() as Credentials;
  } catch {
    return noStore(NextResponse.json({ error: "Datos de acceso no válidos" }, { status: 400 }));
  }
  const { organizationSlug, email, password } = credentials;
  if (
    typeof organizationSlug !== "string" || organizationSlug.length < 1 || organizationSlug.length > 100 ||
    typeof email !== "string" || email.length < 3 || email.length > 254 ||
    typeof password !== "string" || password.length < 1 || password.length > 1024
  ) {
    return noStore(NextResponse.json({ error: "Completa organización, correo y contraseña" }, { status: 400 }));
  }

  try {
    const endpoint = new URL("/api/v1/auth/login", `${sentinelBackendUrl()}/`);
    const upstream = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
      body: new URLSearchParams({ organization_slug: organizationSlug, username: email, password }),
      cache: "no-store",
      redirect: "manual",
    });
    if (!upstream.ok) {
      return noStore(NextResponse.json(
        { error: upstream.status >= 500 ? "Servicio de autenticación no disponible" : "Credenciales no válidas" },
        { status: upstream.status >= 500 ? 503 : 401 },
      ));
    }
    const body: unknown = await upstream.json().catch(() => null);
    const accessToken = typeof body === "object" && body !== null && "access_token" in body
      && typeof body.access_token === "string" && body.access_token.length > 0
      ? body.access_token
      : undefined;
    if (!accessToken) {
      return noStore(NextResponse.json({ error: "Respuesta de autenticación no válida" }, { status: 502 }));
    }
    const csrfToken = randomBytes(32).toString("base64url");
    const response = NextResponse.json({ ok: true, csrfToken });
    response.cookies.set(SESSION_COOKIE, accessToken, sessionCookieOptions());
    response.cookies.set(CSRF_COOKIE, csrfToken, csrfCookieOptions());
    return noStore(response);
  } catch {
    return noStore(NextResponse.json({ error: "Servicio de autenticación no disponible" }, { status: 503 }));
  }
}
