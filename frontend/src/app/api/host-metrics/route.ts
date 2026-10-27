import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { noStore, sessionError, validateSession } from "@/lib/server/session";

const parseMetric = (value: string | undefined): number | null => {
  if (value == null || value.trim() === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

export async function GET(request: Request) {
  const session = await validateSession(request);
  if (!session.ok) return sessionError(session.status);

  try {
    const requestedLimit = Number(new URL(request.url).searchParams.get("limit") || 60);
    const limit = Number.isFinite(requestedLimit) ? Math.max(1, Math.min(requestedLimit, 200)) : 60;
    const csvPath = path.join(process.cwd(), "host-metrics", "data", "metrics.csv");
    if (!fs.existsSync(csvPath)) {
      return noStore(NextResponse.json({ ok: false, error: "metrics.csv not found" }, { status: 404 }));
    }

    const lines = fs.readFileSync(csvPath, "utf8").trim().split(/\r?\n/);
    if (lines.length <= 1) return noStore(NextResponse.json({ ok: true, history: [] }));

    const header = lines[0].split(",");
    const history = lines.slice(1).slice(-limit).map((line) => {
      const columns = line.split(",");
      const row: Record<string, string> = {};
      header.forEach((key, index) => { row[key] = columns[index] ?? ""; });
      return {
        timestamp: row.timestamp,
        cpu_percent: parseMetric(row.cpu_percent),
        mem_percent: parseMetric(row.mem_percent),
        gpu_percent: parseMetric(row.gpu_percent),
        network: {
          net_bytes_sent: parseMetric(row.net_bytes_sent),
          net_bytes_recv: parseMetric(row.net_bytes_recv),
          wifi: {
            ssid: row.wifi_ssid || "",
            signal: parseMetric(row.wifi_signal),
            connected: !!row.wifi_ssid,
          },
        },
      };
    });

    return noStore(NextResponse.json({ ok: true, history }));
  } catch {
    return noStore(NextResponse.json({ ok: false, error: "No se pudieron leer las métricas" }, { status: 500 }));
  }
}
