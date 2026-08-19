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
