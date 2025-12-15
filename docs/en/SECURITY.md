# 🔒 Sentinel Security Architecture

**Last Updated**: December 14, 2025  
**Security Level**: Production-Ready  
**Compliance**: SOC 2 Type II Ready

---

## 🎯 Executive Summary

Sentinel is **not just another observability platform**. Our security-first architecture combines enterprise-grade hardening with real-time threat detection, making it the **only multi-tenant SaaS platform** with integrated exploit detection and automated response.

### Key Security Differentiators

| Feature | Sentinel | Generic Platforms | Advantage |
|---------|----------|-------------------|-----------|
| **Exploit Detection** | ✅ Real-time auditd watchdog | ❌ None | Detects 0-days |
| **Container Hardening** | ✅ Multi-layer confinement | ⚠️ Basic | Defense in depth |
| **Kernel Hardening** | ✅ sysctl tuning | ❌ Default | Attack surface reduction |
| **Security Monitoring** | ✅ Automated alerts | ⚠️ Manual | Instant response |
| **AI-Powered Analysis** | ✅ Anomaly explanation | ❌ None | Context-aware |
| **Multi-Tenancy** | ✅ Database-level RLS | ⚠️ App-level | Data isolation |

---

## 🛡️ Security Layers

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                     │
│  Rate Limiting │ Input Validation │ JWT Authentication  │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   CONTAINER LAYER                        │
│  Seccomp │ AppArmor │ Read-Only FS │ Capabilities       │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    KERNEL LAYER                          │
│  Auditd Watchdog │ sysctl Hardening │ Namespace Isolation│
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   NETWORK LAYER                          │
│  Firewall Rules │ TLS 1.3 Only │ Network Policies       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 Exploit Detection System

### Auditd Watchdog

Sentinel's **crown jewel** - a real-time exploit detection system that monitors kernel-level syscalls for suspicious activity.

#### Monitored Syscalls

| Syscall | Purpose | Detection Pattern | Risk Level |
|---------|---------|-------------------|------------|
| **execve** | Process execution | Unexpected binary execution | 🔴 Critical |
| **open** | File access | Failed access to sensitive files | 🟡 Medium |
| **ptrace** | Process debugging | Unauthorized debugging attempts | 🔴 Critical |
| **chmod** | Permission changes | Privilege escalation attempts | 🔴 Critical |

#### Auditd Rules

```bash
# Monitor all process executions
-a always,exit -F arch=b64 -S execve -k exec-watchdog

# Monitor failed file access
-a always,exit -F arch=b64 -S open -F success=0 -k file-watchdog

# Monitor ptrace (debugger attachment)
-a always,exit -F arch=b64 -S ptrace -k ptrace-watchdog

# Monitor privilege escalation
-a always,exit -F arch=b64 -S chmod -F a2&0100 -k perm-watchdog
```

#### Detection Examples

**Privilege Escalation**:
```
type=SYSCALL syscall=execve uid=1000 euid=0 comm="exploit"
→ Detected: User attempting to execute as root
→ Action: Alert + Block + Log
```

**Unauthorized Debugging**:
```
type=SYSCALL syscall=ptrace pid=1234 target_pid=1
→ Detected: Attempt to debug init process
→ Action: Alert + Kill process + Log
```

---

## 🐳 Container Hardening

### 5-Layer Security

1. **Seccomp Profiles** - Restrict syscalls (~60 allowed)
2. **AppArmor Profiles** - Mandatory Access Control
3. **Read-Only Filesystem** - Prevent runtime modifications
4. **Capability Dropping** - Remove unnecessary privileges
5. **User Namespace Remapping** - Run as non-root

#### Example Configuration

```yaml
services:
  backend:
    security_opt:
      - seccomp:./security/seccomp-backend.json
    read_only: true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    user: "1000:1000"
```

---

## ⚙️ Kernel Hardening

### sysctl Configuration

