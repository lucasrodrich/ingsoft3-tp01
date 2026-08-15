from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import Usuario

bearer = HTTPBearer(auto_error=False)


def create_access_token(user: Usuario) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user.id,
        "email": user.email,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    unauthorized = HTTPException(status_code=401, detail="Autenticación requerida.")
    if not credentials or credentials.scheme.lower() != "bearer":
        raise unauthorized
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        user_id = int(payload["user_id"])
    except (InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized
    user = db.get(Usuario, user_id)
    if not user:
        raise unauthorized
    return user

