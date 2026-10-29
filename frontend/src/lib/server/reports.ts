import { constants } from "node:fs";
import { lstat, open, readdir, realpath } from "node:fs/promises";
import path from "node:path";
import { hostMetricsDirectory } from "@/lib/server/host-metrics";

function reportsDirectory(): string {
  return path.join(hostMetricsDirectory(), "reports");
}

export type Report = { id: string; name: string; type: "html" | "md" | "csv" | "other" };

export function isValidReportName(name: string): boolean {
  return name.length > 0 && name !== "." && name !== ".." && !path.isAbsolute(name)
    && !name.includes("/") && !name.includes("\\") && !name.includes("\0");
}

async function reportsRoot(): Promise<string | undefined> {
  const hostMetricsRoot = hostMetricsDirectory();
  const reportsDir = reportsDirectory();
  try {
    if ((await lstat(hostMetricsRoot)).isSymbolicLink()) return undefined;
    if ((await lstat(reportsDir)).isSymbolicLink()) return undefined;
    const root = await realpath(reportsDir);
    return root === reportsDir ? root : undefined;
  } catch {
    return undefined;
  }
}

export async function listReports(): Promise<Report[]> {
  const root = await reportsRoot();
  if (!root) return [];
  const entries = await readdir(/*turbopackIgnore: true*/ root, { withFileTypes: true });
  return entries.filter((entry) => entry.isFile()).map(({ name }) => {
    const extension = path.extname(name).slice(1).toLowerCase();
    const type = extension === "html" ? "html" : extension === "md" ? "md" : extension === "csv" ? "csv" : "other";
    return { id: name, name, type };
  });
}

export async function readReport(name: string): Promise<Buffer | undefined> {
  if (!isValidReportName(name)) return undefined;
  const root = await reportsRoot();
  if (!root) return undefined;
  let file: Awaited<ReturnType<typeof open>> | undefined;
  try {
    file = await open(path.join(/*turbopackIgnore: true*/ root, name), constants.O_RDONLY | constants.O_NOFOLLOW);
    if (!(await file.stat()).isFile()) return undefined;
    return await file.readFile();
  } catch {
    return undefined;
  } finally {
    await file?.close();
  }
}

export function reportNameFromRequest(request: Request): string | undefined {
  const params = new URL(request.url).searchParams;
  return params.get("id") ?? params.get("name") ?? undefined;
}
