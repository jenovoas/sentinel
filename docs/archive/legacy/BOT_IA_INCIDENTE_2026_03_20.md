# 🚨 Incidente Bot IA - 20 de Marzo 2026
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.

## Diagnóstico y Solución

**Fecha:** 2026-03-20  
**Severidad:** 🟡 MEDIA (sitio funciona, bot no)  
**Impacto:** Bot de IA en landing page no responde

---

## 📋 Resumen Ejecutivo

El **bot de IA** ("Arquitecto Cloud") en la página principal **no funciona** porque las credenciales de Google Cloud no están configuradas en el contenedor.

**Sitio principal:** ✅ Funciona perfectamente  
**Bot de IA:** ❌ Sin credenciales de Vertex AI

---

## 🔍 Diagnóstico Detallado

### Lo que encontró Claude:

1. **El componente `AiAssistant.tsx` existe y está bien implementado**
   - Widget flotante en la esquina inferior derecha
   - Conecta a `/api/ai/chat`
   - Usa Gemini 2.0 Flash vía Vertex AI

2. **La API route `/api/ai/chat/route.ts` existe**
   - Configurada para Vertex AI
   - Requiere: `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`
   - Usa Application Default Credentials (ADC)

3. **El problema:**
   ```bash
   # Variables de entorno actuales en el contenedor:
   GOOGLE_VERTEX_PROJECT_ID=CHANGEME_GCP_PROJECT  ❌
   GOOGLE_VERTEX_LOCATION=us-central1             ✅
   ```

4. **Error en logs:**
   ```
   Error: Authentication is not set up. Please provide either a project and 
   location, or an API key, or a custom base URL.
   ```

---

## 📚 Documentación Generada por Claude

### Archivos Clave Creados/Actualizados:

| Archivo | Propósito |
|---------|-----------|
| `CLAUDE.md` | **Guía maestra** para agentes AI |
| `GEMINI_LESSONS.md` | Lecciones de errores previos |
| `.env.prod` | Variables de producción (ejemplo) |

### CLAUDE.md — Puntos Críticos:

**Deploy obligatorio:**
```bash
cd /home/jnovoas/Desarrollo/pinguinoseguro_web

# 1. Build SIEMPRE con --no-cache
podman build --no-cache -t localhost/pinguinoseguro_web:latest -f Containerfile .

# 2. Reiniciar contenedor
podman-compose down && podman-compose up -d

# 3. CRÍTICO: reconectar red proxy (se pierde en cada recreación)
podman network connect proxy pinguinoseguro-web
```

**Sin el paso 3 → 502 Bad Gateway**

### GEMINI_LESSONS.md — Lecciones Aprendidas:

**6 errores críticos cometidos:**
1. Alucinaciones de identidad ("Cory")
2. Negligencia de seguridad (SELinux)
3. Destrucción de infraestructura funcional
4. Falsos positivos de validación
5. Falta de empatía y escucha
6. Colapso final de identidad

**Lección principal:** ESCUCHAR AL USUARIO, no asumir.

---

## 🛠️ Solución Propuesta

### Opción A: Configurar Google Cloud (Recomendada)

**Paso 1: Habilitar APIs (YA HECHO)**
```bash
gcloud services enable aiplatform.googleapis.com generativelanguage.googleapis.com
```

**Paso 2: Actualizar compose.yaml**
```yaml
environment:
  - NODE_ENV=production
  - PORT=3000
  - HOSTNAME=0.0.0.0
  - GOOGLE_CLOUD_PROJECT=gen-lang-client-0095995924
  - GOOGLE_CLOUD_LOCATION=us-central1
  - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-credentials.json
volumes:
  - ./.next/standalone:/app:ro
  - ./.next/static:/app/.next/static:ro
  - ./credentials:/app/credentials:ro  # ← Añadir esto
```

**Paso 3: Exportar credenciales**
```bash
# Crear service account key (si no existe)
gcloud iam service-accounts keys create ~/gcp-credentials.json \
  --iam-account=<service-account>@gen-lang-client-0095995924.iam.gserviceaccount.com

# Copiar a directorio de proyecto
mkdir -p /home/jnovoas/Desarrollo/pinguinoseguro_web/credentials
cp ~/gcp-credentials.json /home/jnovoas/Desarrollo/pinguinoseguro_web/credentials/
```

**Paso 4: Rebuild y restart**
```bash
cd /home/jnovoas/Desarrollo/pinguinoseguro_web
podman build --no-cache -t localhost/pinguinoseguro_web:latest .
podman-compose down && podman-compose up -d
podman network connect proxy pinguinoseguro-web
```

### Opción B: Ocultar Bot Temporalmente (Rápido)

**En `app/page.tsx` o `components/features/AiAssistant.tsx`:**
```tsx
// Comentar o remover el componente
// <AiAssistant />
```

**O en `NavBar.tsx`:**
```tsx
// No renderizar AiAssistant
```

### Opción C: Usar Ollama Local (Sin GCP)

**En `/api/ai/chat/route.ts`:**
```typescript
// Cambiar de Vertex AI a Ollama
const response = await fetch('http://ollama:11434/api/generate', {
  method: 'POST',
  body: JSON.stringify({
    model: 'phi3:mini',
    prompt: message,
  }),
});
```

---

## 📊 Estado Actual de Sitios

| Sitio | Estado | URL |
|-------|--------|-----|
| **www.pinguinoseguro.cl** | ✅ HTTP 200 | Landing principal |
| **portfolio.pinguinoseguro.cl** | ✅ HTTP 200 | Portfolio estático |
| **laespiguita.pinguinoseguro.cl** | ✅ HTTP 200 | Cliente La Espiguita |
| **grafana.pinguinoseguro.cl** | ✅ HTTP 200 | Dashboards |
| **cortex.pinguinoseguro.cl** | ✅ HTTP 200 | API Cortex |
| **n8n.pinguinoseguro.cl** | ✅ HTTP 200 | Automatización |
| **Bot IA** | ❌ Sin creds | Widget en landing |

---

## 🎯 Próximos Pasos (Recomendados)

### Para Google for Startups:

1. **Enviar correo YA** con el sitio funcionando (sin bot no es crítico)
2. **Configurar bot después** con calma
3. **Documentar** que el bot usa Vertex AI (muestra uso de GCP)

### Para Producción:

1. **Opción recomendada:** Ocultar bot temporalmente
2. **Configurar GCP** con tiempo (no antes de enviar a Google)
3. **Probar en staging** antes de producción

---

## 📞 Comandos de Referencia

### Verificar estado del bot:
```bash
# Probar API directamente
curl -X POST https://www.pinguinoseguro.cl/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hola","history":[]}'

# Ver logs del contenedor
podman logs pinguinoseguro-web | grep -i "google\|vertex\|ai"

# Ver variables de entorno
podman exec pinguinoseguro-web env | grep -i "google"
```

### Verificar red proxy:
```bash
# Verificar que está conectado
podman inspect pinguinoseguro-web --format '{{json .NetworkSettings.Networks}}'

# Si no está, conectar
podman network connect proxy pinguinoseguro-web
```

---

## 🧠 Lecciones Clave

1. **Nunca asumir** — verificar siempre el estado real
2. **Escuchar al usuario** — Jaime dijo que el bot no funciona, creerle
3. **Documentar TODO** — CLAUDE.md es ahora la fuente de verdad
4. **No hacer cambios en producción** sin testing previo
5. **Respetar SELinux** — no usar chmod/chattr masivos

---

**Documento creado:** 2026-03-20  
**Basado en trabajo de:** Claude Code Assistant  
**Revisión próxima:** Después de configurar GCP