# Decisiones

## Enlaces para la corrección (TP6 y TP7)

Lo que vive fuera del repo o es una corrida entre muchas. El detalle está en la sección de cada TP: [Enlaces del TP6](#enlaces-de-este-tp) y [Enlaces del TP7](#enlaces-del-tp7).

- **QA**: [front](https://restoflow-front-qa.onrender.com) · [API `/health`](https://restoflow-api-qa.onrender.com/health) — **PROD**: [front](https://restoflow-frontend-prod.onrender.com) · [API `/health`](https://restoflow-api-prod.onrender.com/health). Vivas hasta la defensa; `/health` devuelve el SHA que corre. El primer pedido tras un rato sin uso tarda 30-60 s.
- **Paquetes públicos** (`docker pull` sin credenciales, etiquetas `sha-<commit>`, sin `latest`): [`ingsoft3-tp01-backend`](https://github.com/lucasrodrich/ingsoft3-tp01/pkgs/container/ingsoft3-tp01-backend) · [`ingsoft3-tp01-frontend`](https://github.com/lucasrodrich/ingsoft3-tp01/pkgs/container/ingsoft3-tp01-frontend).
- **TP6, la cadena**: PR con «Entrar al registry» salteado [runs/36493411995](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/36493411995) · `main` publicando [runs/36493534503](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/36493534503) · el gate, rechazo y aprobación [runs/37859121585](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37859121585).
- **TP7, integración verde y e2e roja**: commit que rompió la app [`141c8be`](https://github.com/lucasrodrich/ingsoft3-tp01/commit/141c8be) · corrida [runs/37876705321](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37876705321) · reportes [`playwright-report-integracion`](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37876705321/artifacts/11592448032) (verde) y [`playwright-report-e2e`](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37876705321/artifacts/11592936587) (roja) · la corrida completa en verde hasta PROD [runs/37878408979](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37878408979).
- **TP5, el freno vigente**: [PR #24](https://github.com/lucasrodrich/ingsoft3-tp01/pull/24), abierto y en rojo.
- **Releases**: [v5.0.0](https://github.com/lucasrodrich/ingsoft3-tp01/releases/tag/v5.0.0) · [v6.0.0](https://github.com/lucasrodrich/ingsoft3-tp01/releases/tag/v6.0.0) · [v7.0.0](https://github.com/lucasrodrich/ingsoft3-tp01/releases/tag/v7.0.0) · [v8.0.0](https://github.com/lucasrodrich/ingsoft3-tp01/releases/tag/v8.0.0) · [v9.0.0](https://github.com/lucasrodrich/ingsoft3-tp01/releases/tag/v9.0.0).

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

Release [`v5.0.0`](https://github.com/lucasrodrich/ingsoft3-tp01/releases/tag/v5.0.0). Suite, umbrales y pipeline en [PR #22](https://github.com/lucasrodrich/ingsoft3-tp01/pull/22), corrida verde [36478866512](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/36478866512) (el *Summary* de cada job trae la tabla de coverage).

### 1. Qué lógica testeé y por qué

La suite que traía del TP2 era de **integración** (`TestClient` contra SQLite): la parte media de la pirámide. Me faltaba la base, unitarios puros sin base ni red, sobre lo que más duele si se rompe:

- **`recalculate_order`** (`app/utils/orders.py`): el total del pedido. Si falla, el cliente paga mal.
- **`ORDER_TRANSITIONS`**: la máquina de estados del pedido. Un bug deja pedidos trabados o permite cobrar uno no entregado.
- **`reservations_overlap`**: si dos reservas chocan. El borde de 120 minutos es donde un `<` vs `<=` cambia todo sin que se note.
- **`hash_password`/`verify_password`**: si fallan, cae la autenticación de todos.
- **`get_current_user`** (`app/auth/jwt.py`): la puerta de cada endpoint protegido; la elegí para el mock.

Están en `backend/tests/test_unit_*.py`: 9 métodos sobre 5 reglas. Después sumé el `DELETE /api/mesas/{id}` (§5).

### 2. Parametrizado, caso de error y AAA

`test_unit_transiciones_pedido.py` y `test_unit_solapamiento_reservas.py` usan `@pytest.mark.parametrize`; cada uno cuenta como **un** método aunque el reporte muestre 4 resultados. Casos de error: `test_transicion_de_pedido_no_permitida_es_rechazada` y `test_get_current_user_sin_credenciales_lanza_401_sin_consultar_la_db`. Para saber si un test vale, invertí la regla a mano (`in` por `not in`) y comprobé que se pusiera rojo. AAA marcado con comentarios cuando hay algo que armar; en los parametrizados el dato entra por parámetro y no hace falta Arrange.

### 3. El mock, sin refactor

`get_current_user` ya recibía la sesión por `Depends(get_db)`, así que era testeable de fábrica. En `test_unit_autenticacion_con_mock.py`:

```python
db_doble = Mock()
db_doble.get.return_value = usuario_autenticado
resultado = get_current_user(credentials=credenciales, db=db_doble)
db_doble.get.assert_called_once_with(Usuario, 42)
```

La última línea es lo que lo hace **mock** y no **stub**: no sólo miro qué devolvió, verifico **cómo** usó la dependencia (una vez, con `Usuario` y el id del JWT).

### 4. Coverage: umbral, métrica y qué quedó afuera

- **Backend** (`pytest-cov`, `branch = True` en `.coveragerc`): umbral **70 %** (`fail_under`) sobre la métrica combinada línea+rama; medido **82,7 %**, ~12 puntos de colchón. Descarté 75-80 %: pegados a la medición, cualquier refactor chico los rompería y el equipo aprendería a ignorar el gate. **Rama pura: 55,2 %**, contra 85 % de línea pura: la combinada esconde que casi la mitad de las decisiones se ejercitan por un solo camino.
- **Afuera de la cuenta (back)**: `main.py`, `database.py`, `config.py` (arranque) y `models/*` (sólo columnas). **No** excluí `schemas/*`: tienen validadores con lógica. Excluir **bajó** el número (84 → 80,8 %): no era para inflarlo.
- **Frontend** (`vitest` + `coverage-v8`, `thresholds` en `vite.config.js`): cuentan `src/utils/**` y `src/api/client.js`; afuera los `.jsx` (necesitan DOM) y los wrappers de una línea, que separé de la lógica moviendo `apiFetch` a `client.js`. Umbral inicial 55 % en las 4 métricas; cuando la rama llegó a 85,24 % lo subí a **75 %** ([#26](https://github.com/lucasrodrich/ingsoft3-tp01/pull/26)) para mantener ~10 puntos de margen.

### 5. El camino sin cubrir

- **Qué línea**: `app/routers/mesas.py:69`, `if active or future:` (y el segundo `if`, línea 71) del `DELETE /api/mesas/{id}`, que no ejecutaba ningún test.
- **Qué entrada la recorre**: una mesa con un pedido activo; después, la misma mesa con el pedido cerrado (historial).
- **Qué decidí**: agregarlo, porque protege el historial. `test_mesa_delete_blocked_by_pending_activity_then_by_history_then_allowed` subió `mesas.py` de 59,4 % a 78,3 % ([#25](https://github.com/lucasrodrich/ingsoft3-tp01/pull/25)).

### 6. Los dos Pull Requests que prueban el freno

- **[PR #23](https://github.com/lucasrodrich/ingsoft3-tp01/pull/23), mergeado**: agregué `validarCapacidadMesa`/`sugerirMesa` sin tests y la corrida [36480751780](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/36480751780) se puso roja en «Correr los tests con coverage (frontend)»: **rama 50,81 %** contra 55 %, con todo compilando y los tests en verde (`mergeStateStatus: BLOCKED`). Con 8 tests nuevos, [36480994825](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/36480994825) quedó verde y lo mergeé.
- **[PR #24](https://github.com/lucasrodrich/ingsoft3-tp01/pull/24), abierto y en rojo hasta la defensa**: `calcularPropina`/`dividirCuenta` sin tests. Prueba que el freno sigue vivo.

Los required checks son los mismos del TP4 (`build-backend`, `build-frontend`): como no renombré los jobs, empezaron a frenar también por cobertura.

### 7. Por qué coverage alto no garantiza calidad

```python
def test_esto_no_verifica_nada():
    recalculate_order(SimpleNamespace(items=[], total=None))  # se ejecuta... y no hay Assert
```

Coverage lo cuenta como cubierto, pero no avisaría si el total saliera mal. Lo mismo con mis números: 85 % de línea convivía con 55 % de rama. Ninguna métrica contesta si un test comprueba algo; eso se ve leyendo el test.

### 8. Problemas encontrados y cómo los resolví

- **`No module named 'app'`** en la etapa de tests de Docker: el `ENTRYPOINT` usaba `pytest` a secas; pasé a `python -m pytest`, que agrega el directorio al `sys.path`.
- **"0 tests collected"**: el `.dockerignore` del TP4 excluía `tests`. Lo saqué.
- **`EBUSY ... rmdir '/app/coverage'`**: vitest no puede borrar un punto de montaje; monté `/out` y escribí en `/out/coverage`.
- **El `-v` de Docker no montaba en Git Bash** (MSYS convierte rutas): `MSYS_NO_PATHCONV=1` sólo local; en el runner anda sin trucos.
- **`docker run | tee` podía esconder un rojo**: sin `set -o pipefail` el pipe devuelve el código de `tee`. Lo comprobé con coverage bajo el umbral antes de confiar.

### 9. Declaración de uso de IA (TP5)

Usé Claude como tutor bloque por bloque y para ejecutar git/gh/docker mientras yo confirmaba en mi terminal. Las decisiones las tomé yo después de que me explicara el trade-off: los umbrales, testear el `DELETE /api/mesas` en vez de descartar el ejercicio, y separar `api.js`/`client.js` en vez de dejar el número mintiendo. Verifiqué que la suite pasara local (28→29 tests de back, 11→20 de front) y que las corridas de Actions dieran lo mismo antes de mergear.

## TP6 — CD: environments, aprobaciones y deployment patterns

### Enlaces de este TP

- **Paquetes públicos** (`docker pull` sin credenciales, verificado con `docker logout`): [`ingsoft3-tp01-backend`](https://github.com/lucasrodrich/ingsoft3-tp01/pkgs/container/ingsoft3-tp01-backend) · [`ingsoft3-tp01-frontend`](https://github.com/lucasrodrich/ingsoft3-tp01/pkgs/container/ingsoft3-tp01-frontend).
- **La cadena**: PR con «Entrar al registry» salteado [runs/36493411995](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/36493411995) · `main`, con «Construir y publicar la imagen» como último paso [runs/36493534503](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/36493534503).
- **QA**: [front](https://restoflow-front-qa.onrender.com) · [API `/health`](https://restoflow-api-qa.onrender.com/health) — **PROD**: [front](https://restoflow-frontend-prod.onrender.com) · [API `/health`](https://restoflow-api-prod.onrender.com/health). Vivas hasta la defensa; el primer pedido tras el sleep tarda 30-60 s.
- **El gate**: [runs/37859121585](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37859121585), intento 1 **rechazado** con motivo, intento 2 **aprobado** (desplegó `7059c3c`).
- **Release** [`v6.0.0`](https://github.com/lucasrodrich/ingsoft3-tp01/releases/tag/v6.0.0) sobre `7059c3c`, el commit que quedó en PROD.

### 1. Continuous Delivery, no Deployment

Cada merge a `main` llega solo a QA; a PROD, sólo con aprobación humana. Continuous Deployment sacaría ese gate, y no lo haría: no tenía métricas ni alertas que detecten un deploy malo, así que el aprobador era el único control posterior a los tests.

### 2. Por qué publico sólo en verde

Tres controles encadenados: nada entra a `main` sin CI verde, sólo `main` publica, y publicar es el último paso del job que corre los tests. Si se publicara igual, `sha-<commit>` dejaría de significar "esta imagen pasó los tests". Lo que no cubre: un `docker push` a mano con mis credenciales.

### 3. La cadena y el alcance de cada secret

```
build-backend ─┐
               ├─► deploy-qa (environment: qa) ─► deploy-prod (environment: production, requiere aprobación)
build-frontend ┘
```

- `needs` fuerza el orden; `if: github.ref == 'refs/heads/main'` hace que los PRs sólo verifiquen.
- Los hooks de Render son **secrets del environment**: los de PROD **no los lee ningún job hasta que el revisor aprueba**. A nivel repo, cualquier workflow (incluso uno de un PR) podría desplegar a producción. Las URLs son *variables*: no son sensibles.
- `concurrency: deploy-prod` sin cancelar: nunca dos deploys a PROD a la vez. Dos aprobaciones pendientes se resuelven rechazando la vieja a mano.

### 4. Qué mira el aprobador

1. `deploy-qa` en verde y su log mostrando que QA corre el **mismo SHA** que se promueve.
2. Que el commit sea el esperado (*Deployments*, no la punta de `main` de memoria).
3. Que no haya otro deploy a PROD pendiente.

Mi rechazo real: *"No despliego a producción hasta haber medido el tiempo de rollback"*. **Qué no ve**: si la app anda para un usuario, errores, latencia o cambios en la base. Hoy la aprobación es más un trámite informado que una verificación independiente.

### 5. La letra chica del free tier

- **Sleep**: el servicio se duerme y el primer pedido tarda 30-60 s; el intento 1 del smoke daba timeout. Por eso reintenta 30 veces cada 20 s (~10 min).
- **Build en cada deploy**: ~1 minuto por deploy, que consume minutos de build.
- **Neon**: `app_qa` y `app_prod` separadas de verdad (lo de QA no aparece en PROD).
- **Demos**: antes de mostrar algo, abro `/health` para despertarlo.

### 6. Lo que pierdo porque Render reconstruye desde el repo

Lo que corre en PROD no es byte a byte lo que pasó los tests, sino otra construcción del mismo commit: los pins de `requirements.txt` achican la deriva, pero la imagen base y las capas pueden diferir. Mitigaba pidiendo el commit (`&ref=`) y verificando el SHA en el smoke. (Lo resolví en el TP7 desplegando la imagen.) La dirección del backend del front (`BACKEND_URL`, `DNS_RESOLVER`) se lee al arrancar desde la plantilla de nginx: la misma imagen sirve en QA y PROD.

### 7. Qué prueba el smoke y qué no

Prueba, con reintentos, que el backend corre **este commit** (`/health` devuelve `sha` y hace `SELECT 1`), que el front responde y que la base anda (registro, login y lectura de `/api/categorias` con token). **No** prueba el SHA del front, ningún flujo de negocio ni rendimiento, y deja un usuario de prueba en cada base. La primera versión daba verde con la versión vieja mientras Render construía; agregar el `sha` a `/health` lo resolvió (se ven intentos con `null` y después el SHA nuevo).

### 8. Deployment pattern y rollback

**Blue-green**: backend sin estado más una base, rollback instantáneo volviendo a apuntar al entorno anterior. Canary exigiría partir el tráfico y medir errores por versión, y no tenía ni balanceador ni métricas. No cubre los cambios de esquema que comparten las dos versiones. Me falta observabilidad: errores y latencia por versión, alertas y logs centralizados.

**Rollback probado**: Render → `restoflow-api-prod` → *Manual Deploy* → *Deploy a specific commit* → `29a99b5` (el anterior en PROD), esperar *Live* y verificar `/health`; para volver, `7059c3c`. **Tiempo medido: 35,1 s** en *Deploys* de Render (37,24 s con cronómetro), reconstruyendo desde el repo. No deshace los datos: haría falta restaurar la base a un punto en el tiempo (Neon lo permite) o migraciones reversibles.

### 9. Problemas encontrados y cómo los resolví

- **508 Loop Detected** (#31): nginx reenviaba el `Host` del front; usé `$proxy_host`.
- **ghcr.io** (#29): desactivé `provenance`/`sbom` y habilité el acceso de Actions al paquete.
- **El smoke daba verde con la versión vieja**: SHA en `/health` (§7).
- **`&ref=` no hace lo que creía**: el rollback con el hook redesplegó la punta (`7059c3c`) en vez del SHA pedido (lo vi en *Events*). Sirve para "desplegá este commit si es la punta", no para rollback; uso *Manual Deploy*.
- **Destino de rollback equivocado**: pensé en `82190c2`, pero PROD nunca lo corrió; estaba en `29a99b5` (*Events*).
- **Sin botón Rollback nativo** en mi plan: camino manual. **`curl` en PowerShell** es `Invoke-WebRequest`: usé `curl.exe`.
- **Un test que fallaba según la hora** (#36): `test_past_reservation_rejected` calculaba "ayer" con la zona del runner (UTC) y la app valida con Córdoba (UTC-3): entre las 00:00 y las 03:00 UTC "ayer" era hoy. Calculé la fecha en la zona de la app; el CI pasó a las 01:42 UTC, dentro de la ventana que fallaba.

### 10. Declaración de uso de IA (TP6)

Claude escribió los jobs `deploy-qa` y `deploy-prod`, el cambio de `/health` y la plantilla de nginx, explicando cada decisión antes de aplicarla. Yo hice lo que requería cuentas y clics: Neon, Render, environments, secrets, el reviewer, el rechazo, la aprobación y el rollback. Verifiqué los deploys *Live*, el SHA de `/health` en QA y PROD y los logs del smoke. Cuando la IA se equivocó (el destino del rollback, `&ref=`), lo detecté con *Events* de Render y lo corregí.

## TP7 — Imagen inmutable, integración y e2e como gate de promoción

### Enlaces del TP7

- **Paquetes públicos** (`docker pull` por `sha-<commit>`, sin credenciales; los dos tienen la etiqueta del commit de PROD, `sha-5233d0bc8d63f6079e1272f84be170c081daee44`): [`ingsoft3-tp01-backend`](https://github.com/lucasrodrich/ingsoft3-tp01/pkgs/container/ingsoft3-tp01-backend) · [`ingsoft3-tp01-frontend`](https://github.com/lucasrodrich/ingsoft3-tp01/pkgs/container/ingsoft3-tp01-frontend).
- **Integración VERDE / e2e ROJA**: el commit que rompió la **app** (no el test) [`141c8be`](https://github.com/lucasrodrich/ingsoft3-tp01/commit/141c8be) (el form de mesas manda `numeroMesa`; no toca `e2e/`) · corrida [runs/37876705321](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37876705321) (smoke e integración verdes, e2e roja, `deploy-prod` sin arrancar) · reportes [`playwright-report-integracion`](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37876705321/artifacts/11592448032) (verde) y [`playwright-report-e2e`](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37876705321/artifacts/11592936587) (roja, con captura y traza).
- **Corrida completa en verde hasta PROD**: [runs/37878408979](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37878408979) (arreglo [`5233d0b`](https://github.com/lucasrodrich/ingsoft3-tp01/commit/5233d0b)). Release [`v7.0.0`](https://github.com/lucasrodrich/ingsoft3-tp01/releases/tag/v7.0.0) sobre ese commit.
- **QA y PROD**: las mismas del TP6. Dos Dockerfiles, así que dos paquetes y **cuatro** servicios de imagen. Los *Events* de Render ("Triggered via Deploy Hook" con el `sha-…`) no se pueden enlazar: los muestro en vivo.

### 1. Build once, deploy many

En el TP6, QA y PROD corrían **otra construcción** del commit, no la imagen que aprobaron los tests, y no podía probar que fueran iguales (el `&ref=` ni siquiera desplegaba el commit pedido si no era la punta). Ahora el pipeline construye **una vez**, publica `…:sha-<commit>` y los cuatro servicios **ejecutan esa imagen**: el hook ya no dice qué construir sino qué ejecutar (`imgURL=…:sha-<commit>`). En [37878408979](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37878408979), `deploy-qa` y `deploy-prod` muestran las mismas dos etiquetas.

### 2. Etiquetas, sin `latest`

- **`sha-<commit>` (40 caracteres)** identifica lo publicado por un commit y se publica una sola vez. La corta (`sha-5233d0b`) **no existe** (404 comprobado).
- **`v7.0.0` en git** es el nombre humano de lo que está en PROD.
- **Sin `latest`**: es móvil, y "qué corre en PROD" dejaría de tener respuesta.
- **Lo configurado en Render no es lo que corre**: cambié la fuente de los cuatro servicios (no creé nuevos, así conservé URL, variables y hooks) a *Existing Image* con `sha-3d8cd4f…`, porque Render exige una. Lo que corre lo decide cada deploy con `imgURL`. Lo comprobé en `restoflow-api-qa`: el encabezado decía `sha-3d8cd4f…` y el digest `c44c194` era el de `sha-3ff3c93…`. **Peligro**: *Manual Deploy* desplegaría lo de *Settings*, o sea, retrocedería en silencio. No lo uso.

### 3. Del tag a la imagen

`git rev-list -n1 v7.0.0` da `5233d0bc…`; la imagen es `ghcr.io/lucasrodrich/ingsoft3-tp01-{backend,frontend}:sha-5233d0bc…`. Volver a esa versión sería disparar el hook con esa `imgURL`; ese rollback por imagen **no lo probé ni lo medí** (el de *Manual Deploy* del TP6 ya no vale).

### 4. Cómo se comprueba, desde afuera, que un entorno ejecuta mi imagen

- **Events de Render**: "Triggered via Deploy Hook" con `…:sha-<commit>` y una corrida que lo respalda.
- **Digest**: el encabezado muestra el digest corto de lo que corre y lo comparo con el del registry. En el front el digest se repite entre commits que no lo cambiaron (capas reutilizadas): ahí la prueba es la etiqueta en *Events*.
- **`/health`**: devuelve el `sha` que grabé **dentro de la imagen** (`ARG`/`ENV GIT_SHA`). No usé `RENDER_GIT_COMMIT` porque Render la pone en servicios construidos desde git.
- **Qué no prueba el smoke**: el SHA del front ni que la app funcione para un usuario; estuvo **verde con el front roto** en [37876705321](https://github.com/lucasrodrich/ingsoft3-tp01/actions/runs/37876705321).

### 5. Qué flujos puse en cada suite (pirámide)

- **Integración** (`frontend/e2e/api.spec.js`, sin navegador, contra la API de QA): alta → listado → baja; capacidad 0 → **422** sin crear nada; y **elegida**: un usuario pide la mesa de otro y recibe 404. Esa regla sólo existe con autenticación y base reales; si se rompe, cualquier cliente ve datos ajenos.
- **e2e** (`frontend/e2e/mesas.spec.js`, Chromium contra el front de QA): crear y borrar una mesa; número repetido → el usuario ve el error; y **elegido**: el login, porque sin él nadie usa nada y además toca la base.
- **Qué no puse**: cálculos, transiciones y solapamientos ya están en los unitarios del TP5, más rápidos y baratos. Cada capa prueba lo que sólo ella puede ver.

### 6. Qué dice el par verde/roja

| smoke | integración | e2e | Lectura |
|---|---|---|---|
| verde | **verde** | **roja** | API y base sanas; lo roto es **cómo el front usa la API** |

Sin abrir el código: la traza del reporte rojo muestra el `POST /api/mesas` con 422 (el front mandó `numeroMesa`). Si se rompía la API, la integración salía roja y la e2e ni corría (`needs`). Ningún unitario lo ataja: los del front no cubren el formulario. Mi gate no ve lo que queda fuera de esos 6 flujos (reservas, pedidos), ni carga ni navegadores distintos de Chromium.

### 7. Por qué la integración es la amplia

Le habla a la API de QA ya desplegada: **gano** probar la misma imagen y la misma base que van a PROD sin infraestructura extra; **pierdo** aislamiento y velocidad de diagnóstico (depende de que QA esté vivo y comparte datos). Lo mitigo con usuarios dedicados, números de mesa únicos y limpieza comprobada.

### 8. Cold start, flaky y base compartida

El smoke ya despertó QA. Las suites esperan lo que buscan con `timeout` de 60 s por test y 15 s por aserción, en vez de `sleep`; `retries: 1` y `workers: 1`. Un **test flaky** pasa o falla sin que cambie el código, y entrena a ignorar el rojo; mi reintento absorbe una demora suelta pero el reporte lo marca *flaky*. No apareció ninguno. Los usuarios `e2e-a` y `e2e-b` quedan para siempre en QA (la app no borra usuarios).

### 9. Una imagen del front para QA y PROD

`BACKEND_URL` y `DNS_RESOLVER` se leen al arrancar (`default.conf.template`); adentro de la imagen sólo quedan la configuración de nginx y los estáticos. Por eso `sha-<commit>` sirve en los dos entornos.

### 10. Límite: un solo QA y dos merges seguidos

La corrida B puede redesplegar QA mientras la integración o la e2e de A lo usan. Lo reconocería en *Events*; rechazaría la corrida A y dejaría valer la B. Regla: **un merge por vez**. No lo provoqué; lo resolvería un entorno por corrida.

### 11. Problemas encontrados y cómo los resolví

- **El SHA del smoke venía de una variable de Render**: lo grabé en la imagen antes de migrar (§4).
- **La API contesta 422, no 400**, ante datos inválidos: la prueba lo afirma.
- **Docker Desktop apagado** en el checkpoint: probé con una consulta anónima al manifest y repetí el `pull` al encenderlo.
- **Errores de tipeo en Git Bash** (el `$` del prompt, una variable sin `SHA`): pasé a pegar la etiqueta completa.
- **Dos runs del TP6 esperando aprobación**: los rechacé antes de migrar para que no se aprobaran por el camino viejo (`&ref=`). El rechazo con motivo del TP6 es el de `37859121585`.
- **vitest tomaba los `*.spec.js` de Playwright**: excluí `e2e/**` en `vite.config.js`.

### 12. Declaración de uso de IA (TP7)

Claude escribió el código: hooks con `imgURL`, `GIT_SHA` en la imagen, las suites de Playwright, los jobs `integracion` y `e2e`, la rotura y el arreglo. Yo cambié la fuente de los servicios en Render, disparé el primer deploy, aprobé y rechacé, leí el reporte rojo y verifiqué *Events*. Las seis pruebas corrieron verdes primero contra mi docker compose; comprobé SHA y digest contra el registry; y pedí mergear la rotura sin tocar `e2e/` para diagnosticarla con mis ojos. El límite del smoke (verde con el front roto) sólo se vio al correr la rotura.

## TP8 — Infraestructura como código: preprod con Terraform

Release [`v8.0.0`](https://github.com/lucasrodrich/ingsoft3-tp01/releases/tag/v8.0.0) sobre el commit que deja `infra/` terminado ([PR #45](https://github.com/lucasrodrich/ingsoft3-tp01/pull/45)).

### 1. Riel elegido y versiones fijadas

**Terraform** v1.16.5 (`winget`) sobre **Neon + Render**, mis cuentas desde el TP6. Providers por versión exacta, con `.terraform.lock.hcl` commiteado:

| Provider | Versión | Para qué |
|---|---|---|
| `kislerdm/neon` | 0.18.0 | proyecto, rol y base de preprod |
| `render-oss/render` | 1.9.1 | los dos servicios de preprod |
| `hashicorp/random` | 3.9.1 | el secreto JWT, para que no esté escrito en ningún archivo |

Declaré un entorno **nuevo, `preprod`**, con las imágenes del TP7 y su propia base; QA y PROD no se tocan. **Sin credenciales en el HCL**: `NEON_API_KEY`, `RENDER_API_KEY` y `RENDER_OWNER_ID` vienen del entorno, el `org_id` por `TF_VAR_neon_org_id`. **Se derivan, no se copian**: la `DATABASE_URL` se arma con el rol, la contraseña y el host que devuelve Neon, y la `BACKEND_URL` del front sale del `url` de su API. **El estado vive en mi máquina** (`.gitignore` desde antes del primer `apply`): tiene la contraseña del rol en texto plano.

### 2. Qué comprobé

- **Idempotencia**: el segundo `plan` dijo *No changes*.
- **`destroy → apply`**: 6 recursos borrados y recreados, con QA y PROD intactos (mismo `sha` antes y después). El orden del `destroy`, visto en la ejecución: front → api → base y secreto → rol → proyecto, el inverso de la creación, deducido del grafo de dependencias. Render devolvió **la misma URL**; cambia la identidad de lo creado, por eso la conexión se deriva.
- **Preprod funciona**: `/health` con el `sha`, el front carga, me registré y la API listó categorías.
- **Drift**: borré `app_preprod` a mano y el plan lo vio y lo reparó; una `base_intrusa` creada a mano **no la ve**: vigila lo declarado, no todo lo que existe.
- **`prevent_destroy`** temporal en la base: el `destroy` se negó nombrando el recurso.

### 3. Límites: qué sigue artesanal

Los cuatro servicios de QA y PROD no están en ningún plan. El estado local no se comparte. Preprod no está conectado al pipeline. El free de Render no deja modificar un servicio desde Terraform (`destroy` + `apply`). Preprod vive en otro workspace de Render, así que no compite por las 750 horas; igual lo destruyo al terminar.

### 4. Problemas encontrados y cómo los resolví

- **Neon pedía `org_id`** (la guía no lo menciona): variable `neon_org_id` vía `TF_VAR_`.
- **El backend lee `DATABASE_URL`**, no `ConnectionStrings__Default`: `postgresql+psycopg://…?sslmode=require` con `urlencode` de la contraseña.
- **`GIT_SHA` no va como variable del servicio**: viene en la imagen y la pisaría.
- **Terraform fuera del `PATH`** tras `winget`: terminal nueva. **PowerShell**: `curl.exe`, y URLs con `$(…)` entre comillas.
- **No veía los servicios nuevos**: estaban en otro workspace de Render.

### 5. Declaración de uso de IA (TP8)

Claude escribió el HCL adaptándolo a mi app y a los cambios de Neon. Yo instalé Terraform, creé y exporté las credenciales, corrí `init`, `plan`, `apply` y `destroy`, e hice los experimentos de drift y `prevent_destroy`. Leí cada plan antes de aplicarlo, comprobé preprod por el front y comparé `/health` de QA y PROD antes y después del `destroy`.

## TP9 — DevSecOps, observabilidad y feedback continuo

Release [`v9.0.0`](https://github.com/lucasrodrich/ingsoft3-tp01/releases/tag/v9.0.0).

### 1. Las tres capas (y qué no mira cada una)

| Capa | Qué tengo | Qué **no** mira | Qué cubre el hueco |
|---|---|---|---|
| Secretos | Secret scanning + **push protection** | Secretos sin patrón conocido (`JWT_SECRET`, la contraseña de Postgres) | `.env` gitignoreado (TP2), secrets por environment (TP4/TP6), credenciales de Terraform por el entorno (TP8) |
| Dependencias | `dependabot.yml` ([#47](https://github.com/lucasrodrich/ingsoft3-tp01/pull/47)) con pip, npm, actions, docker y terraform; alertas y *security updates* | Fallas sin CVE publicado; mi código | CodeQL y los tests |
| Código propio | **CodeQL** default (Python, JS/TS, Actions) en cada PR, push y semanal | Lógica de negocio mal hecha; lo que pasa en ejecución | Tests (TP5/TP7) y Sentry |

Cinco ecosistemas porque las imágenes base y los providers también son código ajeno. **CodeQL** encontró 4 `actions/missing-workflow-permissions` (OWASP **A01**, mínimo privilegio): hoy no explotables (el token por defecto es de lectura), pero si cambia ese default, una action comprometida podría escribir en el repo. Arreglado en [#66](https://github.com/lucasrodrich/ingsoft3-tp01/pull/66) (`permissions: {}` en los deploys, `contents: read` en integración y e2e): **0 alertas abiertas**.

### 2. El PR de Dependabot que mergeé, y por qué

[#58](https://github.com/lucasrodrich/ingsoft3-tp01/pull/58): **`react-router-dom` 7.18.2 → 7.18.4**, un **patch**, con un changelog sin cambios incompatibles. Me animé porque toda la cadena lo verificó: tests y umbral, `deploy-qa`, integración y la **e2e en Chromium**, que navega y usa el router de verdad. Su `deploy-prod` quedó cancelado porque mergeé otro cambio antes; llegó a PROD con `154171f`. Prender Dependabot destapó alertas viejas (PyJWT **crítica**, pytest, `undici`, `source-map-js`): las junté en [#73](https://github.com/lucasrodrich/ingsoft3-tp01/pull/73) para correr una cadena y no tres (pytest 9 es **major**: lo corrí local, 31/31).

### 3. El monitor: cuánto tardó en avisarme

UptimeRobot gratuito (HEAD cada 5 minutos) sobre el `/health` de PROD, con email. Antes de crearlo, `curl -I` daba **405** (FastAPI sólo atendía `GET`): [#67](https://github.com/lucasrodrich/ingsoft3-tp01/pull/67).

- **Primer intento (19/10)**: suspendí de 18:26 a 18:29. **No hubo alerta**: los 3 minutos entraron entre dos chequeos.
- **Caída provocada (20/10)**: *Suspend* 19:22 → **DOWN 19:23:15** (HTTP 503) → *Resume* 19:24 → **UP 19:28:19** (incidente de 5 min 4 s).

**Tardó ~1 minuto**, con suerte; el peor caso es ~5. Sin el monitor me habría enterado por un usuario o en el próximo smoke. Quedó **pausado**: despierto cada 5 minutos se come las 750 horas de Render.

### 4. Sentry: qué falla, qué tarda y qué se usa

Subió en [#68](https://github.com/lucasrodrich/ingsoft3-tp01/pull/68). Back: `sentry-sdk[fastapi]` con `SENTRY_DSN` sólo en PROD (sin la variable queda apagado). Front: `@sentry/react` con el DSN en `main.jsx`: **sólo sirve para enviar**, no para leer, y viaja igual en el JavaScript del navegador.

- **Qué falla**: el error provocado `GET /api/falla` (sacado en [#72](https://github.com/lucasrodrich/ingsoft3-tp01/pull/72)) y uno **real**, `RESTOFLOW-FRONT-1` (§6).
- **La más lenta**: **`POST /api/auth/login`**, **P50 1,67 s / P95 1,68 s**. Bcrypt es lento a propósito y el primer pedido paga el arranque de Neon; `GET /api/categorias` tarda 24 ms. Desde el front, un `POST` con **P95 1,82 s** y 7,7 % de fallos.
- **La más usada**: todo está por debajo de 0,01 TPM porque el único usuario fui yo. Contando pedidos empatan con 2: **`POST /api/auth/login`**, `register` y `GET /api/categorias`.
- **Tarjetas**: [#70](https://github.com/lucasrodrich/ingsoft3-tp01/issues/70) (el P95 de 1,82 s) y [#71](https://github.com/lucasrodrich/ingsoft3-tp01/issues/71) (`POST /api/reservas` con 50 % de fallos, probablemente rechazos 4xx).

**Lo que Sentry ve y el monitor no**: la pantalla en blanco de Mesas tuvo `/health` en verde todo el tiempo.

### 5. Métricas DORA (práctica)

Medidas con la API de *Deployments* de `production`: **8 deploys** a PROD (08/10-19/10); **lead time** merge → PROD de ~5-6 min (#67 4,4; #69 5,7; #68 6,1), el peor de 45 min (#47, esperando mi aprobación); **change failure rate** 1 de 8 (la rotura del TP7 no cuenta: nunca llegó a PROD); **recuperación** ~15 min (§6). Lo primero que mejoraría es el peor lead time, que domina el gate humano; en serio lo cambiaría por un canary con rollback automático por tasa de errores.

### 6. Postmortem sin culpables: pantalla en blanco al salir de Mesas (19/10)

- **Qué pasó**: al salir de *Mesas*, `TypeError: l is not a function` y la app en blanco hasta recargar, sin pérdida de datos. Estaba **desde el primer commit (14/08)** y nadie lo había reportado.
- **Timeline (UTC)**: Sentry llega a PROD 21:59 → entre 22:00 y 22:08 abre `RESTOFLOW-FRONT-1` y lo diagnostico → arreglo con test de regresión ([#69](https://github.com/lucasrodrich/ingsoft3-tp01/pull/69)) mergeado 22:08 → en PROD **22:14**.
- **Causa técnica**: `useEffect(load, [])`; `load` devuelve una Promise y React la toma como limpieza. Arreglo: `useEffect(() => { load() }, [])`.
- **Causa raíz (qué del sistema, no quién)**: no hay ESLint con reglas de hooks; ninguna prueba **salía** de Mesas (los unitarios no cubren páginas y la e2e no navega); y hasta el TP9 un error del navegador no le llegaba a nadie.
- **Acciones**: hechas, el arreglo, revisar las demás páginas (no había otro caso) y Sentry en el front. Pendientes, `eslint-plugin-react-hooks` en `build-frontend`, navegación entre secciones en la e2e y una alerta de Sentry por email.
- **Aprendizaje**: "nadie se quejó" no es "anda"; el monitor dice si está **viva**, no si **funciona**.

### 7. Problemas encontrados y cómo los resolví

- **`/health` daba 405 a `HEAD`**: lo vi con `curl -I` antes del monitor (§3).
- **CodeQL marcó mi pipeline**: los permisos (§1).
- **17 PRs de Dependabot de golpe**: mergeé uno de rutina y junté los de seguridad; el próximo paso sería `groups` en `dependabot.yml`.
- **PyJWT 2.15 avisa con claves HMAC de menos de 32 bytes**: el secreto de los tests tenía 31; lo alargué.
- **Una aprobación olvidada**: la corrida de #72 quedó un día esperando y PROD siguió con `/api/falla` (500). La aprobé al verlo en *Deployments*. Una aprobación pendiente es trabajo sin terminar.

### 8. Declaración de uso de IA (TP9)

Claude escribió el código y la configuración (`dependabot.yml`, `permissions`, `HEAD` en `/health`, Sentry, el arreglo de Mesas, #73), calculó DORA con `gh api` y redactó esta sección. Yo prendí las protecciones, creé los proyectos de Sentry y `SENTRY_DSN`, el monitor, la caída y la vuelta, y aprobé y mergeé. Lo verifiqué en *Security*, con `curl -I` a PROD, con el test de regresión que fallaba antes del arreglo, corriendo local los tests con las dependencias nuevas y contrastando DORA con los tiempos de los jobs.
