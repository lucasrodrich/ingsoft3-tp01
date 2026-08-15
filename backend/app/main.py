from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import Base, engine
from app import models
from app.routers import auth, categorias, dashboard, health, mesas, pedidos, productos, reservas


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Sistema de Gestión de Restaurante", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False,
                   allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(HTTPException)
async def http_error(_request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, exc: RequestValidationError):
    details = [{"field": ".".join(str(x) for x in error["loc"] if x != "body"), "message": error["msg"]}
               for error in exc.errors()]
    return JSONResponse(status_code=422, content={"error": "Datos inválidos.", "details": details})


for router in (health.router, auth.router, mesas.router, categorias.router, productos.router,
               pedidos.router, reservas.router, dashboard.router):
    app.include_router(router)

