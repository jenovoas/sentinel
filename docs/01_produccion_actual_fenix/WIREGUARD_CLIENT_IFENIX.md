# 🔐 WireGuard Cliente — ifenix (Laptop)

**Última actualización**: 2026-04-03  
**Aplica a**: ifenix (laptop de desarrollo, Ubuntu)  
**Servidor VPN**: fenix (GCloud, `34.28.226.63`, puerto `51820`)

---

## ⚠️ REGLAS CRÍTICAS (aprendidas a los golpes)

### 1. `allowed-ips` NUNCA debe incluir la IP pública del endpoint

**MAL** ❌:
```yaml
allowed-ips:
- "10.100.0.0/24"
- "34.28.226.63/32"   # ← NUNCA. Esto crea un loop: el paquete UDP que
                       #   mantiene el túnel se intenta enviar por dentro
                       #   del túnel mismo. El túnel nunca levanta.
```

**BIEN** ✅:
```yaml
allowed-ips:
- "10.100.0.0/24"     # Solo la red interna de la VPN
```

### 2. `dns-search: "~;"` en el passthrough secuestra TODO el DNS del sistema

Si el passthrough de NetworkManager incluye `ipv4.dns-search: "~;"`, el sistema
manda **todo** el DNS por la interfaz WireGuard. Si el DNS del VPN (1.1.1.1) no
es alcanzable por esa interfaz (y no lo es, ya que 1.1.1.1 está fuera del
`10.100.0.0/24`), **te quedás sin navegación aunque la IP funcione**.

**No incluir** `nameservers` ni `dns-search` en el bloque netplan del túnel.

---

## 📋 Configuración correcta — Netplan

Archivo: `/etc/netplan/90-NM-2c5fcbb8-d4e3-46a8-b7e3-65f01c7a1bf1.yaml`

```yaml
network:
  version: 2
  tunnels:
    fenix:
      renderer: NetworkManager
      addresses:
      - "10.100.0.2/24"
      mode: "wireguard"
      keys:
        private: "<CLAVE_PRIVADA_CLIENTE>"
      peers:
      - endpoint: "34.28.226.63:51820"
        keys:
          public: "J24zF0mIFBA5ThwkwusfLopj8PxzDVHYe0ir0x9p53Y="
        allowed-ips:
        - "10.100.0.0/24"
      networkmanager:
        uuid: "2c5fcbb8-d4e3-46a8-b7e3-65f01c7a1bf1"
        name: "fenix"
        passthrough:
          wireguard-peer.J24zF0mIFBA5ThwkwusfLopj8PxzDVHYe0ir0x9p53Y=.persistent-keepalive: "25"
          ipv6.addr-gen-mode: "default"
          ipv6.method: "disabled"
          ipv6.ip6-privacy: "-1"
          proxy._: ""
```

> **Nota**: La clave privada real está en el sistema. Hacer `sudo nmcli -s connection show fenix | grep private-key` para recuperarla si se necesita migrar.

---

## 📋 Configuración SSH — `~/.ssh/config`

```sshconfig
# Acceso por VPN (requiere VPN activa)
Host fenix
    HostName 10.100.0.1
    User jnovoas
    Port 4222
    IdentityFile ~/.ssh/google_compute_engine
    CheckHostIP no
    StrictHostKeyChecking no
    HostKeyAlgorithms ssh-ed25519,ecdsa-sha2-nistp256,rsa-sha2-512,rsa-sha2-256

# Acceso directo por IP pública (siempre funciona, sin VPN)
Host fenix-pub
    HostName 34.28.226.63
    User jnovoas
    Port 4222
    IdentityFile ~/.ssh/google_compute_engine
    CheckHostIP no
    StrictHostKeyChecking no
    HostKeyAlgorithms ssh-ed25519,ecdsa-sha2-nistp256,rsa-sha2-512,rsa-sha2-256
```

---

## 🔄 Setup desde cero (después de reinstalar laptop)

### Paso 1 — Obtener la clave privada del cliente

Si tenés acceso previo al server o al backup, la clave privada del cliente
estaba en el netplan anterior. Si no, hay que generar un nuevo par y registrar
la pública en fenix.

**Generar nuevo par**:
```bash
wg genkey | tee client_private.key | wg pubkey > client_public.key
```

**Registrar en fenix** (editar `/etc/wireguard/wg0.conf` en fenix):
```bash
ssh fenix-pub
sudo cat /etc/wireguard/wg0.conf   # ver la config actual del server
```

### Paso 2 — Crear el archivo netplan

Copiar el bloque YAML de la sección anterior, reemplazando `<CLAVE_PRIVADA_CLIENTE>`.

```bash
sudo nano /etc/netplan/90-fenix-vpn.yaml
# pegar el contenido
sudo chmod 600 /etc/netplan/90-fenix-vpn.yaml
sudo netplan apply
```

### Paso 3 — Activar la conexión

```bash
nmcli connection up fenix
```

### Paso 4 — Verificar

```bash
# La interfaz fenix NO debe tener +DefaultRoute en DNS
resolvectl status | grep -A6 "fenix\|wlo1"

# Ping al gateway de la VPN
ping -c 3 10.100.0.1

# Navegación normal
curl -s https://google.com -o /dev/null -w "%{http_code}"  # debe dar 301

# SSH al servidor
ssh fenix
```

---

## 🏥 Diagnóstico rápido si algo falla

| Síntoma | Causa probable | Fix |
|---------|---------------|-----|
| VPN conecta pero no llegás a `10.100.0.1` | `34.28.226.63/32` en `allowed-ips` | Sacarlo del netplan, `sudo netplan apply`, reconectar |
| VPN conecta, llegás a fenix, pero no navegás | `dns-search: "~;"` en passthrough | Sacarlo del netplan, reconectar |
| DNS no resuelve nada | interfaz `fenix` con `+DefaultRoute` en DNS | `sudo resolvectl default-route fenix false` (temporal) o fix en netplan |
| No podés conectar ni la VPN | Error en clave privada/pública | Regenerar par y actualizar en fenix |

---

## 📍 Topología de red

```
ifenix (laptop)
├── wlo1: 192.168.1.45/24  (WiFi, default route, DNS: 1.1.1.1/8.8.8.8)
└── fenix (WireGuard): 10.100.0.2/24
    └── split tunnel → solo 10.100.0.0/24 va por VPN

fenix (GCloud)
├── eth0: 34.28.226.63 (IP pública)
├── wg0: 10.100.0.1/24 (WireGuard server, puerto 51820 UDP)
└── PowerDNS API: http://10.100.0.1:8081 (solo accesible por VPN)
```

---

**YATRA. Truth Resonates.**
