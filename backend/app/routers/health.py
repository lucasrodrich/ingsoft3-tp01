from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.database import SessionLocal

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    try:
        with SessionLocal() as db: db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})

