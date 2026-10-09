# ---- Etapa 1: build (instala dependencias) ----
FROM python:3.13-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Etapa 2: test (pytest + tu código + tests; NO viaja a producción) ----
FROM python:3.13-slim AS test
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY app ./app
COPY tests ./tests
COPY .coveragerc .
ENTRYPOINT ["python", "-m", "pytest", "tests/", "-v", "--cov", "--cov-report=term-missing", \
            "--cov-report=xml:/out/coverage.xml", "--cov-report=html:/out/htmlcov", \
            "--junitxml=/out/junit.xml"]

# ---- Etapa 3: runtime (solo lo instalado + el código) ----
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=build /install /usr/local
COPY app ./app
# Commit que produjo esta imagen (lo pasa el pipeline con --build-arg). Va al final para no
# invalidar el cache de las capas de arriba; /health lo devuelve como `sha`.
ARG GIT_SHA=unknown
ENV GIT_SHA=$GIT_SHA
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

