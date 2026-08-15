from datetime import datetime
from pydantic import EmailStr, Field, field_validator
from app.schemas.common import ApiModel


class RegisterRequest(ApiModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("nombre")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres.")
        return value

    @field_validator("email")
    @classmethod
    def clean_email(cls, value):
        return str(value).strip().lower()

    @field_validator("password")
    @classmethod
    def valid_bcrypt_length(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar 72 bytes.")
        return value


class LoginRequest(ApiModel):
    email: EmailStr
    password: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def clean_email(cls, value):
        return str(value).strip().lower()


class UserResponse(ApiModel):
    id: int
    nombre: str
    email: str
    created_at: datetime

