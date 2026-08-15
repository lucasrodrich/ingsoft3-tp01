from datetime import date, time
from typing import Literal
from pydantic import Field, field_validator
from app.schemas.common import ApiModel

ReservaEstado = Literal["pendiente", "confirmada", "cancelada", "completada"]


class ReservaCreate(ApiModel):
    nombre_cliente: str = Field(alias="nombreCliente", min_length=2, max_length=100)
    cantidad_personas: int = Field(alias="cantidadPersonas", gt=0)
    fecha: date
    hora: time
    mesa_id: int = Field(alias="mesaId", gt=0)
    observaciones: str | None = Field(default=None, max_length=500)

    @field_validator("nombre_cliente")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres.")
        return value

    @field_validator("observaciones")
    @classmethod
    def clean_notes(cls, value):
        return value.strip() if value else None


class ReservaUpdate(ReservaCreate):
    pass


class ReservaEstadoUpdate(ApiModel):
    estado: ReservaEstado

