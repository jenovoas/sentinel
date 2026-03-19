# Plan: Servidor SMTP + n8n para Campañas de Marketing Automatizadas

**Objetivo:** Configurar infraestructura de email marketing propia para Pinguino Seguro y clientes, con n8n para automatización.

**Stack:**
- **n8n** (automatización workflow, open source)
- **Postfix** o **Mailgun API** (envío SMTP)
- **Traefik** (reverse proxy con SSL)
- **PowerDNS** (ya configurado)

---

## Arquitectura propuesta

```
Internet → Traefik (443) → n8n (5678)
                         ↓
                    Postfix/Mailgun API
                         ↓
          Campañas marketing automatizadas
```

**Subdominios:**
- `n8n.pinguinoseguro.cl` → Interfaz web n8n
- `mail.pinguinoseguro.cl` → Servidor SMTP (opcional si usas Postfix local)

---

## Fase 1: Configurar DNS para Email (PowerDNS)

### 1.1 Records SPF, DKIM, DMARC

**Acceder a PowerDNS API o webadmin:**
```bash
# Si tienes PowerDNS Admin instalado
firefox http://localhost:9191  # o la IP/puerto correspondiente

# Si usas pdnsutil directamente:
pdnsutil list-zone pinguinoseguro.cl
```

**Agregar records DNS:**

```bash
# SPF: autoriza tu servidor para enviar emails
pdnsutil add-record pinguinoseguro.cl @ TXT 3600 "v=spf1 ip4:34.28.226.63 include:mailgun.org ~all"

# DMARC: política de validación
pdnsutil add-record pinguinoseguro.cl _dmarc TXT 3600 "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@pinguinoseguro.cl; pct=100"

# Subdominio mail (si usas Postfix local)
pdnsutil add-record pinguinoseguro.cl mail A 3600 34.28.226.63
```

**Si usas Mailgun (recomendado para agencia):**
```bash
# Mailgun te dará estos records específicos al agregar el dominio:
# mg.pinguinoseguro.cl → CNAME → mailgun.org
# Seguir wizard en https://app.mailgun.com/mg/domains
```

### 1.2 Verificar DNS propagación

```bash
dig +short pinguinoseguro.cl TXT | grep spf
dig +short _dmarc.pinguinoseguro.cl TXT
host -t MX pinguinoseguro.cl
```

---

## Fase 2: Instalar n8n con Docker/Podman

### 2.1 Crear directorio de trabajo

```bash
mkdir -p ~/containers/n8n/{data,config}
cd ~/containers/n8n
```

### 2.2 Crear compose.yaml

```yaml
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    networks:
      - proxy
    ports:
      - "5678:5678"  # Solo para debug local, Traefik lo expone públicamente
    environment:
      - N8N_HOST=n8n.pinguinoseguro.cl
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.pinguinoseguro.cl/
      - GENERIC_TIMEZONE=America/Santiago

      # Autenticación básica (cambiar usuario/contraseña)
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=CambiarEstaClaveSegura123!

      # Base de datos (opcional: usar PostgreSQL en lugar de SQLite)
      # - DB_TYPE=postgresdb
      # - DB_POSTGRESDB_HOST=postgres
      # - DB_POSTGRESDB_DATABASE=n8n
      # - DB_POSTGRESDB_USER=n8n
      # - DB_POSTGRESDB_PASSWORD=n8npassword

      # Email (Mailgun API o SMTP)
      - N8N_EMAIL_MODE=smtp
      - N8N_SMTP_HOST=smtp.mailgun.org
      - N8N_SMTP_PORT=587
      - N8N_SMTP_USER=postmaster@mg.pinguinoseguro.cl
      - N8N_SMTP_PASS=tu-mailgun-smtp-password
      - N8N_SMTP_SENDER=noreply@pinguinoseguro.cl

    volumes:
      - ./data:/home/node/.n8n
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.n8n.rule=Host(`n8n.pinguinoseguro.cl`)"
      - "traefik.http.routers.n8n.entrypoints=websecure"
      - "traefik.http.routers.n8n.tls.certresolver=powerdns"
      - "traefik.http.services.n8n.loadbalancer.server.port=5678"

  # OPCIONAL: PostgreSQL para n8n (mejor que SQLite para producción)
  postgres:
    image: postgres:15-alpine
    container_name: n8n-postgres
    restart: unless-stopped
    networks:
      - proxy
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8npassword
      - POSTGRES_DB=n8n
    volumes:
      - ./postgres-data:/var/lib/postgresql/data

networks:
  proxy:
    external: true
```

