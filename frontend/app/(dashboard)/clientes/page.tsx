"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, apiErrorMessage } from "@/lib/api";
import { formatGs } from "@/lib/format";

interface Client {
  id: number;
  name: string;
  ruc_ci: string | null;
  phone: string | null;
  email: string | null;
  tipo: string;
  credit_balance: number;
}

const TIPO_LABEL: Record<string, string> = {
  minorista: "Minorista",
  mayorista: "Mayorista",
  cuenta_corriente: "Cuenta corriente",
};

export default function ClientesPage() {
  const queryClient = useQueryClient();
  const [q, setQ] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", ruc_ci: "", phone: "", email: "", tipo: "minorista" });
  const [error, setError] = useState<string | null>(null);

  const { data: clients, isLoading } = useQuery<Client[]>({
    queryKey: ["clients", q],
    queryFn: async () => (await api.get("/api/clients", { params: { q: q || undefined } })).data,
  });

  const createClient = useMutation({
    mutationFn: async () => (await api.post("/api/clients", form)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      setShowForm(false);
      setForm({ name: "", ruc_ci: "", phone: "", email: "", tipo: "minorista" });
      setError(null);
    },
    onError: (err) => setError(apiErrorMessage(err, "No se pudo crear el cliente")),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Clientes</h1>
        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancelar" : "Nuevo cliente"}
        </button>
      </div>

      <input
        className="input max-w-sm"
        placeholder="Buscar por nombre, telefono o RUC/CI..."
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />

      {showForm && (
        <form
          className="card space-y-3 max-w-lg"
          onSubmit={(e) => {
            e.preventDefault();
            createClient.mutate();
          }}
        >
          {error && <div className="badge badge-danger py-2 w-full justify-center">{error}</div>}
          <div>
            <label className="block text-sm font-medium mb-1">Nombre</label>
            <input
              className="input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">RUC / CI</label>
              <input className="input" value={form.ruc_ci} onChange={(e) => setForm({ ...form, ruc_ci: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Telefono</label>
              <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input className="input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Tipo</label>
            <select className="input" value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
              <option value="minorista">Minorista</option>
              <option value="mayorista">Mayorista</option>
              <option value="cuenta_corriente">Cuenta corriente</option>
            </select>
          </div>
          <button className="btn-primary" type="submit" disabled={createClient.isPending}>
            Guardar
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
                <th className="py-2">Nombre</th>
                <th>RUC/CI</th>
                <th>Telefono</th>
                <th>Tipo</th>
                <th>Saldo</th>
              </tr>
            </thead>
            <tbody>
              {clients?.map((c) => (
                <tr key={c.id} className="border-t" style={{ borderColor: "var(--color-border)" }}>
                  <td className="py-2 font-medium">{c.name}</td>
                  <td>{c.ruc_ci ?? "-"}</td>
                  <td>{c.phone ?? "-"}</td>
                  <td>
                    <span className="badge badge-info">{TIPO_LABEL[c.tipo] ?? c.tipo}</span>
                  </td>
                  <td className={c.credit_balance > 0 ? "font-medium" : ""} style={c.credit_balance > 0 ? { color: "var(--color-warning)" } : undefined}>
                    {formatGs(c.credit_balance)}
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
