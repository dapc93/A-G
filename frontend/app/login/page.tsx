"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, apiErrorMessage, setToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { data } = await api.post("/api/auth/login", { username, password });
      setToken(data.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(apiErrorMessage(err, "No se pudo iniciar sesion"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <form onSubmit={handleSubmit} className="card w-full max-w-sm space-y-4">
        <div>
          <h1 className="text-xl font-semibold">A&G CRM</h1>
          <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
            Electronica e Informatica
          </p>
        </div>

        {error && (
          <div className="badge badge-danger w-full justify-center py-2">{error}</div>
        )}

        <div>
          <label className="block text-sm font-medium mb-1">Usuario</label>
          <input
            className="input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Contrasena</label>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button className="btn-primary w-full" type="submit" disabled={loading}>
          {loading ? "Ingresando..." : "Ingresar"}
        </button>
      </form>
    </div>
  );
}
