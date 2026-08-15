from datetime import date
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.jwt import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Mesa, Reserva, Usuario
from app.schemas.reserva import ReservaCreate, ReservaEstadoUpdate, ReservaUpdate
from app.utils.reservations import BLOCKING_RESERVATION_STATES, RESERVATION_TRANSITIONS, reservations_overlap
from app.utils.serializers import reserva_json

router = APIRouter(prefix="/api/reservas", tags=["Reservas"])


def today(): return date.today() if not settings.app_timezone else __import__("datetime").datetime.now(ZoneInfo(settings.app_timezone)).date()


def owned(db, user_id, reservation_id):
    item = db.scalar(select(Reserva).where(Reserva.id == reservation_id, Reserva.user_id == user_id))
    if not item: raise HTTPException(404, "Reserva no encontrada.")
    return item


def validate_and_find_table(db, user_id, data, excluded=None):
    mesa = db.scalar(select(Mesa).where(Mesa.id == data.mesa_id, Mesa.user_id == user_id))
    if not mesa: raise HTTPException(404, "Mesa no encontrada.")
    if data.fecha < today(): raise HTTPException(400, "La fecha de reserva no puede estar en el pasado.")
    if data.cantidad_personas > mesa.capacidad: raise HTTPException(400, "La cantidad de personas supera la capacidad de la mesa.")
    query = select(Reserva).where(Reserva.user_id == user_id, Reserva.mesa_id == mesa.id,
                                  Reserva.estado.in_(BLOCKING_RESERVATION_STATES))
    if excluded: query = query.where(Reserva.id != excluded)
    for existing in db.scalars(query).all():
        if reservations_overlap(existing.fecha, existing.hora, data.fecha, data.hora):
            raise HTTPException(409, "La mesa seleccionada ya tiene una reserva que se superpone con ese horario.")
    return mesa


@router.get("")
def list_reservations(fecha: date | None = None, desde: date | None = None, hasta: date | None = None,
                      estado: str | None = None, mesaId: int | None = None, texto: str | None = None,
                      db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    query = select(Reserva).where(Reserva.user_id == user.id)
    if fecha: query = query.where(Reserva.fecha == fecha)
    if desde: query = query.where(Reserva.fecha >= desde)
    if hasta: query = query.where(Reserva.fecha <= hasta)
    if estado:
        if estado not in RESERVATION_TRANSITIONS: raise HTTPException(400, "Estado de reserva inválido.")
        query = query.where(Reserva.estado == estado)
    if mesaId is not None: query = query.where(Reserva.mesa_id == mesaId)
    if texto: query = query.where(Reserva.nombre_cliente.ilike(f"%{texto}%"))
    return [reserva_json(x) for x in db.scalars(query.order_by(Reserva.fecha, Reserva.hora)).all()]


@router.get("/{reservation_id}")
def get_reservation(reservation_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return reserva_json(owned(db, user.id, reservation_id))


@router.post("", status_code=201)
def create_reservation(data: ReservaCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    validate_and_find_table(db, user.id, data)
    item = Reserva(user_id=user.id, estado="pendiente", **data.model_dump())
    db.add(item); db.commit(); db.refresh(item); return reserva_json(item)


@router.put("/{reservation_id}")
def update_reservation(reservation_id: int, data: ReservaUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    item = owned(db, user.id, reservation_id)
    if item.estado in ("cancelada", "completada"): raise HTTPException(409, "Una reserva finalizada no puede editarse.")
    validate_and_find_table(db, user.id, data, item.id)
    for key, value in data.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return reserva_json(item)


@router.patch("/{reservation_id}/estado")
def update_state(reservation_id: int, data: ReservaEstadoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    item = owned(db, user.id, reservation_id)
    if data.estado not in RESERVATION_TRANSITIONS.get(item.estado, set()):
        raise HTTPException(400, f"Transición inválida de {item.estado} a {data.estado}.")
    item.estado = data.estado; db.commit(); db.refresh(item); return reserva_json(item)


@router.delete("/{reservation_id}", status_code=204)
def delete_reservation(reservation_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    item = owned(db, user.id, reservation_id)
    if item.estado not in ("pendiente", "cancelada"): raise HTTPException(409, "Esta reserva debe conservarse como historial.")
    db.delete(item); db.commit(); return Response(status_code=204)

