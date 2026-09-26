from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    linked_sale_id = Column(Integer, ForeignKey("sales.id"), nullable=True)
    amount_gs = Column(Float, nullable=False)
    mode = Column(String, nullable=False, default="efectivo")  # efectivo, transferencia, tarjeta, giro
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    reference_no = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    client = relationship("Client", back_populates="payments")
    linked_sale = relationship("Sale", back_populates="payments")
