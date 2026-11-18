# 🛡️ eBPF-Cortex Integration Status

**Fecha:** 6 de Agosto, 2026 (Actualizado)
**Estado:** ✅ Operativo / Path corregido
**Componentes:** Kernel Ring 0 <-> Userspace Ring Buffer

## 🚨 Incidente de Sincronización (Histórico)

Se detectó una discrepancia entre el `@SYSTEM_PROMPT` (que indicaba la integración como "Completada" el 19/01/2026) y el sistema de archivos (donde faltaban los componentes clave).

**Acción Correctiva:** Se han materializado y verificado los artefactos perdidos.

## ✅ Arquitectura Implementada (Actualizada 2026-08-06)

### 1. Verdad Compartida (`ebpf/cortex_events.h`)

- Definición de structs `cortex_event_t` y `s60_entropy_t`.
- Alineación C/Rust garantizada.
- Tipos `u60` simulados con enteros estrictos.

### 2. Kernel Modules (LSM - Multiple Variants)

- **`guardian_alpha_lsm.c`** — Versión base, hooks `file_open` + `bprm_check_security`
- **`lsm_ai_guardian.c`** — Versión avanzada con AI agent tracking
- **`ai_guardian.c`** — Versión completa ME-60OS con S60 entropy
- **`guardian_cognitive.c`** — Guardian cognitivo
- **`float_detector.c`** — Detector de contaminación float

**Mapas:** `BPF_MAP_TYPE_RINGBUF` (256KB) cada uno.
**Hooks:** `lsm/file_open` y `lsm/bprm_check_security`.
**Lógica:** Cálculo de entropía S60 determinista dentro del kernel.
**Estado:** Código compilado y respaldado.

### 3. Userspace Bridge (`sentinel-cortex/src/ebpf_cortex_bridge.rs`)

- Implementación Rust usando `libbpf-rs`.
- Deserialización segura de eventos desde el Ring Buffer.
- Mapeo a tipos nativos Rust.

### 4. Configuración & Paths Reales (2026-08-06)

- **LSM programs cargados en:** `/sys/fs/bpf/guardian_alpha_lsm`, `/sys/fs/bpf/lsm_ai_guardian`, `/sys/fs/bpf/ai_guardian`, `/sys/fs/bpf/guardian_cognitive`, `/sys/fs/bpf/float_detector`
- **Ring buffer principal (PAI daemon):** `/sys/fs/bpf/sentinel/events` (pinned por `guardian_gamma.c` via `bpftool prog loadall ... pinmaps /sys/fs/bpf/sentinel`)
- **Gamma watchdog:** `/sys/fs/bpf/sentinel/gamma`
- **Configuración:** `sentinel-cortex/Cargo.toml`: dependencias `libbpf-rs` y `libc`
- **PAI Neural Daemon:** Lee de `/sys/fs/bpf/sentinel/events` (fallback a `/sys/fs/bpf/cortex_events` para compatibilidad)

### 5. Verificación (`tests/test_integration_e2e.py`)

- Suite de tests Python creada.
- Validación de existencia de archivos.
- Verificación cruzada de definiciones de estructuras (C vs Rust).
- Simulación de lógica matemática S60 para asegurar consistencia.
- **Resultado:** 5/5 Tests PASADOS.

---

## ⚠️ Notas de Migración (2026-08-06)

| Documento Antiguo | Path Real Actual |
|---|---|
| `/sys/fs/bpf/ai_guardian/cortex_events` | **`/sys/fs/bpf/sentinel/events`** |
| `/sys/fs/bpf/cortex_events` | **`/sys/fs/bpf/sentinel/events`** (fallback) |
| LSM individual pins | `/sys/fs/bpf/guardian_alpha_lsm`, `/sys/fs/bpf/lsm_ai_guardian`, etc. |
| Gamma watchdog | `/sys/fs/bpf/sentinel/gamma` |

**Los docs que referencian `/sys/fs/bpf/ai_guardian/cortex_events` están DESACTUALIZADOS y deben actualizarse.**

---

## 🔧 Comandos de Carga Actuales

