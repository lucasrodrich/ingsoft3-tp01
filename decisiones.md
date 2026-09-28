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

## TP3 — Planificación y trazabilidad

### 1. Duración del sprint

Elegí **2 semanas**, que es la duración que trae por defecto el campo *Iteration* de GitHub
Projects. La cátedra todavía no había publicado la fecha de entrega de este TP en el momento de
armarlo, así que no había un calendario concreto contra el cual ajustar el número; frente a eso,
dejar el default es razonable: dos semanas alcanzan para que una historia con un par de tareas
tenga margen real de principio a fin sin que el sprint quede vacío de contenido, que es el riesgo
de un ciclo demasiado corto para este volumen de trabajo.

### 2. Límite de trabajo en progreso

Elegí **2**, siguiendo la regla de arranque de la guía (cantidad de personas + 1). Trabajando
solo, eso da 1 + 1 = 2: el "+1" es la válvula para poder avanzar en una segunda cosa mientras la
primera queda esperando algo externo (por ejemplo, una respuesta o una revisión) sin que esa espera
bloquee todo el flujo. Si nunca llego a tocar el límite, es señal de que está puesto demasiado alto
para mi volumen real de trabajo en paralelo.

### 3. Diagnóstico de la historia mal escrita

La historia *"Como desarrollador quiero crear la tabla usuarios"* está mal escrita por dos motivos:
le falta el **"para"** (el beneficio que justificaría hacerla), y en realidad es una **tarea
disfrazada de historia** — "crear una tabla" es un paso técnico interno, no algo que un desarrollador
quiera como capacidad de valor observable por alguien. La reescribiría subiendo un nivel de
abstracción, por ejemplo: *"Como usuario quiero poder iniciar sesión en el sistema, para acceder solo
a mi propia información"* — y "crear la tabla usuarios" pasaría a ser una de sus tareas técnicas, no
la historia en sí.

### 4. Problemas encontrados y cómo los resolví

- **El token de `gh` no tenía el scope `project`.** Al intentar `gh project list` tiró un error de
  permisos faltantes. Se resolvió con `gh auth refresh -s project`, confirmando en el navegador el
  permiso nuevo.
- **Continuación de línea con `\` no funciona en PowerShell.** Copié comandos multilínea pensados
  para bash (con `\` al final de cada línea) y PowerShell los interpretó como comandos sueltos,
  tirando errores de `Unexpected token`. Se resolvió escribiendo cada comando en una sola línea, o
  usando here-strings (`@' ... '@`) para los bodies con saltos de línea, y agrupando todo en un
  script `.ps1` para evitar que la terminal partiera un pegado largo en líneas sueltas.
- **Comillas dobles embebidas rompieron un `gh issue create`.** El body del issue del bug tenía
  `"docker compose up"` entre comillas dentro del texto; al pasarlo como argumento a `gh.exe`,
  PowerShell interpretó esas comillas internas como delimitadoras y cortó el argumento a la mitad
  (`unknown arguments ["compose" "up y abrir..."]`). Se resolvió escribiendo el body a un archivo
  (`bug-body.md`) y usando `--body-file` en vez de `--body`, evitando el problema de quoting por
  completo.
- **Confusión inicial sobre qué hace `Closes #N`.** Al principio pensé que alcanzaba con que el
  commit describiera bien el trabajo hecho para que quedara relacionado con el issue. En realidad
  es un mecanismo puramente textual: GitHub busca la palabra clave literal (`Closes`/`Fixes`/
  `Resolves` + `#numero`) en la descripción del PR, sin comparar significado ni contenido. Un commit
  bien nombrado es buena práctica pero no reemplaza esa palabra clave exacta.

### 5. Declaración de uso de IA (TP3)

Usé Claude como apoyo para: automatizar la creación de los issues (épica, historia, 2 tareas, bug)
y su vinculación como sub-issues vía `gh issue edit --add-sub-issue`, diagnosticar los errores de
sintaxis de PowerShell y de quoting que fueron apareciendo, y armar el workflow mínimo
`.github/workflows/ci.yml` del PR de trazabilidad. Las decisiones de fondo —la duración del sprint,
el número del límite de WIP, y la creación de la vista Board y el campo Iteration en la interfaz
web de GitHub Projects— las hice yo, verificando cada paso contra la salida real de mis propios
comandos (`gh issue list`, `gh project item-list`, `gh api .../sub_issues`) y contra lo que veía en
el tablero, en vez de asumir que algo había quedado bien solo porque el comando no tiró error.

