# Postmortem: pantalla en blanco al salir de Mesas — 2026-10-19

## Resumen

Al salir de la pantalla de Mesas hacia cualquier otra, React tiraba `TypeError: l is not a function`
y la aplicación quedaba en blanco hasta recargar. El defecto existía **desde el primer commit
(2026-08-14)**, en todos los entornos. Ninguna prueba ni usuario lo había reportado. Sentry lo
detectó a los minutos de instalarse en producción, y el arreglo estuvo en PROD **~15 minutos**
después.

## Impacto

- **Quién**: cualquier usuario que entrara a *Mesas* y después navegara a otra sección (Menú,
  Pedidos, Reservas…). La función principal de Mesas (listar, crear, editar, borrar) andaba; lo
  que se rompía era **salir** de ella.
- **Qué veía**: pantalla en blanco, sin mensaje. Recargando el navegador volvía a andar.
- **Cuánto tiempo**: latente ~2 meses (14/08 → 19/10). Desde que fue **visible** (Sentry en PROD,
  21:59 UTC) hasta el arreglo en PROD (22:14 UTC): ~15 minutos.
- **Datos**: ninguno. Era un error de la vista, no del backend ni de la base.
- **El monitor**: nunca se enteró. `/health` estuvo en verde todo el tiempo.

## Timeline (2026-10-19, UTC)

| Hora | Evento |
|---|---|
| 2026-08-14 | Commit inicial: `Mesas.jsx` con `useEffect(load, [])`. El defecto entra al código. |
| 21:53 | Se mergea [#68](https://github.com/lucasrodrich/ingsoft3-tp01/pull/68): Sentry en back y front. |
| 21:59 | #68 llega a PROD (aprobación + smoke con SHA en verde). |
| 22:00–22:08 | **Detección**: usando PROD para generar datos en Sentry, navegar `/mesas → /menu` deja la pantalla en blanco, y Sentry abre `RESTOFLOW-FRONT-1` — `TypeError: l is not a function`, con la ruta y el stack (minificado). La hora exacta es el *First seen* del issue en Sentry. |
| 22:00–22:08 | **Diagnóstico**: el stack termina en la limpieza de un efecto de React al desmontar. En `Mesas.jsx`, `load` devuelve una Promise y se pasa directo a `useEffect`: React toma lo que devuelve el efecto como su función de limpieza, y al desmontar intenta llamar a la Promise. Test de regresión (montar y desmontar `Mesas`): **falla** con el código viejo. |
| 22:08 | Se mergea [#69](https://github.com/lucasrodrich/ingsoft3-tp01/pull/69): `useEffect(() => { load() }, [])`. El test pasa. |
| 22:11 | La cadena pasa QA: smoke, integración y e2e en verde. |
| 22:14 | **Resolución**: aprobado y desplegado en PROD; el error no vuelve a aparecer en Sentry. |

## Causa raíz

El **qué** del sistema, no el quién:

1. **Un patrón de React que el lenguaje permite y nada verificaba.** Pasar una función que
   devuelve una Promise como efecto compila, renderiza y anda; sólo falla al **desmontar**. No hay
   regla de lint que lo marque (el proyecto no tiene ESLint con `react-hooks`).
2. **Ninguna capa de pruebas desmontaba Mesas.** Los unitarios del front (TP5) cubren `utils` y
   `client`, no las páginas. La e2e (TP7) crea y borra una mesa **sin salir de la pantalla**: el
   flujo que rompía, navegar a otra sección, no estaba en ningún test.
3. **No había observabilidad del front en producción.** Hasta el TP9, un error de JavaScript en
   el navegador de un usuario no llegaba a ningún lado. El monitor externo mira `/health`, que es
   del backend.

Por eso el defecto sobrevivió dos meses sin que nadie lo viera.

## Acciones

| Acción | Tipo | Dueño | Estado |
|---|---|---|---|
| Arreglo + test de regresión que monta y desmonta Mesas | Corrección | Lucas | ✅ [#69](https://github.com/lucasrodrich/ingsoft3-tp01/pull/69) |
| Buscar el mismo patrón (`useEffect(fn, …)` con una función que devuelve algo) en el resto de las páginas | Prevención | Lucas | ✅ revisado: no hay otro caso |
| Sentry en el front de PROD, para que un error del navegador llegue a alguien | Detección | Lucas | ✅ [#68](https://github.com/lucasrodrich/ingsoft3-tp01/pull/68) |
| Agregar ESLint con `eslint-plugin-react-hooks` al `build-frontend`, para que el pipeline frene el patrón antes del merge | Prevención | Lucas | Pendiente |
| Agregar a la e2e un paso de **navegación entre secciones** (entrar a Mesas y salir) | Prevención | Lucas | Pendiente |
| Alerta de Sentry por email ante un *issue* nuevo en PROD, para no depender de mirar el panel | Detección | Lucas | Pendiente |

## Aprendizajes

- **"Nadie se quejó" no es "anda".** El defecto tenía dos meses y el primer minuto con Sentry lo
  encontró. El monitor de `/health` habría seguido en verde para siempre: mira si la app está
  **viva**, no si **funciona**.
- **Lo que la pirámide no cubre se ve recién en producción.** Elegí en el TP7 qué flujos poner en
  la e2e. Este incidente cae justo en un flujo que dejé afuera. Sentry es la red para lo que los
  tests no previeron.
- **La cadena hizo barato el arreglo.** Del diagnóstico a PROD fueron ~10 minutos, con QA,
  integración, e2e y aprobación incluidos. Detectar rápido sólo sirve si también se puede corregir
  rápido y con confianza.
