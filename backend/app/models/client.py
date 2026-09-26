from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    ruc_ci = Column(String, index=True, nullable=True)
    phone = Column(String, index=True, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    tipo = Column(String, default="minorista", nullable=False)  # minorista, mayorista, cuenta_corriente
    credit_balance = Column(Float, default=0.0, nullable=False)  # saldo fiado / cuenta corriente
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    sales = relationship("Sale", back_populates="client")
    payments = relationship("Payment", back_populates="client")
    repair_orders = relationship("RepairOrder", back_populates="client")
