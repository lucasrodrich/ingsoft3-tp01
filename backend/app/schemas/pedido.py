from typing import Literal
from pydantic import Field
from app.schemas.common import ApiModel

PedidoEstado = Literal["abierto", "en_preparacion", "listo", "entregado", "cerrado", "cancelado"]


class PedidoCreate(ApiModel):
    mesa_id: int = Field(alias="mesaId", gt=0)


class PedidoEstadoUpdate(ApiModel):
    estado: PedidoEstado


class ItemCreate(ApiModel):
    producto_id: int = Field(alias="productoId", gt=0)
    cantidad: int = Field(ge=1, le=99)


class ItemUpdate(ApiModel):
    cantidad: int = Field(ge=1, le=99)

