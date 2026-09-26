import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, clients, dashboard, inventory, repairs, sales
from app.core.config import settings

DEFAULT_SECRET_PREFIX = "cambiar-en-produccion"

if not settings.DEBUG:
    if settings.SECRET_KEY.startswith(DEFAULT_SECRET_PREFIX) or settings.JWT_SECRET_KEY.startswith(
        DEFAULT_SECRET_PREFIX
    ):
        sys.exit(
            "SECRET_KEY / JWT_SECRET_KEY siguen con el valor por defecto. "
            "Configuralos en el .env de produccion antes de arrancar (openssl rand -hex 32)."
        )

app = FastAPI(title="A&G CRM API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(repairs.router)
app.include_router(repairs.public_router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}
