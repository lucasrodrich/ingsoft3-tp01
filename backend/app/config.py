import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int
    app_timezone: str
    server_host: str
    server_port: int
    cors_origins: list[str]


def get_settings() -> Settings:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET es obligatorio. Configure la variable antes de iniciar el backend.")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        name = os.getenv("DB_NAME", "restaurant_db")
        database_url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"
    origins = [item.strip() for item in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    ).split(",") if item.strip()]
    return Settings(
        database_url=database_url,
        jwt_secret=secret,
        jwt_expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "1440")),
        app_timezone=os.getenv("APP_TIMEZONE", "America/Argentina/Cordoba"),
        server_host=os.getenv("SERVER_HOST", "0.0.0.0"),
        server_port=int(os.getenv("SERVER_PORT", "8080")),
        cors_origins=origins,
    )


settings = get_settings()

