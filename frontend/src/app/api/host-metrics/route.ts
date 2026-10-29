import { NextResponse } from "next/server";
import fs from "fs";
import { noStore, sessionError, validateSession } from "@/lib/server/session";
import { hostMetricsFile } from "@/lib/server/host-metrics";

export async function GET(request: Request) {
  const session = await validateSession(request);
  if (!session.ok) return sessionError(session.status);
  try {
    const { searchParams } = new URL(request.url);
    const limit = Math.min(Number(searchParams.get("limit") || 60), 200);

    const csvPath = hostMetricsFile("data", "metrics.csv");
    if (!fs.existsSync(csvPath)) {
      return noStore(NextResponse.json({ ok: false, error: "metrics.csv not found" }, { status: 404 }));
    }

    const content = fs.readFileSync(csvPath, "utf8");
    const lines = content.trim().split(/\r?\n/);
    if (lines.length <= 1) {
      return noStore(NextResponse.json({ ok: true, history: [] }));
    }

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
  } catch (e: any) {
    return noStore(NextResponse.json({ ok: false, error: e?.message || "error" }, { status: 500 }));
  }
}
