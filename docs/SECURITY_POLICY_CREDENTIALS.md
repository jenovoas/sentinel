# 🔐 Política de Seguridad de Credenciales - Sentinel

**Fecha**: 20-Dic-2024  
**Validado por**: Especialistas en ciberseguridad  
**Aplicable a**: Todo el equipo, colaboradores, administradores

---

##  Regla #1: NUNCA Reusar Passwords

### ❌ Prohibido Absolutamente
- Usar la misma password en múltiples servicios
- Compartir passwords entre personas
- Usar passwords débiles o predecibles
- Almacenar passwords en texto plano

### ✅ Requerido Obligatoriamente
- Password única por servicio
- Password manager (1Password, Bitwarden, LastPass)
- Passwords generadas aleatoriamente (min 20 caracteres)
- MFA/2FA en TODOS los servicios

---

## 🔒 Políticas por Servicio

### GitHub
```
✅ Password: Generada aleatoriamente (20+ chars)
✅ 2FA: Obligatorio (TOTP o hardware key)
✅ SSH Keys: Ed25519 con passphrase
✅ Personal Access Tokens: Scoped, expiran en 90 días
❌ Password reuse: PROHIBIDO
```

### AWS / Cloud Provider
```
✅ Password: Generada aleatoriamente (24+ chars)
✅ MFA: Obligatorio (hardware key preferido)
✅ IAM Roles: Usar en lugar de access keys
✅ Access Keys: Rotar cada 30 días
❌ Root account: NUNCA usar para operaciones diarias
```

### Kubernetes / Cluster
```
✅ Service Accounts: Usar en lugar de user credentials
✅ RBAC: Least privilege
✅ Secrets: Encriptados con SOPS o Vault
✅ Certificates: Rotar cada 90 días
❌ Kubeconfig: NUNCA commitear a git
```

### PostgreSQL / Databases
```
✅ Password: Generada aleatoriamente (32+ chars)
✅ Rotation: Cada 90 días
✅ Connection: TLS obligatorio
✅ Secrets: En Vault, no en .env
❌ Default passwords: PROHIBIDO (postgres/postgres)
```

### Grafana / Observability
```
✅ Password: Generada aleatoriamente (20+ chars)
✅ OAuth: Preferir sobre password local
✅ API Keys: Scoped, expiran en 30 días
✅ Session timeout: 1 hora de inactividad
❌ admin/admin: CAMBIAR INMEDIATAMENTE
```

### n8n / Automation
```
✅ Password: Generada aleatoriamente (20+ chars)
✅ Webhook URLs: Tokens únicos
✅ Credentials: Encriptadas en n8n
✅ Access: IP whitelist
❌ Workflows públicos: PROHIBIDO sin autenticación
```

---

## 🛠 Herramientas Requeridas

### Password Manager (Elegir UNO)
- **1Password** (Recomendado para equipos)
- **Bitwarden** (Open source, self-hosted)
- **LastPass** (Enterprise)

**Setup obligatorio**:
```bash
# Instalar 1Password CLI
brew install 1password-cli

# Login
op signin

# Generar password
op generate --length 32 --symbols

# Guardar en vault
op create item login \
  --title "Sentinel PostgreSQL" \
  --vault "Sentinel Team" \
  --url "postgres://..." \
  --username "sentinel_admin" \
  --password "$(op generate --length 32)"
```

### MFA/2FA (Elegir UNO)
- **Authy** (Multi-device, backup)
- **Google Authenticator** (Simple)
- **YubiKey** (Hardware, más seguro)

---

## 📋 Checklist de Onboarding

### Nuevo Colaborador - Día 1
- [ ] Instalar password manager
- [ ] Generar passwords únicas para:
  - [ ] GitHub (+ habilitar 2FA)
  - [ ] Slack/Discord
  - [ ] Email del proyecto
  - [ ] VPN (si aplica)
- [ ] Configurar MFA en todos los servicios
- [ ] Leer esta política completa
- [ ] Firmar acuerdo de confidencialidad

### Acceso a Infraestructura - Semana 1
- [ ] AWS/GCP: IAM user con MFA
- [ ] Kubernetes: Service account con RBAC
- [ ] PostgreSQL: User con password rotada
- [ ] Grafana: OAuth o password única
- [ ] n8n: Credentials encriptadas

---

## 🚨 Detección de Password Reuse

### Automated Checks
```python
# backend/security/password_audit.py

import hashlib
from typing import Set

class PasswordReuseDetector:
    """Detecta si passwords están siendo reusadas"""
    
    def __init__(self):
        self.password_hashes: Set[str] = set()
    
    def check_reuse(self, password: str, service: str) -> bool:
        """
        Retorna True si password ya fue usada en otro servicio
        """
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if pwd_hash in self.password_hashes:
            # PASSWORD REUSADA - ALERTA CRÍTICA
            alert_security_team(
                severity="CRITICAL",
                message=f"Password reuse detected for {service}",
                action="Force password reset"
            )
            return True
        
        self.password_hashes.add(pwd_hash)
        return False
```

