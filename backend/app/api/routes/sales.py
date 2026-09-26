from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.client import Client
from app.models.payment import Payment
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.schemas.sale import PaymentCreate, PaymentOut, SaleCreate, SaleOut

router = APIRouter(prefix="/api/sales", tags=["sales"], dependencies=[Depends(get_current_user)])


def _next_invoice_no(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.query(Sale).filter(Sale.invoice_no.like(f"V-{year}-%")).count()
    return f"V-{year}-{count + 1:05d}"


@router.get("", response_model=list[SaleOut])
def list_sales(client_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Sale)
    if client_id:
        query = query.filter(Sale.client_id == client_id)
    return query.order_by(Sale.date.desc()).all()


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(payload: SaleCreate, db: Session = Depends(get_db)):
    client = None
    if payload.client_id:
        client = db.get(Client, payload.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if payload.payment_type == "cuenta_corriente" and not client:
        raise HTTPException(status_code=400, detail="La venta a cuenta corriente requiere un cliente")

    sale = Sale(
        invoice_no=_next_invoice_no(db),
        client_id=payload.client_id,
        payment_type=payload.payment_type,
        discount_gs=payload.discount_gs,
        date=datetime.now(timezone.utc),
    )

    subtotal = 0.0
    iva_total = 0.0
    for item in payload.items:
        product = db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")
        if product.stock_qty < item.qty:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")

        unit_price = item.unit_price_gs if item.unit_price_gs is not None else product.selling_price_gs
        line_base = unit_price * item.qty - item.discount_gs
        iva_amount = line_base * (product.iva_rate / (100 + product.iva_rate))
        line_total = line_base

        subtotal += line_base - iva_amount
        iva_total += iva_amount

        sale.items.append(
            SaleItem(
                product_id=product.id,
                qty=item.qty,
                unit_price_gs=unit_price,
                iva_rate=product.iva_rate,
                iva_amount_gs=iva_amount,
                discount_gs=item.discount_gs,
                total_gs=line_total,
            )
        )
        product.stock_qty -= item.qty

    sale.subtotal_gs = subtotal
    sale.iva_amount_gs = iva_total
    sale.total_gs = subtotal + iva_total
    sale.amount_paid_gs = payload.amount_paid_gs

    if payload.payment_type == "cuenta_corriente":
        pendiente = sale.total_gs - payload.amount_paid_gs
        sale.payment_status = "pagado" if pendiente <= 0 else ("parcial" if payload.amount_paid_gs > 0 else "pendiente")
        if pendiente > 0:
            client.credit_balance += pendiente
    else:
        sale.payment_status = "pagado" if payload.amount_paid_gs >= sale.total_gs else "parcial"

    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return sale


@router.post("/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def register_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    client = db.get(Client, payload.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    payment = Payment(**payload.model_dump())
    client.credit_balance -= payload.amount_gs

    if payload.linked_sale_id:
        sale = db.get(Sale, payload.linked_sale_id)
        if sale:
            sale.amount_paid_gs += payload.amount_gs
            sale.payment_status = "pagado" if sale.amount_paid_gs >= sale.total_gs else "parcial"

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
