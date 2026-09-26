from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.product import Product
from app.models.purchase import Purchase, PurchaseItem
from app.models.stock_adjustment import StockAdjustment
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.inventory import (
    ProductCreate,
    ProductOut,
    ProductUpdate,
    PurchaseCreate,
    PurchaseOut,
    StockAdjustmentCreate,
    StockAdjustmentOut,
    SupplierCreate,
    SupplierOut,
)

router = APIRouter(prefix="/api/inventory", tags=["inventory"], dependencies=[Depends(get_current_user)])


# ---- Proveedores ----
@router.get("/suppliers", response_model=list[SupplierOut])
def list_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).order_by(Supplier.name).all()


@router.post("/suppliers", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


# ---- Productos ----
@router.get("/products", response_model=list[ProductOut])
def list_products(q: str | None = None, low_stock: bool = False, db: Session = Depends(get_db)):
    query = db.query(Product)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Product.name.ilike(like), Product.sku.ilike(like), Product.barcode.ilike(like)))
    if low_stock:
        query = query.filter(Product.stock_qty <= Product.low_stock_threshold)
    return query.order_by(Product.name).all()


@router.get("/products/available", response_model=list[ProductOut])
def list_available_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.stock_qty > 0).order_by(Product.name).all()


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(status_code=409, detail="SKU ya existe")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(product)
    db.commit()


# ---- Ajustes de stock ----
@router.post("/stock-adjustments", response_model=StockAdjustmentOut, status_code=status.HTTP_201_CREATED)
def create_stock_adjustment(
    payload: StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    new_qty = product.stock_qty + payload.qty_change
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="El ajuste dejaria el stock en negativo")
    product.stock_qty = new_qty
    adjustment = StockAdjustment(
        product_id=payload.product_id,
        qty_change=payload.qty_change,
        reason=payload.reason,
        created_by_user_id=current_user.id,
    )
    db.add(adjustment)
    db.commit()
    db.refresh(adjustment)
    return adjustment


# ---- Compras a proveedores ----
@router.get("/purchases", response_model=list[PurchaseOut])
def list_purchases(db: Session = Depends(get_db)):
    return db.query(Purchase).order_by(Purchase.date.desc()).all()


@router.post("/purchases", response_model=PurchaseOut, status_code=status.HTTP_201_CREATED)
def create_purchase(payload: PurchaseCreate, db: Session = Depends(get_db)):
    supplier = db.get(Supplier, payload.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    purchase = Purchase(
        supplier_id=payload.supplier_id,
        invoice_number=payload.invoice_number,
        notes=payload.notes,
        date=datetime.now(timezone.utc),
    )
    total = 0.0
    for item in payload.items:
        product = db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")
        item_total = item.qty * item.cost_price_gs
        total += item_total
        purchase.items.append(
            PurchaseItem(
                product_id=item.product_id,
                qty=item.qty,
                cost_price_gs=item.cost_price_gs,
                total_gs=item_total,
            )
        )
        product.stock_qty += item.qty
        product.purchase_price_gs = item.cost_price_gs

    purchase.total_amount_gs = total
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase
