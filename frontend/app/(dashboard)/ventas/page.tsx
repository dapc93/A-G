"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, apiErrorMessage } from "@/lib/api";
import { formatDateTime, formatGs } from "@/lib/format";

interface Product {
  id: number;
  name: string;
  sku: string;
  selling_price_gs: number;
  stock_qty: number;
}

interface Client {
  id: number;
  name: string;
}

interface Sale {
  id: number;
  invoice_no: string;
  date: string;
  total_gs: number;
  payment_type: string;
  payment_status: string;
}

interface CartLine {
  product_id: number;
  name: string;
  qty: number;
  unit_price_gs: number;
}

const PAYMENT_STATUS_BADGE: Record<string, string> = {
  pagado: "badge-success",
  parcial: "badge-warning",
  pendiente: "badge-danger",
};

export default function VentasPage() {
  const queryClient = useQueryClient();
  const [clientId, setClientId] = useState<string>("");
  const [paymentType, setPaymentType] = useState("contado");
  const [amountPaid, setAmountPaid] = useState<number>(0);
  const [cart, setCart] = useState<CartLine[]>([]);
  const [productQuery, setProductQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data: sales } = useQuery<Sale[]>({
    queryKey: ["sales"],
    queryFn: async () => (await api.get("/api/sales")).data,
  });

  const { data: clients } = useQuery<Client[]>({
    queryKey: ["clients-all"],
    queryFn: async () => (await api.get("/api/clients")).data,
  });

  const { data: availableProducts } = useQuery<Product[]>({
    queryKey: ["products-available", productQuery],
    queryFn: async () => (await api.get("/api/inventory/products", { params: { q: productQuery || undefined } })).data,
  });

  const total = cart.reduce((sum, l) => sum + l.qty * l.unit_price_gs, 0);

  function addToCart(p: Product) {
    setCart((prev) => {
      const existing = prev.find((l) => l.product_id === p.id);
      if (existing) {
        return prev.map((l) => (l.product_id === p.id ? { ...l, qty: l.qty + 1 } : l));
      }
      return [...prev, { product_id: p.id, name: p.name, qty: 1, unit_price_gs: p.selling_price_gs }];
    });
  }

  function removeFromCart(productId: number) {
    setCart((prev) => prev.filter((l) => l.product_id !== productId));
  }

  const createSale = useMutation({
    mutationFn: async () =>
      (
        await api.post("/api/sales", {
          client_id: clientId ? Number(clientId) : null,
          payment_type: paymentType,
          amount_paid_gs: amountPaid,
          items: cart.map((l) => ({ product_id: l.product_id, qty: l.qty, unit_price_gs: l.unit_price_gs })),
        })
      ).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sales"] });
      queryClient.invalidateQueries({ queryKey: ["products-available"] });
      setCart([]);
      setAmountPaid(0);
      setError(null);
    },
    onError: (err) => setError(apiErrorMessage(err, "No se pudo registrar la venta")),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Ventas</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card space-y-3">
          <h2 className="font-medium">Nueva venta</h2>
          {error && <div className="badge badge-danger py-2 w-full justify-center">{error}</div>}

          <div>
            <label className="block text-sm font-medium mb-1">Cliente (opcional)</label>
            <select className="input" value={clientId} onChange={(e) => setClientId(e.target.value)}>
              <option value="">Consumidor final</option>
              {clients?.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Buscar producto</label>
            <input className="input" value={productQuery} onChange={(e) => setProductQuery(e.target.value)} placeholder="SKU o nombre..." />
            <div className="mt-2 space-y-1 max-h-40 overflow-y-auto">
              {availableProducts?.map((p) => (
                <button
                  type="button"
                  key={p.id}
                  onClick={() => addToCart(p)}
                  className="w-full text-left text-sm px-2 py-1 rounded hover:bg-gray-50 flex justify-between"
                  disabled={p.stock_qty <= 0}
                >
                  <span>
                    {p.name} <span style={{ color: "var(--color-text-muted)" }}>({p.stock_qty} en stock)</span>
                  </span>
                  <span>{formatGs(p.selling_price_gs)}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-1">
            {cart.map((l) => (
              <div key={l.product_id} className="flex justify-between items-center text-sm">
                <span>
                  {l.qty} x {l.name}
                </span>
                <div className="flex items-center gap-2">
                  <span>{formatGs(l.qty * l.unit_price_gs)}</span>
                  <button type="button" onClick={() => removeFromCart(l.product_id)} className="text-xs" style={{ color: "var(--color-danger)" }}>
                    quitar
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-between font-semibold pt-2 border-t" style={{ borderColor: "var(--color-border)" }}>
            <span>Total</span>
            <span>{formatGs(total)}</span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Forma de pago</label>
              <select className="input" value={paymentType} onChange={(e) => setPaymentType(e.target.value)}>
                <option value="contado">Contado</option>
                <option value="tarjeta">Tarjeta</option>
                <option value="transferencia">Transferencia</option>
                <option value="cuenta_corriente">Cuenta corriente</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Monto pagado (Gs.)</label>
              <input className="input" type="number" value={amountPaid} onChange={(e) => setAmountPaid(Number(e.target.value))} />
            </div>
          </div>

          <button
            className="btn-primary w-full"
            disabled={cart.length === 0 || createSale.isPending}
            onClick={() => createSale.mutate()}
          >
            Registrar venta
          </button>
        </div>

        <div className="card">
          <h2 className="font-medium mb-3">Ultimas ventas</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left" style={{ color: "var(--color-text-muted)" }}>
                <th className="py-2">Factura</th>
                <th>Fecha</th>
                <th>Total</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {sales?.map((s) => (
                <tr key={s.id} className="border-t" style={{ borderColor: "var(--color-border)" }}>
                  <td className="py-2">{s.invoice_no}</td>
                  <td>{formatDateTime(s.date)}</td>
                  <td>{formatGs(s.total_gs)}</td>
                  <td>
                    <span className={`badge ${PAYMENT_STATUS_BADGE[s.payment_status] ?? "badge-info"}`}>{s.payment_status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