## TP4 — CI: Pipelines as Code

### 1. Qué dispara el pipeline, y por qué esos dos triggers

El workflow corre en dos eventos: `pull_request` hacia `main` y `push` hacia `main`. No son
redundantes, cada uno cumple un rol distinto:

- **`pull_request`** es el que hace el trabajo real: corre **antes** de que el cambio se mezcle con
  `main`, sobre el resultado propuesto de la mezcla. Es el que alimenta al gate (§5) — sin esto no
  habría nada que exigir como requisito de merge.
- **`push`** corre **después** de cada merge, cuando el commit ya está en `main`. No bloquea nada
  (ya es tarde para eso), pero cumple dos funciones: es la corrida que le da estado al badge del
  README (que siempre lee el último resultado de `main`), y es la que deja el cache disponible "para
  todos" — cualquier PR nuevo que parta de `main` puede reusar esas capas desde su primera corrida,
  en vez de arrancar de cero.

Puede haber CI sin este pipeline: la práctica de "integrar seguido y verificar cada integración" no
depende de una herramienta puntual — podría hacerse (mal) a mano, corriendo los tests localmente
antes de cada push. Y puede haber un pipeline sin que eso sea CI: si nadie lo revisa, si `main` queda
en rojo días enteros sin que se lo trate como prioridad, o si el pipeline no es un requisito real de
merge, tener el YAML no alcanza — es la práctica cultural (§2.1 de la guía) la que lo convierte en
CI de verdad, no el archivo en sí.

### 2. Estructura del pipeline: por qué dos jobs en paralelo

El backend y el frontend tienen cada uno su propio `Dockerfile` desde el TP2 (imágenes base distintas,
etapas distintas, nada que compartan a nivel de build). Por eso el workflow define dos jobs —
`build-backend` y `build-frontend`— en vez de uno solo: cada uno construye una imagen independiente
con `docker/build-push-action`, apuntando a `context: ./backend` y `context: ./frontend`
respectivamente. Al no declarar `needs:` entre ellos, GitHub Actions los corre en paralelo, cada uno
en su propia máquina Ubuntu limpia, sin compartir filesystem ni memoria entre sí. Tiene sentido:
un error en el backend no tiene por qué frenar la verificación del frontend, y viceversa — son dos
piezas independientes que solo comparten repositorio.

El `id` de cada job (`build-backend`, `build-frontend`) no es cosmético: es el nombre exacto del
*check* que después exigí como obligatorio en la protección de rama (§5). Si renombrara el job
después de configurar el gate, quedaría exigiendo un check que ya no existe y bloquearía todo.

**Qué produce el pipeline y dónde queda**: nada que se conserve. Las dos imágenes (`backend:ci`,
`frontend:ci`) nacen y mueren dentro del runner — `push: false` en las dos, a propósito: este TP
verifica que la imagen se pueda construir, no la publica en ningún lado. El lugar de una imagen
publicada es un registry (como hice a mano en el TP2 con GHCR), y automatizar esa publicación queda
para más adelante. La salida real de esta corrida es otra cosa: el check en verde que habilita el
merge.

### 3. Qué cachea el pipeline

Lo que se cachea son las **capas de Docker** de cada imagen — no el código, no dependencias sueltas,
sino literalmente las capas que produce `docker build` (una por cada instrucción `RUN`/`COPY`/`ADD`
del Dockerfile). Se guardan en el almacén de cache de GitHub Actions (`cache-from`/`cache-to:
type=gha`), usando el constructor *buildx* (`docker/setup-buildx-action`) en vez del Docker de
fábrica, porque el de fábrica guarda las capas solo en el disco de la máquina que las construyó —
y esa máquina se destruye al terminar el job, así que ahí no sirven de nada.

Cada job usa un `scope` distinto (`scope=backend` / `scope=frontend`). Es la parte más fácil de
pasar por alto: sin `scope`, los dos jobs comparten el mismo estante de cache por default y se pisan
entre sí — el último en terminar sobreescribe lo que dejó el otro, y el síntoma es que un job
muestra `CACHED` y el otro no, y cuál cambia de una corrida a la siguiente sin razón aparente.