### 2.3 Levantar contenedor

```bash
podman-compose up -d
podman logs -f n8n
```

### 2.4 Verificar acceso

```bash
curl -I https://n8n.pinguinoseguro.cl
# Debe devolver HTTP/2 200 o 401 (si pide autenticación)
```

**Acceder desde browser:**
```
https://n8n.pinguinoseguro.cl
Usuario: admin
Contraseña: CambiarEstaClaveSegura123!
```

---

## Fase 3: Configurar Traefik para n8n

**Si n8n no se autodescubre, crear config manual:**

```bash
# Archivo: ~/containers/traefik/config/dynamic/n8n.yml
cat > ~/containers/traefik/config/dynamic/n8n.yml <<'EOF'
http:
  routers:
    n8n:
      rule: "Host(`n8n.pinguinoseguro.cl`)"
      entryPoints:
        - "websecure"
      service: "n8n"
      tls:
        certResolver: "powerdns"

  services:
    n8n:
      loadBalancer:
        servers:
          - url: "http://n8n:5678"
EOF
```

**Traefik recarga automáticamente en ~5 segundos.**

---

## Fase 4: Configurar Mailgun (Opción Recomendada)

### 4.1 Crear cuenta Mailgun

1. Ir a https://www.mailgun.com/
2. Crear cuenta gratuita (5,000 emails/mes gratis primeros 3 meses)
3. Verificar tarjeta (no cobra hasta superar límite free)

### 4.2 Agregar dominio

1. Dashboard → Sending → Domains → Add New Domain
2. Usar: `mg.pinguinoseguro.cl` (NO usar dominio raíz)
3. Copiar DNS records que Mailgun te da:
   ```
   mg.pinguinoseguro.cl → TXT → v=spf1 include:mailgun.org ~all
   k1._domainkey.mg.pinguinoseguro.cl → TXT → k=rsa; p=MIGfMA0GCS...
   email.mg.pinguinoseguro.cl → CNAME → mailgun.org
   ```

4. Agregar records en PowerDNS:
   ```bash
   pdnsutil add-record pinguinoseguro.cl mg TXT 3600 "v=spf1 include:mailgun.org ~all"
   pdnsutil add-record pinguinoseguro.cl k1._domainkey.mg TXT 3600 "k=rsa; p=CLAVE_LARGA_AQUI"
   pdnsutil add-record pinguinoseguro.cl email.mg CNAME 3600 mailgun.org
   ```

5. Esperar validación (5-10 min)

### 4.3 Obtener API Key

1. Dashboard → API Keys → Copiar "Private API key"
2. Guardar en variable de entorno de n8n:
   ```yaml
   environment:
     - MAILGUN_API_KEY=key-tu-api-key-aqui
     - MAILGUN_DOMAIN=mg.pinguinoseguro.cl
   ```

---

## Fase 5: Crear Workflows en n8n

### 5.1 Workflow básico: Enviar email de bienvenida

**Crear nuevo workflow:**

1. Login en https://n8n.pinguinoseguro.cl
2. Click "New Workflow"
3. Nombre: "Email Bienvenida Cliente"

**Nodos:**

```
[Webhook] → [Set Variables] → [Mailgun] → [Respuesta]
```

**Configuración:**

**Nodo 1: Webhook**
- Method: POST
- Path: `/webhook/bienvenida`
- Authentication: None (o agregar header API key)

**Nodo 2: Set (Variables)**
```json
{
  "nombre": "{{$json.body.nombre}}",
  "email": "{{$json.body.email}}",
  "empresa": "{{$json.body.empresa}}"
}
```

**Nodo 3: Mailgun**
- Credentials: Agregar Mailgun API Key
- From Email: `noreply@mg.pinguinoseguro.cl`
- From Name: `Pinguino Seguro`
- To Email: `{{$node["Set"].json["email"]}}`
- Subject: `¡Bienvenido {{$node["Set"].json["nombre"]}}!`
- Text (HTML):
  ```html
  <h1>¡Hola {{$node["Set"].json["nombre"]}}!</h1>
  <p>Gracias por confiar en Pinguino Seguro para la infraestructura de <strong>{{$node["Set"].json["empresa"]}}</strong>.</p>
  <p>Estamos listos para comenzar.</p>
  <p>Saludos,<br>Equipo Pinguino Seguro</p>
  ```

**Nodo 4: Respond to Webhook**
- Status Code: 200
- Body: `{"status": "email enviado"}`

**Guardar y activar workflow.**