```bash
# Cargar LSMs individuales
sudo bpftool prog load guardian_alpha_lsm.o  /sys/fs/bpf/guardian_alpha_lsm  type lsm
sudo bpftool prog load lsm_ai_guardian.o     /sys/fs/bpf/lsm_ai_guardian     type lsm
sudo bpftool prog load ai_guardian.o         /sys/fs/bpf/ai_guardian         type lsm
sudo bpftool prog load guardian_cognitive.o  /sys/fs/bpf/guardian_cognitive  type lsm
sudo bpftool prog load float_detector.o      /sys/fs/bpf/float_detector      type lsm

# Cargar Gamma (autoattach + pinmaps en /sys/fs/bpf/sentinel)
sudo bpftool prog loadall guardian_gamma.o /sys/fs/bpf/sentinel/gamma autoattach pinmaps /sys/fs/bpf/sentinel

# Verificar estado
sudo bpftool prog show | grep -E "guardian|ai_guardian|float_detector|gamma"
ls -la /sys/fs/bpf/sentinel/
```

---

*Actualizado: 2026-08-06 — Paths corregidos tras verificación en código Rust (`pai_neural_daemon.rs`) y Makefile eBPF.*
## Recuperación del lector integrado en Fénix — 2026-11-18

Preparación local. El mapa de seguridad `events` (ID 285) estaba
asociado a `guardian_execve`; Cortex en producción no podía abrirlo
como UID 1000. El candidato monta solo el pin de seguridad, lo abre
antes de Tokio y ejecuta el lector integrado y la API con UID/GID 1000,
sin capacidades efectivas ni permitidas. Si se sustituye el objeto
pineado, se debe recrear Cortex para abrir la nueva instancia del mapa.

Validación con un mapa temporal aislado: conexión del puente, HTTP 200,
`NoNewPrivs=1`, cero capacidades y 72 pruebas de Cortex aprobadas.
El mapa y el contenedor de prueba se retiraron. Falta verificar el
aporte de un evento real a la malla tras desplegar. El carril de pulsos
de Ring 0 queda fuera de esta corrección. Sin despliegue.

### Recarga del mapa y comprobación del recorrido

La recarga de Guardian puede reemplazar el pin. El lector y el montaje de
Cortex conservan el objeto abierto hasta que el contenedor se recrea. El
montaje requiere que el pin ya exista y Compose no crea la ruta ausente. Tras
una recarga de Guardian autorizada y completada, recrear solo Cortex con el
tag configurado. Un reinicio del proceso en el mismo contenedor conserva el
montaje anterior.

Ejecutar la comprobación desde la raíz del repositorio, después de configurar
el tag del candidato con `scripts/configure-cortex-uplink.sh`. La primera
recreación habilita la traza de aceptación solo para la entrada Ring 0.

```bash
sudo -n docker compose --env-file /etc/sentinel/backend.env \
  -f docker-compose.fenix.yml -f - up -d --no-build --no-deps \
  --force-recreate --wait --wait-timeout 90 cortex <<'YAML'
services:
  cortex:
    environment:
      RUST_LOG: "info,sentinel_cortex::ring0=debug"
YAML

mapa=$(sudo -n bpftool -j map show pinned /sys/fs/bpf/sentinel/events | jq -er .id)
cortex_pid=$(sudo -n docker inspect -f '{{.State.Pid}}' sentinel-cortex)
sudo -n bash -c 'grep -h "^map_id:" /proc/"$1"/fdinfo/*' _ "$cortex_pid" |
  awk -v mapa="$mapa" '$2 == mapa { presente = 1 } END { exit !presente }'
sudo -n awk '/^(Uid|Gid|CapPrm|CapEff|NoNewPrivs):/' "/proc/$cortex_pid/status"

inicio=$(date -u +%Y-%m-%dT%H:%M:%SZ)
marca_kernel=$(python3 -c 'import time; print(time.monotonic_ns())')
pid_prueba=$(sh -c 'printf "%s\n" "$$"; exec /usr/bin/true')
raw_esperado=$((12960000 + pid_prueba % 60))
indice_esperado=$((pid_prueba % 64))
aceptada=0
for intento in $(seq 1 10); do
  if sudo -n docker logs --since "$inicio" sentinel-cortex 2>&1 |
    sed -E 's/\x1B\[[0-9;]*m//g' |
    rg 'Amplitud de Ring 0 aplicada a la malla de seguridad' |
    rg "pid=${pid_prueba} " |
    rg "index=${indice_esperado} " |
    rg "amplitude_raw=${raw_esperado} " |
    rg 'timestamp_ns=[1-9][0-9]*.*dtc_tick=[1-9][0-9]*' |
    awk -v minimo="$marca_kernel" '
      /timestamp_ns=/ {
        for (i = 1; i <= NF; i++) {
          split($i, campo, "=")
          if (campo[1] == "timestamp_ns" && campo[2] + 0 >= minimo) {
            print
            fresca = 1
          }
        }
      }
      END { exit !fresca }
    '; then
    aceptada=1
    break
  fi
  sleep 1
done
test "$aceptada" -eq 1
```

