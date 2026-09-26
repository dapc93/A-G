"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Package,
  ShoppingCart,
  Wrench,
  LogOut,
} from "lucide-react";
import { clearToken } from "@/lib/api";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/clientes", label: "Clientes", icon: Users },
  { href: "/inventario", label: "Inventario", icon: Package },
  { href: "/ventas", label: "Ventas", icon: ShoppingCart },
  { href: "/reparaciones", label: "Reparaciones", icon: Wrench },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  return (
    <aside
      className="w-60 shrink-0 h-screen sticky top-0 flex flex-col justify-between p-4"
      style={{ background: "var(--color-surface)", borderRight: "1px solid var(--color-border)" }}
    >
      <div>
        <div className="px-2 py-3 mb-4">
          <p className="font-bold text-lg" style={{ color: "var(--color-primary)" }}>
            A&G CRM
          </p>
          <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
            Electronica e Informatica
          </p>
        </div>
        <nav className="space-y-1">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname?.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium"
                style={{
                  background: active ? "var(--color-primary-light)" : "transparent",
                  color: active ? "var(--color-primary)" : "var(--color-text)",
                }}
              >
                <Icon size={18} />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>

      <button
        onClick={handleLogout}
        className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium"
        style={{ color: "var(--color-text-muted)" }}
      >
        <LogOut size={18} />
        Cerrar sesion
      </button>
    </aside>
  );
}