Confirmé el cache funcionando con dos corridas seguidas sobre el mismo PR (esperando a que la
primera terminara del todo antes de disparar la segunda con un commit vacío): en la segunda corrida,
el log de `build-backend` mostró `CACHED` en las capas de instalación de dependencias
(`pip install --prefix=/install -r requirements.txt`), que no habían cambiado entre una corrida y
la otra.

**Qué pasa si el cache desaparece**: nada catastrófico, solo se pierde la optimización. GitHub puede
desalojarlo en cualquier momento (tiene límite de tamaño y política de expiración propia), así que
el pipeline tiene que poder reconstruir todo desde cero sin el cache — más lento, pero funcional. Si
un build fallara *sin* cache, no sería un problema de cache: sería una dependencia escondida que
el cache estaba tapando, y eso sí sería un bug real a corregir.

### 4. Por qué el pipeline construye con el Dockerfile en vez de compilar por su cuenta

El workflow no tiene ninguna línea de `pip install` ni `npm run build` sueltas — delega el build
entero a `docker/build-push-action`, que usa el `Dockerfile` de cada carpeta. La razón es evitar
tener **dos definiciones de build** que puedan divergir: si el pipeline compilara "a su manera" con
comandos propios, podría estar verificando una construcción distinta de la que después efectivamente
se empaqueta y se despliega — y un día podrían dar resultados distintos sin que nadie se diera cuenta
hasta que fuera tarde. Usando el mismo Dockerfile que ya usé a mano en el TP2, lo que verifica el
pipeline es exactamente lo que se va a desplegar.

### 5. El gate: qué exige `main` hoy para aceptar un merge

Cierra el círculo con el TP1: allá dejé `main` protegida para que nada entrara sin pasar por un PR;
acá le agrego la verificación automática de ese PR. Hoy, para mergear algo a `main`, se tienen que
cumplir **dos condiciones** a la vez (`Settings → Branches`, sobre la misma regla del TP1):

- **`required_status_checks`, con `contexts: ["build-backend", "build-frontend"]`**: los dos jobs
  tienen que haber terminado en verde sobre el commit que se quiere mergear. Un solo check en rojo
  ya bloquea el botón de merge, no hace falta que fallen los dos.
- **`strict: true`** ("Require branches to be up to date before merging"): no alcanza con que el
  check haya pasado alguna vez — la rama tiene que estar mezclada con la versión **actual** de
  `main` antes de dejar mergear. Por eso, cuando mergeé el PR de la demo rota mientras tenía otro PR
  abierto en paralelo, ese otro PR pasó a mostrar "Update branch": su check verde había quedado
  viejo, sacado contra un `main` que ya no existía.

Las revisiones humanas (`required_approving_review_count`) siguen en **0**, igual que en el TP1: como
trabajo solo, GitHub nunca me deja aprobar mi propio PR, así que un número mayor a 0 me dejaría sin
poder mergear nunca. Lo que bloquea el merge en este TP no es una aprobación de otra persona — es el
pipeline en verde. La revisión humana la sigo haciendo igual, leyendo mi propio diff en "Files
changed" antes de cada merge (regla cultural §2.1 de la guía), aunque la plataforma no me la exija.

### 6. Problemas encontrados y cómo los resolví

- **Un YAML mal pegado quedó con `jobs:` y `build-backend:` duplicados.** Al reemplazar el esqueleto
  del TP3 por el workflow completo, el editor guardó una versión con un bloque roto en el medio
  (una repetición parcial de `on:`/`jobs:` que no tenía sentido ahí). El primer síntoma fue que
  `git add` + `git commit` no detectaban cambios reales, porque en un intento anterior había hecho
  `commit --amend` sin haber guardado la corrección en el editor primero. Se resolvió revisando con
  `git diff` **antes** de cada commit —no asumiendo que lo que veía en el editor ya estaba guardado—
  hasta confirmar que el archivo en disco era exactamente el que quería commitear.
