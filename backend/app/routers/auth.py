from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.auth.jwt import create_access_token, get_current_user
from app.auth.password import hash_password, verify_password
from app.database import get_db
from app.models import CategoriaMenu, Usuario
from app.schemas.auth import LoginRequest, RegisterRequest
from app.utils.serializers import user_json

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])
INITIAL_CATEGORIES = ["Entradas", "Principales", "Pastas", "Pizzas", "Hamburguesas", "Bebidas", "Postres", "Otros"]


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.scalar(select(Usuario).where(func.lower(Usuario.email) == data.email.lower()))
    if exists:
        raise HTTPException(409, "El email ya está registrado.")
    user = Usuario(nombre=data.nombre, email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.flush()
        db.add_all([CategoriaMenu(nombre=name, user_id=user.id) for name in INITIAL_CATEGORIES])
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "El email ya está registrado.")
    return {"user": user_json(user), "token": create_access_token(user)}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(Usuario).where(func.lower(Usuario.email) == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Email o contraseña incorrectos.")
    return {"user": user_json(user), "token": create_access_token(user)}


@router.get("/me")
def me(user: Usuario = Depends(get_current_user)):
    return user_json(user)

