Sistema de Gestión de Restaurante — Especificación completa

0. Instrucción principal para Codex

Desarrollar desde cero una aplicación web full-stack llamada Sistema de Gestión de Restaurante.

Antes de escribir código:

1. Leer esta especificación completa.
2. Revisar la estructura existente del repositorio.
3. Si el repositorio está vacío, crear toda la estructura indicada.
4. Si existen archivos previos, no eliminar archivos ajenos al proyecto sin necesidad.
5. Planificar brevemente la implementación.
6. Implementar todos los requisitos.
7. Ejecutar tests.
8. Ejecutar builds.
9. Levantar Docker Compose si Docker está disponible.
10. Realizar las pruebas funcionales finales especificadas.
11. Corregir cualquier error encontrado.
12. Volver a ejecutar tests y builds después de las correcciones.

No considerar la tarea terminada mientras existan errores solucionables de compilación, ejecución o tests.

No agregar tecnologías, patrones arquitectónicos o funcionalidades excluidas explícitamente en este documento.

────────

1. Objetivo del proyecto

Crear una aplicación web para administrar las operaciones básicas de un restaurante.

Debe permitir:

• registrar usuarios;
• iniciar sesión;
• autenticarse mediante JWT;
• gestionar mesas;
• gestionar categorías del menú;
• gestionar productos/platos;
• crear y administrar pedidos;
• agregar productos a pedidos;
• calcular automáticamente subtotales y totales;
• administrar reservas;
• evitar conflictos de reservas;
• visualizar un dashboard;
• mantener los datos aislados entre usuarios;
• ejecutar frontend, backend y PostgreSQL mediante Docker Compose;
• disponer de tests;
• disponer de healthchecks;
• estar preparada para posteriormente incorporar un proceso DevOps.

El proyecto será utilizado en Ingeniería de Software III para trabajar posteriormente con:

• Git;
• branches;
• Pull Requests;
• protección de main;
• Code Review;
• Continuous Integration;
• GitHub Actions;
• Docker;
• Docker Registry;
• Continuous Delivery;
• Continuous Deployment.

La aplicación debe ser suficientemente completa para parecer un sistema real, pero deliberadamente sencilla desde el punto de vista arquitectónico.

────────

2. Stack tecnológico obligatorio

Backend

Utilizar:

• Python 3.
• FastAPI.
• Uvicorn.
• SQLAlchemy ORM.
• Pydantic.
• PostgreSQL.
• Driver PostgreSQL compatible con SQLAlchemy.
• PyJWT.
• bcrypt.
• Pytest.
• FastAPI TestClient cuando corresponda.

Preferir APIs modernas de SQLAlchemy y Pydantic.

No utilizar Django.

No utilizar Flask.

Frontend

Utilizar:

• React.
• Vite.
• JavaScript.

No utilizar TypeScript.

Utilizar:

• React Router.
• fetch.
• useState.
• useEffect.
• React Context solamente cuando resulte útil para autenticación.
• CSS tradicional.
• Vitest.

No utilizar:

• Redux.
• Zustand.
• MobX.
• Next.js.
• Material UI.
• Bootstrap.
• Tailwind.

Base de datos

Utilizar exclusivamente:

```text
PostgreSQL
```

Nombre sugerido:

```text
restaurant_db
```

Infraestructura

Utilizar:

• Docker.
• Docker Compose.
• Nginx para servir el frontend compilado.
• PostgreSQL oficial.

────────

3. Arquitectura general

La arquitectura debe ser:

```text
┌─────────────────────┐
│    React + Vite     │
│      Frontend       │
└──────────┬──────────┘
           │
           │ HTTP / REST + JWT
           ▼
┌─────────────────────┐
│ Python + FastAPI    │
│      Backend        │
└──────────┬──────────┘
           │
           │ SQLAlchemy
           ▼
┌─────────────────────┐
│     PostgreSQL      │
└─────────────────────┘
```

Debe ser una aplicación monolítica.

Frontend y backend son aplicaciones diferentes, pero el backend debe ser un único servicio.

────────

4. Restricciones arquitectónicas

NO implementar:

• Microservicios.
• Arquitectura distribuida.
• Repository Pattern.
• Clean Architecture.
• Hexagonal Architecture.
• Onion Architecture.
• CQRS.
• Event Sourcing.
• Unit of Work personalizado.
• API Gateway.
• Redis.
• Kafka.
• RabbitMQ.
• Celery.
• GraphQL.
• WebSockets.
• Kubernetes.
• Terraform.
• AWS.
• Azure.
• GCP.
• Firebase.
• Supabase.
• MongoDB.
• múltiples bases de datos.

No crear capas innecesarias como:

```text
repositories/
services/
domain/
application/
infrastructure/
ports/
adapters/
```

para operaciones CRUD simples.

El flujo esperado debe ser aproximadamente:

```text
FastAPI Router
      ↓
SQLAlchemy Session
      ↓
PostgreSQL
```

Puede existir lógica auxiliar reutilizable para:

• autenticación;
• JWT;
• passwords;
• cálculo de pedidos;
• validaciones;
• configuración.

No convertir estas utilidades en una arquitectura empresarial innecesaria.

────────

5. Multiusuario

La aplicación será multiusuario.

Cada usuario registrado administra los datos de su propio restaurante.

Ejemplo:

```text
Usuario A
 ├── Mesas A
 ├── Categorías A
 ├── Productos A
 ├── Pedidos A
 └── Reservas A

Usuario B
 ├── Mesas B
 ├── Categorías B
 ├── Productos B
 ├── Pedidos B
 └── Reservas B
```

Usuario A jamás debe acceder a información perteneciente al Usuario B.

Esto debe aplicarse en TODOS los endpoints protegidos.

────────

6. Regla crítica de ownership

Nunca confiar en un user_id enviado desde el frontend.

Por ejemplo, esto NO debe permitir seleccionar propietario:

```json
{
  "userId": 10
}
```

El backend debe obtener siempre el usuario autenticado mediante el JWT.

Flujo:

```text
Authorization header
        ↓
       JWT
        ↓
     user_id
        ↓
consulta SQLAlchemy filtrada
        ↓
datos pertenecientes al usuario
```

────────

7. Entidades principales

Crear las siguientes entidades:

1. Usuario.
2. Mesa.
3. CategoriaMenu.
4. Producto.
5. Pedido.
6. DetallePedido.
7. Reserva.

No agregar más entidades principales salvo que sea estrictamente necesario.

────────

8. Entidad Usuario

Campos:

```text
id
nombre
email
password_hash
created_at
```

Tipos conceptuales:

```text
id              integer
nombre          varchar
email           varchar
password_hash   varchar
created_at      timestamp
```

Reglas:

nombre

• obligatorio;
• trim;
• mínimo 2 caracteres;
• máximo 100.

email

• obligatorio;
• formato válido;
• trim;
• convertir a minúsculas;
• único.

La comparación para evitar duplicados debe ser case-insensitive.

password

Solo existe en requests.

Nunca almacenar el password original.

Reglas:

• obligatorio;
• mínimo 8 caracteres;
• máximo 72 bytes/caracteres compatible con bcrypt.

────────

9. Passwords

Utilizar bcrypt.

Flujo de registro:

```text
password
   ↓
bcrypt
   ↓
password_hash
   ↓
PostgreSQL
```

Nunca:

• almacenar passwords en texto plano;
• devolver password_hash;
• mostrar el hash en frontend;
• loguear passwords;
• incluir passwords en errores.

────────

10. JWT

Utilizar JWT para autenticación.

Usar PyJWT.

Algoritmo:

```text
HS256
```

El token debe contener como mínimo:

```text
user_id
email
iat
exp
```

Duración predeterminada:

```text
24 horas
```

La duración puede configurarse mediante:

```env
JWT_EXPIRE_MINUTES=1440
```

El secreto debe provenir exclusivamente de:

```env
JWT_SECRET
```

No hardcodear el secreto.

Si JWT_SECRET no existe, el backend debe fallar al iniciar con un mensaje claro.

────────

11. Endpoints de autenticación

Crear:

