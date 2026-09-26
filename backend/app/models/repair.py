import secrets
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base

# recibido -> diagnosticado -> reparando -> esperando_repuesto -> listo -> entregado
#                                                                       -> cancelado
ESTADOS_REPARACION = [
    "recibido",
    "diagnosticado",
    "reparando",
    "esperando_repuesto",
    "listo",
    "entregado",
    "cancelado",
]


def _gen_public_token() -> str:
    return secrets.token_urlsafe(12)


class RepairOrder(Base):
    __tablename__ = "repair_orders"

    id = Column(Integer, primary_key=True, index=True)
    ticket = Column(String, unique=True, index=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    equipo_tipo = Column(String, nullable=False, default="")  # Notebook, PC, Celular, Impresora, Otro
    marca = Column(String, nullable=False, default="")
    modelo = Column(String, nullable=False, default="")
    numero_serie = Column(String, nullable=True)  # IMEI / N. serie

    falla_reportada = Column(Text, nullable=False, default="")
    nota_interna = Column(Text, nullable=True)
    password_equipo = Column(String, nullable=True)  # clave/patron para poder revisar el equipo

    status = Column(String, default="recibido", nullable=False)
    status_history = Column(JSON, default=list)  # [{status, at, by}]

    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    presupuesto_gs = Column(Float, default=0.0, nullable=False)
    sena_gs = Column(Float, default=0.0, nullable=False)  # deposito
    descuento_gs = Column(Float, default=0.0, nullable=False)
    costo_gs = Column(Float, default=0.0, nullable=False)  # costo interno de repuestos/mano de obra
    total_gs = Column(Float, default=0.0, nullable=False)
    payment_status = Column(String, default="pendiente", nullable=False)  # pendiente, parcial, pagado

    foto_ingreso_url = Column(Text, nullable=True)
    foto_egreso_url = Column(Text, nullable=True)

    public_token = Column(String, unique=True, default=_gen_public_token, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    client = relationship("Client", back_populates="repair_orders")
    technician = relationship("User")
    items = relationship("RepairItem", back_populates="repair_order", cascade="all, delete-orphan")
    payments = relationship("RepairPayment", back_populates="repair_order", cascade="all, delete-orphan")


class RepairItem(Base):
    __tablename__ = "repair_items"

    id = Column(Integer, primary_key=True, index=True)
    repair_order_id = Column(Integer, ForeignKey("repair_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # si es un repuesto de inventario
    name = Column(String, nullable=False)  # repuesto o mano de obra
    qty = Column(Float, default=1.0, nullable=False)
    price_gs = Column(Float, default=0.0, nullable=False)
    cost_gs = Column(Float, default=0.0, nullable=False)

    repair_order = relationship("RepairOrder", back_populates="items")
    product = relationship("Product", back_populates="repair_items")


class RepairPayment(Base):
    __tablename__ = "repair_payments"

    id = Column(Integer, primary_key=True, index=True)
    repair_order_id = Column(Integer, ForeignKey("repair_orders.id"), nullable=False)
    amount_gs = Column(Float, default=0.0, nullable=False)
    mode = Column(String, default="efectivo", nullable=False)
    note = Column(String, nullable=True)
    paid_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    repair_order = relationship("RepairOrder", back_populates="payments")
