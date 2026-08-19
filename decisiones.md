# Decisiones — TP1

## 1. Por qué Git no pudo resolver el conflicto solo

Git fusiona automáticamente cuando dos ramas tocan partes distintas del archivo, pero acá las ramas
`feature/titulo-a` y `feature/titulo-b` modificaron **la misma línea** del `README.md` (el título),
cada una partiendo de `main` sin saber de la otra. Frente a dos cambios incompatibles sobre la misma
línea, Git no tiene forma de decidir cuál es "la versión correcta" — esa es una decisión de
contenido, no algo que se pueda inferir mecánicamente. Por eso delega en mí: marca el archivo con los
marcadores (`<<<<<<<`, `=======`, `>>>>>>>`) y espera que yo elija qué queda.

Para que este conflicto nunca hubiera aparecido, alguna de estas condiciones tendría que haberse
dado: que la rama B se creara *después* de mergear la rama A (partiendo ya del título actualizado,
en vez de partir las dos del mismo punto de `main`), o que directamente no se tocara la misma línea
desde dos ramas en paralelo. En un equipo real, esto se evita con ramas cortas e integración
frecuente: cuanto más tiempo vive una rama sin traer los cambios de `main`, más probable es que
choque con algo que se integró mientras tanto.

## 2. Problemas encontrados y cómo los resolví

- **`gh` no estaba instalado.** Al intentar `gh pr create` la terminal devolvió `'gh' is not
  recognized as an internal or external command`. Se resolvió instalando GitHub CLI con
  `winget install --id GitHub.cli -e`, abriendo una terminal nueva (para que tomara el `PATH`
  actualizado) y autenticando con `gh auth login`.

- **`gh pr create` sin flags entra en modo interactivo.** La primera vez que lo corrí sin
  `--title`/`--body`/`--base` quedó esperando respuestas paso a paso dentro de la misma terminal,
  lo cual no es manejable desde un asistente. Se resolvió cancelando con `Ctrl+C` y volviendo a
  correr el comando con todas las opciones explícitas.

- **El ejercicio de conflicto ya estaba a mitad de hacer de una sesión anterior.** Al retomarlo me
  encontré con que el PR #2 (versión A) ya estaba mergeado y el PR #3 (versión B) ya existía abierto
  desde el día anterior — y encima había creado, sin darme cuenta, un PR #4 duplicado con el mismo
  cambio de la versión A sobre una rama nueva. Antes de seguir, usé `gh pr list --state all` y
  `gh pr view <n> --json mergeable,mergeStateStatus` para reconstruir el estado real en GitHub en vez
  de asumir en qué paso estaba. Con eso confirmé que el PR #3 ya estaba en conflicto genuino
  (`mergeable: CONFLICTING`) — que es justo la evidencia #2 — y cerré el PR #4 por redundante
  (`gh pr close 4 --delete-branch`) para no ensuciar el historial con dos PRs proponiendo lo mismo.

- **Un editor externo (VS Code) chocó con un `git switch`.** Al cambiar de rama con el README
  abierto en el editor, un intento de guardar tiró *"The content of the file is newer"* porque el
  archivo en disco había cambiado por debajo del editor. Se resolvió revisando con `git status` y
  `git log`/`git reflog` en qué rama y con qué contenido estaba parado realmente antes de reintentar
  la edición.

## 3. Declaración de uso de IA

Usé Claude (Anthropic) como apoyo puntual: para recordar la sintaxis exacta de algunos comandos de
`git`/`gh` y para diagnosticar dos o tres errores de herramientas (que faltaba instalar `gh`, y un
conflicto de guardado en el editor). El resto —seguir la guía, entender el modelo de ramas y
conflictos de Git, decidir qué versión del título quedaba, mergear los PRs y publicar la release—
lo hice yo, corriendo cada comando en mi propia terminal y revisando el resultado antes de seguir.

Cómo lo verifiqué: no copié ningún comando sin entender qué hacía primero, y contrasté lo que
proponía contra la guía del TP y la salida real de mi terminal.

## TP2 — Contenedores

### Qué app elegí y por qué

Elegí mi propio "Sistema de Gestión de Restaurante": backend en Python (FastAPI) + frontend en React
(Vite) + PostgreSQL. Contra los criterios de la guía:

- **Buildea y corre localmente sin magia**: sí, ya lo tenía funcionando con `docker compose up`
  antes de empezar este TP.