```http
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

register y login son públicos.

me requiere JWT.

────────

12. Register

Endpoint:

```http
POST /api/auth/register
```

Body:

```json
{
  "nombre": "Felipe",
  "email": "felipe@example.com",
  "password": "12345678"
}
```

Proceso:

1. validar nombre;
2. validar email;
3. normalizar email;
4. comprobar duplicados;
5. validar password;
6. generar bcrypt hash;
7. crear usuario;
8. crear categorías iniciales del menú para ese usuario;
9. generar JWT;
10. devolver usuario seguro y token.

Respuesta:

```text
201 Created
```

Ejemplo:

```json
{
  "user": {
    "id": 1,
    "nombre": "Felipe",
    "email": "felipe@example.com",
    "createdAt": "2026-08-14T15:00:00"
  },
  "token": "eyJ..."
}
```

Si el email existe:

```text
409 Conflict
```

────────

13. Categorías iniciales

Al registrar un usuario, crear automáticamente categorías propias:

```text
Entradas
Principales
Pastas
Pizzas
Hamburguesas
Bebidas
Postres
Otros
```

Las categorías deben pertenecer al nuevo usuario.

No crear categorías globales compartidas.

────────

14. Login

Endpoint:

```http
POST /api/auth/login
```

Body:

```json
{
  "email": "felipe@example.com",
  "password": "12345678"
}
```

Proceso:

1. normalizar email;
2. buscar usuario;
3. comparar hash bcrypt;
4. si es correcto, generar JWT.

Respuesta:

```text
200 OK
```

```json
{
  "user": {
    "id": 1,
    "nombre": "Felipe",
    "email": "felipe@example.com"
  },
  "token": "eyJ..."
}
```

Credenciales inválidas:

```text
401 Unauthorized
```

Mensaje genérico.

No revelar si falló:

• email;
• password.

────────

15. GET /auth/me

Endpoint:

```http
GET /api/auth/me
```

Header:

```http
Authorization: Bearer <token>
```

Respuesta:

```json
{
  "id": 1,
  "nombre": "Felipe",
  "email": "felipe@example.com",
  "createdAt": "..."
}
```

Nunca devolver:

```text
password_hash
```

────────

16. Autenticación FastAPI

Crear dependencia similar conceptualmente a:

```text
get_current_user()
```

Responsabilidades:

1. leer header Authorization;
2. verificar Bearer;
3. validar JWT;
4. comprobar expiración;
5. obtener user_id;
6. consultar usuario;
7. devolver usuario autenticado.

Endpoints protegidos deben utilizar esta dependencia.

────────

17. Rutas públicas

Solamente deben ser públicas:

```text
POST /api/auth/register
POST /api/auth/login
GET  /health
```

La documentación automática de FastAPI puede mantenerse disponible para desarrollo:

```text
/docs
/redoc
```

────────

18. Rutas protegidas

Requerir JWT para:

```text
/api/auth/me

