# 🔄 n8n - Automatización de Workflows

## 📋 Resumen Ejecutivo

**n8n** es el robot que hace tareas repetitivas por ti. Conecta diferentes herramientas y las hace trabajar juntas automáticamente.

**Analogía simple**: Como tener un asistente personal que hace tareas aburridas mientras tú duermes.

---

## 🎯 ¿Qué Hace Este Módulo?

### En Palabras Simples

Imagina que cada día tienes que:
1. Revisar 100 logs de seguridad
2. Si encuentras algo sospechoso, enviar email al equipo
3. Crear ticket en Jira
4. Actualizar dashboard

**Sin n8n**: Tú haces todo manualmente (2 horas/día)

**Con n8n**: Robot lo hace automáticamente (0 minutos/día)

### Ejemplo Real

```
WORKFLOW: Detectar Ataque y Responder

TRIGGER: Cada 5 minutos
  ↓
PASO 1: Leer logs de Sentinel
  ↓
PASO 2: ¿Hay intentos de login fallidos > 10?
  ↓ SÍ
PASO 3: Bloquear IP en firewall
  ↓
PASO 4: Enviar email a admin
  ↓
PASO 5: Crear ticket en Jira
  ↓
PASO 6: Actualizar dashboard

TODO AUTOMÁTICO, 24/7
```

---

## 🗂️ Qué Contiene Este Módulo

```
n8n/
├── workflows/              # Workflows pre-configurados
│   ├── security/          # Workflows de seguridad
│   ├── backup/            # Workflows de backup
│   └── monitoring/        # Workflows de monitoreo
│
├── credentials/           # Credenciales (API keys, passwords)
│
└── data/                 # Datos de workflows (historial)
```

**Workflows incluidos**: 50+ workflows listos para usar

---

## 🔑 Workflows Más Importantes

### 1. Auto-Respuesta a Incidentes

**¿Qué hace?**: Cuando detecta ataque, responde automáticamente.

**Pasos**:
1. Detecta: Intento de SQL injection
2. Bloquea: IP del atacante
3. Notifica: Email + Slack
4. Documenta: Crea ticket
5. Aprende: Guarda patrón para futuro

**Ahorro de tiempo**: 30 min → 0 min

### 2. Backup Automático

**¿Qué hace?**: Hace backup de base de datos cada 6 horas.

**Pasos**:
1. Cada 6 horas (automático)
2. Dump de PostgreSQL
3. Comprime archivo
4. Sube a S3
5. Verifica integridad
6. Notifica si falla

**Ahorro de tiempo**: 15 min/día → 0 min

### 3. Reporte Diario

**¿Qué hace?**: Genera reporte ejecutivo cada mañana.

**Pasos**:
1. A las 8 AM (automático)
2. Recolecta métricas de ayer
3. Genera gráficos
4. Crea PDF
5. Envía por email

**Ahorro de tiempo**: 1 hora/día → 0 min

### 4. Monitoreo de SLA

**¿Qué hace?**: Verifica que uptime sea >99.9%.

**Pasos**:
1. Cada hora
2. Ping a servicios
3. Calcula uptime
4. Si <99.9%, alerta
5. Escala a manager

**Ahorro de tiempo**: Previene problemas

---

## 🚀 Cómo Funciona (Flujo Visual)

```
┌─────────────────────────────────────────────────────────────┐
│ TRIGGER (Inicio)                                             │
│ - Cada X minutos                                            │
│ - Cuando llega email                                        │
│ - Cuando webhook recibe datos                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ NODO 1: Obtener Datos                                       │
│ - Leer logs de Sentinel                                     │
│ - Consultar API                                             │
│ - Leer base de datos                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ NODO 2: Procesar                                            │
│ - Filtrar datos                                             │
│ - Transformar formato                                       │
│ - Calcular métricas                                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ NODO 3: Decidir                                             │
│ - IF: ¿Es crítico?                                          │
│   → SÍ: Ir a NODO 4                                        │
│   → NO: Terminar                                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ NODO 4: Actuar                                              │
│ - Enviar email                                              │
│ - Crear ticket                                              │
│ - Ejecutar script                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Jerarquía ITIL (Simplificada)

**En ITIL, n8n es**:

```
Service Operation (Operación del Servicio)
├─ Incident Management (Gestión de Incidentes)
│  └─ Workflows de auto-respuesta a incidentes
│
├─ Request Fulfillment (Cumplimiento de Solicitudes)
│  └─ Workflows de provisioning automático
│
└─ Event Management (Gestión de Eventos)
   └─ Workflows de monitoreo y alertas
