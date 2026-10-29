import "server-only";

export function sentinelBackendUrl(): string {
  const configured = process.env.SENTINEL_BACKEND_URL;
  if (configured) return configured.replace(/\/+$/, "");
  if (process.env.NODE_ENV === "production") {
    throw new Error("SENTINEL_BACKEND_URL must point to the private Fenix API over WireGuard");
  }
  return "http://backend:8000";
}
