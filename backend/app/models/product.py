from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    barcode = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)  # Notebooks, PC Armadas, Componentes, Perifericos, Celulares, Accesorios, Repuestos, Otros
    brand = Column(String, nullable=True)
    unit = Column(String, nullable=False, default="unidad")
    purchase_price_gs = Column(Float, nullable=False, default=0.0)
    selling_price_gs = Column(Float, nullable=False, default=0.0)
    iva_rate = Column(Float, nullable=False, default=10.0)  # 0, 5, 10 (Paraguay)
    stock_qty = Column(Float, nullable=False, default=0.0)
    low_stock_threshold = Column(Float, nullable=False, default=3.0)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    supplier = relationship("Supplier", back_populates="products")
    purchase_items = relationship("PurchaseItem", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")
    stock_adjustments = relationship("StockAdjustment", back_populates="product")
    repair_items = relationship("RepairItem", back_populates="product")
