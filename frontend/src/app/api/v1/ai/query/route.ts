import { proxyCortex } from "@/lib/server/cortex-proxy";

export async function POST(request: Request) {
  return proxyCortex(request, "ai/query");
}
