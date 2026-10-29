import "server-only";
import path from "node:path";

export function hostMetricsDirectory(): string {
  const configured = process.env.SENTINEL_HOST_METRICS_DIR;
  if (configured) return path.resolve(/*turbopackIgnore: true*/ configured);
  return path.resolve(/*turbopackIgnore: true*/ process.cwd(), "host-metrics");
}

export function hostMetricsFile(...segments: string[]): string {
  const root = hostMetricsDirectory();
  const target = path.resolve(root, ...segments);
  const relative = path.relative(root, target);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error("Invalid host metrics path");
  }
  return target;
}
