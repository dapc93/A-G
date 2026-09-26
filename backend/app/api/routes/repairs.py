from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.client import Client
from app.models.product import Product
from app.models.repair import ESTADOS_REPARACION, RepairItem, RepairOrder, RepairPayment
from app.models.user import User
from app.schemas.repair import (
    RepairItemCreate,
    RepairItemOut,
    RepairOrderCreate,
    RepairOrderOut,
    RepairOrderUpdate,
    RepairPaymentCreate,
    RepairPaymentOut,
    RepairPublicStatusOut,
    RepairStatusUpdate,
)

router = APIRouter(prefix="/api/repairs", tags=["repairs"])
public_router = APIRouter(prefix="/api/public/repairs", tags=["repairs-public"])


def _next_ticket(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.query(RepairOrder).filter(RepairOrder.ticket.like(f"R-{year}-%")).count()
    return f"R-{year}-{count + 1:05d}"


def _recalc_totals(repair: RepairOrder) -> None:
    items_total = sum(i.qty * i.price_gs for i in repair.items)
    items_cost = sum(i.qty * i.cost_gs for i in repair.items)
    repair.costo_gs = items_cost
    repair.total_gs = max(items_total - repair.descuento_gs, 0.0)
    paid = sum(p.amount_gs for p in repair.payments) + repair.sena_gs
    if paid <= 0:
        repair.payment_status = "pendiente"
    elif paid < repair.total_gs:
        repair.payment_status = "parcial"
    else:
        repair.payment_status = "pagado"


@router.get("", response_model=list[RepairOrderOut], dependencies=[Depends(get_current_user)])
def list_repairs(status_filter: str | None = None, client_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(RepairOrder)
    if status_filter:
        query = query.filter(RepairOrder.status == status_filter)
    if client_id:
        query = query.filter(RepairOrder.client_id == client_id)
    return query.order_by(RepairOrder.created_at.desc()).all()


@router.post("", response_model=RepairOrderOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def create_repair(payload: RepairOrderCreate, db: Session = Depends(get_db)):
    client = db.get(Client, payload.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    repair = RepairOrder(
        ticket=_next_ticket(db),
        status="recibido",
        status_history=[{"status": "recibido", "at": datetime.now(timezone.utc).isoformat()}],
        **payload.model_dump(),
    )
    db.add(repair)
    db.commit()
    db.refresh(repair)
    return repair


@router.get("/{repair_id}", response_model=RepairOrderOut, dependencies=[Depends(get_current_user)])
def get_repair(repair_id: int, db: Session = Depends(get_db)):
    repair = db.get(RepairOrder, repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Orden de reparacion no encontrada")
    return repair


@router.put("/{repair_id}", response_model=RepairOrderOut, dependencies=[Depends(get_current_user)])
def update_repair(repair_id: int, payload: RepairOrderUpdate, db: Session = Depends(get_db)):
    repair = db.get(RepairOrder, repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Orden de reparacion no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(repair, field, value)
    _recalc_totals(repair)
    db.commit()
    db.refresh(repair)
    return repair


@router.patch("/{repair_id}/status", response_model=RepairOrderOut, dependencies=[Depends(get_current_user)])
def update_repair_status(repair_id: int, payload: RepairStatusUpdate, db: Session = Depends(get_db)):
    repair = db.get(RepairOrder, repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Orden de reparacion no encontrada")
    if payload.status not in ESTADOS_REPARACION:
        raise HTTPException(status_code=400, detail="Estado invalido")

    repair.status = payload.status
    history = list(repair.status_history or [])
    history.append({"status": payload.status, "at": datetime.now(timezone.utc).isoformat()})
    repair.status_history = history
    db.commit()
    db.refresh(repair)
    return repair


@router.post("/{repair_id}/items", response_model=RepairItemOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def add_repair_item(repair_id: int, payload: RepairItemCreate, db: Session = Depends(get_db)):
    repair = db.get(RepairOrder, repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Orden de reparacion no encontrada")

    if payload.product_id:
        product = db.get(Product, payload.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        if product.stock_qty < payload.qty:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")
        product.stock_qty -= payload.qty

    item = RepairItem(repair_order_id=repair_id, **payload.model_dump())
    db.add(item)
    db.flush()
    repair.items.append(item)
    _recalc_totals(repair)
    db.commit()
    db.refresh(item)
    return item


@router.post("/{repair_id}/payments", response_model=RepairPaymentOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def add_repair_payment(repair_id: int, payload: RepairPaymentCreate, db: Session = Depends(get_db)):
    repair = db.get(RepairOrder, repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Orden de reparacion no encontrada")

    payment = RepairPayment(repair_order_id=repair_id, **payload.model_dump())
    db.add(payment)
    db.flush()
    repair.payments.append(payment)
    _recalc_totals(repair)
    db.commit()
    db.refresh(payment)
    return payment


@public_router.get("/status/{public_token}", response_model=RepairPublicStatusOut)
def public_repair_status(public_token: str, db: Session = Depends(get_db)):
    repair = db.query(RepairOrder).filter(RepairOrder.public_token == public_token).first()
    if not repair:
        raise HTTPException(status_code=404, detail="No encontrado")
    return repair
