import { proxyCortex } from "@/lib/server/cortex-proxy";

export async function GET(request: Request) {
  return proxyCortex(request, "ai/health");
}
