from datetime import datetime, time, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.auth.jwt import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Mesa, Pedido, Reserva, Usuario
from app.utils.orders import ACTIVE_ORDER_STATES

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    tz = ZoneInfo(settings.app_timezone)
    local_today = datetime.now(tz).date()
    start = datetime.combine(local_today, time.min, tzinfo=tz).astimezone(timezone.utc)
    end = datetime.combine(local_today, time.max, tzinfo=tz).astimezone(timezone.utc)
    count_table = lambda state: db.scalar(select(func.count(Mesa.id)).where(Mesa.user_id == user.id, Mesa.estado == state)) or 0
    open_orders = db.scalar(select(func.count(Pedido.id)).where(Pedido.user_id == user.id, Pedido.estado.in_(ACTIVE_ORDER_STATES))) or 0
    reservations = db.scalar(select(func.count(Reserva.id)).where(Reserva.user_id == user.id, Reserva.fecha == local_today,
                                                                  Reserva.estado.in_(("pendiente", "confirmada")))) or 0
    sales = db.scalar(select(func.sum(Pedido.total)).where(Pedido.user_id == user.id, Pedido.estado == "cerrado",
                                                           Pedido.closed_at >= start, Pedido.closed_at <= end)) or Decimal("0.00")
    today_orders = db.scalar(select(func.count(Pedido.id)).where(Pedido.user_id == user.id, Pedido.estado != "cancelado",
                                                                 Pedido.created_at >= start, Pedido.created_at <= end)) or 0
    return {"mesasDisponibles": count_table("disponible"), "mesasOcupadas": count_table("ocupada"),
            "mesasReservadas": count_table("reservada"), "pedidosAbiertos": open_orders,
            "reservasHoy": reservations, "ventasHoy": float(sales), "pedidosHoy": today_orders}

