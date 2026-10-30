# Auditoría de la cadena Guardian Beta → Gamma — 2026-10-30

## Topología cotejada

La ruta prevista en el código activo es `Guardian Alpha/eBPF en Marte → sentinel-security-gateway → POST /api/v1/cortex/events en FastAPI/Fenix → CortexDecisionEngine → GammaDecision en PostgreSQL → revisión humana desde Kingu`. El gateway de Marte envía `source="guardian_alpha"`; la recepción de un HTTP 201 confirma ingestión, no que se haya generado una decisión ni que haya llegado a Gamma.

## Evidencia de código vigente

- `sentinel-cortex/src/bin/sentinel-security-gateway.rs` obtiene eventos del ring buffer `/sys/fs/bpf/guardian_alpha/events`, forma eventos con fuente `guardian_alpha` y los envía al endpoint privado de Fenix.
- `backend/app/routers/cortex.py` exige `X-Sentinel-Token` en `POST /api/v1/cortex/events`, instancia `CortexDecisionEngine` y retorna una decisión.
- `CortexDecisionEngine.process_event()` persiste la decisión y llama `_escalate_to_gamma()` solo si la decisión es `escalate`. Esa función crea la fila Gamma, pero pasa `guardian=GuardianSource.ALPHA` de forma fija; no conserva la fuente real del evento.
- `backend/app/routers/gamma.py` define crear, listar, aprobar y rechazar decisiones. Esas operaciones no declaran dependencia de usuario autenticado/rol administrativo ni token de servicio; `backend/app/main.py` no instala middleware de autenticación global. El token de telemetría protege el endpoint de eventos, no las rutas Gamma.
- La app Kingu tiene un BFF con allowlist de rutas y controles de sesión/CSRF, pero la lista `BACKEND_ROUTES` no incluye Gamma. No hay páginas/componentes de Guardian Gamma en `frontend/src/app`.

## Evidencia de runtime — Fenix/Kingu, 2026-10-30

- Los logs disponibles de `sentinel-backend` muestran peticiones repetidas de Marte (`10.88.0.6`) a `POST /api/v1/cortex/events` con HTTP 201. En las últimas 24 h consultadas no aparecieron logs de “Escalated decision” ni errores de escalación.
- `GET /api/v1/gamma/pending?limit=1` respondió HTTP 200 sin credenciales y la respuesta contenía cero decisiones pendientes.
- La ruta BFF de Kingu `GET /api/v1/gamma/pending` sin sesión respondió HTTP 404 por ruta no permitida. No hay UI/BFF operativa para completar la revisión humana.
- No se generó un evento artificial ni se aprobó/rechazó ninguna decisión durante esta auditoría.

## Dictamen y gates pendientes

El transporte Alpha→Fenix está activo; la aceptación de HTTP 201 no prueba el ciclo Cortex→Gamma. No hay evidencia runtime de una escalación reciente, la fuente se fija como Alpha, el API Gamma carece de autorización de aplicación y la UI/BFF Kingu no expone el flujo.

Antes de declarar Beta→Gamma desplegado: conservar la fuente del evento; proteger todas las operaciones Gamma con identidad y rol administrativo (incluidas aprobación/rechazo y limpieza); conectar únicamente las rutas necesarias al BFF Kingu con sesión, CSRF y autorización; añadir una pantalla de decisión; y validar un caso autorizado de extremo a extremo con decisión persistida y audit trail. No se modificó código de API, no se desplegó ningún servicio y no se habilitó enforcement.
