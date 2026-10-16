# Guía de adopción profesional para cualquier repositorio

> **Qué es esto.** Una guía autocontenida para llevar *cualquier* repo (nuevo o ya en producción) al estándar que
> construimos en los TP1–TP8: flujo Git con gate, contenedores, CI, tests con umbral, CD con ambientes y aprobación,
> imagen inmutable, integración/e2e como gate, e infraestructura como código. No depende de la materia, de este repo
> ni de un proveedor concreto: donde se usó Render/Neon/GHCR/Terraform se explica el **principio** y se da el ejemplo.
>
> **Quién la ejecuta.** Una persona o un agente (Claude Code). Si la ejecuta un agente: leé primero el §0.2 (protocolo).
>
> **Cómo se recorre.** Fases `F0`…`F10`. Cada fase tiene: *por qué*, *pasos*, *plantillas*, *definición de terminado (DoD)*
> con comandos de verificación, y *marcha atrás*. No se pasa a la fase siguiente sin cumplir la DoD de la anterior.

---

## Índice

0. Antes de empezar (alcance, protocolo, reglas para repos en producción)
1. Mapa: qué TP se convierte en qué práctica
2. F0 — Auditoría del repo (punto de partida)
3. F1 — Higiene del repo y flujo Git con gate
4. F2 — Contenedores reproducibles
5. F3 — Trazabilidad liviana (issues ↔ PRs ↔ releases)
6. F4 — CI como código
7. F5 — Calidad automatizada: tests, coverage, análisis, seguridad
8. F6 — El artefacto: publicar la imagen que pasó, y solo esa
9. F7 — CD: ambientes, aprobación humana, smoke test, rollback
10. F8 — Integración y e2e como gate de promoción
11. F9 — Infraestructura como código
12. F10 — Documentación viva (ADRs, runbook, README)
13. Transversales (secretos, observabilidad, backups, dependencias)
14. Checklist final: "¿este repo es profesional?"
15. Anexo A — Plantillas completas
16. Anexo B — Errores conocidos (los que ya nos pasaron)
17. Anexo C — Prompt de arranque para un agente

---

# 0. Antes de empezar

## 0.1 Qué se replica y qué se descarta

Los TP mezclaban **práctica profesional** con **andamiaje académico**. Esta guía replica lo primero y descarta lo segundo.

| Se replica (vale la pena) | Se descarta (era para la cátedra) |
|---|---|
| Rama `main` protegida; todo entra por PR con checks obligatorios | `evidencias.md` con capturas para cada TP |
| Dockerfile multi-etapa con etapa de tests; compose; healthchecks; `.env.example` | "Declaración de uso de IA" por TP (si te sirve, una línea en el README) |
| CI en YAML con cache, permisos mínimos y checks nombrados | PRs rojos dejados abiertos "de demo" para siempre |
| Tests con umbral de coverage que **rompe** el build | Un tag `vN.0.0` por TP: se usa SemVer real |
| Imagen etiquetada con el SHA, publicada solo si los tests pasaron | Guías "para la defensa oral" |
| Ambientes QA/PROD con secretos por ambiente y **aprobación humana** hacia PROD | Rechazos/aprobaciones "de ejemplo" para mostrar |
| Smoke test que verifica **qué commit** corre, no solo "que responde" | Elegir free tiers por precio aunque limiten (ver §9.9) |
| Integración + e2e como gate antes de PROD | Estado de Terraform en la notebook |
| Terraform con providers fijados, plan antes de apply, destroy/recreate probado | Un solo QA compartido sin plan de crecimiento |
| `decisiones.md` → ADRs: *qué elegí, por qué, qué pierdo, cómo lo verifiqué* | |

## 0.2 Protocolo de ejecución (obligatorio si lo hace un agente)

1. **Auditar antes de tocar** (F0). Producir la tabla de brechas y proponer el orden. Esperar confirmación.
2. **Un PR por fase** (o por paso, si la fase es grande). Nunca un PR gigante con todo. Cada PR con su DoD verificada.
3. **Acciones hacia afuera = confirmar primero**: cambiar settings del repo, crear secretos/environments, crear recursos
   cloud, publicar imágenes/releases, tocar producción. Mostrar el comando exacto y esperar un "sí".
4. **Secretos: jamás en el chat, en el repo, ni en el historial de la terminal.** Se cargan con `gh secret set NOMBRE --env X`
   (pide el valor por stdin) o por variables de entorno que escribe la persona. Si una clave apareció en un chat/log: se rota.
5. **Verificar de verdad.** "El comando no tiró error" no es evidencia. La evidencia es: el check verde en GitHub, el
   `/health` devolviendo el SHA esperado, el `plan` diciendo *No changes*. Cada DoD dice cuál es.
6. **Dejar un checkpoint** en `docs/adopcion.md` (qué fase está hecha, qué sigue, qué quedó pendiente). Permite retomar
   en otra sesión sin repetir decisiones.
7. **Respetar lo que ya existe.** Si el repo ya tiene CI/Docker/tests, se *adapta*, no se reemplaza. Se justifica cada reemplazo.
8. **Preguntar solo lo que no se pueda deducir**: proveedor cloud, si hay equipo (¿cuántas personas aprueban?), si el repo es
   público o privado (afecta qué features de GitHub existen), y qué es "producción" para ese proyecto.

## 0.3 Reglas especiales para repos que YA están en producción

Estas reglas pisan al resto de la guía:

- **Modo sombra primero.** Todo control nuevo (CI, coverage, escaneos) entra primero como *informativo* (no requerido) durante
  una semana o unos cuantos PRs; recién después pasa a *requerido* en la protección de rama. Así no se frena el trabajo por
  un falso rojo.
- **Los umbrales se fijan sobre lo medido hoy**, no sobre un ideal. Umbral = cobertura actual − ~10 puntos de colchón.
  Después se sube de a poco (*ratchet*). Un umbral aspiracional rompe `main` el primer día.
- **Nunca autodesplegar a producción en el primer día.** El primer CD hacia PROD nace **con** aprobación manual. El
  autodeploy sin aprobación (Continuous Deployment) es una decisión posterior y explícita (ver §9.1).
- **IaC sobre infraestructura existente = `import`, no `apply`.** Primero se *describe* lo que existe y se llega a un
  `plan` que diga **No changes**. Hasta entonces no se aplica nada (ver §11.8).
- **Cambios de base de datos**: nunca acoplar un deploy de código a una migración destructiva. Patrón *expand → migrate →
  contract* (agregar columna nueva compatible; desplegar; migrar datos; recién después borrar lo viejo).
- **Un hotfix tiene que seguir siendo posible.** Al proteger `main`, dejá `enforce_admins=false` hasta que el flujo esté
  probado; el camino de emergencia queda documentado en el runbook (§12.3), no improvisado.
- **Cada fase tiene "marcha atrás"** (se indica abajo). Si algo sale mal, se revierte la fase, no se improvisa.

---

# 1. Mapa: qué TP se convierte en qué práctica

| TP | Tema | Práctica profesional que se conserva | Fase |
|---|---|---|---|
| 1 | Git, PRs, conflictos, releases | `main` protegida, PRs, ramas cortas, release con SemVer, resolución de conflictos | F1 |
| 2 | Contenedores | Dockerfile multi-etapa, compose con healthchecks y volúmenes, `.env.example`, registry | F2 |
| 3 | Planificación y trazabilidad | Issues con plantilla, `Closes #N`, tablero con límite de WIP, definición de terminado | F3 |
| 4 | CI | Pipeline como código, triggers `pull_request`+`push`, cache con `scope`, check = gate | F4 |
| 5 | Testing y calidad | Pirámide, AAA, parametrizados, mocks, coverage con umbral, análisis estático, "romper el gate a propósito" | F5 |
| 6 | CD y ambientes | Publicar imagen solo si pasa; QA automático; PROD con *required reviewer*; smoke test; rollback medido; release | F6, F7 |
| 7 | Imagen inmutable + e2e | Build once/deploy many; SHA verificable en `/health`; integración y e2e como gate previo a PROD | F6, F8 |
| 8 | IaC | Terraform: providers fijados, plan→apply, estado, drift, destroy/recreate, `prevent_destroy` | F9 |
| 1–8 | `decisiones.md` | ADRs: decisión, motivo, costo, verificación | F10 |

**Orden de dependencias** (no saltear):

```
F0 auditoría
 └─ F1 higiene + flujo Git ──┬─ F3 trazabilidad (independiente, liviana)
                             └─ F2 contenedores ─ F4 CI ─ F5 calidad ─ F6 artefacto ─ F7 CD ─ F8 integración/e2e
                                                                                      └─────── F9 IaC (puede empezar tras F7)
                                                                                              F10 docs (se escribe a lo largo de todas)
```

---

# 2. F0 — Auditoría del repo (punto de partida)

**Objetivo:** saber exactamente qué hay y qué falta, sin modificar nada.

## 2.1 Relevamiento (solo lectura)

```bash
# Identidad del repo y remoto
git remote -v && git branch -a && git log --oneline -15 && git tag --list | tail
gh repo view --json name,visibility,defaultBranchRef,isPrivate,hasIssuesEnabled,viewerPermission

# Estructura y stack (¿qué lenguajes/gestores hay?)
git ls-files | head -200
ls -a                                   # .github/, Dockerfile, docker-compose*, infra/, Makefile, etc.
ls package.json requirements*.txt pyproject.toml go.mod pom.xml build.gradle *.csproj Gemfile Cargo.toml 2>/dev/null

# ¿Hay CI? ¿qué hace?
ls .github/workflows 2>/dev/null && cat .github/workflows/*.yml
gh run list --limit 10

# Protección de rama, settings de merge, environments, secretos (nombres), variables
gh api repos/{owner}/{repo}/branches/main/protection 2>&1 | head -40
gh api repos/{owner}/{repo}/rulesets --jq '.[].name' 2>&1
gh api repos/{owner}/{repo} --jq '{squash:.allow_squash_merge,merge:.allow_merge_commit,rebase:.allow_rebase_merge,delete_branch:.delete_branch_on_merge}'
gh api repos/{owner}/{repo}/environments --jq '.environments[].name' 2>&1
gh secret list; gh variable list

# Tests: ¿existen? ¿cuánto cubren?
git ls-files | grep -Ei '(^|/)(test|tests|__tests__|spec|e2e)(/|_|\.)' | head -50
# Y correr la suite una vez para medir (comando según stack, ver §7.1)

# Docker / IaC / docs
ls Dockerfile* */Dockerfile* docker-compose* infra/ terraform/ 2>/dev/null
ls README* CONTRIBUTING* CHANGELOG* docs/ .env.example .gitignore 2>/dev/null
```

También **preguntar** (si no se puede deducir): ¿dónde corre producción (proveedor, servicio)? ¿cuántas personas
commitean? ¿hay base de datos y migraciones? ¿qué pasa si producción cae 10 minutos (criticidad)? ¿hay datos personales?

## 2.2 Tabla de brechas (entregable de F0)

Completar una tabla así y guardarla en `docs/adopcion.md`:

| Área | Estado hoy | Brecha vs estándar | Riesgo de adoptar | Fase |
|---|---|---|---|---|
| Protección de `main` | ninguna | PR + checks obligatorios | bajo | F1 |
| `.gitignore` / `.env.example` | falta `.env.example` | agregar | nulo | F1 |
| Docker | Dockerfile simple | multi-etapa + test stage + healthcheck | bajo | F2 |
| CI | no hay | crear | nulo (modo sombra) | F4 |
| Tests | 12% cobertura | umbral al nivel medido | medio | F5 |
| CD | deploy manual por SSH | hook + aprobación | alto | F7 |
| IaC | todo manual | importar a Terraform | alto | F9 |

Marcar además **qué es crítico** (ej.: "no hay backups probados", "secretos en el repo"). Los hallazgos de seguridad
(secretos commiteados, credenciales en historial) se tratan **antes** que cualquier otra fase: rotar la credencial primero,
limpiar historial después (la rotación es lo que protege; reescribir historial no alcanza si el repo fue público).

## 2.3 DoD de F0
- [ ] `docs/adopcion.md` existe con la tabla de brechas y el orden propuesto, confirmado por la persona responsable.
- [ ] Se identificó qué es "producción" y quién puede aprobar un deploy.
- [ ] No se modificó nada fuera de `docs/adopcion.md`.

---

