# A&G CRM — Deploy en el VPS compartido con OrbitGPS

La topologia real de produccion de OrbitGPS (ver `ORBIT_GPS_PROJECT.md` seccion 5D
de ese repo) **no usa Docker en el servidor** — el `docker-compose.yml` de este
repo es solo para desarrollo local. En produccion Orbit corre:

- Backend: systemd, puerto propio, en `/home/orbitgps/backend`
- Panel admin: PM2, en `/home/orbitgps/admin`
- Postgres/Redis: nativos via systemd (no Docker)
- nginx: el del host (`/etc/nginx/sites-enabled/`), compartido con otros sitios
  de NOBO Consulting

**A&G CRM sigue el mismo patron**, como sistema independiente en el mismo VPS:
propia base de datos, propio servicio systemd, propio subdominio. No comparte
proceso ni base de datos con Orbit.

---

## 1. Base de datos propia

```bash
sudo -u postgres psql -c "CREATE USER ag_crm WITH PASSWORD '<password-fuerte>';"
sudo -u postgres psql -c "CREATE DATABASE ag_crm OWNER ag_crm;"
```

## 2. Clonar y preparar el backend

```bash
sudo mkdir -p /home/agcrm && sudo chown $USER:$USER /home/agcrm
cd /home/agcrm
git clone https://github.com/dapc93/a-g.git app
cd app/backend

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env
```

Variables criticas en `.env`:

| Variable | Valor |
|---|---|
| `DATABASE_URL` | `postgresql+psycopg://ag_crm:<password>@localhost:5432/ag_crm` |
| `SECRET_KEY` / `JWT_SECRET_KEY` | `openssl rand -hex 32` (cada uno) |
| `DEBUG` | `false` |
| `ALLOWED_ORIGINS` | `https://crm.<tu-dominio>` |

El backend **falla el arranque a proposito** si `DEBUG=false` y los secrets
siguen con el valor por defecto (mismo guard que usa Orbit) — evita repetir el
problema de secrets hardcodeados que tuvo ese proyecto.

```bash
alembic upgrade head
python -m app.seed   # crea el usuario admin inicial
```

## 3. Servicio systemd del backend

`/etc/systemd/system/agcrm-api.service`:

```ini
[Unit]
Description=A&G CRM - Backend FastAPI
After=network.target postgresql.service

[Service]
User=agcrm
WorkingDirectory=/home/agcrm/app/backend
Environment="PATH=/home/agcrm/app/backend/.venv/bin"
ExecStart=/home/agcrm/app/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8010
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now agcrm-api
```

Puerto sugerido `8010` (Orbit ya usa 8001 en systemd) — verificar que no choque
con otros servicios del VPS antes de fijarlo.

## 4. Frontend (build + PM2)

```bash
cd /home/agcrm/app/frontend
npm install
NEXT_PUBLIC_API_URL=https://crm.<tu-dominio> npm run build
pm2 start npm --name agcrm-admin -- start -- -p 3010
pm2 save
```

## 5. nginx del host (agregar, no reemplazar el de Orbit)

`/etc/nginx/sites-available/agcrm`:

```nginx
server {
    listen 80;
    server_name crm.<tu-dominio>;

    location /api/ {
        proxy_pass http://127.0.0.1:8010/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:3010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/agcrm /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d crm.<tu-dominio>
```

## 6. Actualizar (deploys siguientes)

```bash
cd /home/agcrm/app
git pull
cd backend && source .venv/bin/activate && pip install -r requirements.txt && alembic upgrade head
sudo systemctl restart agcrm-api
cd ../frontend && npm install && npm run build
pm2 restart agcrm-admin
```

## 7. Backups

```bash
pg_dump -U ag_crm ag_crm > /home/agcrm/backups/ag_crm_$(date +%Y%m%d).sql
```

Programar en cron diario, igual que se recomienda para Orbit.

---

## Pendiente antes de habilitar cobros/facturacion (Fase 2)

Si mas adelante A&G necesita emitir factura electronica legal en Paraguay,
`sifen-service` (microservicio Node.js de OrbitGPS que arma/firma/transmite
documentos electronicos a SIFEN/e-Kuatia via TIPS-SA) se puede reusar tal cual,
corriendo como un tercer servicio en este mismo VPS — no hace falta
reimplementarlo.
