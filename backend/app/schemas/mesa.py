from datetime import datetime
from typing import Literal
from pydantic import Field
from app.schemas.common import ApiModel

MesaEstado = Literal["disponible", "ocupada", "reservada"]


class MesaCreate(ApiModel):
    numero: int = Field(gt=0)
    capacidad: int = Field(gt=0, le=30)


class MesaUpdate(MesaCreate):
    estado: MesaEstado = "disponible"


class MesaEstadoUpdate(ApiModel):
    estado: MesaEstado


class MesaResponse(ApiModel):
    id: int
    numero: int
    capacidad: int
    estado: MesaEstado
    created_at: datetime