# 3. F1 — Higiene del repo y flujo Git con gate

**Por qué:** todo lo demás (CI, CD) se apoya en que `main` siempre sea desplegable y en que nada entre sin verificación.
Sin esto, el pipeline es decorativo.

## 3.1 Archivos base

1. **`.gitignore`** completo para el stack (dependencias, builds, `.env`, cobertura, reportes, estado de Terraform).
   Generá uno a partir de gitignore.io/GitHub templates y *sumá siempre*:
   ```
   .env
   .env.*
   !.env.example
   coverage/
   TestResults/
   playwright-report/
   test-results/
   *.tfstate
   *.tfstate.*
   .terraform/
   *.tfvars
   ```
   (**Ojo:** el `.gitignore` solo evita agregar archivos *nuevos*. Si algo ya está trackeado: `git rm --cached <archivo>`.)
2. **`.env.example`**: todas las variables que la app necesita, con valores **de ejemplo inofensivos** (nunca reales) y un
   comentario por variable. Es el contrato de configuración (principio 12-factor: la config va por entorno, no en el código).
3. **`README.md`** con: qué es, cómo levantarlo en 3 comandos, cómo correr tests, variables de entorno, estructura del repo,
   badge del CI, cómo se despliega (link a runbook). Estructura ideal en §12.4.
4. **`.editorconfig`** (indentación/finales de línea) y, si el stack lo tiene, formateador/linter con config versionada
   (se hace cumplir en F5).
5. **`CODEOWNERS`** (`.github/CODEOWNERS`): quién revisa qué (`*  @usuario` alcanza para empezar; con equipo, por carpeta).
6. **Plantilla de PR** (`.github/pull_request_template.md`, ver Anexo A.9): qué cambia, por qué, cómo se probó, `Closes #N`, riesgos.
7. **`.gitattributes`** con `* text=auto eol=lf` si el equipo mezcla Windows/Linux (evita diffs de fin de línea y scripts rotos).

## 3.2 Configuración del repositorio (settings)

Solo merge por **squash** (historial lineal, un commit por PR, el título del PR es el mensaje) y borrar ramas al mergear:

```bash
gh repo edit --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false --delete-branch-on-merge
```

Activar seguridad básica (gratis en repos públicos; en privados depende del plan): Dependabot alerts/updates, secret scanning,
push protection. Desde la web: *Settings → Code security*. Y `.github/dependabot.yml` (Anexo A.10).

## 3.3 Protección de `main` (el "gate")

Guardar como `protection.json` y aplicar. **Se aplica recién cuando el CI de F4 existe**, porque los `contexts` son nombres
de jobs que deben existir; hasta entonces dejá `contexts: []` (solo exige PR).

```json
{
  "required_status_checks": { "strict": true, "contexts": [] },
  "enforce_admins": false,
  "required_pull_request_reviews": { "required_approving_review_count": 0, "require_code_owner_reviews": false },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
```

```bash
gh api -X PUT repos/{owner}/{repo}/branches/main/protection --input protection.json
```

Decisiones que hay que tomar y escribir en un ADR:

- **`strict: true`** ("la rama debe estar al día con `main`"): el check verde solo vale si se corrió contra el `main` actual.
  Costo: botón *Update branch* cuando entra otro merge. Beneficio: nunca se mergea algo verificado contra un `main` que ya no existe.
- **`required_approving_review_count`**: con **equipo**, `1` como mínimo (más en código crítico). Trabajando **solo**, dejar `0`:
  GitHub no te deja aprobar tu propio PR, así que `1` te dejaría sin poder mergear. El gate real es el CI en verde; la revisión
  humana se sustituye por leer tu propio diff en *Files changed* antes de mergear (regla cultural, anotada en el ADR).
- **`enforce_admins`**: `false` mientras se adopta (hotfix posible); pasar a `true` cuando el flujo esté estable.
- **Nombres de checks**: el `id` del job (o el `name:` si lo definiste) es *literalmente* el nombre del check requerido.
  Renombrar un job después de exigirlo deja el merge bloqueado para siempre esperando un check que ya no existe (§Anexo B).
- Alternativa moderna: **rulesets** (`Settings → Rules → Rulesets`) — misma idea, más flexible (se aplican a varias ramas/tags,
  permiten bypass por rol). Usar uno u otro, no los dos con reglas contradictorias.

## 3.4 Flujo de trabajo diario

```bash
git switch main && git pull --ff-only
git switch -c feature/<descripcion-corta>      # o fix/, docs/, chore/
# ... trabajo, commits chicos y descriptivos ...
git push -u origin HEAD
gh pr create --fill --base main                # o con --title/--body; Closes #N en el body
# CI corre → verde → revisar el diff propio → gh pr merge --squash --delete-branch
```

Reglas:
- **Ramas cortas** (horas o pocos días). Cuanto más vive una rama, más probable el conflicto (TP1: dos ramas tocando la
  misma línea = Git no puede decidir, delega en vos).
- **Commits**: título imperativo y específico (`Fix: el formulario de mesas vuelve a mandar numero`). Opcional pero útil:
  prefijos Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`) — habilitan changelogs automáticos.
- **Resolver un conflicto**: `git fetch && git switch <rama> && git merge origin/main` → editar los marcadores
  (`<<<<<<<`, `=======`, `>>>>>>>`) decidiendo el contenido final → `git add` → `git commit` → push. Nunca borrar marcadores
  "a ciegas": se decide qué línea es la correcta. Ver estado antes de actuar: `git status`, `git diff`, `git log --oneline --graph`.
- **Nunca** `git push --force` sobre `main`. En ramas propias, `--force-with-lease`.

## 3.5 Versionado y releases (SemVer)

`MAJOR.MINOR.PATCH`: MAJOR rompe compatibilidad, MINOR agrega funcionalidad compatible, PATCH corrige. Un **tag anotado**
se pone sobre **el commit que efectivamente está desplegado**, no sobre "lo último de main" (ver §9.7).

```bash
git tag -a v1.4.0 <sha> -m "v1.4.0"
git push origin v1.4.0
gh release create v1.4.0 --verify-tag --generate-notes --title "v1.4.0"
```

`--verify-tag` falla si el tag no existe en el remoto (evita que GitHub cree uno nuevo sobre la punta de `main` por error).
Nunca mover/reescribir un tag ya publicado: se publica uno nuevo.

## 3.6 DoD de F1
- [ ] `git push origin main` directo es **rechazado** (probarlo: debe decir *protected branch*). `gh api .../branches/main/protection` lo confirma.
- [ ] Existe `.gitignore`, `.env.example`, README mínimo, plantilla de PR, CODEOWNERS.
- [ ] Solo squash-merge habilitado; ramas se borran al mergear.
- [ ] Se hizo un PR de prueba de punta a punta (rama → PR → merge squash).
- [ ] ADR de protección de rama escrito (qué se exige, por qué `review_count` vale lo que vale).

**Marcha atrás:** `gh api -X DELETE repos/{owner}/{repo}/branches/main/protection`.

---

# 4. F2 — Contenedores reproducibles

**Por qué:** "en mi máquina anda" desaparece cuando el entorno viaja con la app. Además, **el mismo Dockerfile** lo usan
el desarrollo, el CI y producción: no hay dos definiciones de build que puedan divergir (decisión central del TP4).

## 4.1 Principios

1. **Multi-etapa**: `build` (instala/compila) → `test` (corre la suite, *no viaja a producción*) → `runtime` (mínimo).
2. **Imagen de runtime mínima**: base `slim`/`alpine`/distroless, sin compiladores ni devDependencies, **usuario no-root**.
3. **Base fijada**: `python:3.13-slim`, `node:22-alpine`, `nginx:1.27-alpine` — nunca `latest`. (Opcional avanzado: fijar por digest.)
4. **Orden de capas por frecuencia de cambio**: primero manifests de dependencias (`requirements.txt`, `package*.json`),
   `install`, y *después* el código. Así el cache de capas sobrevive a cambios de código.
5. **`.dockerignore`** (excluir `.git`, `node_modules`, `.env`, `coverage`, tests del runtime, etc.): build más rápido y sin filtrar secretos.
6. **Config por variables de entorno**, jamás horneada en la imagen (una imagen sirve para todos los ambientes).
   Ejemplo del TP7: el front lee `BACKEND_URL` al arrancar (plantilla de nginx con `envsubst`), no al compilar.
7. **Healthcheck** en la imagen o en compose y un endpoint `/health` en el backend que además haga un `SELECT 1` a la base.
8. **El SHA viaja dentro de la imagen** (`ARG GIT_SHA` → `ENV GIT_SHA`) y `/health` lo devuelve. Es lo que permite al smoke test
   comprobar *qué commit corre* (F7). Va al final del Dockerfile para no invalidar el cache de lo anterior.
9. **Un proceso por contenedor**; logs a stdout/stderr (no a archivos).

## 4.2 Plantillas

Las plantillas completas (Python/FastAPI, Node+nginx, y notas para Go/Java/.NET) están en el **Anexo A.1–A.3**.
La etapa `test` es la pieza clave: el CI la construye con `--target test` y la corre, de modo que **el CI ejecuta los tests
dentro del mismo entorno que la imagen final**.

## 4.3 docker-compose para desarrollo y pruebas locales

Requisitos del compose profesional (Anexo A.4):
- Base de datos con **volumen nombrado** (persistencia: el dato sobrevive a `down`; solo `down -v` lo borra) y **healthcheck**
  (`pg_isready`).
- `depends_on: { db: { condition: service_healthy } }` — arrancar en orden *real*, no solo "el contenedor existe".
- Variables vía `.env` (`${VAR}` con defaults donde corresponda), nunca valores reales escritos en el YAML.
- Puertos explícitos y documentados en el README.
- `restart: unless-stopped` para servicios de larga vida.

Verificación de persistencia (hacerla una vez y dejarla anotada):
```bash
docker compose up -d --build
# crear un dato vía API/UI
docker compose down            # SIN -v
docker compose up -d
# el dato sigue ahí → el volumen funciona
```

## 4.4 DoD de F2
- [ ] `docker compose up -d --build` levanta todo desde cero con solo copiar `.env.example` a `.env`.
- [ ] `docker build --target test ./<componente>` corre la suite dentro del contenedor.
- [ ] La imagen final no contiene tests ni devDependencies y corre como no-root (`docker run --rm <img> id`).
- [ ] `curl localhost:<puerto>/health` → 200 con `{"status":"healthy","sha":...}`.
- [ ] Persistencia verificada (`down`/`up` sin `-v` conserva datos).
- [ ] Comparación de tamaño anotada (`docker images`): sirve de línea base.

**Marcha atrás:** los Dockerfiles viejos están en git; el compose nuevo no toca producción.

---

# 5. F3 — Trazabilidad liviana

**Por qué:** poder responder "¿por qué existe este cambio?" y "¿qué se entregó en esta release?" sin arqueología.
Se conserva lo esencial del TP3, sin la ceremonia.

## 5.1 Pasos

1. **Plantillas de issue** (`.github/ISSUE_TEMPLATE/`): *Bug* (pasos para reproducir, esperado vs real, entorno) y *Historia*
   (Como `<rol>` quiero `<capacidad>` para `<beneficio>` + criterios de aceptación). Anexo A.11.
2. **Etiquetas** mínimas: `bug`, `feature`, `chore`, `docs`, `bloqueado`, y de prioridad si hace falta.
3. **Tablero** (GitHub Projects, vista Board): columnas `Backlog → Listo → En curso → En revisión → Hecho`.
   **Límite de WIP**: regla de arranque = (personas + 1). Si nunca lo tocás, está muy alto; si siempre lo tocás, muy bajo.
4. **Cada PR referencia su issue** con una palabra clave *literal* en el body: `Closes #N` / `Fixes #N` / `Resolves #N`.
   Es puramente textual: GitHub no entiende el contenido, busca la palabra clave. Al mergear a la rama por defecto, el issue
   se cierra solo.
5. **Escribir bien una historia**: una historia es valor observable por alguien, no una tarea técnica. "Crear la tabla usuarios"
   es una **tarea**; la historia es "Como usuario quiero iniciar sesión para acceder solo a mi información". Las tareas son
   sub-issues de la historia (`gh issue edit <hist> --add-sub-issue <tarea>`), y una épica agrupa historias.
