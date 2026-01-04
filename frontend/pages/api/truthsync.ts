// Next.js API route that proxies requests to the existing TruthSync FastAPI service
// The backend FastAPI runs on http://127.0.0.1:8000 and already exposes the /truthsync router.
// This proxy simply forwards the request path and method, allowing the frontend to call
// /api/truthsync/* without needing to know the backend address.

import type { NextApiRequest, NextApiResponse } from "next";
import { createProxyMiddleware } from "http-proxy-middleware";

export const config = {
  api: {
    bodyParser: false, // let http-proxy handle the body parsing
  },
};

// Create a proxy that forwards everything under /api/truthsync to the backend service.
export default createProxyMiddleware({
  target: "http://127.0.0.1:8000",
  changeOrigin: true,
  pathRewrite: {
    "^/api/truthsync": "/truthsync", // strip the /api prefix
  },
  // Allow only safe HTTP methods – the backend already validates further.
  onProxyReq: (proxyReq, req: NextApiRequest) => {
    const allowed = ["GET", "POST", "PUT", "DELETE", "PATCH"];
    if (!allowed.includes(req.method ?? "")) {
      proxyReq.abort();
    }
  },
});
