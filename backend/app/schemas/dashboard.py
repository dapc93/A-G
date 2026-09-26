from pydantic import BaseModel


class DashboardOut(BaseModel):
    ventas_mes_gs: float
    cantidad_ventas_mes: int
    reparaciones_abiertas: int
    reparaciones_listas_para_entregar: int
    productos_stock_bajo: int
    total_por_cobrar_gs: float
