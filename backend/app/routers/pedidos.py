from datetime import date, datetime, time, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.jwt import get_current_user
from app.database import get_db
from app.models import DetallePedido, Mesa, Pedido, Producto, Usuario
from app.schemas.pedido import ItemCreate, ItemUpdate, PedidoCreate, PedidoEstadoUpdate
from app.utils.orders import ACTIVE_ORDER_STATES, ORDER_TRANSITIONS, recalculate_order
from app.utils.serializers import pedido_json

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos"])


def owned(db, user_id, order_id):
    order = db.scalar(select(Pedido).where(Pedido.id == order_id, Pedido.user_id == user_id))
    if not order: raise HTTPException(404, "Pedido no encontrado.")
    return order


def editable(order):
    if order.estado not in ACTIVE_ORDER_STATES:
        raise HTTPException(409, "Un pedido cerrado o cancelado no puede modificarse.")


@router.get("")
def list_orders(estado: str | None = None, mesaId: int | None = None, desde: date | None = None, hasta: date | None = None,
                db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    query = select(Pedido).where(Pedido.user_id == user.id)
    if estado:
        if estado not in ORDER_TRANSITIONS: raise HTTPException(400, "Estado de pedido inválido.")
        query = query.where(Pedido.estado == estado)
    if mesaId is not None: query = query.where(Pedido.mesa_id == mesaId)
    if desde: query = query.where(Pedido.created_at >= datetime.combine(desde, time.min))
    if hasta: query = query.where(Pedido.created_at <= datetime.combine(hasta, time.max))
    return [pedido_json(x) for x in db.scalars(query.order_by(Pedido.created_at.desc())).unique().all()]


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return pedido_json(owned(db, user.id, order_id))


@router.post("", status_code=201)
def create_order(data: PedidoCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    mesa = db.scalar(select(Mesa).where(Mesa.id == data.mesa_id, Mesa.user_id == user.id))
    if not mesa: raise HTTPException(404, "Mesa no encontrada.")
    active = db.scalar(select(Pedido.id).where(Pedido.mesa_id == mesa.id, Pedido.estado.in_(ACTIVE_ORDER_STATES)))
    if active: raise HTTPException(409, "La mesa ya tiene un pedido activo.")
    order = Pedido(mesa_id=mesa.id, user_id=user.id, estado="abierto", total=Decimal("0.00"))
    mesa.estado = "ocupada"; db.add(order); db.commit(); db.refresh(order)
    return pedido_json(order)


@router.post("/{order_id}/items", status_code=201)
def add_item(order_id: int, data: ItemCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    order = owned(db, user.id, order_id); editable(order)
    product = db.scalar(select(Producto).where(Producto.id == data.producto_id, Producto.user_id == user.id))
    if not product: raise HTTPException(404, "Producto no encontrado.")
    if not product.disponible: raise HTTPException(409, "El producto no está disponible.")
    item = db.scalar(select(DetallePedido).where(DetallePedido.pedido_id == order.id, DetallePedido.producto_id == product.id))
    if item:
        if item.cantidad + data.cantidad > 99: raise HTTPException(400, "La cantidad total no puede superar 99.")
        item.cantidad += data.cantidad
        item.subtotal = item.precio_unitario * item.cantidad
    else:
        item = DetallePedido(pedido_id=order.id, producto_id=product.id, cantidad=data.cantidad,
                             precio_unitario=product.precio, subtotal=product.precio * data.cantidad)
        db.add(item); db.flush()
    recalculate_order(order); db.commit(); db.refresh(order)
    return pedido_json(order)


@router.put("/{order_id}/items/{item_id}")
def update_item(order_id: int, item_id: int, data: ItemUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    order = owned(db, user.id, order_id); editable(order)
    item = db.scalar(select(DetallePedido).where(DetallePedido.id == item_id, DetallePedido.pedido_id == order.id))
    if not item: raise HTTPException(404, "Item no encontrado.")
    item.cantidad = data.cantidad; item.subtotal = item.precio_unitario * item.cantidad
    recalculate_order(order); db.commit(); db.refresh(order); return pedido_json(order)


@router.delete("/{order_id}/items/{item_id}", status_code=200)
def delete_item(order_id: int, item_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    order = owned(db, user.id, order_id); editable(order)
    item = db.scalar(select(DetallePedido).where(DetallePedido.id == item_id, DetallePedido.pedido_id == order.id))
    if not item: raise HTTPException(404, "Item no encontrado.")
    db.delete(item); db.flush(); recalculate_order(order); db.commit(); db.refresh(order)
    return pedido_json(order)


@router.patch("/{order_id}/estado")
def update_state(order_id: int, data: PedidoEstadoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    order = owned(db, user.id, order_id)
    if data.estado not in ORDER_TRANSITIONS.get(order.estado, set()):
        raise HTTPException(400, f"Transición inválida de {order.estado} a {data.estado}.")
    if data.estado == "cerrado" and not order.items:
        raise HTTPException(409, "No se puede cerrar un pedido sin items.")
    order.estado = data.estado
    if data.estado == "cerrado": order.closed_at = datetime.now(timezone.utc)
    if data.estado in ("cerrado", "cancelado"): order.mesa.estado = "disponible"
    db.commit(); db.refresh(order); return pedido_json(order)


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    order = owned(db, user.id, order_id)
    if order.estado != "abierto" or order.items:
        raise HTTPException(409, "Solo puede eliminarse un pedido abierto sin items.")
    order.mesa.estado = "disponible"; db.delete(order); db.commit(); return Response(status_code=204)

