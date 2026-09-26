from datetime import datetime

from pydantic import BaseModel, Field


class RepairItemCreate(BaseModel):
    product_id: int | None = None
    name: str
    qty: float = Field(default=1.0, gt=0.0)
    price_gs: float = Field(default=0.0, ge=0.0)
    cost_gs: float = Field(default=0.0, ge=0.0)


class RepairOrderCreate(BaseModel):
    client_id: int
    equipo_tipo: str
    marca: str = ""
    modelo: str = ""
    numero_serie: str | None = None
    falla_reportada: str
    nota_interna: str | None = None
    password_equipo: str | None = None
    presupuesto_gs: float = Field(default=0.0, ge=0.0)
    sena_gs: float = Field(default=0.0, ge=0.0)
    technician_id: int | None = None
    foto_ingreso_url: str | None = None


class RepairOrderUpdate(BaseModel):
    equipo_tipo: str | None = None
    marca: str | None = None
    modelo: str | None = None
    numero_serie: str | None = None
    falla_reportada: str | None = None
    nota_interna: str | None = None
    password_equipo: str | None = None
    presupuesto_gs: float | None = None
    sena_gs: float | None = None
    descuento_gs: float | None = None
    technician_id: int | None = None
    foto_egreso_url: str | None = None


class RepairStatusUpdate(BaseModel):
    status: str


class RepairItemOut(BaseModel):
    id: int
    product_id: int | None
    name: str
    qty: float
    price_gs: float
    cost_gs: float

    class Config:
        from_attributes = True


class RepairPaymentCreate(BaseModel):
    amount_gs: float = Field(gt=0.0)
    mode: str = "efectivo"
    note: str | None = None


class RepairPaymentOut(BaseModel):
    id: int
    amount_gs: float
    mode: str
    note: str | None
    paid_at: datetime

    class Config:
        from_attributes = True


class RepairOrderOut(BaseModel):
    id: int
    ticket: str
    client_id: int
    equipo_tipo: str
    marca: str
    modelo: str
    numero_serie: str | None
    falla_reportada: str
    nota_interna: str | None
    status: str
    status_history: list
    technician_id: int | None
    presupuesto_gs: float
    sena_gs: float
    descuento_gs: float
    costo_gs: float
    total_gs: float
    payment_status: str
    foto_ingreso_url: str | None
    foto_egreso_url: str | None
    public_token: str
    items: list[RepairItemOut]
    payments: list[RepairPaymentOut]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RepairPublicStatusOut(BaseModel):
    """Lo que ve el cliente al consultar el estado de su equipo por el link publico."""

    ticket: str
    equipo_tipo: str
    marca: str
    modelo: str
    falla_reportada: str
    status: str
    status_history: list
    presupuesto_gs: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
