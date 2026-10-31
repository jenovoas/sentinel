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

## Actualización de fuente — 2026-10-31, sin despliegue de este recorrido

Los hallazgos anteriores son evidencia histórica del 30/10; no describen el estado de código posterior. El bloqueo de autenticación ya publicado exige `get_current_superuser` para **todas** las operaciones de la cola global: un administrador de tenant no obtiene acceso.

El recorrido de revisión incorporado en fuente reutiliza la sesión HttpOnly, validación de identidad backend, allowlist BFF y CSRF/origen existentes. Solo expone `GET gamma/pending` y `POST gamma/approve/{id}` / `gamma/deny/{id}`; creación y limpieza no se publican por el BFF. `/security/gamma` muestra la cola, contexto/evidencia como texto inerte y una confirmación explícita con justificación obligatoria. Los errores upstream no se presentan como éxitos. La navegación Gamma se muestra únicamente a identidades de plataforma, sin sustituir los controles efectivos BFF/backend.

Cortex valida `source` como `guardian_alpha` o `guardian_beta` y conserva ese origen al escalar, junto con identificadores del evento y de la decisión Cortex. Una fuente desconocida no se etiqueta como Alpha. No se cambia la escala S60 ni la representación `confidence_s60_raw`.

Aprobar/denegar realiza un `UPDATE ... WHERE status='pending' AND timeout_at > now RETURNING ...`, y añade `AuditLog` en **la misma transacción**. El actor procede exclusivamente de `get_current_superuser`, nunca del JSON cliente. Un segundo intento no sobrescribe veredicto/feedback ni genera otra auditoría; si falla la persistencia de auditoría, se revierte el cambio. La auditoría se guarda bajo el tenant/organización del revisor en el mecanismo existente, aunque la cola revisada es global. No se agrega columna, migración ni cambio de RLS.

El contexto/evidencia original permanece en `GammaDecision`; la proyección para navegador y auditoría redacta claves sensibles, credenciales reconocibles y controles, y limita profundidad, nodos y texto. Las marcas `TRUNCATED`/`REDACTED` indican omisiones; el revisor debe obtener evidencia autorizada adicional si la proyección no basta, no aprobar por ausencia de información. La justificación no debe contener secretos. El timeout automático no inventa un actor humano ni registra una aprobación.

`backend/scripts/verify_gamma_flow.py` pasa a inventario de solo lectura: imprime únicamente identificadores de decisiones, origen, tipo, confianza y fechas. Se retira su simulación de eventos y de aprobación con identidad ficticia. Las transiciones pertenecen a pruebas aisladas, no a este script operacional.

### Gates de integración y paso humano real

- Ejecutar las pruebas de permisos/autenticación, transiciones SQL/auditoría y BFF/CSRF incorporadas, y la comprobación de tipos frontend. No se ejecutaron durante esta edición.
- Las pruebas SQL aisladas usan SQLite; la atomicidad/RLS reales de PostgreSQL y dos revisores concurrentes deben validarse en integración no productiva. No sustituyen esa comprobación.
- La comprobación de referencias se hizo por búsqueda exacta de consumidores; no había herramienta LSP montada. No quedan consumidores de `submit_human_verdict`.
- Durante esta edición no se compiló ni desplegó, ni se modificaron decisiones de producción. No se habilita enforcement, XDP, nuevos attaches eBPF ni watchdog.
- Tras integración/despliegue autorizados, un operador real de plataforma debe iniciar sesión normalmente desde Kingu y revisar una **escalación genuina autorizada**. Cotejar el origen, el veredicto persistido y su `AuditLog` sin fabricar eventos, sesión/JWT ni actor. Hasta entonces no se declara probado el ciclo humano de extremo a extremo ni ejecución de una acción.
