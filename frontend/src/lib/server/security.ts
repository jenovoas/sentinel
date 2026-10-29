import { timingSafeEqual } from "node:crypto";

export const SESSION_COOKIE = "sentinel_session";
export const CSRF_COOKIE = "sentinel_csrf";

export function readCookie(request: Request, name: string): string | undefined {
  const prefix = `${name}=`;
  const value = request.headers
    .get("cookie")
    ?.split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(prefix))
    ?.slice(prefix.length);
  if (!value) return undefined;
  try {
    return decodeURIComponent(value);
  } catch {
    return undefined;
  }
}

export function isSameOrigin(request: Request): boolean {
  const origin = request.headers.get("origin");
  if (!origin) return false;
  try {
    const parsedOrigin = new URL(origin);
    const forwardedHost = request.headers.get("x-forwarded-host")?.split(",")[0].trim();
    const requestHost = forwardedHost || request.headers.get("host") || new URL(request.url).host;
    const forwardedProto = request.headers.get("x-forwarded-proto")?.split(",")[0].trim();
    if (parsedOrigin.host.toLowerCase() !== requestHost.toLowerCase()) return false;
    if (forwardedProto && parsedOrigin.protocol !== `${forwardedProto}:`) return false;
    if (process.env.NODE_ENV === "production" && parsedOrigin.protocol !== "https:") return false;
    return parsedOrigin.protocol === "http:" || parsedOrigin.protocol === "https:";
  } catch {
    return false;
  }
}

export function hasValidCsrf(request: Request): boolean {
  const cookie = readCookie(request, CSRF_COOKIE);
  const header = request.headers.get("x-csrf-token");
  if (!cookie || !header) return false;
  const cookieBytes = Buffer.from(cookie);
  const headerBytes = Buffer.from(header);
  return cookieBytes.length === headerBytes.length && timingSafeEqual(cookieBytes, headerBytes);
}