El comando `true` debe estar permitido por la política vigente y ejecutarse
en el host, bajo la identidad autorizada. La traza se emite después de la
inyección y conserva el PID y la marca monotónica del evento real. Una
conexión activa por sí sola acredita que el lector abrió el anillo.

Al terminar, recuperar el nivel de registro normal y repetir la comprobación
del ID del mapa y las credenciales del proceso.

```bash
sudo -n docker compose --env-file /etc/sentinel/backend.env \
  -f docker-compose.fenix.yml up -d --no-build --no-deps \
  --force-recreate --wait --wait-timeout 90 cortex
```

Si se requiere revertir el candidato, restaurar juntos el tag anterior y la
definición de Compose compatible con ese binario. Este comando usa la
definición de la imagen previamente observada y recrea solo Cortex.

```bash
reversion_compose=$(mktemp /tmp/sentinel-cortex-rollback.XXXXXX.yml)
git show d8c109b9:docker-compose.fenix.yml > "$reversion_compose"
sudo -n bash scripts/configure-cortex-uplink.sh sentinel-cortex:d8c109b9
sudo -n docker compose --project-directory "$PWD" --env-file /etc/sentinel/backend.env \
  -f "$reversion_compose" up -d --no-build --no-deps \
  --force-recreate --wait --wait-timeout 90 cortex
```

Artefacto de preparación local generado con
`scripts/build-sentinel-cortex-image.sh sentinel-cortex:ring0-a9d742c8dc3a0814`.
ID local `sha256:67b3531aa15d42b086c68b5b5bfa9581c5651b6bd8cc8982b2c116aa7781b2e5`.
El diff acotado al código y Compose produjo
`a9d742c8dc3a0814cc708166740df30815a7d362e029faa47eeaaa4b56dea92d`.
Validaron las cuatro pruebas de entrada MyCNet, la prueba del paso DTC, la
sintaxis de los tres bloques Bash y el esquema de Compose. No se desplegó.

### Primera aplicación en Fénix y reversión

El 2026-11-18, la imagen `sentinel-cortex:ring0-a9d742c8dc3a0814` pasó
la prueba aislada del endpoint autenticado (HTTP 200, lector activo, UID/GID
1000 y cero capacidades). Se recreó solo Cortex con autorización. El proceso
2759335 fue el único con un descriptor del anillo real 285. Docker informó
`healthy`. Con 1.261 ticks DTC, la cola tenía dos tareas, sin fallos ni
despachos por portal.

Journald conserva 385 aplicaciones a la malla de seguridad entre
15:24:04.027363 y 15:24:18.472806 UTC. La última registró PID 108451,
timestamp monotónico 659291854129 ns, índice 35, amplitud SPA cruda
12960031 y tick 602. Los timestamps monotónicos de esos eventos abarcan
aproximadamente 652–659 segundos de uptime, por lo que eran eventos
retenidos del inicio del host. Después cesaron las aplicaciones registradas
aunque el DTC siguió avanzando. El estímulo autorizado no dejó una
aplicación observable en la ventana de aceptación. Se restauró
`sentinel-cortex:d8c109b9`, verificada `healthy` y con API operativa.
El consumo previo era 81,44 % de un núcleo en 20,01 segundos. No se tomó
una ventana de consumo posterior del candidato, al fallar la aceptación.

