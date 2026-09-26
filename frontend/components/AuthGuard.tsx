"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getToken } from "@/lib/api";
import { useAuthStore } from "@/lib/auth";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const setUser = useAuthStore((s) => s.setUser);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }
    api
      .get("/api/auth/me")
      .then(({ data }) => {
        setUser(data);
        setReady(true);
      })
      .catch(() => router.replace("/login"));
  }, [router, setUser]);

  if (!ready) {
    return <div className="min-h-screen flex items-center justify-center">Cargando...</div>;
  }
  return <>{children}</>;
}