- **`docker build ./backend` fallaba con un error de conexión al daemon.** No tenía nada que ver con
  la dependencia rota que había agregado a propósito: era que Docker Desktop estaba apagado en ese
  momento (el mismo tipo de problema que ya había documentado en el TP2). Se resolvió levantando
  Docker Desktop y esperando a que el motor terminara de iniciar antes de reintentar.
- **El editor chocó de nuevo con un cambio de rama** (mismo problema que en el TP1, esta vez con
  `README.md`): tenía el archivo abierto con una versión vieja en memoria mientras cambiaba entre
  `main` y una rama nueva, y al guardar tiró *"The content of the file is newer"*. Se resolvió
  cerrando la pestaña sin guardar, reabriendo el archivo desde disco, y recién ahí editando de
  nuevo — en vez de forzar el guardado y arriesgarme a pisar contenido que no había visto.
- **"Files changed" del PR de la demo aparecía vacío después de arreglar el error.** Al principio
  pareció que el fix no se había subido. En realidad tenía sentido: rompí y arreglé la misma línea
  de `requirements.txt` dentro del mismo PR, así que el diff neto entre `main` y la rama terminó
  siendo cero (el archivo volvió a quedar igual que al principio). La evidencia de la rotura y el
  arreglo no estaba en "Files changed" —que compara solo el estado final— sino en la pestaña
  **Commits** del PR (los dos commits por separado) y en el historial de corridas de Actions (una
  en rojo, la siguiente en verde).

### 7. Declaración de uso de IA (TP4)

Usé Claude como apoyo para: armar el YAML del workflow (jobs, triggers, cache con `scope` separado),
explicarme línea por línea qué hace cada parte antes de escribirla, y diagnosticar en el momento los
problemas que fueron apareciendo (el YAML duplicado, Docker Desktop apagado, el choque del editor
con `git checkout`, y la confusión del diff vacío en el PR de la demo). Las decisiones de fondo —qué
romper para demostrar el gate, cuándo mergear cada PR, en qué orden dejar los dos PRs abiertos para
poder ver el "Update branch"— las fui resolviendo yo mismo, corriendo cada comando en mi propia
terminal y revisando el resultado real en GitHub (checks, logs de Actions, estado de cada PR) antes
de seguir, en vez de asumir que algo había quedado bien solo porque un comando no tiró error.

### 8. Guía rápida para la defensa: dónde mostrar cada cosa

- **PR #16** — el workflow real (`build-backend`/`build-frontend` + cache), reemplaza al esqueleto
  del TP3.
- **PR #17** — la evidencia central: commit que rompe una dependencia del backend, check en rojo,
  commit que la arregla, check en verde, mergeado. El diff final da vacío a propósito (rompí y
  arreglé la misma línea); la evidencia real está en la pestaña *Commits* del PR y en el historial
  de corridas de *Actions*.
- **PR #18** — el PR de relleno: quedó "desactualizado" cuando mergeé el #17, mostrando el botón
  *Update branch* (evidencia de `strict: true`). Captura en `img/updateBranch.png`.
