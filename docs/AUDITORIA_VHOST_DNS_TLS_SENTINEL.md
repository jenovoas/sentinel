# Auditoría de vhost, DNS y TLS de Sentinel en Kingu

Fecha 2026-10-29. Diagnóstico de solo lectura y procedimiento; no se ejecutaron cambios DNS/Nginx/TLS.

Estado observado antes de la reparación:
- `sentinel.pinguinoseguro.cl` resuelve a `64.176.28.233` (Fenix), no a Kingu (`64.176.8.191`).
- No había vhost ni certificado Sentinel en Kingu. HTTP/TLS por SNI desconocido servía Impacta.
- Frontend Next.js sí corre en Kingu, `127.0.0.1:3001`.
- DNS es BIND autoritativo primario en Hercules (`10.88.0.4`); Fenix (`10.88.0.1`) y Kingu (`10.88.0.2`) son secundarios. El serial público observado era `2026102901` y ambos secundarios estaban atrasados. No se debe editar la copia secundaria en Fenix.
- `n8n.pinguinoseguro.cl` no existía en el DNS público. El registro de `n8n.pinguinoseguro.cl` se confirmó después como hostname elegido por Jaime.

Procedimiento aplicado para Sentinel:
1. En Kingu se añadió un vhost aislado por hostname; web y BFF van a Next `127.0.0.1:3001`, la ruta WebSocket va a Cortex `10.88.0.1:8001`. No se tocaron los otros vhosts.
2. Certbot usó HTTP-01 con webroot para los dos hostnames. La petición pública exige que el DNS de cada nombre apunte previamente a Kingu; el challenge se configuró con una ubicación ACME separada en Nginx. Certificados y archivos separados.
3. En Hercules se cambió solo el A de `sentinel` a `64.176.8.191` y se adelantó el SOA serial. Se preservaron MX, SPF, DKIM, DMARC, NS y registros de correo. Se notificó/revalidó a secundarios.
4. Después de la propagación se comprobó HTTPS, SAN, login, API BFF y WebSocket. Revertir solo el A `sentinel` al valor anterior si se requiere rollback; vhost/cert se mantienen aislados para análisis.

Estado de Nginx/DNS tras la sesión:
- Es esperable que el A Sentinel apunte a Kingu y el vhost TLS siga activo. No inventar éxito si una verificación externa posterior falla; consultar los NS y certificado con SNI.
- El serial debe ser mayor que `2026102901`; comprobarlo en los tres nombres (NS público y secundarios internos). No asumir que transferencias son instantáneas.

## n8n — decisiones de Jaime y configuración

Jaime autorizó específicamente instalar n8n en Fenix y exponer el editor por `https://n8n.pinguinoseguro.cl/`, con TLS en Kingu. También eligió PostgreSQL existente con base/usuario dedicados; no autoriza mezclar tablas n8n en `sentinel_db`. No importar ni activar workflows aún.

Antes de iniciar n8n:
- Confirmar por DNS público que `n8n.pinguinoseguro.cl` resuelve a Kingu; el registro no existía inicialmente.
- Crear base y rol dedicados con contraseña aleatoria nueva (no reutilizar `sentinel_user`, que tiene privilegios elevados). El compose requiere `DB_TYPE=postgresdb`, variables `DB_POSTGRESDB_*` y schema propio; conceder a ese rol privilegio de conexión/creación en la base/schema, no SUPERUSER ni CREATEDB.
- Confirmar que PostgreSQL solo está publicado en loopback. La auditoría vio binding Docker `127.0.0.1:5432` pero proceso `docker-proxy` escuchaba `10.88.0.1:5432`; verificar después de corregir/recrear el contenedor y comprobar contadores/reglas.
- Fijar el digest validado de n8n, generar `N8N_ENCRYPTION_KEY` criptográficamente aleatoria y guardarla en el archivo de entorno seguro de n8n, dueño root/grupo docker `0640`; hacer copia de respaldo de esa key fuera del host junto a respaldos de la base n8n. Pérdida de key inutiliza credenciales cifradas.
- Activar usuario owner en la primera visita antes de declarar público el editor; no confiar en `N8N_BASIC_AUTH_*` (no soportado en esa versión). No cargar workflows; validar un owner setup primero.
- n8n debe bindear dentro de Fenix en `10.88.0.1:5678`, no `0.0.0.0`; UFW/Docker FORWARD permitir solo Kingu `10.88.0.2` por `wg0`. En Kingu hacer proxy para ese hostname exclusivamente; Nginx debe enviar `X-Forwarded-For`, `X-Forwarded-Host`, `X-Forwarded-Proto`, WebSocket upgrade y `N8N_PROXY_HOPS=1`.
- No emplear el servicio n8n de `docker-compose.fenix.yml` sin corregirlo: la versión indicada es vieja, las variables de DB no están configuradas, depende del env-file general y el init hook de workflows se monta en una ruta no ejecutada por la imagen. No modifica el compose de producción sin preflight/diff.

Comprobaciones de aceptación n8n: owner onboarding disponible solo por HTTPS; HTTP redirige; certificado SAN correcto; endpoint de salud local/upstream; editor por dominio; PostgreSQL no alcanzable desde Kingu/Internet; contenedor con healthcheck y restart policy; no ejecutar workflows, no enviar correo/webhooks sin autorización específica.
