from datetime import datetime
from decimal import Decimal
from pydantic import Field, field_validator
from app.schemas.common import ApiModel


class ProductoCreate(ApiModel):
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: str | None = Field(default=None, max_length=500)
    precio: Decimal = Field(gt=0, decimal_places=2, max_digits=12)
    disponible: bool = True
    categoria_id: int = Field(alias="categoriaId", gt=0)

    @field_validator("nombre")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres.")
        return value

    @field_validator("descripcion")
    @classmethod
    def clean_description(cls, value):
        return value.strip() if value else None


class ProductoUpdate(ProductoCreate):
    pass


class DisponibilidadUpdate(ApiModel):
    disponible: bool


class ProductoResponse(ApiModel):
    id: int
    nombre: str
    descripcion: str | None
    precio: Decimal
    disponible: bool
    categoria_id: int
    created_at: datetime
    updated_at: datetime