/api/mesas/*
/api/categorias/*
/api/productos/*
/api/pedidos/*
/api/reservas/*
/api/dashboard
```

────────

19. Entidad Mesa

Campos:

```text
id
numero
capacidad
estado
user_id
created_at
```

Estados válidos:

```text
disponible
ocupada
reservada
```

Estado predeterminado:

```text
disponible
```

────────

20. Validaciones de Mesa

número

• obligatorio;
• entero positivo;
• único dentro del restaurante/usuario.

Usuario A puede tener Mesa 1.

Usuario B también puede tener Mesa 1.

Pero Usuario A no puede tener dos Mesas 1.

capacidad

• obligatoria;
• entero;
• mayor que cero;
• máximo razonable, por ejemplo 30.

estado

Solamente:

```text
disponible
ocupada
reservada
```

────────

21. Reglas de estado de mesa

ocupada debe reflejar principalmente la existencia de un pedido activo.

Al crear un pedido:

```text
disponible/reservada
        ↓
      ocupada
```

Al cerrar o cancelar el pedido:

```text
ocupada
   ↓
disponible
```

Las reservas futuras NO deben cambiar permanentemente el estado actual de la mesa.

reservada puede utilizarse para indicar manualmente que una mesa está reservada actualmente.

No implementar un scheduler automático.

────────

22. CRUD de Mesas

Crear:

```http
GET    /api/mesas
GET    /api/mesas/{id}
POST   /api/mesas
PUT    /api/mesas/{id}
DELETE /api/mesas/{id}
PATCH  /api/mesas/{id}/estado
```

────────

23. Crear mesa

Body ejemplo:

```json
{
  "numero": 4,
  "capacidad": 4
}
```

El user_id no debe aceptarse desde frontend.

Backend lo obtiene del JWT.

Respuesta:

```text
201 Created
```

────────

24. Eliminar mesa

No permitir eliminar una mesa si tiene:

• pedido activo;
• reservas futuras pendientes;
• reservas futuras confirmadas.

Responder:

```text
409 Conflict
```

No borrar pedidos históricos ni reservas automáticamente.

────────

25. Ownership de Mesa

Para:

```http
GET /api/mesas/{id}
PUT /api/mesas/{id}
DELETE /api/mesas/{id}
```

buscar siempre:

```text
id = solicitado
AND
user_id = usuario autenticado
```

Si la mesa pertenece a otro usuario:

```text
404 Not Found
```

No revelar su existencia.

────────

26. Entidad CategoriaMenu

Campos:

```text
id
nombre
user_id
created_at
```

Reglas:

• nombre obligatorio;
• trim;
• mínimo 2 caracteres;
• máximo 50;
• no duplicar dentro del mismo usuario ignorando mayúsculas/minúsculas.

────────

27. CRUD de categorías

Crear:

```http
GET    /api/categorias
GET    /api/categorias/{id}
POST   /api/categorias
PUT    /api/categorias/{id}
DELETE /api/categorias/{id}
```

────────

28. Eliminar categoría

No permitir eliminar una categoría con productos asociados.

Responder:

```text
409 Conflict
```

Ejemplo:

```json
{
  "error": "No se puede eliminar la categoría porque contiene productos."
}
```

────────

29. Entidad Producto

Campos:

```text
id
nombre
descripcion
precio
disponible
categoria_id
user_id
created_at
updated_at
```

Tipos conceptuales:

```text
id             integer
nombre         varchar
descripcion    varchar/text
precio         NUMERIC(12,2)
disponible     boolean
categoria_id   foreign key
user_id        foreign key
```

────────

30. Validaciones de Producto

nombre

• obligatorio;
• trim;
• mínimo 2;
• máximo 150.

descripción

• opcional;
• máximo 500 caracteres.

precio

• obligatorio;
• mayor que cero;
• máximo dos decimales.

Utilizar:

```text
NUMERIC(12,2)
```

en PostgreSQL.

En Python usar:

```text
Decimal
```

para operaciones monetarias.

No utilizar float para cálculos de dinero.

disponible

Boolean.

Predeterminado:

```text
true
```

categoria_id

• obligatorio;
• debe pertenecer al mismo usuario autenticado.

────────

31. CRUD de Productos

Crear:

```http
GET    /api/productos
GET    /api/productos/{id}
POST   /api/productos
PUT    /api/productos/{id}
DELETE /api/productos/{id}
PATCH  /api/productos/{id}/disponibilidad
```

────────

32. Filtros de productos

GET /api/productos debe permitir:

```text
categoriaId
disponible
texto
```

Ejemplos:

```http
GET /api/productos?categoriaId=3
```

```http
GET /api/productos?disponible=true
```

```http
GET /api/productos?texto=milanesa
```

Los filtros deben ser combinables.

La búsqueda por texto debe ser case-insensitive.

────────

33. Disponibilidad de producto

Endpoint:

```http
PATCH /api/productos/{id}/disponibilidad
```

Body:

```json
{
  "disponible": false
}
```

────────

34. Eliminar producto

Si un producto fue utilizado en un pedido histórico, no eliminarlo físicamente.

Responder:

```text
409 Conflict
```

y recomendar marcarlo:

```text
disponible = false
```

Esto permite conservar el historial.

────────

35. Entidad Pedido

Campos:

```text
id
mesa_id
estado
total
user_id
created_at
updated_at
closed_at
```

total:

```text
NUMERIC(12,2)
```

Estado inicial:

```text
abierto
```

────────

36. Estados de Pedido

Estados válidos:

```text
abierto
en_preparacion
listo
entregado
cerrado
cancelado
```

────────

37. Transiciones de pedido

Permitir:

```text
abierto
   ↓
en_preparacion
   ↓
listo
   ↓
entregado
   ↓
cerrado
```

También permitir cancelación desde:

```text
abierto
en_preparacion
listo
```

Estados terminales:

```text
cerrado
cancelado
```

No permitir modificar un pedido cerrado o cancelado.

────────

38. Pedido activo

Se considera pedido activo si su estado está en:

```text
abierto
en_preparacion
listo
entregado
```

Una mesa no puede tener más de un pedido activo simultáneamente.

────────

39. Crear Pedido

Endpoint:

```http
POST /api/pedidos
```

Body:

```json
{
  "mesaId": 4
}
```

No aceptar:

```text
userId
total
estado arbitrario
```

desde frontend.

Backend debe:

1. comprobar ownership de mesa;
2. comprobar que no tenga pedido activo;
3. crear pedido estado abierto;
4. total inicial 0.00;
5. marcar mesa ocupada.

Respuesta:

```text
201 Created
```

────────

40. Entidad DetallePedido

Campos:

```text
id
pedido_id
producto_id
cantidad
precio_unitario
subtotal
created_at
```

────────

41. Cantidad

cantidad:

• entero;
• mínimo 1;
• máximo 99.

────────

42. Precio unitario histórico

Cuando un producto se agrega al pedido:

```text
Producto.precio actual
          ↓
DetallePedido.precio_unitario
```

Guardar el precio en ese momento.

Ejemplo:

```text
14 de agosto:
Milanesa = $15.000

Pedido 20:
precio_unitario = $15.000
```

Si posteriormente:

```text
Milanesa = $18.000
```

el pedido anterior debe seguir mostrando:

```text
$15.000
```

Nunca recalcular pedidos históricos usando el precio actual del producto.

────────

43. Subtotal

El backend debe calcular:

```text
subtotal = precio_unitario × cantidad
```

El frontend jamás debe ser la fuente de verdad del subtotal.

────────

44. Total de Pedido

Backend debe calcular:

```text
total = suma de subtotales
```

Cada vez que:

• se agrega un item;
• cambia una cantidad;
• se elimina un item;

recalcular el total.

No confiar en un total enviado por frontend.

────────

45. Agregar item

Endpoint:

```http
POST /api/pedidos/{pedidoId}/items
```

Body:

```json
{
  "productoId": 8,
  "cantidad": 2
}
```

Backend debe:

1. comprobar ownership del pedido;
2. comprobar que esté activo;
3. comprobar ownership del producto;
4. comprobar que producto esté disponible;
5. tomar precio actual;
6. calcular subtotal;
7. guardar item;
8. recalcular total.

Si el producto ya está presente en el pedido, preferentemente incrementar su cantidad en lugar de crear una línea duplicada.

────────

46. Modificar item

Endpoint:

```http
PUT /api/pedidos/{pedidoId}/items/{itemId}
```

Body:

```json
{
  "cantidad": 3
}
```

Mantener:

```text
precio_unitario
```

original del item.

Recalcular:

```text
subtotal
total del pedido
```

────────

47. Eliminar item

Endpoint:

```http
DELETE /api/pedidos/{pedidoId}/items/{itemId}
```

Después:

```text
recalcular total
```

────────

48. API de pedidos

Crear:

```http
GET    /api/pedidos
GET    /api/pedidos/{id}
POST   /api/pedidos
PATCH  /api/pedidos/{id}/estado
DELETE /api/pedidos/{id}

POST   /api/pedidos/{id}/items
PUT    /api/pedidos/{id}/items/{itemId}
DELETE /api/pedidos/{id}/items/{itemId}
```

────────

49. Listar pedidos

Permitir filtros:

```text
estado
mesaId
desde
hasta
```

Ejemplo:

```http
GET /api/pedidos?estado=abierto
```

```http
GET /api/pedidos?desde=2026-08-01&hasta=2026-08-31
```

Orden predeterminado:

```text
más recientes primero
```

────────

50. Obtener Pedido

Respuesta aproximada:

```json
{
  "id": 20,
  "mesa": {
    "id": 4,
    "numero": 4
  },
  "estado": "abierto",
  "items": [
    {
      "id": 1,
      "productoId": 10,
      "productoNombre": "Milanesa Napolitana",
      "cantidad": 2,
      "precioUnitario": 18500,
      "subtotal": 37000
    },
    {
      "id": 2,
      "productoId": 15,
      "productoNombre": "Coca-Cola",
      "cantidad": 2,
      "precioUnitario": 3500,
      "subtotal": 7000
    }
  ],
  "total": 44000,
  "createdAt": "..."
}
```

────────

51. Cambio de estado

Endpoint:

```http
PATCH /api/pedidos/{id}/estado
```

Body:

```json
{
  "estado": "en_preparacion"
}
```

Validar transiciones.

No permitir saltos arbitrarios.

────────

52. Cerrar pedido

Cuando pasa a:

```text
cerrado
```

backend debe:

1. comprobar transición válida;
2. comprobar que tenga al menos un item;
3. establecer closed_at;
4. conservar total;
5. marcar mesa disponible.

────────

53. Cancelar pedido

Al cancelar:

1. conservar pedido e items como historial;
2. estado cancelado;
3. liberar mesa;
4. no contabilizarlo como venta.

────────

54. Eliminar pedido

Evitar borrar historial.

DELETE /api/pedidos/{id} solo debe permitirse si:

• estado abierto;
• no contiene items.

En cualquier otro caso:

```text
409 Conflict
```

Para pedidos reales usar cancelación.

────────

55. Entidad Reserva

Campos:

```text
id
nombre_cliente
cantidad_personas
fecha
hora
mesa_id
observaciones
estado
user_id
created_at
updated_at
```

────────

56. Estados de Reserva

Estados:

```text
pendiente
confirmada
cancelada
completada
```

Estado inicial:

```text
pendiente
```

────────

57. Validaciones de Reserva

nombre_cliente

• obligatorio;
• trim;
• mínimo 2;
• máximo 100.

cantidad_personas

• entero positivo;
• no puede superar capacidad de la mesa.

fecha

• obligatoria;
• no puede estar en el pasado.

hora

• obligatoria.

observaciones

• opcionales;
• máximo 500 caracteres.

mesa

Debe pertenecer al usuario autenticado.

────────

58. Duración de reserva

Para mantener la lógica simple, considerar que cada reserva ocupa:

```text
120 minutos
```

No crear una entidad adicional para duración.

────────

59. Conflicto de reserva

Para una misma mesa no permitir reservas que se superpongan dentro de su ventana de 120 minutos.

Ejemplo:

```text
Reserva existente:
20:00 → 22:00

Nueva reserva:
21:00 → 23:00
```

Debe rechazarse.

Reservas que bloquean horario:

```text
pendiente
confirmada
```

No deben bloquear:

```text
cancelada
completada
```

Responder:

```text
409 Conflict
```

────────

60. Transiciones de reserva

Permitir:

```text
pendiente → confirmada
pendiente → cancelada

confirmada → completada
confirmada → cancelada
```

Estados terminales:

```text
cancelada
completada
```

────────

61. API de reservas

Crear:

```http
GET    /api/reservas
GET    /api/reservas/{id}
POST   /api/reservas
PUT    /api/reservas/{id}
DELETE /api/reservas/{id}
PATCH  /api/reservas/{id}/estado
```

────────

62. Filtros de reserva

Permitir:

```text
fecha
desde
hasta
estado
mesaId
texto
```

texto puede buscar nombre del cliente.

Ejemplo:

```http
GET /api/reservas?fecha=2026-08-15
```

────────

63. Eliminar Reserva

No borrar reservas históricas completadas.

Permitir DELETE solamente para reservas:

```text
pendiente
cancelada
```

En caso contrario:

```text
409 Conflict
```

────────

64. Dashboard

Crear endpoint:

```http
GET /api/dashboard
```

Debe devolver únicamente datos del usuario autenticado.

────────

65. Dashboard — métricas

Mostrar como mínimo:

```text
mesasDisponibles
mesasOcupadas
mesasReservadas
pedidosAbiertos
reservasHoy
ventasHoy
pedidosHoy
```

Respuesta ejemplo:

```json
{
  "mesasDisponibles": 8,
  "mesasOcupadas": 4,
  "mesasReservadas": 2,
  "pedidosAbiertos": 5,
  "reservasHoy": 7,
  "ventasHoy": 430500.0,
  "pedidosHoy": 32
}
```

────────

66. Definición de ventas del día

ventasHoy debe ser:

```text
SUM(total)
```

únicamente de pedidos:

```text
estado = cerrado
```

cuyo closed_at corresponda al día actual.

Pedidos cancelados:

```text
NO cuentan
```

────────

67. Pedidos abiertos del dashboard

Considerar abiertos:

```text
abierto
en_preparacion
listo
entregado
```

────────

68. Pedidos de hoy

Contar pedidos creados durante el día actual.

Puede excluir cancelados si se documenta claramente.

Preferencia:

```text
pedidosHoy = todos los pedidos creados hoy excepto cancelados
```

────────

69. Zona horaria

Agregar variable opcional:

```env
APP_TIMEZONE=America/Argentina/Cordoba
```

Utilizarla para conceptos como:

```text
hoy
ventas de hoy
reservas de hoy
```

Evitar depender exclusivamente de UTC para las métricas visibles.

Si resulta excesivamente complejo, utilizar timestamps UTC en base de datos y convertir correctamente al timezone configurado para cálculos diarios.

────────

70. Healthcheck

Crear:

```http
GET /health
```

Debe ser público.

Cuando backend y DB funcionen:

```text
200 OK
```

```json
{
  "status": "healthy"
}
```

Backend debe ejecutar una consulta simple equivalente a:

```sql
SELECT 1;
```

Si PostgreSQL no responde:

```text
503 Service Unavailable
```

```json
{
  "status": "unhealthy"
}
```

────────

71. Códigos HTTP

Utilizar correctamente:

```text
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
404 Not Found
409 Conflict
422 Unprocessable Entity
500 Internal Server Error
503 Service Unavailable
```

422 puede utilizarse para errores de schemas Pydantic.

400 para reglas de negocio inválidas.

────────

72. Formato de errores

Utilizar un formato consistente.

Preferentemente:

```json
{
  "error": "Mensaje entendible."
}
```

Para validaciones múltiples puede utilizarse:

```json
{
  "error": "Datos inválidos.",
  "details": [
    {
      "field": "precio",
      "message": "El precio debe ser mayor que cero."
    }
  ]
}
```

No devolver stack traces al frontend.

────────

73. Ownership en TODAS las entidades

Aplicar aislamiento en:

```text
Mesa
CategoriaMenu
Producto
Pedido
Reserva
```

DetallePedido se protege mediante ownership del Pedido.

Nunca permitir relaciones cruzadas entre usuarios.

Ejemplo:

Usuario A no puede crear un pedido usando Mesa de B.

Usuario A no puede agregar Producto de B a su Pedido.

Usuario A no puede reservar Mesa de B.

Responder:

```text
404 Not Found
```

para no revelar recursos de otros usuarios.

────────

74. Modelado SQLAlchemy

Usar modelos SQLAlchemy separados.

Definir:

• primary keys;
• foreign keys;
• relationships;
• indexes;
• constraints cuando sea razonable;
• Numeric(12,2) para dinero;
• timestamps;
• valores predeterminados.

────────

75. Relaciones de datos

```text
Usuario
  │
  ├── 1:N Mesas
  ├── 1:N CategoriasMenu
  ├── 1:N Productos
  ├── 1:N Pedidos
  └── 1:N Reservas

CategoriaMenu
      │
      └── 1:N Productos

Mesa
 │
 ├── 1:N Pedidos
 └── 1:N Reservas

Pedido
   │
   └── 1:N DetallesPedido

Producto
   │
   └── 1:N DetallesPedido
```

────────

76. Constraints importantes

Implementar o validar:

```text
Usuario.email único
Mesa(user_id, numero) único
precio > 0
cantidad > 0
capacidad > 0
```

Las restricciones case-insensitive pueden validarse a nivel aplicación si simplifica la implementación.

────────

77. Inicialización de la base

Para mantener la aplicación sencilla:

• utilizar Base.metadata.create_all(...) al inicio;
• no utilizar Alembic inicialmente;
• no implementar infraestructura compleja de migraciones.

La estructura debe quedar preparada para poder incorporar Alembic posteriormente si fuera necesario.

────────

78. Conexión a PostgreSQL

Centralizar configuración en:

```text
app/database.py
```

Utilizar SQLAlchemy Engine.

Preferir:

```text
pool_pre_ping=True
```

Crear:

```text
SessionLocal
Base
get_db()
```

get_db() debe poder utilizarse como dependency de FastAPI.

────────

79. Configuración

Crear módulo:

```text
app/config.py
```

para leer variables de entorno.

No dispersar os.getenv() por toda la aplicación.

────────

80. Variables de entorno backend

Utilizar:

```env
DB_HOST
DB_PORT
DB_USER
DB_PASSWORD
DB_NAME

JWT_SECRET
JWT_EXPIRE_MINUTES

APP_TIMEZONE

SERVER_HOST
SERVER_PORT

CORS_ORIGINS
```

────────

81. .env.example

Crear en raíz:

```text
.env.example
```

Ejemplo:

```env
POSTGRES_DB=restaurant_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=restaurant_db

JWT_SECRET=change-this-secret-before-production
JWT_EXPIRE_MINUTES=1440

APP_TIMEZONE=America/Argentina/Cordoba

SERVER_HOST=0.0.0.0
SERVER_PORT=8080

CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

No guardar un .env real en Git.

────────

82. Backend — estructura

Crear aproximadamente:

```text
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py
│   │   └── password.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── mesa.py
│   │   ├── categoria.py
│   │   ├── producto.py
│   │   ├── pedido.py
│   │   ├── detalle_pedido.py
│   │   └── reserva.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── mesa.py
│   │   ├── categoria.py
│   │   ├── producto.py
│   │   ├── pedido.py
│   │   └── reserva.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── mesas.py
│   │   ├── categorias.py
│   │   ├── productos.py
│   │   ├── pedidos.py
│   │   ├── reservas.py
│   │   ├── dashboard.py
│   │   └── health.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── orders.py
│       └── reservations.py
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_mesas.py
│   ├── test_productos.py
│   ├── test_pedidos.py
│   ├── test_reservas.py
│   ├── test_ownership.py
│   └── test_health.py
│
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

Puede ajustarse ligeramente si existe una razón técnica.

NO agregar Repository Pattern.

────────

83. FastAPI main.py

app/main.py debe:

1. cargar configuración;
2. inicializar DB;
3. crear tablas;
4. configurar FastAPI;
5. configurar CORS;
6. registrar exception handlers cuando corresponda;
7. registrar routers;
8. exponer /health.

No poner toda la lógica de negocio en main.py.

────────

84. Routers

Separar routers por dominio:

```text
auth
mesas
categorias
productos
pedidos
reservas
dashboard
health
```

Utilizar:

```text
APIRouter
```

con prefixes adecuados.

────────

85. Schemas Pydantic

Separar schemas de entrada y salida.

Ejemplos conceptuales:

```text
MesaCreate
MesaUpdate
MesaResponse

ProductoCreate
ProductoUpdate
ProductoResponse

PedidoCreate
PedidoResponse

ReservaCreate
ReservaUpdate
ReservaResponse
```

Nunca utilizar directamente modelos SQLAlchemy como body de requests.

────────

86. Fechas y timestamps

Usar:

```text
ISO 8601
```

en la API.

Fecha:

```text
YYYY-MM-DD
```

Hora:

```text
HH:MM
```

Timestamps:

```text
ISO 8601
```

Frontend puede mostrar:

```text
DD/MM/YYYY
```

────────

87. Frontend

Crear SPA con React Router.

Rutas:

```text
/login
/register
/dashboard
/mesas
/menu
/pedidos
/reservas
/*
```

────────

88. Página Login

Ruta:

```text
/login
```

Interfaz aproximada:

```text
────────────────────────

Gestión de Restaurante

Email
[_______________________]

Contraseña
[_______________________]

[ Iniciar sesión ]

¿No tenés cuenta?
Crear cuenta

────────────────────────
```

Debe manejar:

• loading;
• errores;
• credenciales inválidas.

────────

89. Página Register

Ruta:

```text
/register
```

Campos:

```text
Nombre
Email
Contraseña
Confirmar contraseña
```

Validaciones frontend:

• obligatorios;
• email básico;
• password mínimo 8;
• passwords deben coincidir.

Backend sigue siendo la fuente definitiva de validaciones.

────────

90. Persistencia del token

Para este proyecto académico utilizar:

```text
localStorage
```

Guardar:

```text
token
```

Puede guardarse información mínima del usuario, pero al recargar la aplicación debe validarse mediante:

```text
GET /api/auth/me
```

────────

91. Nota de seguridad

Documentar en README que:

```text
localStorage
```

se utiliza para mantener la implementación sencilla dentro del alcance académico.

Una aplicación de producción con mayores requerimientos de seguridad podría utilizar cookies HttpOnly.

No implementar cookies HttpOnly ahora.

────────

92. AuthContext

Puede crearse:

```text
src/auth/AuthContext.jsx
```

Responsabilidades:

• usuario actual;
• token;
• login;
• register;
• logout;
• restauración de sesión.

Mantenerlo simple.

────────

93. ProtectedRoute

Crear:

```text
src/auth/ProtectedRoute.jsx
```

Comportamiento:

• no autenticado → /login;
• autenticado → mostrar página;
• mientras valida /auth/me → loading.

────────

94. Manejo global de 401

Crear helper central de API.

Si endpoint protegido responde:

```text
401
```

frontend debe:

1. borrar token;
2. limpiar usuario;
3. redirigir a /login.

Evitar loops.

────────

95. Logout

Cerrar sesión:

1. borrar token;
2. limpiar usuario;
3. redirigir a /login.

No crear endpoint /logout.

JWT será stateless.

────────

96. Layout autenticado

Crear layout con navegación.

Ejemplo:

```text
──────────────────────────────────────

Gestión de Restaurante

Dashboard
Mesas
Menú
Pedidos
Reservas

                     Hola, Felipe
                     Cerrar sesión

──────────────────────────────────────
```

Puede utilizar sidebar o header.

────────

97. Dashboard frontend

Ruta:

```text
/dashboard
```

Mostrar cards:

```text
Mesas disponibles
Mesas ocupadas
Mesas reservadas
Pedidos abiertos
Reservas de hoy
Ventas de hoy
Pedidos de hoy
```

Ejemplo:

```text
┌─────────────────┐
│ Mesas libres    │
│        8        │
└─────────────────┘

┌─────────────────┐
│ Ventas hoy      │
│   $430.500      │
└─────────────────┘
```

No agregar gráficos complejos.

────────

98. Página Mesas

Ruta:

```text
/mesas
```

Debe permitir:

• listar;
• crear;
• editar;
• eliminar;
• cambiar estado.

Mostrar:

```text
Número
Capacidad
Estado
Acciones
```

Estados visualmente distinguibles.

────────

99. Página Menú

Ruta:

```text
/menu
```

Debe incluir dos secciones:

```text
Categorías
Productos
```

Permitir CRUD de ambas.

────────

100. Visualización del menú

Ejemplo:

```text
MENÚ

Entradas
────────────────────────
Bruschetta          $8.500
Empanadas           $7.000

Principales
────────────────────────
Milanesa           $18.500
Hamburguesa        $15.000

Bebidas
────────────────────────
Coca-Cola           $3.500
Agua                $2.500
```

Mostrar disponibilidad.

────────

101. Formulario Producto

Campos:

```text
Nombre
Descripción
Precio
Categoría
Disponible
```

Precio:

```html
<input type="number" min="0.01" step="0.01" />
```

────────

102. Página Pedidos

Ruta:

```text
/pedidos
```

Debe permitir:

• listar pedidos;
• filtrar;
• crear pedido;
• seleccionar mesa;
• abrir detalle;
• agregar productos;
• modificar cantidades;
• eliminar items;
• visualizar subtotal;
• visualizar total;
• cambiar estado;
• cancelar;
• cerrar.

────────

103. Crear pedido frontend

Flujo:

```text
[ Nuevo pedido ]
       ↓
Seleccionar mesa disponible/reservada
       ↓
Crear pedido
       ↓
Abrir detalle
       ↓
Agregar productos
```

────────

104. Detalle visual del pedido

Ejemplo:

```text
Pedido #20
Mesa 4
Estado: Abierto

Producto              Cant.   Precio      Subtotal
---------------------------------------------------
Milanesa Napolitana     2     $18.500      $37.000
Coca-Cola               2      $3.500       $7.000

TOTAL                                      $44.000

[ Agregar producto ]

[ En preparación ]
[ Cancelar ]
```

────────

105. Página Reservas

Ruta:

```text
/reservas
```

Debe permitir:

• crear;
• editar;
• eliminar cuando corresponda;
• confirmar;
• cancelar;
• completar;
• filtrar.

Mostrar:

```text
Cliente
Personas
Fecha
Hora
Mesa
Estado
Acciones
```

────────

106. Formulario Reserva

Campos:

```text
Nombre del cliente
Cantidad de personas
Fecha
Hora
Mesa
Observaciones
```

Mostrar errores de conflicto claramente.

Ejemplo:

```text
La mesa seleccionada ya tiene una reserva que se superpone con ese horario.
```

────────

107. Página 404

Ruta:

```text
/*
```

Mostrar:

```text
404

Página no encontrada.

[ Volver al dashboard ]
```

────────

108. Estructura frontend

Crear aproximadamente:

```text
frontend/
│
├── src/
│   ├── api/
│   │   └── api.js
│   │
│   ├── auth/
│   │   ├── AuthContext.jsx
│   │   └── ProtectedRoute.jsx
│   │
│   ├── components/
│   │   ├── Layout.jsx
│   │   ├── Header.jsx
│   │   ├── Sidebar.jsx
│   │   ├── Loading.jsx
│   │   ├── ErrorMessage.jsx
│   │   ├── ConfirmModal.jsx
│   │   └── ...
│   │
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Mesas.jsx
│   │   ├── Menu.jsx
│   │   ├── Pedidos.jsx
│   │   ├── Reservas.jsx
│   │   └── NotFound.jsx
│   │
│   ├── utils/
│   │   ├── formatCurrency.js
│   │   ├── formatDate.js
│   │   └── validation.js
│   │
│   ├── App.jsx
│   ├── main.jsx
│   └── styles.css
│
├── tests/
│
├── package.json
├── vite.config.js
├── Dockerfile
├── nginx.conf
├── .dockerignore
└── index.html
```

No dividir componentes excesivamente.

────────

109. API frontend

Centralizar comunicación en:

```text
src/api/api.js
```

Crear helper similar a:

```text
apiFetch()
```

Responsabilidades:

• prefijo /api;
• JSON headers;
• Authorization Bearer;
• manejo de errores;
• manejo de 401.

────────

110. Funciones frontend

Crear funciones aproximadamente:

```text
register()
login()
getMe()

getDashboard()

getMesas()
createMesa()
updateMesa()
deleteMesa()
updateMesaEstado()

getCategorias()
createCategoria()
updateCategoria()
deleteCategoria()

getProductos()
createProducto()
updateProducto()
deleteProducto()
updateProductoDisponibilidad()

getPedidos()
getPedido()
createPedido()
updatePedidoEstado()
deletePedido()
addPedidoItem()
updatePedidoItem()
deletePedidoItem()

getReservas()
createReserva()
updateReserva()
deleteReserva()
updateReservaEstado()
```

────────

111. Vite proxy

En desarrollo:

```text
/api
```

debe redirigir a:

```text
http://localhost:8080
```

Frontend debe usar:

```javascript
fetch("/api/mesas");
```

NO:

```javascript
fetch("http://localhost:8080/api/mesas");
```

hardcodeado.

────────

112. Diseño

Interfaz completamente en español.

Diseño:

• limpio;
• moderno;
• profesional;
• sencillo;
• responsive;
• consistente.

Utilizar CSS propio.

No dedicar excesiva complejidad al diseño.

────────

113. Responsive

Debe ser razonablemente usable en:

• escritorio;
• tablet;
• móvil.

Las tablas pueden:

• tener scroll horizontal;
• transformarse en cards.

Elegir solución sencilla.

────────

114. Estados frontend

Todas las páginas deben contemplar:

```text
loading
error
empty
success
```

Ejemplos:

```text
Cargando pedidos...
```

```text
No hay pedidos abiertos.
```

```text
No existen reservas para la fecha seleccionada.
```

────────

115. Confirmaciones

Antes de eliminar:

```text
mesa
categoría
producto
reserva
```

mostrar confirmación.

Ejemplo:

```text
¿Seguro que desea eliminar este producto?
```

────────

116. Moneda

Mostrar precios en pesos argentinos.

Utilizar:

```javascript
Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
});
```

Ejemplo:

```text
$ 18.500,00
```

La base almacena números, no strings con $.

────────

117. Fechas frontend

API:

```text
YYYY-MM-DD
```

Frontend:

```text
DD/MM/YYYY
```

────────

118. Docker — arquitectura

Docker Compose debe tener únicamente tres servicios:

```text
db
backend
frontend
```

Arquitectura:

```text
Browser
   │
   ▼
Frontend
React + Nginx
   │
   ▼
Backend
Python + FastAPI
   │
   ▼
PostgreSQL
```

────────

119. Docker backend

Crear:

```text
backend/Dockerfile
```

Utilizar imagen oficial Python slim.

Preferentemente realizar construcción limpia y pequeña.

Debe:

1. definir working directory;
2. instalar dependencias;
3. copiar aplicación;
4. exponer 8080;
5. ejecutar Uvicorn.

Comando conceptual:

```text
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

No ejecutar con --reload dentro del container de producción.

────────

120. requirements.txt

Incluir solamente dependencias necesarias.

Aproximadamente:

```text
fastapi
uvicorn
sqlalchemy
psycopg / driver PostgreSQL compatible
pydantic
PyJWT
bcrypt
pytest
httpx
```

Agregar dependencias adicionales únicamente cuando sean realmente necesarias.

Utilizar versiones compatibles que puedan instalarse y cuyos tests pasen.

Evitar dependencias obsoletas.

────────

121. .dockerignore backend

Ignorar:

```text
__pycache__
*.pyc
.pytest_cache
.venv
venv
.env
tests/__pycache__
```

y archivos innecesarios para runtime.

────────

122. Docker frontend

Crear:

```text
frontend/Dockerfile
```

Multi-stage.

Etapa 1:

```text
Node
```

Proceso:

```text
npm ci
npm run build
```

Etapa final:

```text
Nginx
```

Copiar:

```text
dist/
```

────────

123. Nginx

Crear:

```text
frontend/nginx.conf
```

Debe:

1. servir React;
2. soportar SPA fallback;
3. hacer proxy /api/;
4. opcionalmente proxy /health.

Proxy:

```text
/api/
    ↓
http://backend:8080
```

SPA:

```text
try_files ... /index.html
```

────────

124. Docker Compose

Crear:

```text
docker-compose.yml
```

en raíz.

Servicios:

```text
db
backend
frontend
```

────────

125. PostgreSQL Docker

Utilizar imagen oficial estable PostgreSQL.

Configurar:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

Crear volumen:

```text
db_data
```

────────

126. Puertos Docker

Frontend:

```text
3000:80
```

Backend:

```text
8080:8080
```

PostgreSQL:

```text
5432:5432
```

────────

127. Healthcheck PostgreSQL

Configurar con:

```text
pg_isready
```

El backend debe depender de DB healthy.

────────

128. Healthcheck backend

Docker Compose debe consultar:

```text
GET /health
```

Backend debe estar healthy antes del frontend cuando sea razonable.

────────

129. Dependencias Compose

Orden lógico:

```text
db
│
│ healthy
▼
backend
│
│ healthy
▼
frontend
```

────────

130. Persistencia

Datos PostgreSQL deben sobrevivir:

```bash
docker compose down
```

Solamente borrarse con:

```bash
docker compose down -v
```

────────

131. Reconexión backend a DB

Además de depends_on, manejar conexión de forma razonable.

Si PostgreSQL todavía no responde, el backend puede:

• reintentar durante un período corto;
• o fallar claramente para que Docker lo reinicie.

No dejar errores silenciosos.

────────

132. CORS

Durante desarrollo permitir frontend local.

Configurar mediante:

```env
CORS_ORIGINS
```

No utilizar:

```text
*
```

junto con credenciales de forma innecesaria.

────────

133. Root .gitignore

Crear:

```text
.gitignore
```

Incluir:

```text
.env

backend/.venv/
backend/venv/
backend/__pycache__/
backend/**/__pycache__/
backend/.pytest_cache/
*.pyc

