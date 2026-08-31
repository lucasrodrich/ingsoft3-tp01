# RestoFlow

Aplicación web full-stack para administrar mesas, menú, pedidos y reservas de un restaurante con datos aislados por usuario.

Proyecto de la materia IngSoft3 - versión A.

[![CI](https://github.com/lucasrodrich/ingsoft3-tp01/actions/workflows/ci.yml/badge.svg)](https://github.com/lucasrodrich/ingsoft3-tp01/actions/workflows/ci.yml)

## Comandos rápidos

Primero cree el archivo de entorno:

```bash
# Linux/macOS
cp .env.example .env
```

```powershell
# PowerShell
Copy-Item .env.example .env
```

```cmd
rem CMD
copy .env.example .env
```

Cambie `JWT_SECRET` antes de usar la aplicación. Luego:

```bash
docker compose up -d --build
```

Este comando construye el backend y el frontend, inicia PostgreSQL, FastAPI y Nginx, y los deja ejecutándose en segundo plano.

| Acción               | Comando                        |
| -------------------- | ------------------------------ |
| Levantar y construir | `docker compose up -d --build` |
| Levantar             | `docker compose up -d`         |
| Ver estado           | `docker compose ps`            |
| Ver logs             | `docker compose logs -f`       |
| Detener              | `docker compose stop`          |
| Iniciar              | `docker compose start`         |
| Reiniciar            | `docker compose restart`       |
| Bajar                | `docker compose down`          |
| Borrar también DB    | `docker compose down -v`       |

URLs: frontend [http://localhost:3000](http://localhost:3000), API [http://localhost:8080](http://localhost:8080), Swagger [http://localhost:8080/docs](http://localhost:8080/docs) y health [http://localhost:8080/health](http://localhost:8080/health).

## Descripción y funcionalidades

Cada cuenta representa un restaurante independiente. El sistema ofrece:

- registro, login, sesión JWT persistente y logout;
- dashboard con estado de mesas, pedidos, reservas y ventas diarias;
- CRUD de mesas y estados disponible, ocupada y reservada;
- categorías iniciales y CRUD de categorías y productos;
- pedidos con detalle, precio histórico, subtotales, total y flujo de estados;
- reservas con capacidad, transiciones y detección de solapamientos de 120 minutos;
- filtros por dominio, mensajes de error, estados vacíos y diseño responsive.

## Stack tecnológico

- Backend: Python 3, FastAPI, Uvicorn, SQLAlchemy 2, Pydantic 2, PyJWT y bcrypt.
- Frontend: React, Vite, JavaScript, React Router, `fetch`, CSS y Vitest.
- Datos: PostgreSQL y `NUMERIC(12,2)`/`Decimal` para importes.
- Infraestructura: Docker Compose y Nginx.
- Tests: Pytest con SQLite aislado para la suite rápida y Vitest con jsdom.

## Arquitectura y decisiones

```text
React + Vite
      │
      │ REST + JWT
      ▼
Python + FastAPI
      │
      │ SQLAlchemy
      ▼
PostgreSQL
```

Es un monolito deliberadamente simple: un backend, una base de datos y una SPA. Los routers usan directamente una sesión SQLAlchemy; no hay microservicios, Repository Pattern, colas ni infraestructura distribuida. Las únicas utilidades compartidas cubren autenticación, serialización, totales y conflictos de reservas.

## Estructura del repositorio

```text
.
├── backend/
│   ├── app/
│   │   ├── auth/       # bcrypt, JWT y usuario actual
│   │   ├── models/     # siete modelos SQLAlchemy
│   │   ├── routers/    # endpoints por dominio
│   │   ├── schemas/    # entradas Pydantic
│   │   ├── utils/      # reglas reutilizables
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/ auth/ components/ pages/ utils/
│   │   ├── App.jsx
│   │   └── styles.css
│   ├── tests/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── .env.example
├── docker-compose.yml
├── spec.md
└── README.md
```

## Modelo de datos y relaciones

Los modelos son `Usuario`, `Mesa`, `CategoriaMenu`, `Producto`, `Pedido`, `DetallePedido` y `Reserva`.

```text
Usuario 1 ── N Mesa ── N Pedido ── N DetallePedido
   │            └───── N Reserva           │
   └── N CategoriaMenu ── N Producto ──────┘
```

El propietario se toma siempre del JWT. Las consultas de recursos incluyen `user_id = usuario autenticado`; un recurso ajeno responde 404. Los detalles se protegen mediante el pedido. Un producto agregado copia su precio a `DetallePedido.precio_unitario`, por lo que cambios posteriores no alteran el historial.

## Autenticación y seguridad

```text
Register → hash bcrypt → JWT → localStorage
                               ↓
                    Authorization: Bearer TOKEN
                               ↓
                     endpoints protegidos
```

El JWT HS256 incluye `user_id`, `email`, `iat` y `exp`; por defecto dura 24 horas. `JWT_SECRET` sólo se obtiene del entorno y el backend falla claramente si falta. Las contraseñas tienen entre 8 y 72 bytes, nunca se almacenan ni devuelven en texto plano.

Para simplificar este proyecto académico, el frontend mantiene el token en `localStorage` y valida la sesión mediante `/api/auth/me` al recargar. Un sistema de producción con requisitos superiores podría usar cookies HttpOnly. Una respuesta 401 limpia la sesión y redirige al login.

## Variables de entorno

| Variable                                                  | Propósito                                |
| --------------------------------------------------------- | ---------------------------------------- |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`       | Inicialización del contenedor PostgreSQL |
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Conexión SQLAlchemy                      |
| `JWT_SECRET`                                              | Secreto obligatorio de firma             |
| `JWT_EXPIRE_MINUTES`                                      | Duración del token, predeterminado 1440  |
| `APP_TIMEZONE`                                            | Día local usado por reservas y dashboard |
| `SERVER_HOST`, `SERVER_PORT`                              | Escucha de Uvicorn                       |
| `CORS_ORIGINS`                                            | Orígenes permitidos separados por coma   |

`.env` está ignorado por Git; `.env.example` sí debe versionarse.

## Endpoints

Sólo registro, login y health son públicos. Swagger y Redoc quedan disponibles para desarrollo.

| Dominio    | Método y ruta                                                                                               |
| ---------- | ----------------------------------------------------------------------------------------------------------- |
| Auth       | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`                                       |
| Mesas      | `GET/POST /api/mesas`, `GET/PUT/DELETE /api/mesas/{id}`, `PATCH /api/mesas/{id}/estado`                     |
| Categorías | `GET/POST /api/categorias`, `GET/PUT/DELETE /api/categorias/{id}`                                           |
| Productos  | `GET/POST /api/productos`, `GET/PUT/DELETE /api/productos/{id}`, `PATCH /api/productos/{id}/disponibilidad` |
| Pedidos    | `GET/POST /api/pedidos`, `GET/DELETE /api/pedidos/{id}`, `PATCH /api/pedidos/{id}/estado`                   |
| Items      | `POST /api/pedidos/{id}/items`, `PUT/DELETE /api/pedidos/{id}/items/{itemId}`                               |
| Reservas   | `GET/POST /api/reservas`, `GET/PUT/DELETE /api/reservas/{id}`, `PATCH /api/reservas/{id}/estado`            |
| Dashboard  | `GET /api/dashboard`                                                                                        |
| Health     | `GET /health`                                                                                               |

Productos acepta `categoriaId`, `disponible` y `texto`; pedidos, `estado`, `mesaId`, `desde` y `hasta`; reservas, `fecha`, `desde`, `hasta`, `estado`, `mesaId` y `texto`.

### Ejemplos API

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Usuario Demo","email":"demo@example.com","password":"12345678"}'
```

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"12345678"}'
```

Para un recurso protegido agregue `-H "Authorization: Bearer TOKEN"`; no use un token real en documentación o commits.

## Docker, persistencia y healthchecks

Compose crea exactamente tres servicios: `db`, `backend` y `frontend`. PostgreSQL debe estar healthy antes de iniciar FastAPI; FastAPI valida `SELECT 1` mediante `/health` antes de iniciar Nginx. Nginx sirve el build, resuelve el fallback de React y proxifica `/api`.

```bash
docker compose ps
docker compose logs
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

`docker compose stop` conserva contenedores y volumen; `docker compose start` los reanuda. Para reiniciar todo o un servicio:

```bash
docker compose restart
docker compose restart backend
docker compose restart frontend
```

`docker compose down` elimina contenedores y red, pero conserva `db_data`. Para reconstruir:

```bash
docker compose build
docker compose up -d
# o en un paso
docker compose up -d --build
```

> ⚠️ **ATENCIÓN:** `docker compose down -v` elimina también el volumen de PostgreSQL y borra todos los datos almacenados.

Para recrear después: `docker compose up -d --build`.

### Entrar a PostgreSQL

```bash
docker compose exec db psql -U postgres -d restaurant_db
```

```sql
\dt
SELECT * FROM usuarios;
\q
```

Adapte usuario/base si cambió `.env`.

## Ejecución local

PostgreSQL debe estar disponible con los valores de entorno elegidos.

```bash
cd backend
python -m venv .venv
```

Active el entorno con `source .venv/bin/activate` (Linux/macOS), `.\.venv\Scripts\Activate.ps1` (PowerShell) o `.venv\Scripts\activate` (CMD). Después:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite sirve [http://localhost:5173](http://localhost:5173) y redirige `/api` a `localhost:8080`.

## Tests y build

```bash
cd backend
python -m compileall app
pytest -q
```

La suite principal reemplaza la conexión por SQLite para no requerir Docker; PostgreSQL continúa siendo la única base de ejecución de la aplicación.

```bash
cd frontend
npm test -- --run
npm run build
```

El build queda en `frontend/dist/`.

## Troubleshooting

- `address already in use`: revise puertos con `docker ps`; 3000, 8080 o 5432 ya están ocupados.
- Docker no refleja cambios: ejecute `docker compose down` y `docker compose up -d --build`.
- Backend no conecta: revise `docker compose logs backend` y `docker compose logs db`, además de las variables `DB_*`.
- JWT inválido/expirado: confirme que `JWT_SECRET` sea estable y vuelva a iniciar sesión.
- Estado general: use `docker compose ps` y `docker compose logs -f`.
- Reset completo: `docker compose down -v` seguido de `docker compose up -d --build`; **esto borra todos los datos**.

## Preparación para DevOps

Los tests, builds reproducibles, healthchecks e imágenes separadas permiten añadir más adelante integración y entrega continua, revisión por Pull Request y publicación en un registry. Este repositorio no incluye todavía workflows, despliegues cloud ni configuración CI/CD, tal como exige el alcance académico.

## Instalación

git clone https://github.com/lucasrodrich/ingsoft3-tp01.git

## Cache de CI

El pipeline de GitHub Actions reutiliza las capas de Docker entre corridas - ver `decisiones.md`.