6. **Definición de terminado (DoD)** del equipo, en `CONTRIBUTING.md`: tests agregados/actualizados, CI verde, docs al día,
   PR revisado, sin secretos, issue referenciado.
7. **Sprint/cadencia** (si se usa Scrum): duración fija (2 semanas por defecto). Si es Kanban: solo WIP y flujo continuo.
   Elegir uno y escribirlo; mezclar sin criterio es ruido.

## 5.2 Notas de uso de `gh` (aprendidas)

- Para `gh project ...` hace falta scope: `gh auth refresh -s project`.
- Cuerpos largos o con comillas: `--body-file archivo.md` (evita problemas de quoting en PowerShell/bash).
- En PowerShell no existe la continuación con `\`; usar una línea o here-strings `@' ... '@`.

## 5.3 DoD de F3
- [ ] Plantillas de issue y de PR activas (aparecen al crear uno desde la web).
- [ ] Un PR de prueba cerró su issue automáticamente con `Closes #N`.
- [ ] Tablero creado con límite de WIP definido y justificado en un ADR de una línea.

**Marcha atrás:** borrar los archivos de `.github/`; no afecta al código.

---

# 6. F4 — CI como código

**Por qué:** integración continua es una *práctica* (integrar seguido y verificar cada integración); el pipeline es la herramienta
que la hace automática. Sin que el pipeline sea **requisito de merge**, no es CI.

## 6.1 Diseño

- **Triggers**: `pull_request` hacia `main` **y** `push` a `main`. No son redundantes:
  - `pull_request` verifica el cambio propuesto *antes* de mezclar (alimenta el gate).
  - `push` verifica `main` *después* de cada merge, mantiene el badge en estado real, calienta el cache y es el único que
    luego publica y despliega (F6/F7).
- **Un job por componente independiente** (backend, frontend), sin `needs:` entre sí → corren en paralelo, un error en uno
  no oculta el estado del otro. Con matriz: `name: build-${{ matrix.component }}` para que el check se llame `build-backend`.
- **Permisos mínimos**: `permissions: contents: read` a nivel workflow; cada job pide solo lo que necesita (`packages: write`
  únicamente donde publica). Es defensa contra que un paso comprometido tenga más poder del necesario.
- **Cache de capas Docker** con buildx: `cache-from/cache-to: type=gha,scope=<nombre-único>`. **`scope` distinto por job**,
  si no los jobs se pisan el estante y el cache "parpadea" sin razón aparente. Si el cache desaparece, el pipeline debe
  funcionar igual (solo más lento): si falla sin cache, había una dependencia escondida.
- **Construir con el Dockerfile** (no con `pip install` / `npm run build` sueltos en el YAML): una sola definición de build.
- **Concurrencia**: cancelar corridas viejas del mismo PR (`concurrency` con `cancel-in-progress` solo en PRs).
- **Timeouts** en cada job (`timeout-minutes`), para que un cuelgue no consuma horas.
- **Versiones de actions fijadas** (por major como mínimo; por SHA de commit en entornos exigentes) y mantenidas por Dependabot.
- **Reportes siempre**: `if: ${{ !cancelled() }}` en la subida de artefactos y resumen, porque el reporte importa **más**
  cuando algo falla (`success()` es el default y lo omitiría).
- **Resumen en la corrida**: escribir a `$GITHUB_STEP_SUMMARY` el coverage y el resultado.

La plantilla completa está en **Anexo A.5** (CI de build+test). Ahí mismo se ve cómo se agrega la publicación (F6).

## 6.2 Pasos

1. Crear `.github/workflows/ci.yml` desde la plantilla, adaptando componentes y rutas.
2. Abrir un PR y verificar que corre. Mirar el log: ¿construye con el Dockerfile? ¿qué tarda?
3. **Probar el cache**: segundo push al mismo PR (esperando a que termine la primera corrida). En el log de la segunda debe
   verse `CACHED` en las capas de instalación de dependencias.
4. Agregar el **badge** al README:
   `![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)`
5. Recién ahora, **marcar los jobs como requeridos** (rellenar `contexts` en `protection.json` con los nombres exactos que
   muestra la UI de checks y re-aplicar). En repo en producción: una semana en modo sombra antes (§0.3).
6. **Probar que el gate frena**: PR descartable que rompe algo a propósito (una dependencia inexistente en `requirements.txt`,
   por ejemplo) → check rojo → el botón de merge queda bloqueado → arreglar → verde. Cerrar el PR sin mergear. (Tip: si
   rompés y arreglás la misma línea en el mismo PR, "Files changed" queda vacío; la evidencia está en la pestaña *Commits*
   y en el historial de *Actions*.)
7. **Probar `strict`**: con dos PRs abiertos, mergear uno; el otro debe mostrar *Update branch*.

## 6.3 DoD de F4
- [ ] CI corre en cada PR y en cada push a `main`; jobs paralelos; permisos mínimos.
- [ ] `CACHED` visible en la segunda corrida.
- [ ] Los checks son **requeridos** en `main` y se comprobó que un rojo bloquea el merge.
- [ ] Badge en README. ADR: por qué esos triggers, qué se cachea, qué exige el gate.

**Marcha atrás:** quitar los `contexts` de la protección (`PUT` con `contexts: []`); el workflow puede borrarse sin efecto en producción.

---

# 7. F5 — Calidad automatizada

**Por qué:** un pipeline que solo compila no verifica comportamiento. Los tests con umbral convierten la calidad en
**requisito** (si baja, el merge se frena), no en un reporte que nadie mira.

## 7.1 Qué testear (pirámide)

```
        /\        e2e (pocos, lentos, frágiles)           → F8
       /  \       integración (API real + base real)       → F8
      /----\      unitarios (muchos, rápidos, aislados)    ← esta fase
```

Testear primero **la lógica de negocio con decisiones**: cálculos (totales, descuentos, impuestos), reglas (transiciones de
estado válidas, solapamientos de reservas), validaciones, autorización/ownership. **No** testear getters, DTOs ni código del
framework: sube el número y no baja el riesgo.

Comandos por stack (para medir y para el gate):

| Stack | Test + coverage | Umbral que rompe el build | Lint / estático |
|---|---|---|---|
| Python | `pytest --cov --cov-branch` | `fail_under` en `.coveragerc` | `ruff check`, `ruff format --check`, `mypy` |
| Node/JS/TS | `vitest run --coverage` / `jest --coverage` | `thresholds` en config | `eslint`, `tsc --noEmit`, `prettier --check` |
| Go | `go test ./... -coverprofile=c.out` | script que compara `go tool cover -func` con el umbral | `golangci-lint run`, `go vet` |
| Java | `mvn verify` + JaCoCo | regla `check` en JaCoCo | `checkstyle`, `spotbugs` |
| .NET | `dotnet test` + coverlet | `/p:Threshold=70 /p:ThresholdType=line` | `dotnet format --verify-no-changes`, analyzers |

## 7.2 Cómo escribir los tests

- **AAA** (Arrange–Act–Assert) en bloques visibles. Un test = una razón para fallar. Nombre = comportamiento esperado
  (`test_pedido_cerrado_no_admite_nuevos_items`).
- **Parametrizados** para tablas de casos (`@pytest.mark.parametrize` / `test.each`): mismas aserciones, muchos datos.
- **Caso de error obligatorio** por regla: no solo el camino feliz (`pytest.raises`, `expect(...).toThrow`).
- **Mock solo en el borde**: mockeá lo no determinista o externo (reloj, red, email, pasarela de pago), no tu propia lógica.
  Si para mockear hay que reestructurar, el refactor mínimo es inyectar la dependencia en vez de importarla fija
  (el código queda mejor *y* testeable).
- **Aislamiento**: tests que no dependen del orden ni del reloj real ni de datos compartidos. **Cuidado con zonas horarias**:
  un test que usa `date.today()` (UTC en el runner) contra lógica en hora local falla solo entre las 00:00 y las 03:00 UTC.
  Fijar el reloj o calcular la fecha con la misma zona que usa el código.
- **Base de datos en tests unitarios**: SQLite en memoria o dobles; la base real se ejerce en F8.

## 7.3 Coverage y el umbral

1. **Medir** con cobertura de **ramas** (branch), no solo líneas.
2. **Excluir con criterio y por escrito** lo que no es lógica (arranque, config, modelos ORM declarativos, `main`), en
   `.coveragerc` / config del runner, con un comentario de por qué. Excluir "lo que cuesta testear" es hacer trampa.
3. **Fijar el umbral**: `medido hoy − ~10 puntos`. Ej.: 80.8 % hoy → umbral 70 %. Justificarlo en un ADR.
   - Un umbral igual a lo medido se rompe con cualquier refactor; uno ridículamente bajo no frena nada.
   - **Ratchet**: cuando la cobertura sube de forma sostenida, subir el umbral. Nunca bajarlo para "hacer pasar" un PR.
4. **El umbral debe romper el build en CI de verdad** (exit code ≠ 0) en **todos los componentes** (backend y frontend).
5. **Coverage por PR** (opcional): comentar la cobertura del *diff* (Codecov/Coveralls o `diff-cover`) para que el código
   nuevo no entre sin tests aunque el promedio global aguante.
6. **Por qué coverage alto no garantiza calidad**: mide qué líneas *se ejecutaron*, no si se *verificó* algo. Un test sin
   aserciones da 100 %. Para medir si los tests detectan errores existe *mutation testing* (`mutmut`, `Stryker`, `PIT`):
   opcional, útil en módulos críticos.

## 7.4 Seguridad en el pipeline (barato y de alto retorno)

Agregar como jobs informativos primero (modo sombra), requeridos después:

| Qué | Herramienta ejemplo | Qué encuentra |
|---|---|---|
| Secretos commiteados | `gitleaks` (action `gitleaks/gitleaks-action`) | claves/tokens en código e historial |
| Dependencias vulnerables | `pip-audit`, `npm audit --omit=dev`, Dependabot | CVEs en librerías |
| Imagen | `trivy image` / `trivy fs` | CVEs del SO y de dependencias en la imagen |
| Código | CodeQL (`github/codeql-action`) | patrones inseguros (inyección, etc.) |
| IaC | `tfsec` / `checkov` | configuraciones inseguras en Terraform |

Política: severidad `HIGH/CRITICAL` con fix disponible = bloquea; el resto = reporte.

## 7.5 Demostrar que el gate frena (obligatorio una vez)

Con el umbral puesto, probar **las dos direcciones** con PRs descartables:
1. PR que **borra/rompe un test** o agrega código sin cubrir → coverage cae bajo el umbral → CI rojo → merge bloqueado.
2. Se agrega el test que cubre la rama → vuelve a verde.
Anotar los números (antes/después). Es la evidencia de que el gate no es de adorno.

## 7.6 DoD de F5
- [ ] Suite ≥ 1 test significativo por regla de negocio, con parametrizados, casos de error y al menos un mock en un borde.
- [ ] El umbral está definido en config versionada, **rompe el build** en CI en cada componente y está justificado (ADR).
- [ ] Reportes (XML/HTML/JUnit) subidos como artefactos y resumen en `$GITHUB_STEP_SUMMARY`.
- [ ] Linter/formatter corren en CI (o están en el plan con fecha).
- [ ] Escaneo de secretos y de dependencias activo.
- [ ] Gate probado en rojo y en verde.

**Marcha atrás:** subir el umbral a 0 en config (temporal y con ADR) — nunca borrar los tests.

---

# 8. F6 — El artefacto: publicar la imagen que pasó, y solo esa

**Por qué:** si cada ambiente reconstruye desde el código, "lo que probaste" y "lo que desplegaste" pueden diferir (otra
versión de una dependencia, otro día, otro build). **Build once, deploy many**: se construye UNA vez, se verifica, y esa
misma imagen sube QA → PROD. Se promueve el artefacto, no el código.

## 8.1 Reglas

1. **Registry** con control de acceso (ghcr.io, ECR, GAR, ACR, Docker Hub). Con ghcr.io + GitHub Actions:
   - Workflow: `permissions: packages: write` en el job que publica + login con `${{ secrets.GITHUB_TOKEN }}`.
   - Settings del repo → Actions → *Workflow permissions*: **Read and write**.
   - Una vez por paquete (cuentas personales): *Package settings → Manage Actions access → Add repository → Write*.
   - Si el proveedor de hosting tira de la imagen **sin credenciales**, el paquete debe ser **público**; si la imagen es
     privada hay que darle credenciales de registry al proveedor. Decisión explícita (¿hay algo secreto en la imagen? No debería:
     la config va por env vars).