```

**Traducción**: n8n automatiza las tareas operativas de ITIL.

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Crear Workflow Simple

**Objetivo**: Enviar email cuando CPU > 90%

**Pasos en n8n**:
1. Abrir n8n: http://localhost:5678
2. Click "New Workflow"
3. Agregar nodo "Schedule" (cada 5 min)
4. Agregar nodo "HTTP Request" (obtener CPU de Prometheus)
5. Agregar nodo "IF" (CPU > 90?)
6. Agregar nodo "Send Email"
7. Conectar nodos
8. Activar workflow

**Tiempo**: 5 minutos para crear

### Ejemplo 2: Workflow de Backup

**Ya incluido**, solo activar:
1. n8n → Workflows → "Backup Database"
2. Click "Active"
3. Configurar S3 credentials
4. Guardar

**Tiempo**: 2 minutos para activar

### Ejemplo 3: Integrar con Slack

**Objetivo**: Notificar en Slack cuando hay alerta

**Pasos**:
1. n8n → Credentials → "Add Credential"
2. Tipo: "Slack"
3. Pegar Webhook URL de Slack
4. En workflow, agregar nodo "Slack"
5. Seleccionar credential
6. Escribir mensaje
7. Activar

**Tiempo**: 3 minutos

---

## 🛠️ Comandos Útiles

```bash
# Abrir n8n
# URL: http://localhost:5678
# Usuario: admin
# Password: (ver .env)

# Ver workflows activos
docker-compose exec n8n n8n list:workflow

# Ejecutar workflow manualmente
docker-compose exec n8n n8n execute --id=1

# Exportar workflow
docker-compose exec n8n n8n export:workflow --id=1 --output=/data/backup.json

# Importar workflow
docker-compose exec n8n n8n import:workflow --input=/data/backup.json

# Ver logs
docker-compose logs -f n8n
```

---

## 💼 Valor de Negocio

### Para Inversionistas

**Este módulo representa**:
- **10% del valor técnico** de Sentinel
- **Ahorro de tiempo**: 2-4 horas/día por ingeniero
- **Reducción de errores**: Automatización = 0 errores humanos

**ROI**:
```
Sin n8n:
- Ingeniero: $80K/año
- Tiempo en tareas manuales: 25% (2 horas/día)
- Costo: $20K/año

Con n8n:
- Costo: $0 (incluido)
- Tiempo automatizado: 100%
- Ahorro: $20K/año por ingeniero
```

### Comparación con Competidores

| Feature | Sentinel (n8n) | Zapier | Tines |
|---------|----------------|--------|-------|
| **Costo** | $0/mes | $20-50/mes | $100+/mes |
| **Workflows** | Ilimitados | 20-100 | Ilimitados |
| **Self-hosted** | ✅ | ❌ | ❌ |
| **Código custom** | ✅ | ⚠️ Limitado | ✅ |

---

## 🎓 Para Nuevos Desarrolladores

### Onboarding (15 minutos)

1. **Abrir n8n**: http://localhost:5678
2. **Explorar workflows**: Click "Workflows"
3. **Ver workflow de ejemplo**: Abrir "Backup Database"
4. **Crear workflow simple**: New → Schedule → HTTP Request → Email
5. **Activar**: Toggle "Active"

### Crear Tu Primer Workflow

**Objetivo**: Notificar cuando Sentinel está caído

**Paso 1**: New Workflow

**Paso 2**: Agregar nodos:
```
Schedule (cada 5 min)
  ↓
HTTP Request (GET http://localhost:8000/health)
  ↓
IF (response.status != 200)
  ↓
Send Email ("Sentinel está caído!")
```

**Paso 3**: Activar

¡Listo! Ya tienes monitoreo automático.

---

## 🌟 Features Destacadas

### 1. Visual Workflow Editor
Arrastra y suelta nodos, no necesitas código.

### 2. 400+ Integraciones
Slack, Email, Jira, GitHub, AWS, etc.

### 3. Código Custom
Si necesitas algo especial, puedes escribir JavaScript.

### 4. Historial de Ejecuciones
Ve qué pasó en cada ejecución (debugging fácil).

---

## 📚 Documentación Relacionada

- **Workflows de Seguridad**: `/n8n-cybersecurity-workflows/`
- **Guía de n8n**: `/docs/N8N_QUICKSTART.md`
- **Análisis de Workflows**: `/docs/N8N_ANALYSIS_WALKTHROUGH.md`

---

**Última actualización**: Diciembre 2024  
**Mantenedor**: Equipo Automation  
**Contacto**: automation@sentinel.dev

---

## ❓ Preguntas Frecuentes

**P: ¿Necesito saber programar para usar n8n?**  
R: No, la mayoría de workflows se crean arrastrando nodos.

**P: ¿Puedo usar código custom?**  
R: Sí, hay nodo "Function" para JavaScript.

**P: ¿Los workflows afectan performance?**  
R: No, corren en contenedor separado.

**P: ¿Cuántos workflows puedo tener?**  
R: Ilimitados (self-hosted).

**P: ¿Qué pasa si workflow falla?**  
R: n8n reintenta automáticamente y te notifica.
