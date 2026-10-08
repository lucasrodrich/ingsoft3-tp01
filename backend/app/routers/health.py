import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.database import SessionLocal

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    try:
        with SessionLocal() as db: db.execute(text("SELECT 1"))
        # Render inyecta RENDER_GIT_COMMIT con el SHA desplegado; el smoke de CD lo compara
        # con el commit del pipeline. En local/tests no existe -> "unknown".
        return {"status": "healthy", "sha": os.environ.get("RENDER_GIT_COMMIT", "unknown")}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})