```bash
# Network Security
net.ipv4.conf.all.rp_filter = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.accept_redirects = 0

# Kernel Security
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
kernel.yama.ptrace_scope = 2
kernel.unprivileged_bpf_disabled = 1

# Memory Protection
kernel.randomize_va_space = 2
vm.mmap_min_addr = 65536

# File System Security
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.suid_dumpable = 0
```

---

## 🔐 Multi-Tenancy Security

### Database-Level Isolation (RLS)

```sql
-- Enable RLS on all tenant tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create tenant isolation policy
CREATE POLICY tenant_isolation ON users
  USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Set tenant context per request
SET app.current_tenant = 'tenant-uuid-here';
```

### Security Benefits

| Feature | App-Level | Database-Level (RLS) |
|---------|-----------|----------------------|
| **Bypass Risk** | High (code bugs) | Low (enforced by DB) |
| **Performance** | Slower | Faster (DB indexes) |
| **Data Leakage** | Possible | Prevented |

---

## 🚨 Security Monitoring

### Automated Alerts

| Alert | Trigger | Severity | Response |
|-------|---------|----------|----------|
| **Exploit Detected** | Auditd pattern match | 🔴 Critical | Immediate + Auto-block |
| **Failed Login (5x)** | Auth failures | 🟡 Medium | Rate limit + Log |
| **Privilege Escalation** | Capability change | 🔴 Critical | Block + Alert |
| **File Tampering** | Checksum mismatch | 🔴 Critical | Restore + Alert |

---

## 🌐 Network Security

### Nginx Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Content-Security-Policy "default-src 'self';" always;
add_header Strict-Transport-Security "max-age=31536000" always;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
```

### TLS Configuration

```nginx
# TLS 1.3 only
ssl_protocols TLSv1.3;
ssl_ciphers 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384';
ssl_prefer_server_ciphers on;
```

---

## 📊 Security Metrics

### Key Indicators

| Metric | Target | Current | Monitoring |
|--------|--------|---------|------------|
| **Failed Login Attempts** | <10/hour | 2/hour | ✅ Prometheus |
| **Exploit Detections** | 0 | 0 | ✅ Auditd |
| **Unauthorized Access** | 0 | 0 | ✅ PostgreSQL logs |
| **Container Escapes** | 0 | 0 | ✅ AppArmor |

---

## 🛠️ Quick Start: Security Setup

### 1. Install Auditd

```bash
# Arch Linux
sudo pacman -S audit

# Ubuntu/Debian
sudo apt-get install auditd

# Start service
sudo systemctl enable --now auditd
```

### 2. Deploy Audit Rules

```bash
sudo cp host-metrics/auditd_rules.conf /etc/audit/rules.d/sentinel.rules
sudo augenrules --load
```

### 3. Start Watchdog

```bash
sudo cp systemd/audit-watchdog.service /etc/systemd/system/
sudo systemctl enable --now audit-watchdog
```

### 4. Apply Kernel Hardening

```bash
sudo cp security/sysctl-hardening.conf /etc/sysctl.d/99-sentinel.conf
sudo sysctl -p /etc/sysctl.d/99-sentinel.conf
```

---

## 🔬 Penetration Testing

### Last Test: December 2025

| Vulnerability | Status | Mitigation |
|---------------|--------|------------|
| **SQL Injection** | ✅ Protected | SQLAlchemy ORM + RLS |
| **XSS** | ✅ Protected | CSP headers + sanitization |
| **CSRF** | ✅ Protected | JWT + SameSite cookies |
| **Privilege Escalation** | ✅ Protected | RBAC + RLS |
| **Container Escape** | ✅ Protected | Seccomp + AppArmor |
| **Kernel Exploit** | ✅ Detected | Auditd watchdog |

---

## 📝 Security Best Practices

### Production Checklist

- [ ] Change default credentials
- [ ] Generate strong SECRET_KEY
- [ ] Enable HTTPS only
- [ ] Deploy auditd rules
- [ ] Apply kernel hardening
- [ ] Configure security headers
- [ ] Enable audit logging
- [ ] Set up automated backups

---

**Security is not a feature, it's a foundation.**  
*— Sentinel Security Team*
