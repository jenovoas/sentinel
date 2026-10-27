"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Navigation } from "@/components/Navigation";
import { WipModal } from "@/components/WipModal";

type SessionState = "checking" | "anonymous" | "authenticated";

export function SessionGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [state, setState] = useState<SessionState>("checking");
  const isLogin = pathname === "/login";

  useEffect(() => {
    if (isLogin) {
      setState("anonymous");
      return;
    }
    if (state === "authenticated") return;

    const controller = new AbortController();
    setState("checking");
    fetch("/api/auth/me", { cache: "no-store", signal: controller.signal })
      .then((response) => {
        if (response.ok) setState("authenticated");
        else {
          setState("anonymous");
          router.replace("/login");
        }
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setState("anonymous");
          router.replace("/login");
        }
      });

    return () => controller.abort();
  }, [isLogin, pathname, router, state]);

  if (isLogin) return children;
  if (state !== "authenticated") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-300" role="status" aria-live="polite">
        <p>Comprobando sesión…</p>
      </div>
    );
  }

  return (
    <>
      <WipModal />
      <Navigation />
      <main style={{ paddingTop: "72px" }}>{children}</main>
    </>
  );
}
