# Auditoría de segmentación de Hercules y Ocean — 2026-10-30

## Alcance de esta captura

Lectura de Firewalld/nftables, interfaces y listeners en Hercules (`10.88.0.4`) y Ocean (`10.88.0.5`), comprobación de SSH por WireGuard y lectura de las reglas GCP, Vultr y Linode disponibles. Esta captura no representa todavía una auditoría completa de todos los nodos ni sustituye una prueba desde una tercera red externa.

## Resultado

- **DMZ configurada:** Hercules pertenece a GCP `default`, con `ens4` en la zona Firewalld explícita `dmz` (`target=DROP`), que solo permite DNS TCP/UDP 53 y WireGuard UDP/51820 desde los tres peers públicos configurados. `wg0` permanece en `wgmesh`. Ocean mantiene nftables con `input policy drop`, DNS TCP/UDP 53 y WireGuard UDP/51820 en `eth0`; se añadió y asignó el Cloud Firewall `ocean-dmz` con política inbound `DROP`, esas mismas excepciones para IPv4/IPv6 y outbound `ACCEPT`.
- **Administración SSH:** ambos `sshd` escuchan en TCP/4222; el firewall del host solo lo acepta por `wg0` desde `10.88.0.1` y `10.88.0.3`. GCP y Linode Cloud Firewall no permiten SSH público en TCP/22 ni TCP/4222. Se comprobó SSH por VPN y se probaron ambos puertos desde iFenix por IP pública: quedaron filtrados. No existe listener en TCP/22.
- **Exposición DNS pública intencional:** ambos hosts responden SOA para `pinguinoseguro.cl` en TCP/UDP 53 en sus IP públicas. GCP permite 53 desde cualquier origen solo a instancias con tag `dns-authoritative`; Hercules tiene ese tag y permite DNS en `dmz`. Ocean acepta DNS TCP/UDP 53 por `eth0`; nftables y Linode Cloud Firewall mantienen DNS en IPv4 e IPv6 públicas. Si DNS autoritativo debe seguir público, estas excepciones son necesarias.
- **Capas de nube:** GCP tiene DNS TCP/UDP 53 público para el tag `dns-authoritative`; `allow-kingu-wireguard` limita UDP/51820 al origen Fenix, Kingu y Ocean y al tag `dns-server`. Se creó `deny-hercules-internal-vpc` (prioridad 900) para descartar todo tráfico de `10.128.0.0/9` al tag `dns-server`, antes de `default-allow-internal` (65534); las consultas públicas DNS desde fuentes externas siguen permitidas por la regla DNS (1000). Se eliminaron reglas generales públicas TCP/22, TCP/4222 y TCP/3389. En el grupo Vultr de Kingu se eliminó TCP/22, aunque TCP/4222 sigue permitido desde cualquier origen en Vultr y es rechazado por Firewalld del host.
- **Validación posterior:** Firewalld de Hercules y nftables de Ocean validan configuración; SSH por VPN a ambos nodos funciona; los puertos 22/4222 públicos están filtrados; SOA pública continúa respondiendo desde ambas IP. En Ocean el firewall Linode `ocean-dmz` figura enabled y asignado al Linode `109391597`. No se ejecutó escaneo de vulnerabilidades ni pruebas de explotación.

## Pendiente de decisión

“Solo acceso por VPN” se aplica a SSH y servicios internos; el DNS autoritativo y el transporte WireGuard siguen publicados como excepciones funcionales. Hacer privado también DNS requeriría cambiar delegación/NS y probar resolvers antes de cerrar el acceso público. La DMZ es aislamiento por firewall del host y del proveedor sobre interfaces públicas, no una VPC/subred físicamente separada.

## Hallazgos complementarios del inventario conocido

Pruebas TCP desde el punto externo iFenix a los cinco servidores públicos y lectura de listeners en Fenix:

- **Fenix:** SMTP 25/465/587 e IMAPS 993 aceptaron conexiones, según el rol de correo. SSH/4222 aceptó desde la IP pública de iFenix, que está permitida por una regla de origen; 22 no respondió. Los contenedores Impacta `impacta-db`, `impacta-redis` y `impacta-backend` publican 5435→5432, 6381→6379 y 3102→3101 en `0.0.0.0` y `::`. Las pruebas externas agotaron tiempo y tcpdump no observó llegada del SYN al puerto 5435 desde iFenix, así que no se confirmó acceso WAN. Aun así, el `DOCKER-USER` actual no restringe esos tres puertos y la cadena Firewalld acepta tráfico DNAT; su protección depende de una capa anterior no identificada. Recomendación: enlazar DB/Redis a loopback o a la IP VPN si requieren acceso remoto.
- **Kingu:** 80/443 aceptaron; 22/4222 y puertos de backend probados fueron rechazados o filtrados desde iFenix. Vultr aún permite TCP/4222 desde cualquier origen, aunque Firewalld lo rechaza en la interfaz pública; conviene retirar esa regla cloud si no se necesita SSH público de contingencia.
- **Marte:** 22, 4222, 3000, 3100 y 8090 no aceptaron conexiones desde iFenix.
- **SSH de iFenix:** `PasswordAuthentication yes`; el puerto 4222 escucha en todas las interfaces, pero la zona pública no lo permite y la VPN usa la zona `trusted`. Endurecimiento opcional: deshabilitar autenticación por contraseña si no es necesaria.
- **Actualizaciones:** `apt list --upgradable` mostró solo `tzdata` en Kingu y ninguna actualización pendiente en los otros cinco nodos. El servicio `unattended-upgrades` está activo en Fenix, Kingu y Hercules; no activo en iFenix, Ocean y Marte.

El alcance observado son los seis nodos conocidos y una prueba de puertos desde iFenix. Incluye la política Cloud Firewall Linode de Ocean, pero no el router doméstico, otros dispositivos finales, un escaneo completo de vulnerabilidades ni revisión de cuentas.

## Límites de verificación de esta captura

- **GCP:** verificado con `gcloud compute firewall-rules describe` (prioridades 900/1000/65534, tags y rangos de origen).
- **Linode:** verificado con la API: `ocean-dmz` está `enabled`, asignado al Linode `109391597`, inbound `DROP` con solo DNS 53 y UDP/51820.
- **Vultr:** no verificable desde Fenix. La API rechaza la IP de origen `64.176.28.233` con `401 Unauthorized IP address`; la regla TCP/4222 de Vultr se mantiene como dato de la revisión del operador, no como verificación independiente de esta captura.
- **Hosts Hercules/Ocean:** verificado por SSH con `firewall-cmd`, `nft`, `ss` y `sshd -T`.
- **Pruebas desde iFenix:** se registran como evidencia de la captura; no se repitieron desde una tercera red externa.
