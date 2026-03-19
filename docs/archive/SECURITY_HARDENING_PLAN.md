# 🔒 Security Hardening Plan - Vulnerabilidades Identificadas

**Fecha**: 19 Diciembre 2024  
**Severidad**: 3 brechas (1 CRÍTICA, 1 ALTA, 1 MEDIA)  
**Estado**: Plan de mitigación creado

---

## ⚠ RESUMEN EJECUTIVO

**Análisis forense identificó 3 vulnerabilidades** que requieren hardening antes de producción:

1. **Whitelist Dinámica Vulnerable** (CRÍTICO) - Atacante con acceso host puede modificar eBPF maps
2. **mTLS Bypass via SSRF** (ALTO) - SSRF en n8n puede inyectar headers falsos  
3. **WAL Replay Attack** (MEDIO) - Replay de eventos antiguos oculta ataques reales

---

## 🔴 VULNERABILIDAD 1: Whitelist Dinámica Vulnerable

### Attack Vector
```bash
bpftool map update name ai_whitelist \
  key hex 2f 65 74 63 2f 73 68 61 64 6f 77 \
  value hex 01  # ALLOW_AI
cat /etc/shadow  # ✅ BYPASS COMPLETO
```

### Mitigación: ECDSA Signatures

**eBPF con verificación criptográfica**:
```c
struct WhitelistEntry {
    char path[256];
    __u64 path_hash;
    __u8 policy;
    __u8 signature[64];  // ECDSA-P256
    __u64 timestamp;
};

SEC("lsm/file_open")
int ai_guardian_signed(struct file *file) {
    // Verificar firma ECDSA antes de permitir
    if (!verify_ecdsa_signature(entry, KERNEL_PUBKEY)) {
        return -EPERM;
    }
    return 0;
}
```

**Validación**: `bpftool map update` sin firma válida → REJECTED

---

## 🟠 VULNERABILIDAD 2: mTLS Bypass via SSRF

### Attack Vector
```bash
# SSRF en n8n forja header
POST /loki/api/v1/push
X-Scope-OrgID: sentinel-security  # Forjado
# Loki acepta logs maliciosos como legítimos
```

### Mitigación: Header HMAC Signing

**Nginx con verificación**:
```nginx
location /loki/api/v1/push {
    # Verificar firma HMAC en header
    access_by_lua_block {
        local expected_sig = hmac_sha256(tenant + timestamp + body)
        if sig ~= expected_sig then
            ngx.exit(403)
        end
    }
    proxy_pass http://loki;
}
```

**Validación**: Header forjado → 403 Invalid signature

---

## 🟡 VULNERABILIDAD 3: WAL Replay Attack

### Attack Vector
```bash
# Replay evento antiguo durante ataque
cat benign_old.log >> /app/wal/current.wal
# Timeline forense muestra actividad normal
```

### Mitigación: Nonce + HMAC

**WAL con protección**:
```python
class WALRecordSigned:
    nonce: int          # Monotonic counter
    timestamp: int      # Kernel monotonic time
    event: dict
    hmac: bytes         # HMAC(event + nonce + ts)

# Replay verifica monotonía
if record.nonce <= last_nonce:
    alert("WAL REPLAY ATTACK")
```

**Validación**: Replay detectado → IntegrityGap alert

---

## ✅ CHECKLIST IMPLEMENTACIÓN (90 min)

**Fase 1: Whitelist** (40 min)
- [ ] Generar claves ECDSA P-256
- [ ] Actualizar eBPF LSM con verificación
- [ ] Test: bpftool → REJECTED

**Fase 2: mTLS** (30 min)
- [ ] Implementar HMAC en Nginx
- [ ] Actualizar cliente Loki
- [ ] Test: SSRF → 403

**Fase 3: WAL** (20 min)
- [ ] Implementar nonce + HMAC
- [ ] Actualizar replay
- [ ] Test: Replay → Alert

---

##  IMPACTO

**Antes**: Grado militar (6/6 criterios)  
**Después**: **Grado militar HARDENED** (resistente a ataques avanzados)

**Diferenciador**: "Único sistema con protección criptográfica end-to-end (kernel → storage)"

---

Ver detalles completos en: `SOLUCIONES_SEGURIDAD_GRADO_MILITAR.md`