frontend/node_modules/
frontend/dist/

coverage/
*.log

.vscode/
.idea/

.DS_Store
```

No ignorar:

```text
.env.example
```

────────

134. Tests backend

Utilizar:

```text
pytest
```

Tests deben poder ejecutarse:

```bash
cd backend
pytest
```

Preferentemente también:

```bash
pytest -q
```

────────

135. Base de datos para tests

Los tests no deberían necesitar obligatoriamente Docker para ejecutarse.

Cuando sea práctico:

• utilizar una base SQLite temporal/in-memory mediante dependency override;
• mantener los modelos compatibles;
• utilizar fixtures independientes;
• limpiar datos entre tests.

Para comportamiento específico de PostgreSQL, puede existir una prueba de integración opcional, pero la suite principal debe ser rápida.

────────

136. Tests de autenticación

Crear como mínimo:

1. registro válido;
2. nombre inválido;
3. email inválido;
4. email duplicado;
5. password corta;
6. login válido;
7. login password incorrecta;
8. login email inexistente;
9. JWT válido;
10. JWT inválido;
11. JWT ausente;
12. /auth/me válido;
13. endpoint protegido sin token devuelve 401.

────────

137. Tests de ownership

Crear dos usuarios:

```text
Usuario A
Usuario B
```

Comprobar que B no puede:

• ver Mesa A;
• editar Mesa A;
• eliminar Mesa A;
• ver Producto A;
• crear pedido en Mesa A;
• agregar Producto A;
• ver Pedido A;
• editar Pedido A;
• ver Reserva A.

Debe responder:

```text
404
```

cuando corresponde.

────────

138. Tests de Mesas

Como mínimo:

• crear mesa válida;
• número inválido;
• capacidad cero;
• capacidad negativa;
• duplicar número para mismo usuario;
• mismo número permitido para otro usuario;
• estado inválido;
• eliminar mesa con pedido activo rechazado.

────────

139. Tests de Productos

Como mínimo:

• crear válido;
• precio cero;
• precio negativo;
• categoría inexistente;
• categoría de otro usuario;
• disponibilidad;
• filtros;
• producto histórico no puede eliminarse.

────────

140. Tests de Pedidos

Como mínimo:

1. crear pedido;
2. mesa inexistente;
3. mesa ajena;
4. segunda orden activa en misma mesa rechazada;
5. mesa pasa a ocupada;
6. agregar producto;
7. producto no disponible rechazado;
8. cantidad inválida;
9. subtotal correcto;
10. total correcto;
11. modificar cantidad recalcula;
12. eliminar item recalcula;
13. transición válida;
14. transición inválida;
15. cerrar pedido libera mesa;
16. cancelar libera mesa;
17. pedido cerrado no puede editarse;
18. precio histórico se conserva.

────────

141. Test obligatorio de precio histórico

Escenario:

1. crear producto a 1000;
2. crear pedido;
3. agregar producto;
4. verificar precio_unitario 1000;
5. modificar producto a 1500;
6. volver a obtener pedido;
7. verificar que el detalle continúa en 1000.

────────

142. Tests de Reservas

Como mínimo:

• crear válida;
• fecha pasada;
• personas > capacidad;
• mesa ajena;
• conflicto mismo horario;
• conflicto con superposición parcial;
• reserva sin conflicto;
• cancelada no bloquea horario;
• completada no bloquea horario;
• transición válida;
• transición inválida.

────────

143. Test de conflicto

Ejemplo:

```text
Reserva A:
20:00 → 22:00

