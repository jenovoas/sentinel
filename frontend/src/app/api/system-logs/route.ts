import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = Math.min(Number(searchParams.get("limit") || 100), 500);
    const level = searchParams.get("level"); // CRITICAL, ERROR, WARNING, INFO

    const base = process.cwd();
    const csvPath = path.join(base, "host-metrics", "data", "system-logs.csv");
    const summaryPath = path.join(base, "host-metrics", "data", "logs-summary.json");

    // Leer resumen
    let summary = null;
    if (fs.existsSync(summaryPath)) {
      const summaryContent = fs.readFileSync(summaryPath, "utf8");
      summary = JSON.parse(summaryContent);
    }

    // Leer logs CSV
    if (!fs.existsSync(csvPath)) {
      return NextResponse.json({ 
        ok: true, 
        logs: [], 
        summary: summary || { critical_count: 0, error_count: 0, warning_count: 0, total_issues: 0 } 
      });
    }

    const content = fs.readFileSync(csvPath, "utf8");
    const lines = content.trim().split(/\r?\n/);
    
    if (lines.length <= 1) {
      return NextResponse.json({ ok: true, logs: [], summary });
    }

    const header = lines[0].split(",");
    const dataLines = lines.slice(1);

    // Parsear y filtrar logs
    let logs = dataLines.map((line) => {
      const cols = line.split(",");
      return {
        timestamp: cols[0] || "",
        level: cols[1] || "INFO",
        unit: cols[2] || "system",
        message: cols.slice(3).join(",") || "",
      };
    });

    // Filtrar por nivel si se especifica
    if (level) {
      logs = logs.filter((log) => log.level === level.toUpperCase());
    }

    // Ordenar por timestamp descendente y limitar
    logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    logs = logs.slice(0, limit);

    return NextResponse.json({ 
      ok: true, 
      logs,
      summary: summary || { critical_count: 0, error_count: 0, warning_count: 0, total_issues: 0 },
      total: logs.length 
    });
  } catch (e: any) {
    return NextResponse.json({ ok: false, error: e?.message || "error" }, { status: 500 });
  }
}