En el candidato siguiente, una prueba con búfer de capacidad dos y tres
envíos verifica que el consumidor reanuda tras `Lagged`, recibe también
un evento posterior y sale al cerrarse el canal. El código anterior
terminaba la tarea ante ese error y no lo registraba. También se registran
pérdidas por canal lleno o cerrado antes de la inyección, con mensajes en
los recuentos acumulados que son potencias de dos. El defecto se reprodujo
en prueba local. No se atribuye el cese en vivo a una causa única sin una
traza operativa adicional.

Segundo artefacto local `sentinel-cortex:ring0-fe5bcbfb6be24b62`, ID
`sha256:5f4b4dacb722b666a09ba1dfdfe354550e41c6600e417ae9b938ad0930292751`.
SHA-256 del diff acotado al código y Compose
`fe5bcbfb6be24b622bb3447c0d428590df8ee6558dc61c26c76725bae926e32b`.
La prueba de ráfaga pasó con
`cargo test --offline -p sentinel-cortex --bin sentinel-cortex ring0_lattice_consumer_continues_after_broadcast_lag`.
El segundo artefacto todavía no se aplicó.
## Entrega local de Ring 0 al cristal — 2026-11-18

El único lector de Cortex entrega los eventos a una cola Tokio acotada. El
procesador aplica Guardian, actualiza la malla resonante, la malla líquida y la
memoria neural, y entrega la amplitud cruda a CrystalRuntime por una segunda
cola acotada, dedicada a Ring 0. Cuando esa cola se llena, la espera se propaga
al lector. El hilo del cristal comprueba los plazos del DTC, el paso y las
tareas del GAP entre aplicaciones de Ring 0. MyCNet y el pulso térmico siguen
usando su cola previa. WebSocket recibe una copia por `broadcast` y puede
perderla si su suscriptor se retrasa.

La prueba `ring0_rafaga_llega_al_cristal_aunque_observador_se_retrase` saturó
las colas acotadas de dos posiciones con 257 eventos. Los 257 llegaron en
orden con su PID, timestamp, índice y amplitud SPA exactos. Se verificó el
incremento acumulado de amplitud de la malla de seguridad en un CrystalRuntime
en memoria. El observador omitió 255 eventos. La suite
`cargo test -p sentinel-cortex` pasó con 161 pruebas.

El cierre de canales internos se registra por separado del atraso de un
observador. La contrapresión puede llenar el anillo del kernel. Guardian
Alpha retorna sin incrementar un contador cuando falla
`bpf_ringbuf_reserve` en `ebpf/guardian_alpha_lsm.c`. La prueba ejercitó la
ruta posterior a la lectura. Quedan por medir las pérdidas antes de la
lectura, el rendimiento y las cadencias bajo carga real. Preparación local.

Artefacto local `sentinel-cortex:ring0-4dba806ef3302060` (Linux amd64),
ID `sha256:b99d49b39d70c5c06569a8e533527fd47c3b7ea61706324a3830ad9919a933a5`.
El script `scripts/build-sentinel-cortex-image.sh` terminó correctamente.
SHA-256 del diff de Compose y de las cuatro fuentes de Cortex involucradas
`4dba806ef330206037463a3b8cf564f5b4f56f2edda46a8602df89d8806e9f0b`.
`docker compose config --quiet` validó la definición candidata con el
entorno de Fénix. La creación de la imagen no recreó servicios.

### Aplicación del candidato y reversión en Fénix

El 2026-11-18 se recreó únicamente Cortex con
`sentinel-cortex:ring0-4dba806ef3302060` y la traza de aceptación habilitada.
La configuración anterior quedó respaldada por el instalador. El candidato
quedó `healthy` y se conectó al mapa `events` 285 de 262.144 bytes. El único
descriptor del mapa en el host fue el 3 del proceso Cortex 3013340.
Los cuatro UID y GID eran 1000, `CapPrm=CapEff=0` y `NoNewPrivs=1`.

