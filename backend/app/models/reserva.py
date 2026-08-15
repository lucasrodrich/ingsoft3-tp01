from datetime import date, datetime, time
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.usuario import utcnow


class Reserva(Base):
    __tablename__ = "reservas"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_cliente: Mapped[str] = mapped_column(String(100), index=True)
    cantidad_personas: Mapped[int] = mapped_column(Integer)
    fecha: Mapped[date] = mapped_column(Date, index=True)
    hora: Mapped[time] = mapped_column(Time)
    mesa_id: Mapped[int] = mapped_column(ForeignKey("mesas.id"), index=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    usuario = relationship("Usuario", back_populates="reservas")
    mesa = relationship("Mesa", back_populates="reservas")

