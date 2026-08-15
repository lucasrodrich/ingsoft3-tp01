from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.auth.jwt import get_current_user
from app.database import get_db
from app.models import CategoriaMenu, Producto, Usuario
from app.schemas.categoria import CategoriaCreate
from app.utils.serializers import categoria_json

router = APIRouter(prefix="/api/categorias", tags=["Categorías"])


def owned(db, user_id, category_id):
    item = db.scalar(select(CategoriaMenu).where(CategoriaMenu.id == category_id, CategoriaMenu.user_id == user_id))
    if not item: raise HTTPException(404, "Categoría no encontrada.")
    return item


def duplicate(db, user_id, name, excluded=None):
    query = select(CategoriaMenu).where(CategoriaMenu.user_id == user_id, func.lower(CategoriaMenu.nombre) == name.lower())
    if excluded: query = query.where(CategoriaMenu.id != excluded)
    return db.scalar(query)


@router.get("")
def list_categories(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return [categoria_json(x) for x in db.scalars(select(CategoriaMenu).where(CategoriaMenu.user_id == user.id).order_by(CategoriaMenu.nombre)).all()]


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return categoria_json(owned(db, user.id, category_id))


@router.post("", status_code=201)
def create_category(data: CategoriaCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    if duplicate(db, user.id, data.nombre): raise HTTPException(409, "Ya existe una categoría con ese nombre.")
    item = CategoriaMenu(nombre=data.nombre, user_id=user.id); db.add(item); db.commit(); db.refresh(item)
    return categoria_json(item)


@router.put("/{category_id}")
def update_category(category_id: int, data: CategoriaCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    item = owned(db, user.id, category_id)
    if duplicate(db, user.id, data.nombre, item.id): raise HTTPException(409, "Ya existe una categoría con ese nombre.")
    item.nombre = data.nombre; db.commit(); db.refresh(item)
    return categoria_json(item)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    item = owned(db, user.id, category_id)
    if db.scalar(select(Producto.id).where(Producto.categoria_id == item.id)):
        raise HTTPException(409, "No se puede eliminar la categoría porque contiene productos.")
    db.delete(item); db.commit(); return Response(status_code=204)