No apareció, en diez segundos, el estímulo permitido `/usr/bin/true` de UID
1000 y PID 3016304, índice esperado 48, amplitud esperada 12960044 y marca
mínima 245483565780038 ns. Se restauró `sentinel-cortex:d8c109b9`, ID
`sha256:ad570b825736f20e2dc848e39c2c8bcd8e00d12dbec1d45b5396cfd0ecdc05fc`,
con Compose de esa revisión. La imagen anterior volvió a `healthy` y
`/health` respondió HTTP 200. Guardian y el resto de servicios siguieron activos.

Journald registra 1.856 aplicaciones del candidato en 81,726 s (22,698/s),
desde el tick DTC 0 al 3406. La edad desde la generación del evento hasta su
registro tras la aplicación, usando ambas marcas monotónicas en el mismo
host, creció de 840,983 a 883,986 s (mediana 858,025 s). Los eventos
aplicados cubrieron 38,723 s de tiempo de origen, una densidad observada de
47,9 eventos/s retenidos. Ninguna aplicación fue posterior en origen al
estímulo. Estas trazas no permiten conocer cuántas reservas fallaron en el
kernel ni aislar qué fracción del atraso correspondía a cada cola.

El historial explica el paso por evento. `869beaf6` lo introdujo para
`ResonantLatticeBridge` junto con el paso térmico de 500 ms. `22716ef0`
unificó los lectores de la malla con CrystalRuntime e hizo que sus
inyecciones por evento evolucionaran solo en el paso de 500 ms. `f2f522bc`
volvió a introducir la malla de consulta con ambos pasos al portar los
cambios de Alpine. Hoy la malla de consulta sigue alimentando lattice,
holograma, fonones, métricas y estado de Sentinel.

Una sonda aislada en Fénix enlazada a `libme60os_core.rlib` de release midió
la secuencia de inyección y paso de `ResonantMatrix` en tres lotes de 32
pasos, tras precalentar 32. En 67.951 nodos la mediana fue 32,555 ms por
evento en modo disipativo y 34,472 ms en modo superconductor. La inyección
sola en lotes de 20.000 tardó 46 ns y 20 ns por evento, respectivamente. En
64 nodos, las medianas de inyección y paso fueron 56 y 59 µs. El paso
atraviesa toda la malla y realiza la transferencia entre vecinos.

### Candidato con paso periódico en la malla de consulta

La preparación local mantiene cada inyección Ring 0 en la malla de
consulta y ejecuta una sola evolución con el pulso existente de 500 ms.
El test `ring0_inyecta_en_la_malla_de_consulta_hasta_el_siguiente_pulso`
verificó dos entradas consecutivas: ambas conservan su amplitud SPA y
orden en la cola del cristal, el nodo de consulta suma ambas, las fases
permanecen estables entre entradas y el pulso térmico produce las mismas
amplitudes y fases que un paso de referencia. La suite
`cargo test -p sentinel-cortex` pasó con 162 pruebas.

Para distinguir atraso de pérdida durante la aceptación, medir las
aplicaciones en ventanas de 10 segundos, usando el reloj monotónico de
Journald y el timestamp del evento. Esperar una aplicación de hasta dos
segundos de edad antes de emitir el estímulo autorizado. Si la edad
deja de converger durante tres ventanas, o no llega al umbral en 90
segundos, revertir. Guardian 1379 carece de `run_cnt` porque el host tiene
`kernel.bpf_stats_enabled=0`. El ritmo total previo a la reserva no se
midió. Se conserva la densidad histórica de 47,9 eventos/s retenidos como
cota inferior de aquella ventana.

El segundo candidato, `sentinel-cortex:ring0-5e1252faaece50e8`, ID
`sha256:02de615f788c3d1984fb494d83328baa603a851c2a8384e9de36e509444f2839`,
quedó `healthy` en Fénix. El proceso 3104631 conservó el único descriptor
(3) del mapa 285 con UID/GID 1000, capacidades efectivas y permitidas en cero
y `NoNewPrivs=1`. Se midieron siete ventanas de diez segundos con
435/435/440/438/435/437/438 aplicaciones. La edad del último evento en cada
ventana fue 1329,116 / 1333,436 / 589,862 / 581,641 / 584,894 / 593,797 /
599,461 s. La tasa de aplicación fue 43,5–44,0/s. Estas ventanas miden edad
y tasa, sin determinar el número de eventos pendientes en cada cola.

