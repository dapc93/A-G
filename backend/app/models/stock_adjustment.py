from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty_change = Column(Float, nullable=False)  # positivo = alta, negativo = baja
    reason = Column(String, nullable=False)  # Rotura, Devolucion, Correccion, Garantia, Uso interno
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="stock_adjustments")
    user = relationship("User")