2. **Etiqueta inmutable = commit**: `ghcr.io/<owner>/<repo>-<componente>:sha-<40 caracteres>`. Nunca se reetiqueta ni se pisa.
   Etiquetas móviles (`latest`, `main`) son opcionales y **nunca** se despliegan. Con versión: además `:1.4.0` al hacer release.
   Mejor aún (avanzado): desplegar por **digest** (`@sha256:...`), que es inmutable por construcción.
3. **Se publica solo si los tests pasaron y solo desde `main`**: el orden de pasos *es* la condición. Los tests corren antes en
   el mismo job (o en un job del que `build` depende con `needs:`); el `push` de la imagen queda condicionado a
   `github.event_name == 'push' && github.ref == 'refs/heads/main'`.
4. **El PR construye pero no publica** (verifica que la imagen se puede construir; no ensucia el registry con ramas).
5. **`GIT_SHA` como build-arg** (ver F2) para que `/health` diga qué commit corre.
6. **`provenance: false` / `sbom: false`** en `build-push-action` si no vas a darle los permisos extra (`attestations: write`,
   `id-token: write`); si querés atestaciones de cadena de suministro, activalas y dale esos permisos (mejora de seguridad).
7. **Cleanup**: política de retención en el registry (borrar `sha-*` de más de N días salvo los release).

La plantilla (publicación incluida) está en el **Anexo A.5**.

## 8.2 DoD de F6
- [ ] En `main`, el pipeline publica `…:sha-<commit>` de cada componente; en un PR no publica.
- [ ] La imagen se puede bajar desde donde la va a consumir el ambiente (`docker pull` desde una máquina sin tu login si es pública).
- [ ] `docker run … /health` devuelve el SHA correcto.

**Marcha atrás:** quitar el paso de publicación; las imágenes ya publicadas no afectan a nadie.

---

# 9. F7 — CD: ambientes, aprobación humana, smoke test, rollback

## 9.1 La escalera (decidir y escribir cuál se está)

- **CI**: cada integración se verifica.
- **Continuous Delivery**: cada commit verde queda *desplegable*; el paso a PROD es una **decisión humana** (botón/aprobación).
- **Continuous Deployment**: cada commit verde va a PROD solo, sin humano. Exige tests fuertes, feature flags, observabilidad
  y rollback automático. **Empezar siempre por Delivery.** (ADR: por qué.)

## 9.2 Ambientes

| Ambiente | Para qué | Cómo se despliega | Base de datos |
|---|---|---|---|
| `qa` / `staging` | verificar lo que va a salir, con la imagen real | **automático** en cada merge a `main` | propia (nunca la de PROD) |
| `production` | usuarios reales | **con aprobación humana** | propia |
| `preprod` / efímeros (opcional) | réplica de PROD / ambiente por PR | creados por IaC (F9) | propia |

**Aislamiento de datos**: cada ambiente con su base y sus credenciales. Verificarlo: crear un registro en QA y comprobar que
**no** aparece en PROD. Es el error más caro de ambientes copiados a mano (un entorno apuntando a la base del otro).

## 9.3 GitHub Environments y secretos por ambiente

Los secretos y variables viven **dentro del environment**, de modo que solo un job con `environment: production` puede leer
las credenciales de PROD. Un job de QA nunca ve un secreto de PROD.

```bash
# Crear environments (qa sin protección; production con reviewers)
gh api -X PUT repos/{owner}/{repo}/environments/qa
ME=$(gh api user --jq .id)
cat > env-prod.json <<EOF
{ "reviewers": [ { "type": "User", "id": $ME } ],
  "prevent_self_review": false,
  "deployment_branch_policy": { "protected_branches": false, "custom_branch_policies": true } }
EOF
gh api -X PUT repos/{owner}/{repo}/environments/production --input env-prod.json
gh api -X POST repos/{owner}/{repo}/environments/production/deployment-branch-policies -f name=main

# Secretos (el valor lo pide por stdin: no queda en el historial) y variables (no secretas)
gh secret set DEPLOY_HOOK_API --env qa
gh secret set DEPLOY_HOOK_API --env production
gh variable set API_URL    --env qa         --body "https://api-qa.ejemplo.com"
gh variable set API_URL    --env production --body "https://api.ejemplo.com"
```

Notas:
- *Required reviewers* en repos **privados** exige plan de pago (Team/Enterprise); en repos públicos es gratis. Si no está
  disponible, el equivalente es un workflow `workflow_dispatch` manual solo para PROD, protegido por permisos del repo.
- Con **equipo**, `prevent_self_review: true` (quien disparó no aprueba su propio deploy). Trabajando **solo**, `false`.
- `deployment_branch_policy`: solo `main` puede desplegar a PROD (un job desde una rama cualquiera queda bloqueado).
- Variables ≠ secretos: URLs públicas van como variables; tokens, hooks y claves como secretos. Un deploy hook **es** un secreto
  (cualquiera con la URL puede disparar un deploy).

## 9.4 El job de deploy a QA (automático)

Estructura (plantilla completa en **Anexo A.6**):

```yaml
deploy-qa:
  needs: [build-backend, build-frontend]       # sin CI verde no hay deploy
  if: github.ref == 'refs/heads/main'          # los PR verifican; solo main despliega
  environment: qa
  steps:
    - name: Desplegar la IMAGEN de este commit
      run: ...        # mecanismo según proveedor (ver 9.5)
    - name: Smoke test (espera a que QA conteste con ESTE commit)
      run: ./scripts/smoke.sh ...
```

## 9.5 Mecanismos de deploy según proveedor (elegí uno; el principio es el mismo)

El proveedor debe **ejecutar la imagen etiquetada con el SHA**, no reconstruir desde el repo, y el *auto-deploy propio del
proveedor debe estar apagado* (si no, hay dos caminos de deploy y el pipeline deja de ser el único).

| Proveedor | Cómo se le dice "corré esta imagen" |
|---|---|
| Render (servicio de imagen) | Deploy Hook + `imgURL=<imagen>:sha-<sha>` (`curl --get --data-urlencode "imgURL=..." "$HOOK"`; **la URL del hook va última**) |
| Fly.io | `flyctl deploy --image ghcr.io/…:sha-…` |
| Google Cloud Run | `gcloud run deploy <svc> --image …` (auth por OIDC / Workload Identity, sin claves largas) |
| AWS ECS/App Runner | `aws ecs update-service` con task definition nueva / `apprunner update-service` (auth por OIDC) |
| Azure Container Apps | `az containerapp update --image …` |
| Kubernetes | `kubectl set image` / `helm upgrade --set image.tag=sha-…` / GitOps (Argo CD, Flux) |
| VPS propio | `ssh` + `docker compose pull && up -d` con tag fijo (menos recomendable: llave larga en secretos) |

Preferir **autenticación federada por OIDC** (el job obtiene un token efímero) a guardar claves de larga duración como secreto.

## 9.6 El smoke test: probar *qué corre*, no solo *que responde*

Un `curl /health` → 200 pasa también si sigue corriendo la **versión vieja**. El smoke profesional comprueba:

1. **Identidad**: `/health` devuelve el `sha`; el script **reintenta hasta que sea igual a `$GITHUB_SHA`** (mientras el
   proveedor despliega, contesta el SHA viejo: es esperable, se reintenta).
2. **Dependencias**: el health hace `SELECT 1` (la base responde).
3. **Camino real**: registrar/loguear un usuario de prueba (idempotente: 201 la primera vez, 409 las siguientes = ambos OK) y
   leer un endpoint autenticado → atraviesa API + auth + base.
4. **Front servido** (200 en `/`).
5. **Reintentos largos** (p. ej. 30 × 20 s): los free tiers duermen el servicio y el *cold start* tarda 30–60 s.
6. **Falla ruidosa**: si agota los intentos, `exit 1` y el job queda rojo.

Limitación a documentar: si solo el backend expone su SHA, el SHA del front no se valida. (Mitigación: servir un
`/version.json` desde el front.)

Script reutilizable: **Anexo A.7**.

## 9.7 El gate hacia PROD y la release

```yaml
deploy-prod:
  needs: [deploy-qa, integracion, e2e]     # (integracion/e2e llegan en F8)
  if: github.ref == 'refs/heads/main'
  environment: production                  # required reviewer: el job queda "Waiting"
  concurrency: { group: deploy-prod, cancel-in-progress: false }
```

- **`concurrency` con `cancel-in-progress: false`**: nunca dos deploys a PROD a la vez, y un deploy en curso no se corta a
  la mitad (dejaría el ambiente medio desplegado). Limitación: no resuelve dos aprobaciones pendientes simultáneas →
  **rechazar a mano la vieja**.
- **Qué mira quien aprueba** (escribirlo en el runbook): ¿qué commit/qué PR es (Summary del run)? ¿QA verde con ESE commit?
  ¿integración y e2e verdes? ¿es horario razonable para desplegar? ¿hay un incidente abierto? ¿hay migración de base?
- **Rechazar con un motivo propio y específico** (queda en el historial del deployment). Una frase genérica no sirve de auditoría.
- **Runs que quedan "esperando"**: cada merge posterior a `main` genera un `deploy-prod` pendiente. Quien aprueba debe
  **elegir cuál** aprobar; los que ya no se van a desplegar se rechazan con comentario para no dejar pendientes colgados.
- **Release = el commit que realmente está en PROD**, no la punta de `main` (puede haber entrado otro merge sin aprobar):
  ```bash
  SHA=$(gh api 'repos/{owner}/{repo}/deployments?environment=production' --jq '.[0].sha')
  git tag -a v1.4.0 $SHA -m "v1.4.0" && git push origin v1.4.0
  gh release create v1.4.0 --verify-tag --generate-notes
  ```
  La imagen de esa release es `…:sha-$SHA`: tag → commit → imagen es una cadena sin ambigüedad.

## 9.8 Deployment patterns y rollback

**Patrones** (elegir uno para PROD y justificar en un ADR; el free tier suele limitarte a *recreate/rolling*):

| Patrón | Idea | Riesgo / costo | Cuándo |
|---|---|---|---|
| Recreate | apagar viejo, levantar nuevo | downtime | internos, bajo tráfico |
| Rolling | reemplazar instancias de a poco | versiones mezcladas un rato (compatibilidad API/DB) | default razonable |
| Blue/Green | dos ambientes completos; se conmuta el tráfico | doble costo; rollback instantáneo | crítico |
| Canary | % chico de tráfico a la versión nueva, se amplía si las métricas aguantan | requiere métricas y routing | alto tráfico |
| Feature flags | desplegar apagado, prender gradualmente | deuda de flags | desacopla deploy de release |

**Rollback** = volver a desplegar **una imagen anterior ya publicada** (por eso no se reconstruye ni se borran imágenes viejas).
Procedimiento a escribir en el runbook y **medir una vez en serio**:
1. Identificar el SHA bueno anterior (`gh api .../deployments?environment=production` o la release previa).
2. Disparar el mismo mecanismo de deploy con esa imagen.
3. Cronometrar hasta que el ambiente corra la versión vieja (verificado con `/health`). Registrar el tiempo real → **RTO medido**.
4. Hallazgo real del TP6 a tener en cuenta: el parámetro `ref` de un hook que reconstruye desde Git **no** garantiza desplegar
   un commit distinto de la punta; con imágenes por tag/digest el problema desaparece (otra razón para F6). Y el botón
   "Manual Deploy" de algunos proveedores re-despliega lo configurado en Settings, no lo último: puede *retroceder* sin avisar.
   Documentar qué mecanismos **no** usar.
5. Rollback con base de datos: si hubo migración, el rollback de código solo es seguro si la migración fue *expand-only*
   (§0.3). Si no, requiere plan específico.

## 9.9 La letra chica de los free tiers (decidir con los ojos abiertos)

- Servicios que **se duermen** por inactividad (cold start 30–60 s): el smoke necesita reintentos largos; antes de una demo,
  despertar con un `curl /health`.
- Horas mensuales **compartidas por workspace** (p. ej. 750 h): ambientes efímeros se destruyen al terminar la sesión.
- Bases que **se pausan/expiran** (algunos free tiers): verificar política antes de usarlas para algo que importa.
- Límites de retención/ancho de banda/builds. Si el proveedor exige tarjeta, entender qué se cobra al exceder.
- Un free tier no es un SLA: para PROD real, pasar a plan pago con backups y soporte. Anotarlo como límite conocido.

