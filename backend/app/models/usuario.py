from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    mesas = relationship("Mesa", back_populates="usuario", cascade="all, delete-orphan")
    categorias = relationship("CategoriaMenu", back_populates="usuario", cascade="all, delete-orphan")
    productos = relationship("Producto", back_populates="usuario", cascade="all, delete-orphan")
    pedidos = relationship("Pedido", back_populates="usuario", cascade="all, delete-orphan")
    reservas = relationship("Reserva", back_populates="usuario", cascade="all, delete-orphan")