Nueva:
21:00 → 23:00
```

Debe devolver:

```text
409
```

────────

144. Tests Dashboard

Comprobar:

• mesas por estado;
• pedidos abiertos;
• reservas de hoy;
• ventas de hoy;
• pedidos de hoy;
• pedidos cancelados no suman ventas;
• datos de otro usuario no afectan dashboard.

────────

145. Test health

Comprobar:

```text
GET /health
```

retorna:

```text
200
```

cuando DB está disponible.

────────

146. Frontend tests

Utilizar Vitest.

Ejecutar:

```bash
cd frontend
npm test -- --run
```

────────

147. Frontend — tests mínimos

Crear tests para:

• formato ARS;
• formato de fechas;
• validación login;
• validación register;
• passwords coinciden;
• helper Authorization;
• token guardado;
• logout elimina token;
• manejo básico de errores.

No crear suite E2E compleja.

────────

148. Build frontend

Debe funcionar:

```bash
cd frontend
npm install
npm test -- --run
npm run build
```

────────

149. Verificación backend

Debe poder ejecutarse:

```bash
cd backend
python -m compileall app
pytest
```

Sin errores.

────────

150. Ejecución local backend

Documentar:

```bash
cd backend
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

CMD:

```cmd
.venv\Scripts\activate
```

