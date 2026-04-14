import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const p = searchParams.get("path");
  if (!p) return NextResponse.json({ ok: false, error: "path required" }, { status: 400 });

  const baseDir = path.resolve(process.cwd(), "host-metrics", "reports");
  const absolutePath = path.resolve(p);

  // Robust path traversal check
  const relative = path.relative(baseDir, absolutePath);
  const isOutside = relative.startsWith('..') || path.isAbsolute(relative);

  if (isOutside) {
    return NextResponse.json({ ok: false, error: "Access denied" }, { status: 403 });
  }

  if (!fs.existsSync(absolutePath) || fs.lstatSync(absolutePath).isDirectory()) {
    return NextResponse.json({ ok: false, error: "File not found" }, { status: 404 });
  }

  const name = path.basename(absolutePath);
  const buf = fs.readFileSync(absolutePath);
  return new NextResponse(buf, {
    headers: {
      "Content-Type": "application/octet-stream",
      "Content-Disposition": `attachment; filename=${name}`,
    },
  });
}
