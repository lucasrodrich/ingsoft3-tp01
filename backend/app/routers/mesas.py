from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.auth.jwt import get_current_user
from app.database import get_db
from app.models import Mesa, Pedido, Reserva, Usuario
from app.schemas.mesa import MesaCreate, MesaEstadoUpdate, MesaUpdate
from app.utils.orders import ACTIVE_ORDER_STATES
from app.utils.serializers import mesa_json

router = APIRouter(prefix="/api/mesas", tags=["Mesas"])


def owned(db, user_id, mesa_id):
    mesa = db.scalar(select(Mesa).where(Mesa.id == mesa_id, Mesa.user_id == user_id))
    if not mesa:
        raise HTTPException(404, "Mesa no encontrada.")
    return mesa


@router.get("")
def list_mesas(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return [mesa_json(x) for x in db.scalars(select(Mesa).where(Mesa.user_id == user.id).order_by(Mesa.numero)).all()]


@router.get("/{mesa_id}")
def get_mesa(mesa_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return mesa_json(owned(db, user.id, mesa_id))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_mesa(data: MesaCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    if db.scalar(select(Mesa).where(Mesa.user_id == user.id, Mesa.numero == data.numero)):
        raise HTTPException(409, "Ya existe una mesa con ese número.")
    mesa = Mesa(numero=data.numero, capacidad=data.capacidad, user_id=user.id)
    db.add(mesa)
    try:
        db.commit(); db.refresh(mesa)
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "Ya existe una mesa con ese número.")
    return mesa_json(mesa)


@router.put("/{mesa_id}")
def update_mesa(mesa_id: int, data: MesaUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    mesa = owned(db, user.id, mesa_id)
    duplicate = db.scalar(select(Mesa).where(Mesa.user_id == user.id, Mesa.numero == data.numero, Mesa.id != mesa.id))
    if duplicate:
        raise HTTPException(409, "Ya existe una mesa con ese número.")
    mesa.numero, mesa.capacidad, mesa.estado = data.numero, data.capacidad, data.estado
    db.commit(); db.refresh(mesa)
    return mesa_json(mesa)


@router.patch("/{mesa_id}/estado")
def update_estado(mesa_id: int, data: MesaEstadoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    mesa = owned(db, user.id, mesa_id)
    mesa.estado = data.estado; db.commit(); db.refresh(mesa)
    return mesa_json(mesa)


@router.delete("/{mesa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mesa(mesa_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    mesa = owned(db, user.id, mesa_id)
    active = db.scalar(select(Pedido.id).where(Pedido.mesa_id == mesa.id, Pedido.estado.in_(ACTIVE_ORDER_STATES)))
    future = db.scalar(select(Reserva.id).where(Reserva.mesa_id == mesa.id, Reserva.fecha >= date.today(), Reserva.estado.in_(("pendiente", "confirmada"))))
    if active or future:
        raise HTTPException(409, "No se puede eliminar la mesa porque tiene actividad pendiente.")
    if db.scalar(select(Pedido.id).where(Pedido.mesa_id == mesa.id)) or db.scalar(select(Reserva.id).where(Reserva.mesa_id == mesa.id)):
        raise HTTPException(409, "No se puede eliminar la mesa porque tiene historial asociado.")
    db.delete(mesa); db.commit()
    return Response(status_code=204)
