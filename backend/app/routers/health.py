import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.database import SessionLocal

router = APIRouter(tags=["Health"])


# GET y HEAD: el plan gratuito de UptimeRobot consulta con HEAD (solo cabeceras, sin cuerpo).
@router.api_route("/health", methods=["GET", "HEAD"])
def health():
    try:
        with SessionLocal() as db: db.execute(text("SELECT 1"))
        # GIT_SHA lo graba el pipeline dentro de la imagen (--build-arg); el smoke de CD lo compara
        # con el commit de la corrida. Fuera de una imagen del pipeline (local/tests) -> "unknown".
        return {"status": "healthy", "sha": os.environ.get("GIT_SHA", "unknown")}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})

