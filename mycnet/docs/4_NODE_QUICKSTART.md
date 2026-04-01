# MycNet: Quickstart con 4 Nodos (PCs)

**Configuración inicial**: 4 PCs viejas con Linux  
**Objetivo**: Validar mesh + storage distribuido  
**Timeline**: 3-5 días

---

## 📋 Hardware Requerido

### Por nodo (x4)

- **CPU**: Dual-core+ (Intel/AMD post-2010)
- **RAM**: 4GB mínimo (8GB ideal)
- **Storage**: HDD 500GB+ o SSD 128GB+
- **Red**: Ethernet Gigabit
- **OS**: Ubuntu Server 22.04 LTS

### Red

- Switch Gigabit Ethernet (5 puertos mínimo)
- Cables Ethernet Cat5e/Cat6

---

## 🗺️ Topología 4 Nodos

```
    n1 ---- n2
    |  \  /  |
    |   \/   |
    |   /\   |
    |  /  \  |
    n3 ---- n4
```

**Características**:

- Cada nodo: 2-3 vecinos
- Tolerancia: 1 nodo muerto (25%)
- Rutas múltiples entre cualquier par

---

## 🚀 Instalación Rápida

### **Paso 1: Preparar Nodos (todos)**

```bash
# Actualizar sistema
sudo apt update && sudo apt -y upgrade

# Instalar dependencias
sudo apt -y install vim git curl jq iperf3 fping batctl chrony

# Configurar hostname (ajustar por nodo)
sudo hostnamectl set-hostname n1  # n1, n2, n3, n4

# Configurar IP estática en /etc/netplan/00-installer-config.yaml
network:
  ethernets:
    eth0:  # Ajustar nombre interfaz
      addresses:
        - 192.168.1.11/24  # n1: .11, n2: .12, n3: .13, n4: .14
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
  version: 2

# Aplicar
sudo netplan apply

# Configurar /etc/hosts (todos los nodos)
192.168.1.11 n1
192.168.1.12 n2
192.168.1.13 n3
192.168.1.14 n4
```

### **Paso 2: Setup Mesh batman-adv (todos)**

```bash
# Clonar repo MycNet
git clone <repo_url> ~/mycnet
cd ~/mycnet/scripts

# Ejecutar setup (ajustar número de nodo)
./mesh_setup.sh 1  # n1
./mesh_setup.sh 2  # n2
./mesh_setup.sh 3  # n3
./mesh_setup.sh 4  # n4

# Verificar vecinos (esperar 10-20 segundos)
batctl n

# Probar conectividad
ping -c 5 10.10.0.12  # desde n1 a n2
```

**Criterio de éxito**: Todos los nodos ven ≥2 vecinos

---

### **Paso 3: Deploy MinIO (todos)**

```bash
# Ejecutar deployment
cd ~/mycnet/scripts
./minio_deploy.sh

# Verificar servicio
sudo systemctl status minio

# Instalar mc client (solo en n1)
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/

# Configurar alias
mc alias set mycnet http://n1:9000 minioadmin minioadmin

# Crear bucket de prueba
mc mb mycnet/test

# Test upload
dd if=/dev/urandom of=/tmp/test.bin bs=1M count=100
mc cp /tmp/test.bin mycnet/test/
mc ls mycnet/test/
```

**Criterio de éxito**: Upload exitoso, archivo visible en todos los nodos

---

### **Paso 4: Aplicar AQM (todos)**

```bash
# Activar fq_codel en bat0
sudo tc qdisc replace dev bat0 root fq_codel

# Verificar
tc -s qdisc show dev bat0
```

---

### **Paso 5: Pruebas de Resiliencia**

#### **Test 1: Saturación + Latencia**

```bash
# En n1 (servidor):
iperf3 -s

# En n2, n3, n4 (clientes):
iperf3 -c 10.10.0.11 -P 5 -t 60

# En n1 (paralelo, medir latencia):
fping -D -p 20 -c 300 10.10.0.12 | tee latency_n2.log
```

**Criterio**: p95 RTT < 50ms

#### **Test 2: Fail 1 Nodo**

```bash
# Apagar n2 (nodo puente)
# En n2:
sudo shutdown -h now

# En n1, monitorear convergencia:
ping 10.10.0.13 -i 0.2 | ts '%s' | tee failover.log

# Analizar log: tiempo hasta 5 pings consecutivos sin pérdida
```

**Criterio**: Convergencia < 1s, pérdida < 2%

#### **Test 3: Storage bajo Fallo**

```bash
# Apagar n3
# En n1:
mc cp mycnet/test/test.bin /tmp/test_recovered.bin
sha256sum /tmp/test.bin /tmp/test_recovered.bin
```

**Criterio**: Lectura exitosa (MinIO EC 2+2 tolera 2 nodos muertos)

---

## 📊 Métricas S60

```bash
# Ejecutar monitor
cd ~/mycnet/scripts
python3 mycnet_s60_monitor.py

# Output esperado:
{
  "mesh_coherence_decimal": 0.92,
  "mesh_coherence_s60": "S60[000; 55, 12, 00, 00]",
  "target_s60": "S60[000; 51, 00, 00, 00]",
  "status": "HEALTHY",
  ...
}
```

**Criterio**: Coherencia S60 > 0.85

---

## 🔄 Escalado a 6+ Nodos

Cuando consigas más PCs:

1. **Agregar nodos nuevos** (n5, n6, ...):
   - Repetir Paso 1-2
   - Mesh se auto-descubre

2. **Actualizar MinIO**:
   - Editar `/etc/systemd/system/minio.service`
   - Cambiar `http://n{1...4}` → `http://n{1...6}`
   - Reiniciar servicio en TODOS los nodos

3. **Migrar a Ceph** (opcional):
   - Seguir Fase 5 del plan completo
   - Replicación 3x con 6+ nodos

---

## 🎯 Resultados Esperados (4 nodos)

| Métrica | Target | Notas |
|---------|--------|-------|
| **Vecinos por nodo** | 2-3 | Topología malla |
| **Ping RTT** | < 5ms | LAN Gigabit |
| **p95 RTT (carga)** | < 50ms | Con AQM |
| **Convergencia** | < 1s | Fail 1 nodo |
| **Coherencia S60** | > 0.85 | Mesh saludable |
| **Storage tolerancia** | 2 nodos | MinIO EC 2+2 |

---

## 📝 Troubleshooting

### **Vecinos no aparecen**

- Verificar firewall: `sudo ufw disable` (temporal)
- Verificar interfaz física: `ip link show eth0`
- Revisar logs: `sudo journalctl -u batman-adv`

### **MinIO no inicia**

- Verificar puertos: `sudo netstat -tlnp | grep 9000`
- Revisar logs: `sudo journalctl -u minio -f`
- Verificar conectividad: `ping n2` desde n1

### **Latencia alta**

- Verificar switch (no usar WiFi)
- Revisar colas: `tc -s qdisc show dev bat0`
- Medir baseline: `ping -c 100 10.10.0.12`

---

**Siguiente paso**: Ejecutar Paso 1 en las 4 PCs y reportar resultados. 🚀
