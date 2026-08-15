from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.usuario import utcnow


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (CheckConstraint("precio > 0"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), index=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias_menu.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    usuario = relationship("Usuario", back_populates="productos")
    categoria = relationship("CategoriaMenu", back_populates="productos")
    detalles = relationship("DetallePedido", back_populates="producto")