### Manual Audit (Mensual)
```bash
# Auditar passwords en uso
./scripts/audit_passwords.sh

# Verificar:
# - Passwords débiles (< 20 chars)
# - Passwords sin rotación (> 90 días)
# - Servicios sin MFA
# - Secrets en plaintext
```

---

## 🔄 Rotación de Credenciales

### Schedule Automático

| Servicio | Frecuencia | Responsable | Automatizado |
|----------|-----------|-------------|--------------|
| **GitHub PAT** | 90 días | DevOps | ✅ |
| **AWS Access Keys** | 30 días | DevOps | ✅ |
| **Database Passwords** | 90 días | DBA | ⚠ Manual |
| **API Keys** | 30 días | Backend Lead | ✅ |
| **TLS Certificates** | 90 días | DevOps | ✅ (cert-manager) |
| **SSH Keys** | 365 días | Cada usuario | ❌ Manual |

### Proceso de Rotación
```bash
# 1. Generar nueva credential
NEW_PASSWORD=$(op generate --length 32)

# 2. Actualizar en servicio
kubectl create secret generic db-password \
  --from-literal=password="$NEW_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Actualizar en password manager
op item edit "Sentinel PostgreSQL" password="$NEW_PASSWORD"

# 4. Verificar que funciona
./scripts/test_db_connection.sh

# 5. Revocar credential anterior
# (después de 24h de grace period)
```

---

##  Secrets Management

### Vault (Recomendado para Producción)
```bash
# Setup Vault
vault kv put secret/sentinel/postgres \
  username=sentinel_admin \
  password="$(op generate --length 32)"

# Leer en aplicación
vault kv get -field=password secret/sentinel/postgres
```

### SOPS (Para archivos de configuración)
```bash
# Encriptar .env
sops --encrypt .env > .env.encrypted

# Desencriptar (requiere GPG key)
sops --decrypt .env.encrypted > .env

# Commitear solo .env.encrypted a git
```

### Kubernetes Secrets (Encriptados)
```yaml
# sealed-secret.yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-credentials
spec:
  encryptedData:
    password: AgBx7f9... # Encriptado, safe to commit
```

---

## ⚠ Incidentes de Seguridad

### Si Password Comprometida

**Acción inmediata** (< 5 minutos):
1. Revocar credential comprometida
2. Generar nueva credential
3. Actualizar en todos los servicios
4. Verificar logs de acceso
5. Notificar a equipo de seguridad

**Investigación** (< 24 horas):
1. Identificar scope de compromiso
2. Revisar audit logs
3. Determinar si hubo acceso no autorizado
4. Documentar incident report

**Post-mortem** (< 7 días):
1. Root cause analysis
2. Lecciones aprendidas
3. Actualizar políticas
4. Training para equipo

---

## 📊 Métricas de Seguridad

### KPIs Mensuales
- **Password Strength Score**: Promedio > 90/100
- **MFA Adoption**: 100% del equipo
- **Rotation Compliance**: > 95%
- **Secrets in Plaintext**: 0
- **Password Reuse Incidents**: 0

### Dashboard Grafana
```promql
# Passwords próximas a expirar
sentinel_password_days_until_expiry < 7

# Servicios sin MFA
sentinel_services_without_mfa > 0

# Secrets en plaintext detectados
sentinel_plaintext_secrets_detected > 0
```

---

## ✅ Compliance

### SOC 2 Requirements
- ✅ Password complexity enforced
- ✅ MFA mandatory
- ✅ Credential rotation automated
- ✅ Secrets encrypted at rest
- ✅ Audit trail completo

### ISO 27001 Requirements
- ✅ Access control policy documented
- ✅ Password policy enforced
- ✅ Privileged access management
- ✅ Incident response procedures

---

##  Quick Start

### Para Nuevo Colaborador
```bash
# 1. Instalar password manager
brew install 1password-cli

# 2. Crear vault del equipo
op vault create "Sentinel Team"

# 3. Generar passwords para servicios
for service in github aws postgres grafana; do
  op create item login \
    --title "Sentinel $service" \
    --vault "Sentinel Team" \
    --password "$(op generate --length 32)"
done

# 4. Habilitar MFA en todos los servicios
# (seguir guías específicas de cada servicio)
```

---

## 📚 Recursos

### Guías de MFA
- [GitHub 2FA](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa)
- [AWS MFA](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa.html)
- [Google 2FA](https://www.google.com/landing/2step/)

### Password Managers
- [1Password Teams](https://1password.com/teams/)
- [Bitwarden](https://bitwarden.com/)
- [Vault by HashiCorp](https://www.vaultproject.io/)

### Security Best Practices
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)

---

**Política aprobada por**: Equipo de Seguridad  
**Última revisión**: 20-Dic-2024  
**Próxima revisión**: 20-Mar-2025  
**Violaciones**: Reportar a security@sentinel.com
