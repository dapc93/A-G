from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String, unique=True, index=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    subtotal_gs = Column(Float, nullable=False, default=0.0)
    iva_amount_gs = Column(Float, nullable=False, default=0.0)
    discount_gs = Column(Float, nullable=False, default=0.0)
    total_gs = Column(Float, nullable=False, default=0.0)
    payment_type = Column(String, nullable=False, default="contado")  # contado, cuenta_corriente, tarjeta, transferencia
    amount_paid_gs = Column(Float, nullable=False, default=0.0)
    payment_status = Column(String, nullable=False, default="pagado")  # pagado, parcial, pendiente
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    client = relationship("Client", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="linked_sale")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty = Column(Float, nullable=False)
    unit_price_gs = Column(Float, nullable=False)
    iva_rate = Column(Float, nullable=False, default=10.0)
    iva_amount_gs = Column(Float, nullable=False, default=0.0)
    discount_gs = Column(Float, nullable=False, default=0.0)
    total_gs = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
