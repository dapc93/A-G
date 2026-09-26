"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatDateTime, formatGs } from "@/lib/format";

interface PublicStatus {
  ticket: string;
  equipo_tipo: string;
  marca: string;
  modelo: string;
  falla_reportada: string;
  status: string;
  status_history: { status: string; at: string }[];
  presupuesto_gs: number;
  created_at: string;
  updated_at: string;
}

const ESTADO_LABEL: Record<string, string> = {
  recibido: "Recibido",
  diagnosticado: "Diagnosticado",
  reparando: "En reparacion",
  esperando_repuesto: "Esperando repuesto",
  listo: "Listo para retirar",
  entregado: "Entregado",
  cancelado: "Cancelado",
};

export default function PublicStatusPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = use(params);

  const { data, isLoading, isError } = useQuery<PublicStatus>({
    queryKey: ["public-repair-status", token],
    queryFn: async () => (await api.get(`/api/public/repairs/status/${token}`)).data,
  });

  if (isLoading) return <div className="min-h-screen flex items-center justify-center">Cargando...</div>;
  if (isError || !data)
    return <div className="min-h-screen flex items-center justify-center">No se encontro esta orden de reparacion.</div>;

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10">
      <div className="card w-full max-w-md space-y-4">
        <div>
          <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
            A&G Electronica e Informatica
          </p>
          <h1 className="text-lg font-semibold">Orden {data.ticket}</h1>
        </div>

        <div className="badge badge-info text-sm py-2 px-4">{ESTADO_LABEL[data.status] ?? data.status}</div>

        <div className="text-sm space-y-1">
          <p>
            <strong>Equipo:</strong> {data.equipo_tipo} {data.marca} {data.modelo}
          </p>
          <p>
            <strong>Falla reportada:</strong> {data.falla_reportada}
          </p>
          {data.presupuesto_gs > 0 && (
            <p>
              <strong>Presupuesto estimado:</strong> {formatGs(data.presupuesto_gs)}
            </p>
          )}
        </div>

        <div>
          <p className="text-sm font-medium mb-2">Historial</p>
          <ul className="space-y-1 text-sm">
            {data.status_history.map((h, i) => (
              <li key={i} className="flex justify-between">
                <span>{ESTADO_LABEL[h.status] ?? h.status}</span>
                <span style={{ color: "var(--color-text-muted)" }}>{formatDateTime(h.at)}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
