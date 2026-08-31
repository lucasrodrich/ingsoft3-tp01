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
