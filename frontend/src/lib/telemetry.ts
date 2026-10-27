export function openTelemetrySocket(): WebSocket {
  const endpoint = new URL("/api/v1/telemetry", window.location.origin);
  endpoint.protocol = endpoint.protocol === "https:" ? "wss:" : "ws:";
  // El navegador adjunta automáticamente las cookies del mismo host al handshake.
  return new WebSocket(endpoint);
}