**Probar:**
```bash
curl -X POST https://n8n.pinguinoseguro.cl/webhook/bienvenida \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Jaime",
    "email": "tu-email@example.com",
    "empresa": "Test SPA"
  }'
```

### 5.2 Workflow avanzado: Campaña automatizada con seguimiento

**Escenario:** Cliente se registra → Email bienvenida → Espera 3 días → Email recordatorio

**Nodos:**
```
[Webhook] → [Google Sheets: Agregar Row] → [Mailgun: Bienvenida]
             ↓
          [Wait 3 days] → [Mailgun: Recordatorio]
```

**Configuración Wait:**
- Amount: 3
- Unit: Days

**Mailgun Recordatorio:**
- Subject: `¿Ya revisaste nuestra propuesta?`
- Body: Template personalizado

---

## Fase 6: Integración con Aplicaciones

### 6.1 Desde Next.js (pinguinoseguro_web)

```typescript
// app/api/contacto/route.ts
export async function POST(req: Request) {
  const { nombre, email, empresa } = await req.json();

  // Trigger n8n webhook
  const response = await fetch('https://n8n.pinguinoseguro.cl/webhook/bienvenida', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nombre, email, empresa })
  });

  if (!response.ok) {
    return Response.json({ error: 'Error al enviar email' }, { status: 500 });
  }

  return Response.json({ success: true });
}
```

### 6.2 Desde Python (Sentinel)

```python
import requests

def enviar_email_bienvenida(nombre: str, email: str, empresa: str):
    payload = {
        "nombre": nombre,
        "email": email,
        "empresa": empresa
    }

    response = requests.post(
        "https://n8n.pinguinoseguro.cl/webhook/bienvenida",
        json=payload,
        timeout=10
    )

    return response.status_code == 200
```

---

## Fase 7: Monitoreo y Métricas

### 7.1 Logs de n8n

```bash
podman logs -f n8n
```

### 7.2 Métricas de Mailgun

Dashboard → Analytics:
- Emails enviados
- Tasa de apertura
- Bounces/rechazos
- Clicks en enlaces

### 7.3 Alertas en Prometheus (opcional)

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    metrics_path: '/metrics'
```

---

## Fase 8: Seguridad y Best Practices

### 8.1 Rate Limiting en Traefik

```yaml
# traefik/config/dynamic/n8n.yml
http:
  middlewares:
    n8n-ratelimit:
      rateLimit:
        average: 100
        burst: 50
        period: 1m

  routers:
    n8n:
      middlewares:
        - "n8n-ratelimit"
```

### 8.2 Autenticación robusta

**Cambiar de Basic Auth a OAuth2 (opcional):**

En n8n environment:
```yaml
- N8N_BASIC_AUTH_ACTIVE=false
- N8N_JWT_AUTH_ACTIVE=true
- N8N_ENCRYPTION_KEY=genera-clave-aleatoria-256bits
```

### 8.3 Backup automático de workflows

```bash
# Cron job: backup diario
crontab -e

# Agregar:
0 2 * * * podman exec n8n tar -czf /backup/n8n-$(date +\%Y\%m\%d).tar.gz /home/node/.n8n
```

---

## Checklist Final

- [ ] DNS configurado (SPF, DKIM, DMARC)
- [ ] n8n levantado y accesible en https://n8n.pinguinoseguro.cl
- [ ] Mailgun verificado y API key configurada
- [ ] Workflow de prueba funcionando
- [ ] Integración con Next.js/Python probada
- [ ] Rate limiting activado
- [ ] Backups automatizados
- [ ] Monitoreo en Grafana (opcional)

---

## Templates de Campañas

### Template 1: Onboarding Cliente

**Día 1:** Email bienvenida
**Día 3:** "¿Necesitas ayuda para empezar?"
**Día 7:** "Casos de éxito de otros clientes"
**Día 14:** "Oferta especial: 20% descuento segundo mes"

### Template 2: Newsletter Mensual

**Trigger:** Cron (1er día del mes)
**Contenido:**
- Nuevas features lanzadas
- Tips de seguridad
- Cliente destacado del mes
- Próximos eventos/webinars

---

## Recursos adicionales

- [n8n Documentation](https://docs.n8n.io/)
- [Mailgun API Docs](https://documentation.mailgun.com/)
- [Email Design Best Practices](https://www.campaignmonitor.com/resources/guides/email-design/)
- [PowerDNS DKIM Setup](https://doc.powerdns.com/authoritative/guides/dkim.html)

---

**Tiempo estimado:** 4-6 horas
**Costo mensual:** $0-10 USD (Mailgun free tier: 5k emails/mes)