Después:

```bash
pip install -r requirements.txt
```

Ejecutar:

```bash
uvicorn app.main:app --reload --port 8080
```

────────

151. Ejecución local frontend

```bash
cd frontend
npm install
npm run dev
```

URL:

```text
http://localhost:5173
```

────────

152. URLs principales Docker

Frontend:

```text
http://localhost:3000
```

Backend:

```text
http://localhost:8080
```

Health:

```text
http://localhost:8080/health
```

Swagger:

```text
http://localhost:8080/docs
```

────────

153. README obligatorio

Crear:

```text
README.md
```

Debe estar en español.

Debe reflejar la implementación REAL.

No inventar:

• rutas;
• puertos;
• comandos;
• variables;
• endpoints;
• archivos.

Antes de terminar el README, revisar el repositorio final.

────────

154. README — principio obligatorio

El README debe empezar:

```text
# Sistema de Gestión de Restaurante

Descripción muy breve.

## Comandos rápidos
```

Comandos rápidos debe estar casi al comienzo.

────────

155. README — preparar .env

Mostrar:

Linux/macOS:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

CMD:

```cmd
copy .env.example .env
```

────────

156. README — levantar Docker

Incluir al principio:

```bash
docker compose up -d --build
```

Explicar:

• build;
• PostgreSQL;
• backend;
• frontend;
• segundo plano.

