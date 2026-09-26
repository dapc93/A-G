from datetime import datetime

from pydantic import BaseModel, Field


class SaleItemCreate(BaseModel):
    product_id: int
    qty: float = Field(gt=0.0)
    unit_price_gs: float | None = None  # si es None, se usa el precio de lista del producto
    discount_gs: float = Field(default=0.0, ge=0.0)


class SaleCreate(BaseModel):
    client_id: int | None = None  # None = consumidor final
    payment_type: str = "contado"
    amount_paid_gs: float = Field(default=0.0, ge=0.0)
    discount_gs: float = Field(default=0.0, ge=0.0)
    items: list[SaleItemCreate]


class SaleItemOut(BaseModel):
    id: int
    product_id: int
    qty: float
    unit_price_gs: float
    iva_rate: float
    iva_amount_gs: float
    discount_gs: float
    total_gs: float

    class Config:
        from_attributes = True


class SaleOut(BaseModel):
    id: int
    invoice_no: str
    client_id: int | None
    date: datetime
    subtotal_gs: float
    iva_amount_gs: float
    discount_gs: float
    total_gs: float
    payment_type: str
    amount_paid_gs: float
    payment_status: str
    items: list[SaleItemOut]

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    client_id: int
    linked_sale_id: int | None = None
    amount_gs: float = Field(gt=0.0)
    mode: str = "efectivo"
    reference_no: str | None = None
    notes: str | None = None


class PaymentOut(BaseModel):
    id: int
    client_id: int
    linked_sale_id: int | None
    amount_gs: float
    mode: str
    date: datetime
    reference_no: str | None
    notes: str | None

    class Config:
        from_attributes = True
