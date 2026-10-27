import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { noStore, sessionError, validateSession } from "@/lib/server/session";

export async function GET(request: Request) {
  const session = await validateSession(request);
  if (!session.ok) return sessionError(session.status);

  try {
    const { searchParams } = new URL(request.url);
    const requestedLimit = Number(searchParams.get("limit") || 100);
    const limit = Number.isFinite(requestedLimit) ? Math.max(1, Math.min(requestedLimit, 500)) : 100;
    const level = searchParams.get("level")?.toUpperCase();

    const dataDirectory = path.join(process.cwd(), "host-metrics", "data");
    const csvPath = path.join(dataDirectory, "system-logs.csv");
    const summaryPath = path.join(dataDirectory, "logs-summary.json");
    let summary = null;
    if (fs.existsSync(summaryPath)) summary = JSON.parse(fs.readFileSync(summaryPath, "utf8"));

    if (!fs.existsSync(csvPath)) {
      return noStore(NextResponse.json({
        ok: true,
        available: false,
        logs: [],
        summary: summary || { critical_count: 0, error_count: 0, warning_count: 0, total_issues: 0 },
      }));
    }

    const lines = fs.readFileSync(csvPath, "utf8").trim().split(/\r?\n/);
    if (lines.length <= 1) return noStore(NextResponse.json({ ok: true, available: true, logs: [], summary }));

    let logs = lines.slice(1).map((line) => {
      const columns = line.split(",");
      return {
        timestamp: columns[0] || "",
        level: columns[1] || "INFO",
        unit: columns[2] || "system",
        message: columns.slice(3).join(",") || "",
      };
    });
    if (level) logs = logs.filter((log) => log.level === level);
    logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    logs = logs.slice(0, limit);

    return noStore(NextResponse.json({
      ok: true,
      available: true,
      logs,
      summary: summary || { critical_count: 0, error_count: 0, warning_count: 0, total_issues: 0 },
      total: logs.length,
    }));
  } catch {
    return noStore(NextResponse.json({ ok: false, error: "No se pudieron leer los registros" }, { status: 500 }));
  }
}