────────

157. README — iniciar sin rebuild

```bash
docker compose up -d
```

────────

158. README — estado

```bash
docker compose ps
```

────────

159. README — logs

Todos:

```bash
docker compose logs
```

Tiempo real:

```bash
docker compose logs -f
```

Backend:

```bash
docker compose logs -f backend
```

Frontend:

```bash
docker compose logs -f frontend
```

DB:

```bash
docker compose logs -f db
```

────────

160. README — detener

```bash
docker compose stop
```

Explicar que conserva containers y volumen.

────────

161. README — volver a iniciar

```bash
docker compose start
```

────────

162. README — reiniciar

```bash
docker compose restart
```

Ejemplos:

```bash
docker compose restart backend
```

```bash
docker compose restart frontend
```

────────

163. README — bajar

```bash
docker compose down
```

Explicar:

• elimina containers;
• elimina red Compose;
• NO elimina volumen PostgreSQL.

────────

164. README — borrar base

Mostrar:

```bash
docker compose down -v
```

Advertencia visible:

```text
⚠️ ATENCIÓN: este comando elimina también el volumen de PostgreSQL
y borra todos los datos almacenados.
```

Para recrear:

```bash
docker compose up -d --build
```

────────

165. README — rebuild

```bash
docker compose build
docker compose up -d
```

y también:

```bash
docker compose up -d --build
```

Explicar diferencia brevemente.

────────

166. README — tabla rápida

Crear tabla:

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

────────

167. README — entrar a PostgreSQL

Documentar comando real.

Conceptualmente:

```bash
docker compose exec db psql -U postgres -d restaurant_db
```

Dentro:

```text
\dt
```

```text
SELECT * FROM usuarios;
```

Adaptar nombres reales.

Salir:

```text
\q
```

────────

168. README — contenido completo

Después de comandos rápidos incluir:

```text
Descripción
Funcionalidades
Stack tecnológico
Arquitectura
Estructura del repositorio
Modelo de datos
Relaciones
Autenticación
JWT
Variables de entorno
Base de datos
Endpoints
Ejemplos API
Docker
Persistencia
Healthchecks
Ejecución local
Tests backend
Tests frontend
Build
Troubleshooting
Preparación para DevOps
Decisiones arquitectónicas
```

────────

169. README — arquitectura

Mostrar:

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

Explicar:

• arquitectura monolítica;
• backend único;
• DB única;
• sin Repository Pattern;
• sin microservicios.

────────

170. README — autenticación

Explicar:

```text
Register
   ↓
bcrypt password
   ↓
JWT
   ↓
localStorage
   ↓
Authorization: Bearer TOKEN
   ↓
Endpoints protegidos
```

Aclarar simplificación académica de localStorage.

────────

171. README — endpoints

Documentar TODOS los endpoints reales agrupados:

```text
Auth
Mesas
Categorías
Productos
Pedidos
Reservas
Dashboard
Health
```

────────

172. README — ejemplos curl

Agregar ejemplos cortos para:

Register

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Usuario Demo",
    "email": "demo@example.com",
    "password": "12345678"
  }'
```

Login

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "12345678"
  }'
```

No incluir token real.

────────

173. README — troubleshooting

Incluir:

Puerto ocupado

```text
address already in use
```

Revisar:

```bash
docker ps
```

Docker no refleja cambios

```bash
docker compose down
docker compose up -d --build
```

Reset de DB

```bash
docker compose down -v
docker compose up -d --build
```

Advertir pérdida de datos.

Backend no conecta a DB

```bash
docker compose logs backend
docker compose logs db
```

Ver logs completos

```bash
docker compose logs -f
```

JWT inválido

Explicar verificar:

• JWT_SECRET;
• token expirado;
• reiniciar sesión.

────────

174. Estructura final del repositorio

Aproximadamente:

```text
restaurant-management/
│
├── SPEC.md
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   │
│   │   ├── auth/
│   │   │   ├── jwt.py
│   │   │   └── password.py
│   │   │
│   │   ├── models/
│   │   │   ├── usuario.py
│   │   │   ├── mesa.py
│   │   │   ├── categoria.py
│   │   │   ├── producto.py
│   │   │   ├── pedido.py
│   │   │   ├── detalle_pedido.py
│   │   │   └── reserva.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── mesa.py
│   │   │   ├── categoria.py
│   │   │   ├── producto.py
│   │   │   ├── pedido.py
│   │   │   └── reserva.py
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── mesas.py
│   │   │   ├── categorias.py
│   │   │   ├── productos.py
│   │   │   ├── pedidos.py
│   │   │   ├── reservas.py
│   │   │   ├── dashboard.py
│   │   │   └── health.py
│   │   │
│   │   └── utils/
│   │       ├── orders.py
│   │       └── reservations.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
└── frontend/
    ├── src/
    │   ├── api/
    │   ├── auth/
    │   ├── components/
    │   ├── pages/
    │   ├── utils/
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── styles.css
    │
    ├── tests/
    ├── package.json
    ├── vite.config.js
    ├── Dockerfile
    ├── nginx.conf
    ├── .dockerignore
    └── index.html
```

Adaptar si técnicamente necesario, manteniendo simplicidad.

────────

175. DevOps — preparación

El proyecto debe quedar preparado para posteriormente incorporar:

```text
.github/workflows/ci.yml
```

y trabajar:

• feature branches;
• Pull Requests;
• protección de main;
• tests automáticos;
• builds automáticos;
• Docker images;
• Docker Registry;
• Continuous Integration;
• Continuous Delivery;
• Continuous Deployment.

────────

176. NO implementar CI/CD todavía

No crear:

```text
.github/workflows/ci.yml
.github/workflows/cd.yml
```

No configurar:

• GitHub Actions;
• Docker Hub;
• GHCR;
• deployments;
• cloud;
• Kubernetes;
• Terraform.

Esto se realizará posteriormente durante la materia.

────────

177. Principios de código

Priorizar:

```text
Simple > Complejo

Legible > Abstracto

Explícito > Mágico

Funcional > Sobrearquitecturado
```

Evitar:

• clases innecesarias;
• abstracciones sin utilidad;
• patrones usados solo por moda;
• lógica duplicada evidente.

Pero no agregar cinco capas para evitar pocas líneas repetidas.

────────

178. Seguridad mínima obligatoria

Implementar:

• bcrypt;
• JWT firmado;
• expiración;
• secretos mediante entorno;
• validación de inputs;
• ownership;
• SQLAlchemy parametrizado;
• no devolver password hash;
• no loguear passwords;
• no loguear tokens completos;
• errores sin stack trace al cliente;
• email normalizado;
• 401 ante token inválido;
• 404 ante recursos ajenos.

────────

179. No implementar

Queda explícitamente fuera de alcance:

• roles;
• empleados;
• mozos;
• cocineros;
• administrador;
• permisos;
• recuperación de contraseña;
• verificación por email;
• OAuth;
• Google Login;
• GitHub Login;
• MFA;
• refresh tokens;
• inventario de ingredientes;
• proveedores;
• recetas;
• stock de materias primas;
• facturación fiscal;
• ARCA/AFIP;
• Mercado Pago;
• pagos online;
• delivery;
• take-away;
• impresoras de comandas;
• cocina en tiempo real;
• WebSockets;
• notificaciones push;
• integración con WhatsApp;
• integración con APIs externas;
• BI avanzado.

────────

