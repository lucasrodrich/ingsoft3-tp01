from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.usuario import utcnow


class Mesa(Base):
    __tablename__ = "mesas"
    __table_args__ = (
        UniqueConstraint("user_id", "numero", name="uq_mesa_usuario_numero"),
        CheckConstraint("numero > 0"), CheckConstraint("capacidad > 0"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    capacidad: Mapped[int] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(20), default="disponible")
    user_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    usuario = relationship("Usuario", back_populates="mesas")
    pedidos = relationship("Pedido", back_populates="mesa")
    reservas = relationship("Reserva", back_populates="mesa")

