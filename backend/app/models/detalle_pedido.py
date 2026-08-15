from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.usuario import utcnow


class DetallePedido(Base):
    __tablename__ = "detalles_pedido"
    __table_args__ = (CheckConstraint("cantidad > 0"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), index=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), index=True)
    cantidad: Mapped[int] = mapped_column(Integer)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto", back_populates="detalles")

