# Procedimiento Estándar de Despliegue — Sentinel / PinguinoSeguro

**Vigencia:** 2026-10-30 · **Rama:** `main` (systemd) / `alpine_fenix` (Alpine/OpenRC, no mezclar)
**Origen:** lecciones del despliegue 2026-10-30 (auditoría multínodo + auditoría sesión Codex `01a18afb`).
**Fuente de verdad de topología:** `docs/ops/CABLEADO_Y_TOPOLOGIA_CANONICA.md`.

---

## 1. Alcance

### Incluye

| Nodo | Rol | Qué se despliega |
|---|---|---|
| `fenix` (10.88.0.1) | Backend central + PDC | `sentinel-backend`, `sentinel-cortex`, postgres, redis, n8n, Samba AD PDC, QHC agent |
| `kingu` (10.88.0.2) | Frontend producción + BDC | `sentinel-frontend.service`, nginx edge :80/:443, Guacamole + AD, Samba AD BDC |
| `marte` (10.88.0.6:4222) | Seguridad + observabilidad | Grafana, Prometheus, Mimir, Loki, Alloy, Guardian/eBPF + forwarder a Fenix |
| `hercules` / `ocean` | DNS externos (DMZ) | Solo DNS público. **Nada de AD, nada de Sentinel.** |

### Excluye explícitamente

- **Soma / orquestación de agentes**: aparcado, no se despliega ni se inicia.
- **Inferencia IA**: sin GPU y sin cliente piloto; no se despliega. El bus (`mycnet-memory` + `sentinel_bridge`) queda reservado.
- **FPU como daemon, hardware de laboratorio** (memoria fotónica, etc.): no desplegables. Ver `AUDITORIA_DESPLIEGUE_MULTINODO_2026-10-30.md` § cotejo papers.

---

## 2. Reglas duras para agentes (IA o humano)

Nacidas de la auditoría a la sesión Codex del 2026-10-30. **Violarlas detiene el despliegue.**

1. **Todo `sudo` remoto lleva `-n`.** Sin excepción: `ssh host 'sudo -n …'`. Un sudo colgado esperando password bloquea horas (Marte, caso real).
2. **Cero passwords en CLI.** Ni `--data-urlencode password=`, ni `PGPASSWORD=` en línea, ni tokens en URLs. Usar archivos con `0600`, variables de entorno vía fichero, o `psql` con `.pgpass`.
3. **Prohibido `curl -k` / `--insecure`** contra cualquier dominio productivo. Si TLS falla, se arregla TLS, no se salta.
4. **Prohibido `sed -i` directo sobre `/etc/`.** Cambios en `/etc/sentinel/*`: plantilla versionada en repo → copiar → `chown root:docker 0640` → `compose config --quiet` valida. Backup previo: `cp -a f f.$(date +%F)`.
5. **`graphify update .` una sola vez** por sesión, al final si hubo cambios. Nunca en loop (20× en un día sobre 207k nodos).
6. **Imágenes con pin.** Nada de `postgres:16-alpine` flotante en producción: tag inmutable o digest.
7. **Un `apply`/cambio = un `git commit` + push.** La sesión auditada dejó 4 archivos sin commitear tras "comitea y empuja".
8. **Leer la vault y los experimentos antes de preguntar al operador.** La generalización ("proyecto genérico") está prohibida: es investigación de años con código propio.
9. **SSH a marte: puerto 4222, sin asumir ruta.** Si `No route to host` desde una ruta, se reporta como límite de la ruta, no como caída del nodo. El operador verifica por su vía.
10. **`hercules`/`ocean` son DMZ**: ningún cambio de AD, firewall interno o Sentinel los toca.

---

## 3. Preflight (obligatorio, antes de tocar nada)

```bash
# 3.1 Rama y árbol limpio en cada checkout tocado
git status --porcelain=v1 -b && git log --oneline -3

# 3.2 Conectividad mesh (desde el operador o nodo con ruta)
for h in fenix kingu marte hercules ocean; do
  printf '%s: ' "$h"
  timeout 8 ssh -o BatchMode=yes -o ConnectTimeout=5 "$h" 'hostname' 2>&1
done
# marte va por 4222; si falla SOLO desde una ruta, anotar y seguir por vía del operador.

# 3.3 Estado de servicios por nodo
ssh fenix  'sudo -n docker ps --format "{{.Names}} {{.Status}}"'        # backend + cortex + guacamole
ssh kingu  'systemctl is-active sentinel-frontend.service; sudo -n ss -lnt | grep -E ":443|:80"'
ssh -p 4222 marte 'sudo -n docker ps --format "{{.Names}} {{.Status}}"'  # grafana/mimir/prometheus/loki/alloy

# 3.4 AD: PDC responde, BDC unido
ssh fenix 'sudo -n samba-tool domain level show'   # PDC
# join kingu solo si BDC ausente; comando de una línea, sin saltos (rompe zsh del operador).

# 3.5 Firewall efectivo ANTES de agregar reglas
ssh fenix 'sudo -n firewall-cmd --get-active-zones; sudo -n firewall-cmd --get-policies'
```

Si cualquier preflight falla: **detener, diagnosticar, no desplegar encima.**