## 9.10 DoD de F7
- [ ] Un merge a `main` despliega solo a QA y el smoke queda verde con **el SHA del commit**.
- [ ] `production` exige aprobación; se vio un job quedar en *Waiting*, y se hizo **un rechazo (con motivo propio)** y **una aprobación**.
- [ ] Secretos de PROD solo en el environment `production`; auto-deploy del proveedor **apagado** en todos los servicios.
- [ ] Verificación de aislamiento de datos QA ≠ PROD.
- [ ] Release/tag sobre el commit de PROD (obtenido de Deployments).
- [ ] Rollback ejecutado y **cronometrado**; tiempo anotado en el runbook.
- [ ] ADR: Delivery vs Deployment, pattern elegido, límites del proveedor, qué prueba y qué no el smoke.

**Marcha atrás:** quitar el job `deploy-prod`; los deploys manuales anteriores siguen siendo válidos (por eso el runbook los documenta).

---

# 10. F8 — Integración y e2e como gate de promoción

**Por qué:** hasta acá se probó cada pieza (unit) y que "arranca" (smoke). Falta probar que **las piezas trabajan juntas en el
ambiente real**. Estas suites corren *después* de desplegar a QA y *antes* de poder aprobar PROD.

## 10.1 Dos escalones

| Escalón | Qué hace | Herramienta ejemplo | Rápido/estable |
|---|---|---|---|
| **Integración** | Le pega a la **API desplegada** con su base real, sin navegador ni dobles | Playwright `request`, `supertest`, `pytest`+`httpx`, Postman/Newman | rápido, estable |
| **e2e** | Un **navegador real** usa el front desplegado | Playwright (recomendado), Cypress | lento, más frágil |

La integración es el escalón **ancho** (muchos casos de API: validaciones, permisos, ownership, flujos), el e2e el **angosto**
(pocos flujos críticos de usuario: registrarse → loguearse → crear → ver). Si algo falla en la API, el e2e ni se ejecuta
(`needs: integracion`): no se gasta un browser en confirmar lo que la API ya dijo.

## 10.2 Cómo escribirlas bien

- **Flujos con valor**: los 3–5 caminos de los que depende el negocio. No testear en e2e lo que ya cubre un unit.
- **Datos aislados e idempotentes**: usuarios de prueba fijos (`e2e-a@...`, `e2e-b@...`, registro tolerante a 409) y entidades con
  **identificador único por corrida** (timestamp + random) para que correr dos veces no choque. Limpiar si el ambiente lo
  necesita. Dos usuarios permiten probar permisos (A no ve lo de B).
- **Selectores estables**: por rol/etiqueta/`data-testid`, no por clases CSS o texto frágil.
- **Esperas por condición**, nunca `sleep` fijo (auto-wait de Playwright, `expect(...).toBeVisible()`).
- **Timeouts generosos para el cold start** (60 s por test, 15 s por aserción) pero **timeout de job** que corte cuelgues.
- **Flaky tests**: 1 *retry* absorbe una demora suelta y el reporte lo marca como *flaky* (señal para arreglarlo). Más retries
  esconden bugs. Un test flaky se arregla o se borra, no se ignora. `workers: 1` si comparten la base de QA.
- **Trazas y screenshots solo ante fallo** (`trace: 'on-first-retry'`, `screenshot: 'only-on-failure'`) y el **reporte HTML
  se sube siempre** como artefacto (`if: !cancelled()`, nombres distintos por job o la corrida se rompe).
- **Probar localmente primero** contra el compose (F2), con las dos URLs separadas (`API_BASE_URL`, `E2E_BASE_URL`).
- Vitest/Jest **excluyen** la carpeta `e2e/` (no deben recoger los specs de Playwright).

Plantillas: config y specs de ejemplo en **Anexo A.8**; los jobs de CI en **Anexo A.6**.

## 10.3 Demostración del gate: romper la APP, no el test

Una suite que nunca se vio fallar no demuestra nada. Protocolo (una vez):
1. En un PR, introducir un bug **real en la aplicación** que la API sigue aceptando pero rompe la experiencia (p. ej. el front
   manda un campo renombrado). Los unit siguen verdes (no lo ven).
2. Mergear. Esperado: `deploy-qa` ✔, `integracion` ✔ (la API en sí está bien), `e2e` ✘, `deploy-prod` **skipped** (ni
   pide aprobación). Descargar el reporte del run rojo (artefacto) y guardar el análisis.
3. Arreglar en otro PR; run completo en verde; recién entonces aprobar PROD.
4. Anotar en el ADR **qué dice el par verde/roja**: qué capa vio el bug y cuál no, y por qué.

## 10.4 Límites conocidos (documentarlos)

- **Un solo QA compartido**: dos merges seguidos pueden pisarse las suites. Mitigación hoy: mergear de a uno. Evolución:
  ambientes efímeros por PR (F9) o cola de despliegues.
- Los usuarios de prueba quedan en QA (aceptable) pero **nunca** correr e2e destructivos contra PROD.
- Tiempo del pipeline: cada gate suma minutos; paralelizar lo independiente y mantener el e2e corto.

## 10.5 DoD de F8
- [ ] `integracion` y `e2e` corren en CI contra QA tras `deploy-qa`; `deploy-prod` depende de ambos.
- [ ] Probadas en local contra compose y en CI contra QA.
- [ ] Se vio una corrida roja real frenando PROD y su corrección (con reporte archivado).
- [ ] ADR: pirámide (qué cubre cada capa), flaky policy, límite del QA compartido.

**Marcha atrás:** quitar `integracion`/`e2e` de `needs:` de `deploy-prod` (temporal, con ADR).

---

# 11. F9 — Infraestructura como código (IaC)

**Por qué:** infraestructura creada a mano en consolas es irrepetible, no se revisa, no se puede recrear tras un desastre y
nadie recuerda qué se tocó. IaC la vuelve **código**: versionada, revisada en PR, reproducible.

## 11.1 Conceptos que hay que tener claros

- **Declarativo**: describís el estado deseado; la herramienta calcula las acciones.
- **Idempotente**: aplicar dos veces da lo mismo (el 2.º `plan` debe decir *No changes*).
- **Estado** (`terraform.tfstate`): la memoria de qué recursos reales corresponden a qué bloques del código. **Contiene
  secretos en texto plano** (contraseñas generadas, URLs de conexión). Nunca al repo.
- **`plan`**: el "what-if". Se **lee** antes de cada `apply` (qué se crea, cambia, **destruye** o **reemplaza**).
- **Drift**: la realidad se separó del código (alguien tocó la consola). El `plan` lo detecta *solo para lo declarado*; no ve
  recursos extra no declarados.
- **Grafo de dependencias**: el orden de creación/destrucción sale de las referencias entre recursos (destroy = inverso).

## 11.2 Estructura recomendada

```
infra/
  main.tf          # providers + recursos
  variables.tf     # entradas (sin secretos con default)
  outputs.tf       # URLs/ids útiles (marcar sensitive los secretos)
  versions.tf      # (opcional) required_version y required_providers
  .terraform.lock.hcl   # SE COMMITEA (fija hashes de providers)
  envs/preprod.tfvars   # SOLO valores no secretos (o ninguno)
```

Terraform es lo más difundido; alternativas equivalentes: **OpenTofu** (fork abierto, drop-in), Pulumi (lenguajes generales),
Bicep (Azure), CloudFormation/CDK (AWS), Crossplane (Kubernetes). El principio no cambia.

## 11.3 Reglas

1. **Fijar versiones**: `required_version` y cada provider con versión **exacta** o rango estrecho; commitear
   `.terraform.lock.hcl`. Un provider que cambia sin avisar rompe el plan. (Mirar si el provider está mantenido/archivado.)
2. **Credenciales por variables de entorno** (`NEON_API_KEY`, `RENDER_API_KEY`…) o, mejor, por **OIDC** en CI. Nunca en `.tf`
   ni `.tfvars` commiteados. Secretos generados por Terraform (`random_password`) para que no existan escritos en ningún archivo.
3. **Valores derivados, no copiados**: la cadena de conexión se *arma* con atributos que devuelve el recurso de base de datos;
   la URL del backend que lee el front sale del atributo `url` del servicio. Copiar y pegar valores entre consolas fue el
   error más caro del TP6.
4. **No declarar lo que ya viene en la imagen** (ej. `GIT_SHA`): una variable del servicio lo pisaría.
5. **Un recurso por responsabilidad, nombres con el ambiente** (`restoflow-api-preprod`), `tags/labels` de ownership y costo.
6. **`terraform fmt` y `terraform validate`** en CI (barato). `tfsec`/`checkov` para seguridad.
7. **Proteger lo irreemplazable**: `lifecycle { prevent_destroy = true }` en bases de datos de PROD. Probar que el `destroy` se niega.
8. **Estado remoto** en cuanto haya más de una persona o un pipeline que aplique: backend remoto con **locking y cifrado**
   (S3 + lockfile/DynamoDB, GCS, Azure Blob, Terraform Cloud/HCP, Spacelift…). El estado local de los TP es una concesión
   didáctica: no se puede compartir ni hay locking. Documentar como límite si todavía es local.
9. **Planes de costo**: free tiers que no permiten *modificar* (p. ej. Render free vía Terraform solo crea/destruye) → los
   cambios se hacen con `-replace`/destroy+apply; documentarlo.

## 11.4 Ciclo de trabajo

```bash
cd infra
terraform init                 # baja providers (lockfile)
terraform fmt -check && terraform validate
terraform plan -out=tfplan     # LEER el plan entero
terraform apply tfplan
terraform plan                 # debe decir: No changes  (idempotencia)
terraform output
```

Variables sensibles por entorno (PowerShell: `$env:VAR="..."`; bash: `export VAR=...`) y `TF_VAR_<nombre>` para variables de Terraform.

## 11.5 Qué verificar para dar por buena la IaC (los experimentos de TP8)

1. **Idempotencia**: 2.º `plan` = *No changes*.
2. **El estado por dentro**: abrir `terraform.tfstate` y encontrar la contraseña en texto plano → entender por qué no se commitea.
3. **Drift**: borrar a mano un recurso en la consola → el `plan` lo detecta y `apply` lo repara. Crear a mano uno **no declarado**
   → el plan **no lo ve** (Terraform vigila lo declarado, no todo lo que existe).
4. **Ciclo de vida**: `destroy` → (se ve el orden inverso en ejecución) → `apply` → el entorno vuelve **funcionalmente idéntico**
   (`/health` con el SHA, el front carga, login y lectura contra la base nueva). Anotar qué cambia (ids/hosts nuevos) y qué no.
   Verificar que **QA y PROD** quedaron intactos (mismos `/health` antes y después).
5. **`prevent_destroy`** puesto → `destroy` se niega nombrando el recurso → sacar la línea si era una prueba.

## 11.6 IaC en el pipeline

- **Plan en cada PR** que toque `infra/`: job que corre `init`/`validate`/`plan` y **publica el plan como comentario** del PR
  (la infraestructura se revisa como el código). Credenciales solo de **lectura** cuando sea posible.
- **Apply**: manual o desde `main` con *environment* aprobado — **nunca** automático en PR. Mismo gate humano que el deploy.
- **Detección de drift**: workflow `schedule` (cron semanal) que corre `terraform plan -detailed-exitcode` y abre un issue
  si el exit code es 2.
- **Preprod efímero**: un entorno que nace para validar un release y se destruye después (ahorra cuota y evita drift).

## 11.7 Ambientes por Terraform: preprod

El "ambiente que falta" entre QA y PROD: igual a PROD en forma (misma imagen, misma topología), declarado por código, creado
bajo demanda. Se declara **nuevo** (no se toca QA/PROD hasta tener la confianza de `import`). Corre **las mismas imágenes**
`sha-…` (F6): la IaC no construye nada, solo dice qué ejecutar y con qué config.

## 11.8 IaC sobre infraestructura que ya existe (repos en producción)

1. Escribir el recurso en `.tf` describiendo lo existente.
2. Importar: bloque `import { to = render_web_service.api  id = "srv-xxxx" }` (Terraform ≥ 1.5) o `terraform import ...`.
3. `terraform plan` → **debe decir No changes**. Si propone cambios, el código no describe la realidad: ajustar el `.tf`
   (no aplicar) hasta que dé *No changes*. Un `plan` que quiere **destruir/reemplazar** un recurso de PROD es una alarma: parar.