El consumidor se despertaba cerca del vencimiento del DTC, aplicaba un
evento y volvía al trabajo periódico. El presupuesto hasta el mismo plazo
ya vencido explicaba la tasa cercana a un evento por tick. La frescura no
alcanzó el umbral acordado y empeoró tres ventanas consecutivas. Se omitió
el estímulo y se restauró `sentinel-cortex:d8c109b9`, `healthy`, PID
3123460, con HTTP 200 en `/health`. El salto en los timestamps de origen
no permite contar reservas fallidas del kernel. El mapa y Guardian se
mantuvieron en su estado operativo.

### Drenado tras el vencimiento físico

El siguiente candidato atiende DTC, paso y tareas GAP antes de drenar la
cola Ring 0 hasta el próximo vencimiento, con un tope por ciclo de 1.024
entradas. Si el plazo ya vence, conserva el progreso de una entrada por
ciclo. La traza de diagnóstico muestrea cuántas entradas quedan antes y
después de cada drenado muestreado y cuántas se aplicaron en ese ciclo.

La prueba `ring0_drena_varias_entradas_tras_atender_el_plazo_del_cristal`
comprueba que, con el plazo vencido, queda la cola pendiente tras una
entrada. Un tick real de CrystalRuntime avanza la cadencia, y el margen
siguiente admite las 31 entradas restantes con el incremento exacto de
amplitud y sin ticks adicionales. La suite pasó con 163 pruebas.
Artefacto `sentinel-cortex:ring0-960d006283355f53`, ID
`sha256:5b75847c2725176b55de039953e567e918ff5803470ec0e67c32f66127731b85`.
El script de build oficial y `docker compose config --quiet` terminaron
correctamente. SHA-256 del diff del candidato
`960d006283355f53bf5541c4542f99363811b6cbc597553c2f61df8c1fc702c3`.

### Aceptación y estado operativo de Fénix

El 2026-11-18 quedó desplegado `sentinel-cortex:ring0-960d006283355f53`.
Se recreó solo Cortex. Durante la traza, el PID 3165136 tuvo el único
descriptor (3) del anillo 285. En una ventana de diez segundos se
observaron 1.175 aplicaciones y el evento más reciente tenía 0,246 s de
edad. Doce muestras de la cola de CrystalRuntime mostraron 1–43 entradas
antes del drenado, 0–42 después y 1–19 aplicaciones por ciclo muestreado.
La ventana incluye recuperación de eventos retenidos.

El estímulo autorizado `/usr/bin/true` (UID 1000, PID 3171868) se aplicó
en el índice 28, con amplitud cruda 12960028 y tick DTC 1709. La marca
del evento, 246420195451225 ns, superó la marca tomada antes del estímulo
(246420194020863 ns). La latencia monotónica de generación a registro
posterior a la aplicación fue 13,671 ms.

Tras volver a `RUST_LOG=info` sin cambiar la imagen, Cortex quedó
`healthy` y `/health` respondió HTTP 200. El nuevo PID 3176786 conservó
el único descriptor (3) del mismo anillo 285, UID/GID 1000 en los cuatro
campos, capacidades efectivas y permitidas en cero y `NoNewPrivs=1`.
En 45,002 s, `cpu.stat` del cgroup midió 77,51 % de un núcleo y el DTC
avanzó de 1279 a 3149 (41,554 Hz). La cola GAP se mantuvo en dos tareas.
Se observaron cero despachos por portal, cero fallos y un checkpoint
crítico, confirmado por el log de persistencia de las 16:06:39 UTC. La
comprobación posterior mantuvo el mismo PID, imagen y estado `healthy`,
con DTC 3742. Guardian y los demás servicios se mantuvieron en su
configuración. No se dispone de un contador de reservas fallidas del
anillo en el kernel.
