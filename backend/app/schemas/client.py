from datetime import datetime

from pydantic import BaseModel


class ClientCreate(BaseModel):
    name: str
    ruc_ci: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    tipo: str = "minorista"
    notes: str | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    ruc_ci: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    tipo: str | None = None
    notes: str | None = None


class ClientOut(BaseModel):
    id: int
    name: str
    ruc_ci: str | None
    phone: str | None
    email: str | None
    address: str | None
    tipo: str
    credit_balance: float
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True
