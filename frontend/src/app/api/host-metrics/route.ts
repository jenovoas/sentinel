import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

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
        cpu_percent: Number(row.cpu_percent || 0),
        mem_percent: Number(row.mem_percent || 0),
        gpu_percent: Number(row.gpu_percent || 0),
        network: {
          net_bytes_sent: Number(row.net_bytes_sent || 0),
          net_bytes_recv: Number(row.net_bytes_recv || 0),
          wifi: {
            ssid: row.wifi_ssid || "",
            signal: Number(row.wifi_signal || 0),
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
