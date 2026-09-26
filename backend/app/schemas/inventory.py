from datetime import datetime

from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None


class SupplierOut(BaseModel):
    id: int
    name: str
    contact_person: str | None
    phone: str | None
    email: str | None
    address: str | None

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    sku: str
    barcode: str | None = None
    name: str
    category: str
    brand: str | None = None
    unit: str = "unidad"
    purchase_price_gs: float = Field(ge=0.0, default=0.0)
    selling_price_gs: float = Field(ge=0.0, default=0.0)
    iva_rate: float = 10.0
    stock_qty: float = Field(ge=0.0, default=0.0)
    low_stock_threshold: float = Field(ge=0.0, default=3.0)
    supplier_id: int | None = None


class ProductUpdate(BaseModel):
    barcode: str | None = None
    name: str | None = None
    category: str | None = None
    brand: str | None = None
    unit: str | None = None
    purchase_price_gs: float | None = None
    selling_price_gs: float | None = None
    iva_rate: float | None = None
    low_stock_threshold: float | None = None
    supplier_id: int | None = None


class ProductOut(BaseModel):
    id: int
    sku: str
    barcode: str | None
    name: str
    category: str
    brand: str | None
    unit: str
    purchase_price_gs: float
    selling_price_gs: float
    iva_rate: float
    stock_qty: float
    low_stock_threshold: float
    supplier_id: int | None

    class Config:
        from_attributes = True


class StockAdjustmentCreate(BaseModel):
    product_id: int
    qty_change: float
    reason: str


class StockAdjustmentOut(BaseModel):
    id: int
    product_id: int
    qty_change: float
    reason: str
    date: datetime

    class Config:
        from_attributes = True


class PurchaseItemCreate(BaseModel):
    product_id: int
    qty: float = Field(gt=0.0)
    cost_price_gs: float = Field(ge=0.0)


class PurchaseCreate(BaseModel):
    supplier_id: int
    invoice_number: str | None = None
    notes: str | None = None
    items: list[PurchaseItemCreate]


class PurchaseItemOut(BaseModel):
    id: int
    product_id: int
    qty: float
    cost_price_gs: float
    total_gs: float

    class Config:
        from_attributes = True


class PurchaseOut(BaseModel):
    id: int
    supplier_id: int
    invoice_number: str | None
    date: datetime
    total_amount_gs: float
    notes: str | None
    items: list[PurchaseItemOut]

    class Config:
        from_attributes = True