- **Tiene tests**: el backend trae `pytest` (auth, mesas/productos, pedidos, reservas) y el frontend
  tiene tests con Vitest — base para el TP5.
- **La entiendo lo suficiente para modificarla**: la escribí yo, así que puedo tocar cualquier parte
  en la defensa oral o en el Integrador.
- **Tamaño**: alcanza con CRUD + un puñado de pantallas (mesas, menú, pedidos, reservas) — no le
  agregué nada de más.

### Decisiones de contenerización

- **Imágenes base**: `python:3.13-slim` para el backend (liviana, sin herramientas de más),
  `node:22-alpine` solo para la etapa de *build* del frontend, y `nginx:1.27-alpine` para servirlo en
  producción.
- **Multi-stage en los dos**: el backend separa una etapa que instala las dependencias con `pip
  install --prefix=/install` de una etapa final que solo copia ese directorio y el código — así el
  cache de `pip` no viaja a la imagen final. El frontend separa el build de Vite (que necesita todo
  el toolchain de Node) de la imagen final, que es nginx sirviendo estáticos.
- **Qué persiste y qué no**: solo los datos de PostgreSQL, en el volumen nombrado `db_data`. Los
  contenedores de `backend` y `frontend` son descartables — se pueden recrear sin perder nada, porque
  no guardan estado propio.
- **Comunicación por nombre, no por IP**: el backend se conecta a `Host=db`, el nombre del servicio
  en la red de compose; el frontend llama a `/api/...` con ruta relativa y es **nginx** el que la
  reenvía a `http://backend:8080` puertas adentro — así el mismo build del frontend sirve en
  cualquier entorno, sin CORS que configurar.
- **Puerto de la base en el host**: mapeado a `5433` (en vez del estándar `5432`) porque en mi
  máquina ya había otro PostgreSQL usando ese puerto. Puertas adentro de la red de compose el puerto
  sigue siendo el interno de Postgres (`5432`), así que no afecta a cómo se conectan `backend` y
  `db` entre sí.

### Problemas encontrados y cómo los resolví

- **El `backend/Dockerfile` no era multi-stage.** Tenía una sola etapa que instalaba dependencias y
  copiaba el código en la misma imagen final. Lo separé en una etapa `build` (solo instala con `pip
  install --prefix=/install`) y una etapa final que copia `/install` y el código — reconstruí y
  confirmé que el backend seguía respondiendo `{"status":"healthy"}` igual que antes.
- **Docker Desktop estaba apagado.** `docker ps` devolvía `Cannot connect to the Docker daemon`
  aunque `docker --version` sí contestaba (eso solo prueba que el binario está instalado, no que el
  motor está corriendo). Se resolvió abriendo Docker Desktop y esperando a que levantara.
- **ghcr.io exige un token clásico, no *fine-grained*.** Generé el Personal Access Token yo mismo
  desde GitHub (con el scope `write:packages`) y lo pegué directamente en el `docker login` de mi
  propia terminal — nunca se lo compartí a la IA ni quedó en ningún comando registrado.
- **Un `docker push` se cortó a mitad de camino** (bloqueado por el clasificador de permisos de la
  herramienta que estaba usando). Se resolvió simplemente reintentando el mismo comando.

### Sobre la arquitectura de las imágenes publicadas

Las imágenes se construyeron en mi máquina Windows (arquitectura Intel/AMD64), así que sirven para
esa arquitectura. Si alguien con un procesador ARM (por ejemplo, una Mac moderna) intenta correrlas,
va a ver `no matching manifest`. No lo resolví en este TP —queda para cuando aparezca `docker
buildx` en el TP7— pero lo dejo anotado acá porque es exactamente el tipo de detalle que se pregunta
en la defensa.

### Declaración de uso de IA (TP2)

Usé Claude como apoyo para: recordar la sintaxis de comandos de Docker/Compose, detectar que el
Dockerfile del backend no era multi-stage, y automatizar la ejecución de la guía (levantar el
stack, probar persistencia, comparar tamaños, tagear y publicar las imágenes) mientras yo confirmaba
los pasos sensibles. Generar el Personal Access Token de GitHub y pegarlo en `docker login` lo hice
yo mismo, en mi propia terminal, sin compartirlo. Verifiqué cada resultado con salidas reales
(`docker compose ps`, `curl` a `/health` y a la API, `docker images`, la página de *Packages* de
GitHub) en vez de asumir que algo había funcionado porque el comando no dio error.
