import { NextResponse } from "next/server";
import fs from "fs";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const p = searchParams.get("path");
  if (!p) return NextResponse.json({ ok: false, error: "path required" }, { status: 400 });
  const html = fs.readFileSync(p, "utf8");
  return new NextResponse(html, {
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}