4. Recién con *No changes* estable, los cambios futuros se hacen por PR.
5. Mientras haya recursos sin importar, documentar el inventario de "lo que sigue artesanal" (honestidad: un plan limpio no
   dice nada sobre lo que no está en el plan).

## 11.9 Esqueleto mínimo

Ver **Anexo A.12** (providers fijados, secreto generado, cadena derivada, servicios por imagen, outputs, `.gitignore`).

## 11.10 DoD de F9
- [ ] `infra/` con providers fijados y `.terraform.lock.hcl` commiteado; `.gitignore` cubre estado y `*.tfvars` **antes** del primer `apply`.
- [ ] Sin credenciales en el repo; secretos por env/OIDC; JWT/contraseñas generadas por Terraform.
- [ ] Los cinco experimentos (§11.5) hechos y anotados con resultados reales.
- [ ] CI: `fmt`/`validate` (y `plan` en PR si se hizo F9 completo).
- [ ] Inventario de lo que sigue creado a mano + plan de import.
- [ ] Ambiente efímero **destruido** al terminar (cuota/costo).

**Marcha atrás:** `terraform destroy` del entorno nuevo; no afecta a lo existente.

---

# 12. F10 — Documentación viva

La documentación que importa es la que permite a otra persona (o vos en 6 meses) **operar y decidir** sin preguntarte.

## 12.1 ADRs / `decisiones.md`

Un ADR por decisión que tenga costo de revertir (`docs/adr/0001-titulo.md`, o secciones en `decisiones.md`). Formato corto:

```
# ADR-000N — Título
Estado: aceptado | reemplazado por ADR-000M     Fecha: AAAA-MM-DD
## Contexto      (qué problema, qué restricciones)
## Decisión      (qué se eligió)
## Alternativas  (qué se descartó y por qué)
## Consecuencias (qué se gana, qué se PIERDE, qué queda como deuda)
## Cómo se verificó  (comando/evidencia concreta, no "anda")
```

Decisiones que siempre merecen ADR: protección de rama y reviews, umbral de coverage, estrategia de cache, Delivery vs
Deployment, pattern de despliegue, proveedor y límites del free tier, estrategia de datos entre ambientes, IaC (riel, estado),
política de flaky tests. Documentar **los límites conocidos y lo no probado** con honestidad es parte del valor.

## 12.2 Registro de problemas

Dentro de cada ADR o en `docs/problemas.md`: *problema → causa real → cómo se resolvió → cómo evitarlo*. Es lo que más ahorra
tiempo futuro (ver Anexo B).

## 12.3 Runbook (`docs/runbook.md`)

Procedimientos paso a paso, escritos para ejecutarse bajo estrés:
- **Cómo se despliega** (normal) y **cómo aprobar/rechazar** (qué mirar).
- **Rollback** (comandos exactos + tiempo medido).
- **Hotfix** (camino de emergencia con la protección de rama).
- **Qué hacer si PROD cae**: dónde ver logs, quién avisa, comunicación.
- **Restaurar la base** desde backup (probado).
- **Rotar un secreto** (cuáles, dónde viven, cómo se actualizan).
- **Ambientes**: URLs, dónde están las consolas, quién tiene acceso.
- **Cómo levantar/destruir preprod**.

## 12.4 Estructura del README

1. Qué es + badge de CI. 2. Quick start (3 comandos). 3. Stack. 4. Arquitectura (diagrama simple). 5. Variables de entorno
(tabla). 6. Tests y coverage. 7. Pipeline (diagrama de jobs + cómo se promueve a PROD). 8. Ambientes y URLs. 9. IaC (cómo
crear/destruir). 10. Contribuir (flujo de ramas/PR, DoD). 11. Links a `decisiones`/ADRs y runbook.

## 12.5 Changelog / notas de versión

`gh release create --generate-notes` agrupa PRs por etiqueta (configurable en `.github/release.yml`); con commits
convencionales se puede automatizar el changelog (`release-please`, `semantic-release`). Una release = qué cambió, qué
migraciones, qué riesgo.

## 12.6 DoD de F10
- [ ] README permite a alguien nuevo levantar el proyecto y entender el pipeline sin ayuda.
- [ ] Cada decisión de este documento tiene su ADR.
- [ ] Runbook probado (al menos deploy, rollback y restore se ejecutaron una vez).
- [ ] `docs/adopcion.md` marcado como completo con la fecha.

---

# 13. Transversales

## 13.1 Secretos
- Inventario: qué secretos existen, dónde viven (environment de GitHub, gestor del proveedor), quién los puede leer.
- Rotación: calendario (p. ej. cada 90 días) y **rotar inmediatamente** si hubo exposición (chat, log, commit, captura).
- Mínimo privilegio: tokens con el scope mínimo; claves de IaC de plan con solo lectura cuando se pueda.
- Push protection y secret scanning activados. Un secreto commiteado se **rota**; reescribir el historial no basta.
- La app falla **rápido** si falta un secreto obligatorio al arrancar (no arrancar con `change-this-secret`).

## 13.2 Observabilidad mínima
- Logs estructurados a stdout; nivel configurable por env.
- Chequeo externo de disponibilidad (UptimeRobot, Better Stack, Healthchecks.io) sobre `/health` de PROD, con alerta.
- Error tracking (Sentry u otro) en front y back.
- Métricas de los cuatro golden signals (latencia, tráfico, errores, saturación) si el proveedor las ofrece; alerta sobre tasa de errores.
- Anotar en dashboards los momentos de deploy (correlacionar incidentes con releases).

## 13.3 Datos y backups
- Backups automáticos de la base con retención definida y **una restauración probada** (un backup no probado no existe).
- Migraciones versionadas (Alembic, Flyway, Prisma, EF…), aplicadas por el pipeline o el arranque, compatibles hacia atrás (expand/contract).
- Datos de prueba ≠ datos reales. Nunca copiar PROD a QA sin anonimizar.

## 13.4 Dependencias y cadena de suministro
- Dependabot (o Renovate) semanal para dependencias, actions, Docker y Terraform; PRs chicos que pasan por el mismo gate.
- Lockfiles commiteados (`package-lock.json`, `poetry.lock`/`requirements` con versiones fijas). Evitar `latest` en
  `package.json`/`requirements` (las builds dejan de ser reproducibles).
- Pin de actions por SHA en proyectos exigentes; SBOM/atestaciones si hay requisitos de compliance.

## 13.5 Costo y limpieza
- Ambientes efímeros se destruyen (`terraform destroy`); retención de imágenes y artefactos de Actions acotada
  (`retention-days`); alertas de presupuesto en la cuenta cloud.

## 13.6 Uso de IA (si aplica)
- Una línea en el README/ADR sobre qué se hizo con asistencia. La responsabilidad de entender y verificar cada cambio es de
  la persona: nada se aplica sin saber qué hace. Las credenciales **nunca** se pegan en un chat con una IA.

---

# 14. Checklist final: "¿este repo es profesional?"

Marcar con evidencia (link/comando), no con impresión.

**Repo y flujo**
- [ ] `main` protegida: PR obligatorio, checks requeridos, `strict`, sin force-push (`gh api …/protection`)
- [ ] Solo squash-merge, ramas se borran, historial lineal
- [ ] `.gitignore`/`.env.example`/README/CODEOWNERS/plantillas de PR e issue
- [ ] Sin secretos en el repo (gitleaks limpio) y push protection activo
- [ ] Releases SemVer sobre el commit desplegado, con notas

**Contenedores y CI**
- [ ] Dockerfile multi-etapa (build/test/runtime), base fijada, no-root, `.dockerignore`, healthcheck
- [ ] `docker compose up` desde cero con solo `.env.example`; persistencia verificada
- [ ] CI en PR y push; jobs paralelos; permisos mínimos; cache con `scope`; timeouts
- [ ] Badge, resumen en cada run y artefactos de reportes

**Calidad**
- [ ] Tests unitarios significativos (parametrizados, errores, mock en el borde)
- [ ] Umbral de coverage que **rompe** el build en cada componente, justificado y con ratchet
- [ ] Lint/format/tipos y escaneo de dependencias/imagen/secretos
- [ ] Gate demostrado en rojo y verde

**Entrega**
- [ ] Imagen etiquetada `sha-<commit>`, publicada solo desde `main` y solo si pasó; mismo artefacto en todos los ambientes
- [ ] `/health` expone el SHA; el smoke espera ese SHA exacto
- [ ] QA automático; PROD con aprobación humana, `concurrency`, secretos por environment, auto-deploy del proveedor apagado
- [ ] Integración + e2e como gate antes de PROD, vistos fallar de verdad
- [ ] Rollback documentado y cronometrado; datos aislados entre ambientes

**Infra**
- [ ] IaC con providers fijados, lockfile commiteado, estado fuera del repo (remoto con locking cuando hay más de una persona)
- [ ] `plan` limpio (*No changes*); drift y destroy/apply probados; `prevent_destroy` en datos de PROD
- [ ] Inventario de lo que sigue manual

**Operación y docs**
- [ ] ADRs de las decisiones clave, con límites conocidos
- [ ] Runbook probado (deploy, rollback, restore, hotfix, rotación de secretos)
- [ ] Monitoreo externo de `/health` con alerta; backups con restauración probada
- [ ] Dependabot/Renovate activo

---

# 15. Anexo A — Plantillas completas

> Adaptá nombres (`backend`, `frontend`), puertos, versiones de lenguaje y comandos. Las versiones de las actions son las que
> usó este proyecto en sus corridas; dejá que Dependabot las mantenga.

## A.1 Dockerfile — Python (FastAPI/Flask/Django)

```dockerfile
# ---- build: instala dependencias en un prefijo aparte ----
FROM python:3.13-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- test: pytest + código + tests. NO viaja a producción ----
FROM python:3.13-slim AS test
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY app ./app
COPY tests ./tests
COPY .coveragerc .
ENTRYPOINT ["python","-m","pytest","tests/","-v","--cov","--cov-report=term-missing", \
            "--cov-report=xml:/out/coverage.xml","--cov-report=html:/out/htmlcov","--junitxml=/out/junit.xml"]

# ---- runtime: solo lo instalado + el código ----
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --system --uid 10001 --no-create-home app
COPY --from=build /install /usr/local
COPY app ./app
# Va al final: no invalida el cache de lo anterior. /health lo devuelve como `sha`.
ARG GIT_SHA=unknown
ENV GIT_SHA=$GIT_SHA
USER app
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')" || exit 1
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080"]
```

## A.2 Dockerfile — Node (SPA/React/Vue + nginx)

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- test: reutiliza build (mismas dependencias y código) ----
FROM build AS test
ENTRYPOINT ["npx","vitest","run","--coverage","--coverage.reportsDirectory=/out/coverage"]

# ---- runtime: nginx sirve estáticos; el backend se lee de env al ARRANCAR ----
FROM nginx:1.27-alpine
# default.conf.template usa ${BACKEND_URL} y ${DNS_RESOLVER}; la imagen oficial hace envsubst al iniciar
COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
ENV BACKEND_URL=http://backend:8080 DNS_RESOLVER=127.0.0.11
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
```

Notas de nginx (aprendidas): usar `proxy_set_header Host $proxy_host;` (con `$host` algunos proveedores devuelven 508 por
loop); con proveedor externo el `DNS_RESOLVER` es `8.8.8.8` y `BACKEND_URL` con `https://`; en compose, `127.0.0.11`.

## A.3 Otros stacks (esqueleto)

- **Go**: `FROM golang:1.23 AS build` → `CGO_ENABLED=0 go build -o /out/app` → runtime `gcr.io/distroless/static` + `USER nonroot`; etapa `test` con `go test ./... -cover`.
- **Java**: `FROM maven:3-eclipse-temurin-21 AS build` (`mvn -B package -DskipTests`), `test` con `mvn verify`, runtime `eclipse-temurin:21-jre` con `USER`.
- **.NET**: `mcr.microsoft.com/dotnet/sdk` para build/test, runtime `…/aspnet`; `dotnet test` con coverlet en la etapa `test`.

## A.4 docker-compose.yml (desarrollo y e2e local)

