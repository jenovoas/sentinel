# QWEN TASK — Fase Alif: Anycast VIP sobre batman-adv mesh

**Asignado por**: Claude (Arquitecto)
**Prioridad**: ALTA
**Fecha**: 2026-02-28

---

## Objetivo

Completar el mesh batman-adv entre nodos del enjambre y activar un
Anycast VIP en bat0 para alta disponibilidad.

---

## Estado actual (verificado por Claude)

| Nodo     | WireGuard IP | bat0 IP      | GRE tunnel          |
|----------|--------------|--------------|---------------------|
| fenix    | 10.10.10.8   | 10.10.0.8/24 | gre-sentinel UP ✅  |
| sentinel | 10.10.10.2   | ?            | verificar           |
| kingu    | 10.10.10.4   | ?            | no existe aún       |

- `gre-sentinel` en fenix: GRETAP remote=10.10.10.2 local=10.10.10.8, master=bat0, carrier=1
- WireGuard OK: ping entre todos los nodos por 10.10.10.x funciona

---

## REGLA: NO INVENTAR

Mostrar output real de cada comando. Si algo falla, reportar el error exacto.
No simular éxito. No omitir errores.

---

## Pasos

### 1. Verificar sentinel

```bash
ssh 10.10.10.2 "ip link show type gretap; ip addr show bat0 2>/dev/null"
```

Si NO existe gre-fenix en sentinel, crearlo:

```bash
ssh 10.10.10.2 "
  modprobe batman-adv 2>&1 || true
  ip link add gre-fenix type gretap remote 10.10.10.8 local 10.10.10.2 ttl 64 2>&1 || true
  ip link set gre-fenix master bat0 2>&1 || true
  ip link set gre-fenix up 2>&1
  ip addr add 10.10.0.2/24 dev bat0 2>&1 || true
  ip link set bat0 up 2>&1
  ip addr show bat0
"
```

### 2. Verificar vecinos batman-adv

```bash
cat /proc/net/batman-adv/bat0/originators 2>/dev/null || echo "no originators"
ssh 10.10.10.2 "cat /proc/net/batman-adv/bat0/originators 2>/dev/null || echo 'no originators'"
```

Si hay MACs listadas: mesh activo, saltar al Paso 4.

### 3. Agregar kingu al mesh

```bash
# En kingu:
ssh 10.10.10.4 "
  modprobe batman-adv 2>&1 || true
  ip link add bat0 type batadv 2>/dev/null || true
  ip link add gre-fenix type gretap remote 10.10.10.8 local 10.10.10.4 ttl 64 2>&1 || true
  ip link set gre-fenix master bat0 2>&1 || true
  ip link set gre-fenix up 2>&1
  ip addr add 10.10.0.4/24 dev bat0 2>&1 || true
  ip link set bat0 up 2>&1
"
# En fenix, agregar lado kingu:
ip link add gre-kingu type gretap remote 10.10.10.4 local 10.10.10.8 ttl 64 2>&1 || true
ip link set gre-kingu master bat0 2>&1 || true
ip link set gre-kingu up 2>&1
```

### 4. Anycast VIP

```bash
ip addr add 10.10.0.1/32 dev bat0 2>/dev/null || true
ssh 10.10.10.2 "ip addr add 10.10.0.1/32 dev bat0 2>/dev/null || true"
ssh 10.10.10.4 "ip addr add 10.10.0.1/32 dev bat0 2>/dev/null || true"
```

### 5. Persistencia systemd en fenix

Crear `/usr/local/bin/mycnet-mesh-up.sh` con los comandos que funcionaron.
Crear `/etc/systemd/system/mycnet-mesh.service`:

```ini
[Unit]
Description=MycNet batman-adv mesh (Fase Alif)
After=wg-quick@wg0.service network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/mycnet-mesh-up.sh

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload && systemctl enable mycnet-mesh.service
```

### 6. Redis

```bash
REDIS_PASS=$(grep requirepass /etc/redis/redis.conf 2>/dev/null | awk '{print $2}')
redis-cli -h 10.10.10.2 -a "$REDIS_PASS" SET swarm:infra:alif_status "ACTIVE"
redis-cli -h 10.10.10.2 -a "$REDIS_PASS" HSET swarm:infra:alif \
  mesh_nodes "fenix,sentinel,kingu" anycast_vip "10.10.0.1" timestamp "$(date -u +%s)"
```

---

## Verificación final

```bash
ping -c3 10.10.0.1
ping -c3 10.10.0.2
cat /proc/net/batman-adv/bat0/originators
```

---

## Output requerido

Crear `QWEN_RESULT.md` con output real de cada paso (sin inventar).
