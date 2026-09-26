"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, apiErrorMessage } from "@/lib/api";
import { formatGs } from "@/lib/format";

interface Product {
  id: number;
  sku: string;
  name: string;
  category: string;
  brand: string | null;
  selling_price_gs: number;
  purchase_price_gs: number;
  stock_qty: number;
  low_stock_threshold: number;
}

const emptyForm = {
  sku: "",
  name: "",
  category: "Notebooks",
  brand: "",
  purchase_price_gs: 0,
  selling_price_gs: 0,
  iva_rate: 10,
  stock_qty: 0,
  low_stock_threshold: 3,
};

export default function InventarioPage() {
  const queryClient = useQueryClient();
  const [q, setQ] = useState("");
  const [onlyLowStock, setOnlyLowStock] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState<string | null>(null);

  const { data: products, isLoading } = useQuery<Product[]>({
    queryKey: ["products", q, onlyLowStock],
    queryFn: async () =>
      (await api.get("/api/inventory/products", { params: { q: q || undefined, low_stock: onlyLowStock } })).data,
  });

  const createProduct = useMutation({
    mutationFn: async () => (await api.post("/api/inventory/products", form)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      setShowForm(false);
      setForm(emptyForm);
      setError(null);
    },
    onError: (err) => setError(apiErrorMessage(err, "No se pudo crear el producto")),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Inventario</h1>
        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancelar" : "Nuevo producto"}
        </button>
      </div>

      <div className="flex gap-3 items-center">
        <input className="input max-w-sm" placeholder="Buscar por nombre, SKU o codigo de barras..." value={q} onChange={(e) => setQ(e.target.value)} />
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={onlyLowStock} onChange={(e) => setOnlyLowStock(e.target.checked)} />
          Solo stock bajo
        </label>
      </div>

      {showForm && (
        <form
          className="card space-y-3 max-w-lg"
          onSubmit={(e) => {
            e.preventDefault();
            createProduct.mutate();
          }}
        >
          {error && <div className="badge badge-danger py-2 w-full justify-center">{error}</div>}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">SKU</label>
              <input className="input" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} required />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Categoria</label>
              <select className="input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                <option>Notebooks</option>
                <option>PC Armadas</option>
                <option>Componentes</option>
                <option>Perifericos</option>
                <option>Celulares</option>
                <option>Accesorios</option>
                <option>Repuestos</option>
                <option>Otros</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Nombre</label>
            <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Precio de costo (Gs.)</label>
              <input
                className="input"
                type="number"
                value={form.purchase_price_gs}
                onChange={(e) => setForm({ ...form, purchase_price_gs: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Precio de venta (Gs.)</label>
              <input
                className="input"
                type="number"
                value={form.selling_price_gs}
                onChange={(e) => setForm({ ...form, selling_price_gs: Number(e.target.value) })}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Stock inicial</label>
              <input
                className="input"
                type="number"
                value={form.stock_qty}
                onChange={(e) => setForm({ ...form, stock_qty: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Umbral stock bajo</label>
              <input
                className="input"
                type="number"
                value={form.low_stock_threshold}
                onChange={(e) => setForm({ ...form, low_stock_threshold: Number(e.target.value) })}
              />
            </div>
          </div>
          <button className="btn-primary" type="submit" disabled={createProduct.isPending}>
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
                <th className="py-2">SKU</th>
                <th>Nombre</th>
                <th>Categoria</th>
                <th>Precio venta</th>
                <th>Stock</th>
              </tr>
            </thead>
            <tbody>
              {products?.map((p) => {
                const isLow = p.stock_qty <= p.low_stock_threshold;
                return (
                  <tr key={p.id} className="border-t" style={{ borderColor: "var(--color-border)" }}>
                    <td className="py-2">{p.sku}</td>
                    <td className="font-medium">{p.name}</td>
                    <td>{p.category}</td>
                    <td>{formatGs(p.selling_price_gs)}</td>
                    <td>
                      <span className={`badge ${isLow ? "badge-danger" : "badge-success"}`}>{p.stock_qty}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
