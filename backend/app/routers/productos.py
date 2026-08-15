from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.auth.jwt import get_current_user
from app.database import get_db
from app.models import CategoriaMenu, DetallePedido, Producto, Usuario
from app.schemas.producto import DisponibilidadUpdate, ProductoCreate, ProductoUpdate
from app.utils.serializers import producto_json

router = APIRouter(prefix="/api/productos", tags=["Productos"])


def owned(db, user_id, product_id):
    item = db.scalar(select(Producto).where(Producto.id == product_id, Producto.user_id == user_id))
    if not item: raise HTTPException(404, "Producto no encontrado.")
    return item


def owned_category(db, user_id, category_id):
    item = db.scalar(select(CategoriaMenu).where(CategoriaMenu.id == category_id, CategoriaMenu.user_id == user_id))
    if not item: raise HTTPException(404, "Categoría no encontrada.")
    return item


@router.get("")
def list_products(categoriaId: int | None = None, disponible: bool | None = None, texto: str | None = None,
                  db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    query = select(Producto).where(Producto.user_id == user.id)
    if categoriaId is not None: query = query.where(Producto.categoria_id == categoriaId)
    if disponible is not None: query = query.where(Producto.disponible == disponible)
    if texto: query = query.where(or_(Producto.nombre.ilike(f"%{texto}%"), Producto.descripcion.ilike(f"%{texto}%")))
    return [producto_json(x) for x in db.scalars(query.order_by(Producto.nombre)).all()]


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return producto_json(owned(db, user.id, product_id))


@router.post("", status_code=201)
def create_product(data: ProductoCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    owned_category(db, user.id, data.categoria_id)
    item = Producto(user_id=user.id, **data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return producto_json(item)


@router.put("/{product_id}")
def update_product(product_id: int, data: ProductoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    item = owned(db, user.id, product_id); owned_category(db, user.id, data.categoria_id)
    for key, value in data.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return producto_json(item)


@router.patch("/{product_id}/disponibilidad")
def availability(product_id: int, data: DisponibilidadUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    item = owned(db, user.id, product_id); item.disponible = data.disponible
    db.commit(); db.refresh(item); return producto_json(item)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    item = owned(db, user.id, product_id)
    if db.scalar(select(DetallePedido.id).where(DetallePedido.producto_id == item.id)):
        raise HTTPException(409, "El producto tiene historial; márquelo como no disponible.")
    db.delete(item); db.commit(); return Response(status_code=204)

