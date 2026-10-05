import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const parseMetric = (value: string | undefined): number | null => {
  if (value == null || value.trim() === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = Math.min(Number(searchParams.get("limit") || 60), 200);

    const base = process.cwd();
    const csvPath = path.join(base, "host-metrics", "data", "metrics.csv");
    if (!fs.existsSync(csvPath)) {
      return NextResponse.json({ ok: false, error: "metrics.csv not found" }, { status: 404 });
    }

    const content = fs.readFileSync(csvPath, "utf8");
    const lines = content.trim().split(/\r?\n/);
    if (lines.length <= 1) {
      return NextResponse.json({ ok: true, history: [] });
    }

    const header = lines[0].split(",");
    const dataLines = lines.slice(1);
    const recent = dataLines.slice(-limit);

    const history = recent.map((line) => {
      const cols = line.split(",");
      const row: Record<string, string> = {};
      header.forEach((h, i) => (row[h] = cols[i] ?? ""));

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

    return NextResponse.json({ ok: true, history });
  } catch (e: any) {
    return NextResponse.json({ ok: false, error: e?.message || "error" }, { status: 500 });
  }
}