- **PR #19** — badge del README + esta misma sección de `decisiones.md`.
- **`Settings → Branches`**, regla de `main` — ahí están las dos condiciones del gate (§5) en vivo.
- **Pestaña `Actions`**, cualquier corrida con dos jobs — para mostrar `CACHED` en el log de
  `build-backend` (segunda corrida del PR #16 en adelante).
- **Tag y release `v4.0.0`** — cierre del práctico, mismo mecanismo que TP1/TP2/TP3.

## TP5 — Calidad automatizada: tests, coverage y el umbral que frena un merge

### 1. Qué lógica elegí testear y por qué

El TP2/TP3 ya me habían dejado una suite (`test_auth.py`, `test_mesas_productos.py`,
`test_pedidos.py`, `test_reservas_ownership_dashboard.py`) pero es una suite de **integración**: pasa
por `TestClient` contra una base SQLite real, ejercitando la app de punta a punta. Es la base **media**
de la pirámide (§2.1 de la guía), no la base. Lo que le faltaba a mi repo era la base de verdad: unit
tests puros, sin tocar DB ni red, sobre la lógica que más duele si se rompe. Elegí 5 reglas:

- **`recalculate_order`** (`app/utils/orders.py`): el total de un pedido. Si esto se rompe, un cliente
  paga mal — es la regla con más impacto económico directo de toda la app.
- **`ORDER_TRANSITIONS`** (misma clase): la máquina de estados de un pedido. Un bug acá deja pedidos
  "trabados" o permite saltarse un estado (ej. cobrar un pedido que nunca se entregó).
- **`reservations_overlap`** (`app/utils/reservations.py`): decide si dos reservas chocan. El borde
  exacto (120 minutos) es justo donde un `<` vs `<=` cambia el comportamiento sin que se note a simple
  vista — el tipo de bug que un test de integración normal no atrapa porque nadie prueba el minuto
  exacto del límite.
- **`hash_password`/`verify_password`** (`app/auth/password.py`): si esto falla, se compromete la
  autenticación de todos los usuarios.
- **`get_current_user`** (`app/auth/jwt.py`): la puerta de entrada a cada endpoint protegido, y la
  elegida para el test con mock obligatorio (§3).

Más tarde, mirando el reporte de coverage (§4), sumé una sexta: el `DELETE /api/mesas/{id}`, que
tenía dos reglas de integridad de datos (no borrar una mesa con pedidos abiertos, no borrar una con
historial) sin un solo test encima.

Los archivos nuevos son `backend/tests/test_unit_*.py` (uno por regla, con el prefijo `unit` para
distinguirlos de la suite de integración que ya tenía) — 9 métodos de test sobre 5 reglas, más el
método que agregué después en `test_mesas_productos.py`.

### 2. Parametrizado, caso de error y AAA

`test_unit_transiciones_pedido.py` y `test_unit_solapamiento_reservas.py` usan
`@pytest.mark.parametrize` (el `[Theory]`/`[InlineData]` de la guía): en vez de un test por dato,
un método que corre varias veces. **Cuentan como un solo método cada uno** para el mínimo de 8 —ojo
con esa trampa, la señala el instructivo— aunque el reporte muestre 4 resultados por el
parametrizado de transiciones y 4 por el de reservas.

Caso de error: `test_transicion_de_pedido_no_permitida_es_rechazada` (un estado terminal no tiene
salida) y `test_get_current_user_sin_credenciales_lanza_401_sin_consultar_la_db` (rechazo sin
siquiera tocar la base). El criterio que usé para juzgar si un test "vale": si invierto la regla que
prueba (cambié `in` por `not in` en la máquina de estados, a mano, como prueba), el test se pone en
rojo. Lo hice antes de dar por terminado cada archivo.

AAA: en todos los tests nuevos separé Arrange/Act/Assert con comentarios cuando había algo que
armar (`SimpleNamespace` para simular un pedido sin tocar la base, un doble de la sesión de DB); en
los parametrizados no hay Arrange porque el dato entra directo por parámetro, y eso también es
correcto según la guía (un Arrange forzado sería peor que ninguno).

### 3. El mock, y por qué no tuve que refactorizar nada

El ejemplo de la guía arranca con una clase que fabrica su dependencia con `new` adentro del
constructor, y hay que sacarla para poder mockear. Mi caso fue distinto: `get_current_user` ya recibe
la sesión de base de datos por parámetro gracias a `Depends(get_db)` de FastAPI — ya era código
testeable de fábrica, sin que yo hiciera nada. Así que el test
(`test_unit_autenticacion_con_mock.py`) usa directamente `unittest.mock.Mock()` para reemplazar `db`:

```python
db_doble = Mock()
db_doble.get.return_value = usuario_autenticado
resultado = get_current_user(credentials=credenciales, db=db_doble)
db_doble.get.assert_called_once_with(Usuario, 42)
```

Lo que lo hace un **mock** y no un **stub** es la última línea: no miro solo qué devolvió la función
(eso sería un stub), miro **cómo** usó la dependencia — que llamó a `db.get` exactamente una vez, con
el modelo `Usuario` y el id que venía adentro del JWT. Si mañana alguien busca por email en vez de por
id, o llama dos veces, este test se rompe aunque el resultado final "parezca" correcto.

### 4. Coverage: el número, qué excluí, y una diferencia que no esperaba

**Backend** (`pytest-cov` + `.coveragerc`, `branch = True`): excluí `app/main.py`, `app/database.py`
y `app/config.py` (arranque/config, sin reglas de negocio) y `app/models/*` (clases de datos de
SQLAlchemy, solo columnas y relaciones, sin comportamiento). **No excluí `app/schemas/*`** a pesar de
parecer "solo campos": tienen `@field_validator` con lógica real (normalizan nombres, validan
formato de email, longitud de contraseña) — excluirlos hubiera sido exactamente la trampa que
describe la guía, esconder reglas de negocio detrás de la etiqueta "son solo datos".

Con esa exclusión, el número **bajó** de 84% a 80.8% (subió después a 82.7% con el test del §1) —
la prueba de que excluir arranque no es hacer trampa: si fuera para inflar el número, hubiera subido,
no bajado. `main.py`/`database.py` estaban casi al 100% y "regalaban" puntos al promedio; sacarlos
deja el número midiendo solo lo que importa.

Elegí **70%** de umbral (`fail_under` en `.coveragerc`) sobre la métrica combinada que reporta
`pytest-cov` (línea+rama), con ~12 puntos de colchón sobre mi medición real (82.7% hoy). Descarté 75%
y 80% por ser umbrales casi pegados a la medición actual: cualquier refactor chico que no toque lógica
de negocio los rompería, entrenando a ignorar el gate en vez de respetarlo.

**Lo que no esperaba**: medido por separado, la cobertura de **rama pura** da **55.2%**, bien por
debajo del 85.0% de **línea pura** — la métrica combinada (82.7%) esconde esa diferencia. Es la
demostración concreta de la advertencia de la guía ("branch es la métrica más honesta, line puede
mentirte más"): con 85% de línea podría creer que casi todo está probado, cuando en realidad casi la
mitad de las decisiones (`if`/`?.`/`??`) del código sólo se ejercitan por un camino.

**Frontend** (`vitest` + `@vitest/coverage-v8`, `thresholds` en `vite.config.js`): incluí solo
`src/utils/**` y `src/api/client.js` — **no** los `.jsx` (necesitarían DOM para testear de verdad, y
esta materia pide unit tests sin DOM) ni `src/api/api.js` completo. Ese último archivo mezclaba
`apiFetch` (lógica real, ya testeada) con ~20 funciones de una sola línea (`mesasApi.create`,
`productosApi.list`, etc.) que no tienen comportamiento propio, solo mapean un nombre a una ruta.
En vez de excluirlas "a ojo", separé el archivo: `src/api/client.js` (la lógica, la que entra en la
cuenta) y `src/api/api.js` (reexporta `client.js` + los wrappers sin lógica, afuera de la cuenta) —
mismo criterio que la guía usa para `Program.cs`: mover lo que no tiene comportamiento a su propio
archivo en vez de fingir que se puede excluir "a medias" un archivo mezclado.

Elegí **55%** sobre las 4 métricas (`statements`, `branches`, `functions`, `lines`) — con la medición
de ese momento en 66.66% de rama (la más baja), me daba ~11 puntos de colchón, el mismo criterio de
margen que usé en el backend. La suite creció después (agregué 2 tests más sobre casos reales de
`client.js` que no estaban probados: la respuesta exitosa y el 401 que limpia el token, más los tests
de `validarCapacidadMesa`/`sugerirMesa` del PR #23) y el umbral se quedó atrás: para cuando terminé el
TP, medía 85.24% de rama contra un umbral de 55% — casi 30 puntos de colchón, demasiado laxo para
seguir siendo un gate exigente. Lo revisé y lo subí a **75%**: mismo criterio de ~10 puntos de margen
que usé en el backend, aplicado sobre la medición final en vez de la del peor momento. Con 75%, un PR
que agregue lógica nueva sin testearla lo suficiente vuelve a poder romper el build de verdad — que es
lo que un umbral tiene que hacer.

### 5. El ejercicio de la rama sin cubrir

Mirando el reporte del backend encontré que **todo** el endpoint `DELETE /api/mesas/{id}`
(`app/routers/mesas.py`, líneas 66-74) estaba en rojo: ni un test lo ejecutaba, ninguna de sus dos
reglas de integridad (no borrar con pedidos abiertos, no borrar con historial) tenía nada que la
verificara.

- **Qué línea es**: `app/routers/mesas.py:69`, `if active or future:` (y también 71, el segundo `if`
  de la misma función).
- **Qué entrada la recorrería**: una mesa con un pedido en estado activo (para el primer `if`), y
  luego esa misma mesa con el pedido ya cerrado pero existente (para el segundo `if`, "historial").
- **Qué decidí**: agregarlo. Es una regla de integridad real (evita perder el historial de una mesa
  borrándola por error) y el costo de escribirlo era bajo con la infraestructura de tests que ya
  tenía (`client`/`register` de `conftest.py`). El test quedó en
  `test_mesas_productos.py::test_mesa_delete_blocked_by_pending_activity_then_by_history_then_allowed`
  y subió la cobertura de `mesas.py` de 59.4% a 78.3%.

### 6. Los dos Pull Requests que prueban el freno

Son dos PRs distintos, con roles distintos (la guía avisa que es el punto que más se confunde):

- **[PR #23](https://github.com/lucasrodrich/ingsoft3-tp01/pull/23)** — la historia completa,
  **mergeado**. Primer commit: agregué `validarCapacidadMesa`/`sugerirMesa` (lógica real de negocio
  para el frontend, validar que una reserva entre en la mesa elegida) **sin tests**. La corrida
  [36480751780](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/36480751780) se puso roja
  en el paso "Correr los tests con coverage (frontend)" —branches cayó a 50.81%, contra el 55%
  configurado— y `gh pr view` confirmó `mergeStateStatus: BLOCKED` con el build **compilando** y el
  resto de los tests en verde: la cobertura era la única razón. Segundo commit, misma rama: agregué
  8 tests (parametrizado + AAA) que faltaban. La corrida
  [36480994825](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/36480994825) quedó verde,
  `mergeStateStatus` pasó a `CLEAN`, y mergeé.
- **[PR #24](https://github.com/lucasrodrich/ingsoft3-tp01/pull/24)** — queda **abierto y en rojo
  hasta la defensa**, a propósito. Agrega `calcularPropina`/`dividirCuenta`/`sugerirPorcentajePropina`
  (otra pieza de lógica real, cálculo de propina y división de cuenta) sin tests, y **no lo arreglo**:
  es la prueba de que el freno sigue funcionando sin que yo tenga que intervenir de nuevo cada vez.
  `gh pr view 24` da `mergeStateStatus: BLOCKED`.

Los dos required checks (`build-backend`, `build-frontend`) son los mismos del TP4 — no tuve que
tocar la configuración de la rama protegida: al no renombrar los jobs, los checks que ya eran
obligatorios automáticamente pasaron a reaccionar también a la cobertura, no solo al build.

### 7. Por qué coverage alto no garantiza calidad (con mi propio ejemplo)

No hizo falta inventar el ejemplo: mientras armaba `test_unit_calculo_pedido.py` escribí a propósito
una versión mala primero, para verla en la práctica —

```python
def test_esto_no_verifica_nada():
    recalculate_order(SimpleNamespace(items=[], total=None))  # se ejecuta... y no hay ningún Assert
```

— y coverage la cuenta igual que a un test de verdad: la línea se ejecutó, así que "está cubierta".
Ese test no me hubiera avisado si `recalculate_order` empezara a devolver el total mal calculado. Es
la razón de fondo por la que branch coverage (§4) me dio una sorpresa: un número alto (línea, 85%)
puede convivir con la mitad de las decisiones del código sin verificar (rama, 55.2%) — ninguna de las
dos métricas, por sí sola, contesta "¿mis tests comprueban algo de verdad?". Eso solo lo contesta
mirar el test y preguntarse qué invertiría el resultado sin que ningún assert lo note.

### 8. Problemas encontrados y cómo los resolví

- **`ModuleNotFoundError: No module named 'app'` corriendo la etapa de tests en Docker.** Local usaba
  `python -m pytest` (que agrega el directorio actual al `sys.path`); el `ENTRYPOINT` del Dockerfile
  tenía `pytest` a secas, que no lo hace. Se resolvió cambiando el `ENTRYPOINT` a
  `["python", "-m", "pytest", ...]`.
- **`.dockerignore` del backend excluía `tests`** desde el TP4 (cuando la imagen no los necesitaba
  para nada). Al agregar la etapa de tests, `COPY tests ./tests` copiaba una carpeta vacía sin ningún
  error visible — el síntoma era "0 tests collected", no un fallo de build. Se resolvió sacando
  `tests` del `.dockerignore`.
- **`EBUSY: resource busy or locked, rmdir '/app/coverage'`** corriendo la etapa de tests del
  frontend con un volumen montado directo sobre la carpeta de coverage: `vitest` intenta borrar y
  recrear esa carpeta antes de escribir, y no se puede hacer `rmdir` sobre un punto de montaje. Se
  resolvió montando un directorio contenedor (`/out`) y apuntando `--coverage.reportsDirectory` a una
  subcarpeta adentro (`/out/coverage`), que sí se puede crear y borrar libremente.
- **El `-v` de Docker no montaba nada probando local en Git Bash** (`/tmp/...` quedaba vacío del lado
  del host aunque el contenedor decía haber escrito ahí). Es la conversión automática de rutas de
  MSYS rompiendo el argumento `host:contenedor` por el `:` del medio. Se resolvió con
  `MSYS_NO_PATHCONV=1` delante del `docker run` **solo para probar local** — en el runner de GitHub
  Actions (bash de Linux nativo) el mismo `-v` del `ci.yml` anda sin ningún truco.
- **Un `docker run | tee archivo` podía esconder un test en rojo.** Sin `set -o pipefail`, bash
  devuelve el código de salida del último comando del pipe (`tee`, que casi siempre sale bien) y no
  el de `docker run` — el job seguiría "verde" con la suite rota. Lo comprobé a propósito: corrí
  `vitest` con coverage por debajo del umbral y confirmé `exit code 1` **sin** el pipe antes de
  confiar en que `set -o pipefail` lo iba a propagar bien dentro del `ci.yml`.

### 9. Declaración de uso de IA (TP5)

Usé Claude como tutor paso a paso, bloque por bloque (suite → coverage → pipeline → gate → PRs de
demostración → esta sección), pidiéndole que me explicara cada decisión antes de escribir código, y
como ejecutor de los comandos de git/gh/docker en su propia terminal mientras yo confirmaba cada
resultado en la mía. Las decisiones de fondo las tomé yo después de que me explicara el trade-off:
elegí 70%/55% de umbral entre las opciones que me dio, decidí testear el `DELETE /api/mesas` en vez
de descartar el ejercicio, y elegí separar `api.js`/`client.js` en vez de dejar el número de coverage
mintiendo. Verifiqué en mi propia terminal que la suite pasaba (28→29 tests de backend, 11→20 de
frontend) y en GitHub que las corridas reales de Actions daban lo mismo que local antes de mergear
cada PR — no di por buena ninguna corrida que no viera yo mismo en verde.

### 10. Guía rápida para la defensa: dónde mostrar cada cosa

- **[PR #22](https://github.com/lucasrodrich/ingsoft3-tp01/pull/22)** — la suite completa (9 tests
  de backend + ampliación de frontend), `.coveragerc`/`vite.config.js` con los umbrales, y las dos
  etapas `test` de los Dockerfiles + `ci.yml` extendido. Corrida verde:
  [36478866512](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/36478866512) — el Summary
  de cada job tiene la tabla de coverage completa, sin descargar nada.
- **[PR #23](https://github.com/lucasrodrich/ingsoft3-tp01/pull/23)** — rojo→tests→verde→merge. Ver
  la pestaña *Commits* (dos commits: el que rompe, el que arregla) y las dos corridas de Actions
  linkeadas en §6.
- **[PR #24](https://github.com/lucasrodrich/ingsoft3-tp01/pull/24)** — el freno vigente, abierto y
  en rojo hasta la defensa. `mergeStateStatus: BLOCKED`.
- **`test_mesa_delete_blocked_by_pending_activity_then_by_history_then_allowed`** en
  `backend/tests/test_mesas_productos.py` — el ejercicio de la rama sin cubrir (§5).
- **`test_unit_autenticacion_con_mock.py`** — el test con mock obligatorio, con el
  `assert_called_once_with` que lo distingue de un stub.
- **Tag y release `v5.0.0`** — cierre del práctico, sobre el commit que agrega esta sección.
