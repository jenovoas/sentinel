# Auditoría de segmentación de Hercules y Ocean — 2026-10-30

## Alcance de esta captura

Lectura de Firewalld/nftables, interfaces y listeners en Hercules (`10.88.0.4`) y Ocean (`10.88.0.5`), comprobación de SSH por WireGuard y lectura de las reglas GCP/Vultr disponibles. Esta captura no representa todavía una auditoría completa de todos los nodos ni sustituye una prueba desde una tercera red externa.

## Resultado

- **No están asignados a una DMZ explícita.** Hercules pertenece a la red GCP `default`; su interfaz externa `ens4` está en la zona Firewalld `public` y `wg0` en `wgmesh`. Ocean usa `nftables`, sin zonas Firewalld; `eth0` tiene IPv4/IPv6 públicas y `wg0` lleva `10.88.0.5/24`.
- **Administración SSH:** `sshd` escucha en TCP/4222. Firewalld de Hercules limita ese puerto en `wgmesh` a `10.88.0.1` y `10.88.0.3`; nftables de Ocean permite TCP/4222 solo por `wg0` desde esas IP. Se verificó acceso por los alias SSH privados; no hay listener en TCP/22.
- **Exposición DNS pública intencional:** ambos hosts responden SOA para `pinguinoseguro.cl` en TCP/UDP 53 en sus IP públicas. GCP permite 53 desde cualquier origen solo a instancias con tag `dns-authoritative`; el host Hercules tiene ese tag y Firewalld permite DNS en `public`. Ocean acepta DNS TCP/UDP 53 por `eth0`; al no restringir familia IP, también incluye su IPv6 pública. Si DNS autoritativo debe seguir público, estas excepciones son necesarias.
- **Ocean:** nftables está habilitado y activo; `input` usa política `drop`. El archivo `/etc/nftables.conf` valida con `nft -c`. Los servicios Samba/AD están permitidos solo por `wg0` y origen `10.88.0.0/24`.
- **Capas de nube:** GCP tenía reglas de entrada desde `0.0.0.0/0` para TCP/22, TCP/4222 y TCP/3389. Se eliminaron `default-allow-ssh`, `allow-kingu-ssh-4222` y `default-allow-rdp`: no hay servicios 22 ni RDP configurados, y el acceso TCP/4222 previsto llega dentro de WireGuard por UDP/51820. En el grupo Vultr de Kingu se eliminó también la regla TCP/22 (regla 1); TCP/4222 aún aparece permitido desde cualquier origen en Vultr, pero una prueba desde iFenix fue rechazada por el Firewalld del host. Se conservaron DNS autoritativo y WireGuard. Vultr no gestiona Ocean (la instancia consultada no aparece en ese inventario); no se verificó la política de red del proveedor de Ocean.
- **Regla GCP restante:** `default-allow-internal` admite TCP/UDP de `10.128.0.0/9` entre instancias de la VPC. En el host Hercules la zona `public` limita la entrada a DNS; SSH y AD siguen en la interfaz WireGuard. Esta regla es más amplia que la malla WireGuard y debe considerarse al añadir otros servicios/instancias a esa VPC. También existe `deny-hercules-internal-vpc` (INGRESS, prioridad 1100, `10.128.0.0/9` → tag `dns-server`, deny all), que mitiga esa regla para Hercules; verificar prioridad/efecto antes de asumirlo como control completo.
- **Validación posterior:** siguen habilitados los accesos SSH por WireGuard a Hercules y Ocean, GCP mantiene DNS 53 y UDP/51820, y las consultas SOA públicas a ambos DNS respondieron. No se ejecutó escaneo de vulnerabilidades ni pruebas de explotación.

## Pendiente de decisión

“Solo acceso por VPN” debe entenderse como administración y servicios internos; el DNS autoritativo continúa público. Hacer también privados los puertos 53 requeriría cambiar delegación/NS y comprobar resolvers antes de cerrar el acceso público. No se cambió la asignación de zona `public` ni se asignó Ocean a una DMZ; ambas máquinas conservan su política de firewall efectiva descrita arriba.

## Hallazgos complementarios del inventario conocido

Pruebas TCP desde el punto externo iFenix a los cinco servidores públicos y lectura de listeners en Fenix:

- **Fenix:** SMTP 25/465/587 e IMAPS 993 aceptaron conexiones, según el rol de correo. SSH/4222 aceptó desde la IP pública de iFenix, que está permitida por una regla de origen; 22 no respondió. Los contenedores Impacta `impacta-db`, `impacta-redis` y `impacta-backend` publican 5435→5432, 6381→6379 y 3102→3101 en `0.0.0.0` y `::`. Las pruebas externas agotaron tiempo y tcpdump no observó llegada del SYN al puerto 5435 desde iFenix, así que no se confirmó acceso WAN. Aun así, el `DOCKER-USER` actual no restringe esos tres puertos y la cadena Firewalld acepta tráfico DNAT; su protección depende de una capa anterior no identificada. Recomendación: enlazar DB/Redis a loopback o a la IP VPN si requieren acceso remoto.
- **Kingu:** 80/443 aceptaron; 22/4222 y puertos de backend probados fueron rechazados o filtrados desde iFenix. Vultr aún permite TCP/4222 desde cualquier origen, aunque Firewalld lo rechaza en la interfaz pública; conviene retirar esa regla cloud si no se necesita SSH público de contingencia.
- **Marte:** 22, 4222, 3000, 3100 y 8090 no aceptaron conexiones desde iFenix.
- **SSH de iFenix:** `PasswordAuthentication yes`; el puerto 4222 escucha en todas las interfaces, pero la zona pública no lo permite y la VPN usa la zona `trusted`. Endurecimiento opcional: deshabilitar autenticación por contraseña si no es necesaria.
- **Actualizaciones:** `apt list --upgradable` mostró solo `tzdata` en Kingu y ninguna actualización pendiente en los otros cinco nodos. El servicio `unattended-upgrades` está activo en Fenix, Kingu y Hercules; no activo en iFenix, Ocean y Marte.

El alcance observado son los seis nodos conocidos y una prueba de puertos desde iFenix. No incluye router doméstico, otros dispositivos finales, escaneo completo de vulnerabilidades, revisión de cuentas ni validación del firewall cloud del proveedor de Ocean.
