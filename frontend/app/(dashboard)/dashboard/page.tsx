"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatGs } from "@/lib/format";

interface DashboardData {
  ventas_mes_gs: number;
  cantidad_ventas_mes: number;
  reparaciones_abiertas: number;
  reparaciones_listas_para_entregar: number;
  productos_stock_bajo: number;
  total_por_cobrar_gs: number;
}

function StatCard({ label, value, tone }: { label: string; value: string; tone?: "warning" | "danger" }) {
  return (
    <div className="card">
      <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
        {label}
      </p>
      <p
        className="text-2xl font-semibold mt-1"
        style={{ color: tone === "warning" ? "var(--color-warning)" : tone === "danger" ? "var(--color-danger)" : "var(--color-text)" }}
      >
        {value}
      </p>
    </div>
  );
}

export default function DashboardPage() {
  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: async () => (await api.get("/api/dashboard")).data,
  });

  if (isLoading || !data) return <p>Cargando...</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard label="Ventas del mes" value={formatGs(data.ventas_mes_gs)} />
        <StatCard label="Cantidad de ventas" value={String(data.cantidad_ventas_mes)} />
        <StatCard label="Por cobrar (cuenta corriente)" value={formatGs(data.total_por_cobrar_gs)} tone="warning" />
        <StatCard label="Reparaciones abiertas" value={String(data.reparaciones_abiertas)} />
        <StatCard label="Listas para entregar" value={String(data.reparaciones_listas_para_entregar)} tone="warning" />
        <StatCard label="Productos con stock bajo" value={String(data.productos_stock_bajo)} tone="danger" />
      </div>
    </div>
  );
}