## 3.6 Zonas firewalld Fenix — diseño final (verificado 2026-10-30)

| Zona | Sources | Forward | Propósito |
|---|---|---|---|
| `guac-internal` | `172.25.0.0/16` | yes | Red interna Guacamole (DB). DROP por defecto, solo forwarding gestionado |
| `guac-edge` | `172.26.0.0/16 172.27.0.0/16` | no | Sesiones guacd→destinos. DROP, egress por rich rules puntuales, no forward global |
| `ad-ldap` | `172.21/16 172.23/16 172.24/16` | — | Contenedores que autentican LDAPS contra Fenix |
| `sentinel-bridge` | `br-cbd16f207701` | — | Bridge contenedores Sentinel |
| `wgmesh` | `wg0` | — | Mesh WireGuard 10.88.0.0/24 |
| `public` | `enp1s0` (default) | — | Solo :80/:443 edge, resto DROP |

No crear más zonas sin registrar aquí.

---

## 4. Fases de despliegue

### Fase A — Fenix (backend)

1. Checkout limpio en la rama del entorno (`main`). `git pull`, árbol limpio.
2. Build imagen cortex versionada: `./scripts/build-sentinel-cortex-image.sh sentinel-cortex:<SHA>` (conservar anterior para rollback).
3. Fijar `SENTINEL_CORTEX_IMAGE=sentinel-cortex:<SHA>` en `/etc/sentinel/backend.env` (vía plantilla, regla 4), `0640 root:docker`.
4. `docker compose --env-file /etc/sentinel/backend.env -f docker-compose.fenix.yml config --quiet` **antes** de `up`.
5. `up -d --no-build --no-deps <servicio>` — solo el servicio cambiado. Nunca reiniciar postgres/redis "por si acaso".
6. Verificar: contenedor `healthy` + endpoint con y sin auth (`401` sin bearer = middleware vivo, no = roto).

### Fase B — Kingu (frontend + edge)

1. `sentinel-frontend.service`: release nuevo bajo `/opt/sentinel/frontend/releases/<SHA>`, cambio atómico de enlace, `systemctl reload-or-restart`.
2. `nginx -t` antes de `reload`. HTTPS: `/login` 200, HSTS/CSP presentes (hardening pendiente desde auditoría: verificar cabeceras).
3. Guacamole: smoke con usuario de prueba inexistente (debe rechazar, no 500) + login real del operador.

### Fase C — Marte (observabilidad + Guardian)

Precondición: **whitelist de ejecutables y rutas críticas poblada y verificada.** Bootstrap en auditoría, enforcement solo con autorización explícita separada.

1. Grafana/Prometheus/Mimir/Loki/Alloy: `healthy`, apuntando a Fenix (`10.88.0.1`) por WireGuard.
2. Guardian/eBPF: adjuntar en **auditoría**, verificar eventos en `POST /api/v1/cortex/events` (cabecera `X-Sentinel-Token`, secreto distribuido fuera de CLI).
3. Forwarder remoto verificable (el actual `bpftool prog tracelog` solo escribe local: insuficiente).

### Fase D — Registro

1. `git commit` + `push` de todo lo cambiado (código, `/etc` plantillas, docs).
2. Entrada en vault (`personalvault`) con: SHA desplegados, evidencia de smoke tests, estado por nodo, brechas abiertas.
3. Actualizar este documento si el despliegue enseñó algo nuevo.

---

## 5. Smoke tests mínimos por despliegue

| # | Prueba | OK esperado |
|---|---|---|
| 1 | `git status` limpio en todos los checkouts tocados | vacío |
| 2 | Endpoints públicos: Sentinel `/login`, portal, Guacamole | 200 + TLS válido, sin `-k` |
| 3 | Endpoints privados sin bearer | 401 (no 500, no timeout) |
| 4 | `docker ps` / `systemctl`: servicios objetivo | `healthy` / `active` |
| 5 | Cortex: `PULSE CHECK` en logs post-QHC | `QHC=true`, sin `DEAD MAN SWITCH` |
| 6 | Firewall: sonda desde nodo NO autorizado a puertos API | timeout/rechazo |
| 7 | Alembic `current` == head (si hubo migración) | coincide |

---

## 6. Rollback

- **Cortex/backend:** imagen anterior conservada → fijar tag previo en `backend.env` → `up -d` → smoke 1–6.
- **Frontend:** re-enlazar release previo → `reload-or-restart` → smoke 2.
- **Firewall:** `firewall-cmd --runtime` primero para probar; `--permanent` + `reload` solo tras verificar. Regla mala = `--remove-*` en runtime, sin reload a ciegas.
- **AD:** nunca "des-unir" para probar. Si el join falla, el error de `samba-tool` manda; no reintentar con variantes inventadas.

---

## 7. Prohibiciones reiteradas (resumen pegable en prompts a agentes)

> Despliegue Sentinel: `sudo -n` siempre en remoto; cero passwords/tokens en CLI; prohibido `curl -k`; prohibido `sed -i` en `/etc` (plantilla + backup + validate); imágenes pineadas; `graphify update` una vez; Soma e inferencia fuera de alcance; hercules/ocean no se tocan salvo DNS; marte por 4222; un cambio = un commit + push + entrada en vault.