```yaml
services:
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports: ["5433:5432"]               # 5433 en el host para no chocar con un Postgres local
    volumes: [db_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL","pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10
  backend:
    build: ./backend
    environment:
      DB_HOST: db
      DB_PORT: 5432
      DB_USER: ${POSTGRES_USER}
      DB_PASSWORD: ${POSTGRES_PASSWORD}
      DB_NAME: ${POSTGRES_DB}
      JWT_SECRET: ${JWT_SECRET}
      SERVER_PORT: 8080
    ports: ["8080:8080"]
    depends_on: { db: { condition: service_healthy } }
    restart: unless-stopped
    healthcheck:
      test: ["CMD","python","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"]
      interval: 10s
      timeout: 5s
      retries: 10
  frontend:
    build: ./frontend
    ports: ["3000:80"]
    depends_on: { backend: { condition: service_healthy } }
    restart: unless-stopped
volumes:
  db_data:
```

## A.5 `.github/workflows/ci.yml` — build + test + publicar

```yaml
name: CI

on:
  pull_request: { branches: [main] }
  push:         { branches: [main] }

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}   # cancela corridas viejas del PR; nunca las de main

jobs:
  build:
    name: build-${{ matrix.component }}           # => checks "build-backend" y "build-frontend" (estos son los que se exigen)
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions: { contents: read, packages: write }
    strategy:
      fail-fast: false
      matrix:
        include:
          - { component: backend,  out: TestResults/backend,  tail: 50 }
          - { component: frontend, out: TestResults/frontend, tail: 20 }
    steps:
      - name: Qué estamos verificando
        env: { RAMA: "${{ github.head_ref || github.ref_name }}" }
        run: echo "Rama $RAMA · commit $GITHUB_SHA"
      - uses: actions/checkout@v6
      - uses: docker/setup-buildx-action@v4

      - name: Construir la etapa de tests
        uses: docker/build-push-action@v7
        with:
          context: ./${{ matrix.component }}
          target: test
          load: true
          push: false
          tags: ${{ matrix.component }}-test:ci
          cache-from: type=gha,scope=${{ matrix.component }}-test
          cache-to: type=gha,mode=max,scope=${{ matrix.component }}-test

      - name: Correr tests con coverage (el umbral rompe el build)
        run: |
          set -o pipefail
          mkdir -p ${{ matrix.out }}
          docker run --rm -v "${{ github.workspace }}/${{ matrix.out }}:/out" ${{ matrix.component }}-test:ci \
            | tee ${{ matrix.out }}/test-output.txt

      - name: Resumen en el run
        if: ${{ !cancelled() }}
        run: |
          { echo "### Tests y coverage — ${{ matrix.component }}"; echo '```';
            tail -${{ matrix.tail }} ${{ matrix.out }}/test-output.txt; echo '```'; } >> "$GITHUB_STEP_SUMMARY"

      - name: Subir reportes
        if: ${{ !cancelled() }}                   # el reporte importa MÁS cuando falla
        uses: actions/upload-artifact@v4
        with:
          name: reportes-${{ matrix.component }}
          path: ${{ matrix.out }}
          retention-days: 14

      # --- Publicación: solo push a main, y solo después de que lo de arriba pasó ---
      - name: Login al registry
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: docker/login-action@v4
        with: { registry: ghcr.io, username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }

      - name: Construir (y publicar si es main) la imagen final
        uses: docker/build-push-action@v7
        with:
          context: ./${{ matrix.component }}
          push: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
          tags: ghcr.io/${{ github.repository }}-${{ matrix.component }}:sha-${{ github.sha }}
          build-args: GIT_SHA=${{ github.sha }}       # (ignorado por el front si su Dockerfile no declara el ARG)
          cache-from: type=gha,scope=${{ matrix.component }}
          cache-to: type=gha,mode=max,scope=${{ matrix.component }}
          provenance: false
          sbom: false
```

Notas: `${{ github.repository }}` ya viene en minúsculas salvo que tu usuario/repo tengan mayúsculas (ghcr.io las rechaza:
escribilo a mano). Tests unitarios corren *dentro* de la imagen `test`: el gate usa el mismo entorno que producción.

## A.6 Jobs de deploy y gates (se agregan al mismo `ci.yml`)

```yaml
  deploy-qa:
    runs-on: ubuntu-latest
    needs: [build]
    if: github.ref == 'refs/heads/main'
    environment: qa
    steps:
      - uses: actions/checkout@v6          # para tener scripts/smoke.sh
      - name: Desplegar la IMAGEN de este commit (ejemplo: Render por deploy hook)
        env:
          HOOK_API:   ${{ secrets.DEPLOY_HOOK_API }}
          HOOK_FRONT: ${{ secrets.DEPLOY_HOOK_FRONT }}
        run: |
          IMG_API="ghcr.io/${{ github.repository }}-backend:sha-${{ github.sha }}"
          IMG_FRONT="ghcr.io/${{ github.repository }}-frontend:sha-${{ github.sha }}"
          # La URL del hook va ÚLTIMA: --data-urlencode se lleva el valor que tiene al lado.
          curl -fsS --max-time 30 --get --data-urlencode "imgURL=$IMG_API"   "$HOOK_API"
          curl -fsS --max-time 30 --get --data-urlencode "imgURL=$IMG_FRONT" "$HOOK_FRONT"
      - name: Smoke test
        env:
          URL_API: ${{ vars.API_URL }}
          URL_FRONT: ${{ vars.FRONT_URL }}
          EXPECTED_SHA: ${{ github.sha }}
          SMOKE_EMAIL: smoke-qa@ejemplo.dev
          SMOKE_PASSWORD: ${{ secrets.SMOKE_PASSWORD }}
        run: bash scripts/smoke.sh

  integracion:
    runs-on: ubuntu-latest
    needs: deploy-qa
    if: github.ref == 'refs/heads/main'
    environment: qa                       # solo para leer las variables del environment
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: "22", cache: npm, cache-dependency-path: frontend/package-lock.json }
      - run: npm ci                       # sin browser
        working-directory: ./frontend
      - run: npx playwright test e2e/api.spec.js
        working-directory: ./frontend
        env: { API_BASE_URL: "${{ vars.API_URL }}" }
      - if: ${{ !cancelled() }}
        uses: actions/upload-artifact@v4
        with: { name: playwright-report-integracion, path: frontend/playwright-report, retention-days: 7 }

  e2e:
    runs-on: ubuntu-latest
    needs: integracion                    # si la API está rota, no se gasta un browser
    if: github.ref == 'refs/heads/main'
    environment: qa
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: "22", cache: npm, cache-dependency-path: frontend/package-lock.json }
      - run: |
          npm ci
          npx playwright install --with-deps chromium
        working-directory: ./frontend
      - run: npx playwright test e2e/mesas.spec.js     # SU archivo: si no, correría también la integración
        working-directory: ./frontend
        env:
          E2E_BASE_URL: ${{ vars.FRONT_URL }}
          API_BASE_URL: ${{ vars.API_URL }}
      - if: ${{ !cancelled() }}
        uses: actions/upload-artifact@v4
        with: { name: playwright-report-e2e, path: frontend/playwright-report, retention-days: 7 }

  deploy-prod:
    runs-on: ubuntu-latest
    needs: e2e                            # EL gate: sin integración y e2e verdes ni siquiera se pide aprobación
    if: github.ref == 'refs/heads/main'
    environment: production               # required reviewer → queda en "Waiting"
    concurrency: { group: deploy-prod, cancel-in-progress: false }
    steps:
      - uses: actions/checkout@v6
      - name: Desplegar en PROD la MISMA imagen que pasó por QA (build once, deploy many)
        env:
          HOOK_API:   ${{ secrets.DEPLOY_HOOK_API }}      # mismo nombre, otro valor: es el secret del environment production
          HOOK_FRONT: ${{ secrets.DEPLOY_HOOK_FRONT }}
        run: |
          IMG_API="ghcr.io/${{ github.repository }}-backend:sha-${{ github.sha }}"
          IMG_FRONT="ghcr.io/${{ github.repository }}-frontend:sha-${{ github.sha }}"
          curl -fsS --max-time 30 --get --data-urlencode "imgURL=$IMG_API"   "$HOOK_API"
          curl -fsS --max-time 30 --get --data-urlencode "imgURL=$IMG_FRONT" "$HOOK_FRONT"
      - name: Smoke test (PROD)
        env:
          URL_API: ${{ vars.API_URL }}          # en el environment production vale la URL de PROD
          URL_FRONT: ${{ vars.FRONT_URL }}
          EXPECTED_SHA: ${{ github.sha }}
          SMOKE_EMAIL: smoke-prod@ejemplo.dev
          SMOKE_PASSWORD: ${{ secrets.SMOKE_PASSWORD }}
        run: bash scripts/smoke.sh
```

Para otros proveedores, reemplazar solo el paso "Desplegar" (ver §9.5). Si el deploy es por SSH/CLI, el resto no cambia.

## A.7 `scripts/smoke.sh`

```bash
#!/usr/bin/env bash
# Espera a que el ambiente corra EXPECTED_SHA y recorre el camino real (front + auth + base).
# Env: URL_API URL_FRONT EXPECTED_SHA SMOKE_EMAIL SMOKE_PASSWORD  [TRIES=30] [SLEEP=20] [AUTH_PATH=/api/categorias]
set -u
TRIES=${TRIES:-30}; SLEEP=${SLEEP:-20}; AUTH_PATH=${AUTH_PATH:-/api/categorias}
CREDS=$(jq -nc --arg e "$SMOKE_EMAIL" --arg p "$SMOKE_PASSWORD" '{email:$e,password:$p}')
REG=$(jq -nc --arg e "$SMOKE_EMAIL" --arg p "$SMOKE_PASSWORD" '{nombre:"Smoke",email:$e,password:$p}')

for i in $(seq 1 "$TRIES"); do
  echo "Intento $i/$TRIES"
  RUNNING=$(curl -fsS --max-time 10 "$URL_API/health" | jq -r .sha) || RUNNING=""
  echo "  backend corre: ${RUNNING:-sin respuesta} (esperado: $EXPECTED_SHA)"
  if [ "$RUNNING" = "$EXPECTED_SHA" ] && curl -fsS --max-time 10 "$URL_FRONT/" >/dev/null; then
    # 201 la primera vez, 409 si ya existe: ambos son válidos
    curl -sS --max-time 20 -o /dev/null -X POST "$URL_API/api/auth/register" \
      -H 'Content-Type: application/json' -d "$REG" || true
    TOKEN=$(curl -fsS --max-time 20 -X POST "$URL_API/api/auth/login" \
      -H 'Content-Type: application/json' -d "$CREDS" | jq -r .token) || TOKEN=""
    if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ] \
       && curl -fsS --max-time 10 -H "Authorization: Bearer $TOKEN" "$URL_API$AUTH_PATH" >/dev/null; then
      echo "✅ Ambiente OK (API + BD + front, commit correcto)"; exit 0
    fi
  fi
  sleep "$SLEEP"
done
echo "❌ El ambiente no respondió con el commit esperado a tiempo"; exit 1
```

(En un `run:` con YAML evitá partir líneas con `\` dentro de `if [ ... ] \ &&` mal indentadas: pasá el script como archivo,
como acá, y evitás copiar/pegar con saltos que se rompen.)

## A.8 Playwright — `frontend/playwright.config.js`

```js
import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,                   // tope por test (cold start)
  expect: { timeout: 15_000 },
  workers: 1,                        // comparten la base de QA
  retries: 1,                        // 1 retry: si pasa recién ahí, el reporte lo marca flaky
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',   // el FRONT; la API tiene su variable
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  reporter: [['html', { open: 'never' }], ['list']],
})
```

Patrones de los specs:
```js
// e2e/usuarios.js — usuarios fijos, registro tolerante
export async function asegurarUsuario(request, u) {
  await request.post(`${process.env.API_BASE_URL}/api/auth/register`, { data: u })   // 201 o 409: ambos sirven
  const r = await request.post(`${process.env.API_BASE_URL}/api/auth/login`, { data: { email: u.email, password: u.password } })
  return (await r.json()).token
}
export const unico = (p) => `${p}-${Date.now()}-${Math.floor(Math.random()*1e4)}`   // identificador por corrida
```
- `api.spec.js` (integración): auth, validación (422/400), permisos (A no ve lo de B → 403/404), flujo crear→listar→actualizar→borrar.
- `mesas.spec.js` (e2e): login por UI → crear una entidad con valor único → verla en la lista; selectores por rol/etiqueta.
- vitest/jest: `exclude: ['e2e/**']`. `.gitignore`: `playwright-report/`, `test-results/`.

## A.9 `.github/pull_request_template.md`

```markdown
## Qué cambia y por qué
<!-- una o dos frases; el "por qué" es lo importante -->

