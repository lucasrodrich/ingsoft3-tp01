from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.usuario import utcnow


class CategoriaMenu(Base):
    __tablename__ = "categorias_menu"
    __table_args__ = (UniqueConstraint("user_id", "nombre", name="uq_categoria_usuario_nombre"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50))
    user_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    usuario = relationship("Usuario", back_populates="categorias")
    productos = relationship("Producto", back_populates="categoria")

