"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, apiErrorMessage } from "@/lib/api";
import { formatDateTime, formatGs } from "@/lib/format";

interface Client {
  id: number;
  name: string;
}

interface RepairOrder {
  id: number;
  ticket: string;
  client_id: number;
  equipo_tipo: string;
  marca: string;
  modelo: string;
  falla_reportada: string;
  status: string;
  presupuesto_gs: number;
  total_gs: number;
  payment_status: string;
  public_token: string;
  created_at: string;
}

const ESTADOS = ["recibido", "diagnosticado", "reparando", "esperando_repuesto", "listo", "entregado", "cancelado"];

const ESTADO_BADGE: Record<string, string> = {
  recibido: "badge-info",
  diagnosticado: "badge-info",
  reparando: "badge-warning",
  esperando_repuesto: "badge-warning",
  listo: "badge-success",
  entregado: "badge-success",
  cancelado: "badge-danger",
};

const emptyForm = {
  client_id: "",
  equipo_tipo: "Notebook",
  marca: "",
  modelo: "",
  falla_reportada: "",
  presupuesto_gs: 0,
};

export default function ReparacionesPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState<string | null>(null);

  const { data: repairs, isLoading } = useQuery<RepairOrder[]>({
    queryKey: ["repairs"],
    queryFn: async () => (await api.get("/api/repairs")).data,
  });

  const { data: clients } = useQuery<Client[]>({
    queryKey: ["clients-all"],
    queryFn: async () => (await api.get("/api/clients")).data,
  });

  const createRepair = useMutation({
    mutationFn: async () =>
      (
        await api.post("/api/repairs", {
          ...form,
          client_id: Number(form.client_id),
        })
      ).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repairs"] });
      setShowForm(false);
      setForm(emptyForm);
      setError(null);
    },
    onError: (err) => setError(apiErrorMessage(err, "No se pudo crear la orden")),
  });

  const updateStatus = useMutation({
    mutationFn: async ({ id, status }: { id: number; status: string }) =>
      (await api.patch(`/api/repairs/${id}/status`, { status })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["repairs"] }),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Servicio tecnico</h1>
        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancelar" : "Nueva orden"}
        </button>
      </div>

      {showForm && (
        <form
          className="card space-y-3 max-w-lg"
          onSubmit={(e) => {
            e.preventDefault();
            createRepair.mutate();
          }}
        >
          {error && <div className="badge badge-danger py-2 w-full justify-center">{error}</div>}
          <div>
            <label className="block text-sm font-medium mb-1">Cliente</label>
            <select className="input" value={form.client_id} onChange={(e) => setForm({ ...form, client_id: e.target.value })} required>
              <option value="">Seleccionar...</option>
              {clients?.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Equipo</label>
              <select className="input" value={form.equipo_tipo} onChange={(e) => setForm({ ...form, equipo_tipo: e.target.value })}>
                <option>Notebook</option>
                <option>PC</option>
                <option>Celular</option>
                <option>Impresora</option>
                <option>Otro</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Marca</label>
              <input className="input" value={form.marca} onChange={(e) => setForm({ ...form, marca: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Modelo</label>
              <input className="input" value={form.modelo} onChange={(e) => setForm({ ...form, modelo: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Falla reportada</label>
            <textarea
              className="input"
              value={form.falla_reportada}
              onChange={(e) => setForm({ ...form, falla_reportada: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Presupuesto estimado (Gs.)</label>
            <input
              className="input"
              type="number"
              value={form.presupuesto_gs}
              onChange={(e) => setForm({ ...form, presupuesto_gs: Number(e.target.value) })}
            />
          </div>
          <button className="btn-primary" type="submit" disabled={createRepair.isPending}>
            Crear orden
          </button>
        </form>
      )}

      <div className="card overflow-x-auto">
        {isLoading ? (
          <p>Cargando...</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left" style={{ color: "var(--color-text-muted)" }}>
                <th className="py-2">Ticket</th>
                <th>Equipo</th>
                <th>Falla</th>
                <th>Estado</th>
                <th>Presupuesto</th>
                <th>Link publico</th>
              </tr>
            </thead>
            <tbody>
              {repairs?.map((r) => (
                <tr key={r.id} className="border-t align-top" style={{ borderColor: "var(--color-border)" }}>
                  <td className="py-2 font-medium">{r.ticket}</td>
                  <td>
                    {r.equipo_tipo} {r.marca} {r.modelo}
                  </td>
                  <td className="max-w-xs">{r.falla_reportada}</td>
                  <td>
                    <select
                      className="badge input"
                      style={{ padding: "0.125rem 0.5rem" }}
                      value={r.status}
                      onChange={(e) => updateStatus.mutate({ id: r.id, status: e.target.value })}
                    >
                      {ESTADOS.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                    <span className={`badge ${ESTADO_BADGE[r.status]} ml-1`}>{r.status}</span>
                  </td>
                  <td>{formatGs(r.presupuesto_gs)}</td>
                  <td>
                    <a
                      className="text-xs underline"
                      style={{ color: "var(--color-primary)" }}
                      href={`/estado/${r.public_token}`}
                      target="_blank"
                    >
                      Ver estado
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
