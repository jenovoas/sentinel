import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    const base = process.cwd();
    const dir = path.join(base, "host-metrics", "reports");
    if (!fs.existsSync(dir)) {
      return NextResponse.json({ ok: true, items: [] });
    }
    const files = fs.readdirSync(dir);
    const items = files.map((name) => {
      const ext = name.split(".").pop()?.toLowerCase() || "";
      const type = ext === "html" ? "html" : ext === "md" ? "md" : ext === "csv" ? "csv" : "other";
      return { name, path: path.join(dir, name), type };
    });
    return NextResponse.json({ ok: true, items });
  } catch (e: any) {
    return NextResponse.json({ ok: false, error: e?.message || "error" }, { status: 500 });
  }
}