180. Criterios de aceptación — Auth

☐ Register funciona.
☐ Login funciona.
☐ Email duplicado rechazado.
☐ Password hasheada.
☐ Hash nunca sale por JSON.
☐ JWT tiene expiración.
☐ JWT inválido devuelve 401.
☐ /auth/me funciona.
☐ Logout frontend funciona.
☐ Recargar página mantiene sesión válida.
☐ Token expirado redirige a login.

────────

181. Criterios — Mesas

☐ CRUD funciona.
☐ Número único por usuario.
☐ Capacidad validada.
☐ Estados válidos.
☐ Ownership funciona.
☐ Pedido activo ocupa mesa.
☐ Cerrar/cancelar libera mesa.
☐ Mesa con actividad no puede borrarse incorrectamente.

────────

182. Criterios — Menú

☐ Categorías iniciales.
☐ CRUD categorías.
☐ CRUD productos.
☐ Precio Decimal/Numeric.
☐ Disponibilidad.
☐ Filtros.
☐ Producto utilizado históricamente no se elimina.

────────

183. Criterios — Pedidos

☐ Crear pedido.
☐ Una orden activa por mesa.
☐ Agregar items.
☐ Modificar cantidades.
☐ Eliminar items.
☐ Precio unitario se copia al detalle.
☐ Subtotal calculado backend.
☐ Total calculado backend.
☐ Precio histórico preservado.
☐ Estados válidos.
☐ Transiciones válidas.
☐ Cerrar funciona.
☐ Cancelar funciona.
☐ Mesa se actualiza correctamente.
☐ Ownership funciona.

────────

184. Criterios — Reservas

☐ Crear reserva.
☐ Editar.
☐ Filtrar.
☐ Confirmar.
☐ Cancelar.
☐ Completar.
☐ Personas <= capacidad.
☐ Fecha futura.
☐ Conflictos detectados.
☐ Ventana 120 minutos.
☐ Ownership funciona.

────────

185. Criterios — Dashboard

☐ Mesas disponibles.
☐ Mesas ocupadas.
☐ Mesas reservadas.
☐ Pedidos abiertos.
☐ Reservas hoy.
☐ Ventas hoy.
☐ Pedidos hoy.
☐ Datos exclusivos del usuario autenticado.

────────

186. Criterios — Frontend

☐ /login.
☐ /register.
☐ /dashboard.
☐ /mesas.
☐ /menu.
☐ /pedidos.
☐ /reservas.
☐ 404.
☐ ProtectedRoute.
☐ React Router.
☐ JWT enviado.
☐ 401 manejado.
☐ Responsive.
☐ Loading.
☐ Error.
☐ Empty state.
☐ Confirmaciones.
☐ Tests pasan.
☐ Build pasa.

────────

187. Criterios — Docker

☐ Backend Dockerfile.
☐ Frontend Dockerfile multi-stage.
☐ Nginx.
☐ PostgreSQL.
☐ Docker Compose.
☐ Solo 3 servicios.
☐ Volumen persistente.
☐ Healthcheck DB.
☐ Healthcheck backend.
☐ Frontend → backend funciona.
☐ Backend → PostgreSQL funciona.
☐ .env funciona.

────────

188. Verificación final — backend

Ejecutar:

```bash
cd backend
```

Crear entorno si hace falta.

Instalar:

```bash
pip install -r requirements.txt
```

Comprobar sintaxis/imports:

```bash
python -m compileall app
```

Tests:

```bash
pytest
```

Corregir cualquier error.

────────

189. Verificación final — frontend

Ejecutar:

```bash
cd frontend
npm install
npm test -- --run
npm run build
```

Todo debe finalizar correctamente.

Corregir errores antes de continuar.

────────

190. Verificación final — Docker

Desde raíz:

```bash
docker compose down
docker compose up -d --build
```

Verificar:

```bash
docker compose ps
```

Todos los servicios deben estar funcionando/healthy cuando corresponda.

────────

191. Verificar health

Comprobar:

```text
GET http://localhost:8080/health
```

Debe devolver:

```text
200
```

────────

192. Prueba funcional integral obligatoria

Realizar la siguiente prueba si el entorno permite ejecutar Docker.

Paso 1

Registrar:

```text
Usuario A
```

Paso 2

Registrar:

```text
Usuario B
```

Paso 3

Login Usuario A.

Obtener Token A.

Paso 4

Crear:

```text
Mesa 1
capacidad 4
```

con Token A.

Paso 5

Comprobar categorías iniciales.

Paso 6

Crear producto:

```text
Milanesa Napolitana
precio 18500
```

Paso 7

Crear:

```text
Pedido para Mesa 1
```

Paso 8

Agregar:

```text
2 × Milanesa Napolitana
```

Paso 9

Verificar:

```text
precioUnitario = 18500
subtotal = 37000
total = 37000
```

Paso 10

Modificar producto a:

```text
20000
```

Paso 11

Volver a consultar pedido.

Debe continuar:

```text
precioUnitario = 18500
subtotal = 37000
```

Paso 12

Cambiar pedido:

```text
abierto
→ en_preparacion
→ listo
→ entregado
→ cerrado
```

Paso 13

Verificar que Mesa 1 quede:

```text
disponible
```

Paso 14

Crear reserva futura para Mesa 1 a:

```text
20:00
```

Paso 15

Intentar nueva reserva misma mesa:

```text
21:00
```

Debe devolver:

```text
409 Conflict
```

Paso 16

Login Usuario B.

Paso 17

Con Token B comprobar que no pueda acceder a:

```text
Mesa de A
Producto de A
Pedido de A
Reserva de A
```

Paso 18

Comprobar dashboard A.

Debe mostrar únicamente datos A.

Paso 19

Abrir:

```text
http://localhost:3000
```

Paso 20

Probar visualmente:

• login;
• dashboard;
• mesas;
• menú;
• pedidos;
• reservas;
• logout.

────────

193. Si Docker no está disponible

No inventar resultados.

Indicar claramente:

```text
Docker no estuvo disponible en el entorno de ejecución.
```

Aun así:

• revisar Dockerfiles;
• revisar Compose;
• revisar Nginx;
• ejecutar tests backend;
• ejecutar tests frontend;
• ejecutar build frontend.

────────

194. README final

Después de terminar la implementación:

1. revisar estructura real;
2. revisar rutas reales;
3. revisar variables reales;
4. revisar comandos reales;
5. revisar Docker Compose;
6. actualizar README para reflejar exactamente el resultado final.

No copiar documentación incorrecta desde este SPEC si la implementación final requirió un pequeño ajuste técnico.

────────

195. Resultado final esperado

La aplicación final debe tener esta arquitectura:

```text
                    Usuario
                       │
                       ▼
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

Funcionalidades:

```text
Autenticación
├── Register
├── Login
├── JWT
├── Logout
└── Sesión persistente

Restaurante
├── Dashboard
├── Mesas
├── Menú
│   ├── Categorías
│   └── Productos
├── Pedidos
│   └── Detalles
└── Reservas
```

Infraestructura:

```text
Docker Compose

db
backend
frontend
```

────────

196. Resumen obligatorio de Codex al finalizar

Después de implementar y verificar el proyecto, responder con un resumen corto que indique:

Archivos

• principales archivos creados;
• estructura final.

Backend

• tecnologías;
• modelos;
• endpoints.

Frontend

• páginas;
• componentes principales.

Seguridad

• JWT;
• bcrypt;
• ownership.

Docker

• servicios;
• puertos;
• healthchecks.

Tests

Indicar resultado real de:

```text
pytest
npm test -- --run
```

Builds

Indicar resultado real de:

```text
python -m compileall app
npm run build
```

Docker

Indicar si:

```text
docker compose up -d --build
```

pudo ejecutarse correctamente.

Prueba integral

Indicar qué escenarios fueron comprobados.

Limitaciones

Si alguna parte no pudo ejecutarse por limitaciones del entorno, decirlo explícitamente.

────────

197. Instrucción final

Implementar toda la aplicación descrita.

No omitir funcionalidades de esta especificación.

No agregar arquitectura distribuida.

No agregar Repository Pattern.

No agregar microservicios.

No agregar CI/CD todavía.

No detenerse solamente después de generar archivos.

Ejecutar pruebas y builds.

Corregir errores encontrados.

El resultado debe ser una aplicación full-stack funcional, legible, dockerizada, testeable y adecuada para aplicar posteriormente un proceso DevOps en Ingeniería de Software III.
