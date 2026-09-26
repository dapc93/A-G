# A&G CRM

CRM para A&G — tienda de venta de electronicos e informaticos.

Gestiona clientes (incl. cuenta corriente/fiado), inventario, ventas (POS),
compras a proveedores y servicio tecnico/reparaciones, con una pagina publica
para que el cliente consulte el estado de su equipo sin necesidad de login.

## Origen del proyecto

Este CRM combina patrones de tres fuentes:

- **[OrbitGPS](https://github.com/dapc93/orbitgps)** (proyecto propio): stack base
  (FastAPI + PostgreSQL + Next.js 16 + Tailwind v4), patron de autenticacion JWT,
  arquitectura de `design-tokens/` (primitiva → semantica → componente), guard de
  secretos en produccion, y el patron real de deploy en un VPS compartido.
- **[Tejas3545/CRM](https://github.com/Tejas3545/CRM)** (referencia externa, MIT):
  modelo de datos de CRM+inventario para un negocio minorista (clientes con saldo
  de cuenta corriente, productos con SKU/stock, proveedores, compras, ventas con
  impuesto, pagos, ajustes de stock). Adaptado de GST (India) a IVA Paraguayo
  (10% / 5% / exento).
- **[repairnote-open-source](https://github.com/srmming/repairnote-open-source)**
  (referencia externa): modelo de ordenes de reparacion (ticket, historial de
  estado, tecnico, presupuesto/sena, fotos) y la idea de una pagina publica de
  estado del equipo por token, sin necesidad de que el cliente inicie sesion.

## Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic + PostgreSQL. Ver `backend/`.
- **Frontend**: Next.js 16 (App Router) + Tailwind v4 + TanStack Query + Zustand.
  Ver `frontend/`.
- **design-tokens/**: paleta compartida (capa primitiva), consumida por el
  frontend via `@theme` en `app/globals.css`.

## Desarrollo local

```bash
cp backend/.env.example backend/.env   # editar DATABASE_URL si hace falta
docker compose up --build
```

- Backend: http://localhost:8000/docs (Swagger)
- Frontend: http://localhost:3000

Primer usuario (dueno) — crear con el seed:

```bash
docker compose exec backend python -m app.seed
```

Esto crea `admin` / `cambiar123` (cambiar la contrasena despues del primer login).

### Sin Docker

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Modulos

| Modulo | Que resuelve |
|---|---|
| Clientes | Alta, busqueda, tipo (minorista/mayorista/cuenta corriente), saldo fiado |
| Inventario | Productos, proveedores, compras (ingreso de stock), ajustes de stock, alerta de stock bajo |
| Ventas | POS simple: carrito, IVA automatico, contado/tarjeta/transferencia/cuenta corriente |
| Reparaciones | Ticket con historial de estado, tecnico asignado, presupuesto/sena, items (repuestos descuentan stock), pagina publica de estado |
| Dashboard | Ventas del mes, por cobrar, reparaciones abiertas/listas, stock bajo |

## Deploy en produccion

Ver `DEPLOY.md` — se despliega en el mismo VPS que OrbitGPS, con su propia base
de datos, su propio subdominio y su propio servicio systemd (no comparte
proceso ni base de datos con Orbit).