## Cómo se probó
- [ ] Tests nuevos/actualizados   - [ ] Probado local (compose)   - [ ] Sin cambios de comportamiento

## Riesgos / rollback
<!-- ¿migración? ¿cambia config o variables? ¿cómo se revierte? -->

## Checklist
- [ ] CI verde  - [ ] Docs/ADR al día  - [ ] Sin secretos  - [ ] Leí mi propio diff

Closes #
```

## A.10 `.github/dependabot.yml`

```yaml
version: 2
updates:
  - { package-ecosystem: github-actions, directory: "/",         schedule: { interval: weekly } }
  - { package-ecosystem: docker,         directory: "/backend",  schedule: { interval: weekly } }
  - { package-ecosystem: docker,         directory: "/frontend", schedule: { interval: weekly } }
  - { package-ecosystem: pip,            directory: "/backend",  schedule: { interval: weekly } }
  - { package-ecosystem: npm,            directory: "/frontend", schedule: { interval: weekly } }
  - { package-ecosystem: terraform,      directory: "/infra",    schedule: { interval: weekly } }
```

## A.11 `.github/ISSUE_TEMPLATE/bug.md` y `historia.md`

```markdown
---
name: Bug
about: Algo no funciona como debería
labels: bug
---
**Pasos para reproducir** 1. … 2. …
**Esperado** …   **Real** …
**Entorno** (ambiente, navegador, commit/versión) …   **Evidencia** (log/captura)
```
```markdown
---
name: Historia
about: Capacidad con valor observable
labels: feature
---
**Como** <rol> **quiero** <capacidad> **para** <beneficio>.
**Criterios de aceptación** - [ ] Dado … cuando … entonces …
**Fuera de alcance** …
```

## A.12 Terraform — esqueleto (`infra/main.tf`)

```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    neon   = { source = "kislerdm/neon",       version = "0.18.0" }  # fijadas; revisar si el provider sigue mantenido
    render = { source = "render-oss/render",   version = "1.9.1" }
    random = { source = "hashicorp/random",    version = "3.9.1" }
  }
  # En equipo/pipeline: backend remoto con locking y cifrado en vez de estado local
  # backend "s3" { bucket = "..." key = "preprod/terraform.tfstate" region = "..." use_lockfile = true encrypt = true }
}

provider "neon" {}     # NEON_API_KEY del entorno
provider "render" {}   # RENDER_API_KEY y RENDER_OWNER_ID del entorno

resource "neon_project" "preprod" {
  name                      = "app-preprod"
  org_id                    = var.neon_org_id          # TF_VAR_neon_org_id (no es secreto)
  history_retention_seconds = 21600                    # tope del plan gratuito
}
resource "neon_role" "preprod" {
  project_id = neon_project.preprod.id
  branch_id  = neon_project.preprod.default_branch_id
  name       = "app_preprod_owner"
}
resource "neon_database" "preprod" {
  project_id = neon_project.preprod.id
  branch_id  = neon_project.preprod.default_branch_id
  name       = "app_preprod"
  owner_name = neon_role.preprod.name
  # lifecycle { prevent_destroy = true }               # en PROD: descomentar
}

resource "random_password" "jwt" {
  length  = 48
  special = false                                       # el secreto no existe escrito en ningún archivo
}

locals {
  # Se ARMA con lo que devolvió el recurso: nadie lo copia y pega
  database_url = "postgresql+psycopg://${neon_role.preprod.name}:${urlencode(neon_role.preprod.password)}@${neon_project.preprod.database_host}/${neon_database.preprod.name}?sslmode=require"
}

resource "render_web_service" "api" {
  name   = "app-api-preprod"
  plan   = "free"
  region = var.region
  runtime_source = { image = { image_url = var.image_repo_api, tag = var.image_tag } }   # SIN la etiqueta pegada
  env_vars = {
    DATABASE_URL = { value = local.database_url }
    JWT_SECRET   = { value = random_password.jwt.result }
    SERVER_PORT  = { value = "8080" }
    # NO declarar GIT_SHA: viene grabado en la imagen y una variable lo pisaría
  }
}

resource "render_web_service" "front" {
  name   = "app-front-preprod"
  plan   = "free"
  region = var.region
  runtime_source = { image = { image_url = var.image_repo_front, tag = var.image_tag } }
  env_vars = {
    BACKEND_URL  = { value = render_web_service.api.url }   # derivado, no copiado
    DNS_RESOLVER = { value = "8.8.8.8" }
  }
}
```
`variables.tf` define `neon_org_id` (sin default), `image_repo_*`, `image_tag` (`sha-…`), `region`. `outputs.tf` expone
`api_url`, `front_url`, `db_host` (los secretos con `sensitive = true`).

Adaptaciones: AWS/GCP/Azure → mismos conceptos con `aws_*`/`google_*`/`azurerm_*`; en Kubernetes, Helm provider o GitOps.
Plan C 100 % local: provider `kreuzwerker/docker` (contenedores locales) cumple el aprendizaje sin nube.

---

# 16. Anexo B — Errores conocidos (los que ya nos pasaron)

| Síntoma | Causa real | Solución / prevención |
|---|---|---|
| Merge bloqueado para siempre "esperando check" | Se renombró un job que estaba como requerido | Los `contexts` de la protección = nombres actuales de los jobs. Cambiar protección y workflow en el orden correcto |
| Cache "parpadea": un job `CACHED`, el otro no | Falta `scope` distinto por job | `scope=<job>` en `cache-from/to` |
| Segundo run no muestra `CACHED` | Se disparó antes de que terminara el primero | Esperar que termine y recién entonces re-correr |
| `git commit` dice "nothing to commit" tras editar | El editor no guardó / `--amend` previo | `git diff` antes de cada commit; confirmar el archivo en disco |
| Editor: "The content of the file is newer" tras `git switch` | Archivo abierto con versión vieja | Cerrar sin guardar, reabrir desde disco, recién ahí editar |
| "Files changed" vacío tras romper y arreglar | Diff neto = 0 | La evidencia está en *Commits* y en historial de *Actions* |
| Falla de conexión al daemon en `docker build` | Docker Desktop apagado | Levantarlo y esperar a que inicie |
| `denied` al publicar en ghcr.io | Faltan `packages: write`, o workflow permissions Read-only, o falta "Manage Actions access" del paquete | Las tres cosas (§8.1) |
| ghcr.io rechaza el push | Mayúsculas en usuario/repo | Escribir el nombre en minúsculas a mano |
| Error de attestations/permisos al publicar | `build-push-action` genera provenance/sbom | `provenance: false`, `sbom: false` o dar los permisos |
| Proveedor devuelve 508 / loop | nginx pasaba `Host: $host` | `proxy_set_header Host $proxy_host;` |
| Front en blanco / errores justo tras inactividad | Free tier dormido (cold start) | Reintentos largos en smoke; despertar con `/health` antes de demos |
| Smoke verde pero PROD corre versión vieja | `/health` sin SHA | `GIT_SHA` en imagen + el smoke compara contra `$GITHUB_SHA` |
| `RENDER_GIT_COMMIT` nulo | Servicio que ejecuta imagen no construye desde Git | Usar `GIT_SHA` horneado en la imagen |
| Hook de deploy devuelve 404/400 | Etiqueta corta, o URL del hook no está última en `curl` | Etiqueta `sha-<40 chars>` completa; hook al final |
| "Manual Deploy" retrocede la versión | Re-despliega lo configurado en Settings, no lo último | No usarlo; todo deploy sale del pipeline |
| Hook con `ref=<sha viejo>` desplegó la punta | `ref` no garantiza commits que no sean la punta | Desplegar por imagen etiquetada, no por ref de Git |
| Varios `deploy-prod` esperando | Cada merge a `main` genera uno | Aprobar uno, rechazar con comentario el resto |
| Test pasa de día y falla entre 00:00–03:00 UTC | Mezcla de `date.today()` (UTC) con hora local | Fijar el reloj / misma zona en test y código |
| Dos merges seguidos pisan las suites en QA | QA único y compartido | Mergear de a uno; evolucionar a efímeros |
| `ERESOLVE` instalando el plugin de coverage | Versión de vitest/coverage desalineada | Instalar el número EXACTO de la versión; nunca `--force` |
| Umbral del front no rompe el build | Config fuera de `vite.config`/`vitest.config` o `include` equivocado | Probar bajando un test y viendo exit ≠ 0 |
| `Error: org_id is required` (Neon) | Los proyectos viven en una organización | Variable `neon_org_id` vía `TF_VAR_` |
| Neon: error de retención de historial | Default pide más que el plan gratis | `history_retention_seconds` al tope del plan |
| App no conecta a la base nueva | Formato de cadena distinto al esperado por la app (`DATABASE_URL` vs `ConnectionStrings__X`) / falta SSL | Armar la URL en el formato que lee la app, `sslmode=require`, `urlencode` en la contraseña |
| `terraform` no se encuentra tras instalarlo | Terminal abierta antes de actualizar el PATH | Abrir una terminal nueva |
| PowerShell rompe URLs/comandos | `curl` es alias de `Invoke-WebRequest`; `$(…)` sin comillas parte argumentos | `curl.exe`; comillas alrededor de URLs; `--body-file` |
| Servicios "no aparecen" en el proveedor | Quedaron en otro workspace/proyecto | Revisar el selector de workspace |
| Plan de Terraform quiere destruir algo de PROD | El `.tf` no describe la realidad | Parar. Ajustar el código hasta *No changes*; `prevent_destroy` |
| Credencial expuesta en chat/log/captura | Se pegó sin pensar | Rotarla ya; usar `gh secret set` (stdin) y env vars |

---

# 17. Anexo C — Prompt de arranque para un agente

Pegar esto en una sesión nueva de Claude Code, parado en la raíz del repo objetivo, con esta guía accesible
(copiada al repo en `docs/` o referenciada por ruta):

```
Quiero llevar este repositorio al estándar de la guía GUIA-PROFESIONAL.md (adjunta/en <ruta>).
Seguí el protocolo del §0.2 al pie de la letra:

1. Ejecutá la Fase F0: auditá el repo en modo solo-lectura, sin modificar nada salvo docs/adopcion.md. Mostrame la tabla de
   brechas, qué detectaste como producción, y el orden de fases que proponés. Esperá mi confirmación.
2. Después trabajá de a una fase por vez, un PR por fase, verificando la DoD de cada una con la evidencia que indica la guía.
   No avances de fase hasta que yo confirme.
3. Antes de cualquier acción hacia afuera (settings del repo, secretos, environments, recursos cloud, releases, deploys)
   mostrame el comando exacto y esperá mi "sí". Nunca me pidas que te pegue un secreto: guiame para cargarlo por stdin
   (gh secret set) o por variable de entorno.
4. Este repo [ESTÁ / NO ESTÁ] en producción: aplicá las reglas del §0.3 si está (modo sombra, umbrales sobre lo medido,
   aprobación manual a PROD, import antes de apply).
5. Datos que necesito que me preguntes (si no los podés deducir): proveedor de hosting/registry, si hay equipo y cuántos
   aprueban, si el repo es público o privado, criticidad de producción.
6. Actualizá docs/adopcion.md al terminar cada fase (qué quedó hecho, qué sigue) para poder retomar en otra sesión.
```

---

## Cierre

El estándar completo se resume en una cadena que no se corta:

```
PR (rama corta) → CI verde (tests + umbral + escaneos) → merge a main protegida
   → imagen sha-<commit> publicada (una sola vez) → QA automático + smoke con SHA
   → integración → e2e → [aprobación humana] → PROD con la MISMA imagen → smoke
   → release SemVer sobre el commit en PROD → rollback = redesplegar una imagen anterior
Todo reproducible desde código (Dockerfile, workflows, Terraform) y explicado en ADRs + runbook.
```

Si en algún momento una práctica de esta guía choca con la realidad del proyecto, **no se omite en silencio**: se adapta
y se escribe el motivo en un ADR. Esa trazabilidad de decisiones es, en sí misma, parte del estándar profesional.
