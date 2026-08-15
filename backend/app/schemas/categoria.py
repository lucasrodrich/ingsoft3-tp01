from datetime import datetime
from pydantic import Field, field_validator
from app.schemas.common import ApiModel


class CategoriaCreate(ApiModel):
    nombre: str = Field(min_length=2, max_length=50)

    @field_validator("nombre")
    @classmethod
    def clean(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres.")
        return value


class CategoriaResponse(ApiModel):
    id: int
    nombre: str
    created_at: datetime

