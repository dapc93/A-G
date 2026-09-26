from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.client import Client
from app.models.product import Product
from app.models.repair import RepairOrder
from app.models.sale import Sale
from app.schemas.dashboard import DashboardOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    ventas_mes = db.query(Sale).filter(Sale.date >= month_start).all()
    ventas_mes_gs = sum(v.total_gs for v in ventas_mes)

    reparaciones_abiertas = (
        db.query(func.count(RepairOrder.id))
        .filter(RepairOrder.status.notin_(["entregado", "cancelado"]))
        .scalar()
    )
    reparaciones_listas = (
        db.query(func.count(RepairOrder.id)).filter(RepairOrder.status == "listo").scalar()
    )
    productos_stock_bajo = (
        db.query(func.count(Product.id)).filter(Product.stock_qty <= Product.low_stock_threshold).scalar()
    )
    total_por_cobrar = db.query(func.coalesce(func.sum(Client.credit_balance), 0.0)).scalar()

    return DashboardOut(
        ventas_mes_gs=ventas_mes_gs,
        cantidad_ventas_mes=len(ventas_mes),
        reparaciones_abiertas=reparaciones_abiertas or 0,
        reparaciones_listas_para_entregar=reparaciones_listas or 0,
        productos_stock_bajo=productos_stock_bajo or 0,
        total_por_cobrar_gs=float(total_por_cobrar or 0.0),
    )
