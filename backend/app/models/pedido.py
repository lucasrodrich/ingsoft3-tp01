from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.usuario import utcnow


class Pedido(Base):
    __tablename__ = "pedidos"
    id: Mapped[int] = mapped_column(primary_key=True)
    mesa_id: Mapped[int] = mapped_column(ForeignKey("mesas.id"), index=True)
    estado: Mapped[str] = mapped_column(String(30), default="abierto", index=True)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    user_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    usuario = relationship("Usuario", back_populates="pedidos")
    mesa = relationship("Mesa", back_populates="pedidos")
    items = relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")

