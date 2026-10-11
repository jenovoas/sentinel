# 📊 Observability - Monitoreo y Métricas

## 📋 Resumen Ejecutivo

**Observability** es el sistema de salud de Sentinel. Monitorea todo 24/7 y te avisa cuando algo va mal.

**Analogía simple**: Como el panel de instrumentos de un avión (velocidad, altitud, combustible, etc.).

---

## 🎯 ¿Qué Hace Este Módulo?

### En Palabras Simples

Imagina que tienes 100 servidores. Observability es como tener:
1. **Termómetro** (CPU, RAM, disco)
2. **Cámara de seguridad** (logs de todo lo que pasa)
3. **Alarma** (te avisa cuando algo va mal)
4. **Grabadora** (guarda historial para investigar después)

### Ejemplo Real

```
ANTES (Sin Observability):
- Servidor se cae
- Clientes reportan: "No funciona!"
- Tú: "¿Qué pasó? ¿Cuándo? ¿Por qué?"
- Investigas a ciegas por horas

DESPUÉS (Con Observability):
- Servidor empieza a ir lento
- Observability: "⚠️ RAM al 95%, CPU al 90%"
- Tú: Ves gráfico, identificas proceso problemático
- Solucionas ANTES de que se caiga
- Tiempo: 5 minutos
```

---

## 🗂️ Qué Contiene Este Módulo

```
observability/
├── prometheus/          # Recolecta métricas (CPU, RAM, etc.)
│   └── prometheus.yml   # Configuración
│
├── loki/               # Recolecta logs (texto de lo que pasa)
│   └── loki.yml        # Configuración
│
├── grafana/            # Dashboards visuales (gráficos bonitos)
│   └── dashboards/     # Dashboards pre-configurados
│
├── promtail/           # Envía logs a Loki
│   └── promtail.yml    # Configuración
│
└── exporters/          # Recolectores especializados
    ├── node-exporter/  # Métricas del servidor (CPU, RAM)
    ├── postgres-exporter/  # Métricas de base de datos
    └── redis-exporter/     # Métricas de cache
```

---

## 🔑 Componentes Clave

### 1. Prometheus (Métricas)

**¿Qué hace?**: Recolecta números cada 15 segundos.

**Ejemplos de métricas**:
```
cpu_usage_percent = 45%
ram_usage_gb = 6.2 GB
disk_free_gb = 120 GB
http_requests_per_second = 150
database_queries_per_second = 300
```

**Analogía**: Como un doctor que toma tu presión arterial cada 15 segundos.

**Acceso**: http://localhost:9090

### 2. Loki (Logs)

**¿Qué hace?**: Guarda texto de todo lo que pasa.

**Ejemplos de logs**:
```
[2024-12-18 10:30:15] INFO: Usuario "admin" inició sesión
[2024-12-18 10:30:20] WARNING: Intento de acceso a /admin desde IP 1.2.3.4
[2024-12-18 10:30:25] ERROR: Base de datos no responde
```

**Analogía**: Como la caja negra de un avión que graba todo.

**Acceso**: A través de Grafana (puerto 3001)

### 3. Grafana (Dashboards)

**¿Qué hace?**: Convierte números y logs en gráficos bonitos.

**Dashboards incluidos**:
- **System Overview**: CPU, RAM, Disco de todos los servidores
- **Application Metrics**: Requests, errores, latencia
- **Database Performance**: Queries lentas, conexiones
- **Security Events**: Intentos de acceso, alertas

**Analogía**: Como el panel de un Tesla que muestra todo visualmente.

**Acceso**: http://localhost:3001  
**Usuario**: admin  
**Password**: (ver `.env`)

### 4. Exporters (Recolectores)

**¿Qué hacen?**: Extraen métricas de diferentes fuentes.

**Node Exporter** (Servidor):
```
- CPU usage
- RAM usage
- Disk I/O
- Network traffic
```

**PostgreSQL Exporter** (Base de datos):
```
- Queries por segundo
- Conexiones activas
- Tamaño de tablas
- Queries lentas
```

**Redis Exporter** (Cache):
```
- Hit rate (% de aciertos)
- Memoria usada
- Comandos por segundo
```

---

## 🚀 Cómo Funciona (Flujo Completo)

```
┌─────────────────────────────────────────────────────────────┐
│ PASO 1: Fuentes Generan Datos                               │
│ - Servidor: CPU al 80%                                      │
│ - Backend: 150 requests/segundo                             │
│ - PostgreSQL: Query tardó 2 segundos                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ PASO 2: Exporters Recolectan                                │
│ - Node Exporter → CPU: 80%                                  │
│ - Backend → Requests: 150/s                                 │
│ - PostgreSQL Exporter → Query: 2s                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ PASO 3: Prometheus Almacena (Métricas)                      │
│         Loki Almacena (Logs)                                │
│ - Retención: 15 días                                        │
│ - Compresión: 10x                                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ PASO 4: Grafana Visualiza                                   │
│ - Gráfico de CPU (últimas 24h)                             │
│ - Tabla de queries lentas                                   │
│ - Alerta si CPU > 90%                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Jerarquía ITIL (Simplificada)

**En ITIL, Observability es**:

```
Service Operation (Operación del Servicio)
├─ Event Management (Gestión de Eventos)
│  └─ Prometheus detecta eventos (CPU alto, disco lleno)
│
├─ Incident Management (Gestión de Incidentes)
│  └─ Alertas automáticas cuando algo va mal
│
└─ Problem Management (Gestión de Problemas)
   └─ Análisis de tendencias para prevenir problemas
```

**Traducción**: Observability te ayuda a operar servicios sin apagar fuegos todo el día.

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Detectar Servidor Lento

**Dashboard muestra**:
```
CPU: 95% ⚠️
RAM: 90% ⚠️
Proceso: python3 (PID 1234)
```

**Tú haces**:
```bash
# Ver qué hace ese proceso
ps aux | grep 1234

# Matar proceso problemático
kill 1234

# CPU vuelve a 20% ✅
```

**Tiempo total**: 2 minutos

### Ejemplo 2: Investigar Error Pasado

**Cliente reporta**: "Ayer a las 3 PM no pude acceder"

**Tú haces**:
1. Abres Grafana
2. Seleccionas rango: "Ayer 2:50 PM - 3:10 PM"
3. Ves logs:
   ```
   [15:02:35] ERROR: Database connection timeout
   [15:02:40] ERROR: PostgreSQL not responding
   ```
4. Conclusión: Base de datos se cayó por 5 minutos

**Tiempo total**: 30 segundos (vs horas investigando a ciegas)

### Ejemplo 3: Prevenir Problema Futuro

**Grafana muestra tendencia**:
```
Disco usado:
- Hace 30 días: 50 GB
- Hace 15 días: 75 GB
- Hoy: 95 GB
- Predicción: Lleno en 5 días
```

**Tú haces**:
- Limpias logs antiguos
- Aumentas disco
- Problema prevenido ✅

---

## 📈 Métricas que Puedes Ver

### Métricas de Sistema
- **CPU**: % de uso por core
- **RAM**: GB usados / GB totales
- **Disco**: GB libres, I/O por segundo
- **Red**: MB/s entrada/salida

### Métricas de Aplicación
- **Requests**: Cantidad por segundo
- **Latencia**: Tiempo de respuesta (P50, P95, P99)
- **Errores**: Cantidad de errores 4xx, 5xx
- **Usuarios**: Usuarios activos simultáneos

### Métricas de Base de Datos
- **Queries**: Cantidad por segundo
- **Conexiones**: Activas / Máximo
- **Slow Queries**: Queries que tardan >1 segundo
- **Tamaño**: GB por tabla

---

## 🔔 Alertas Configuradas

### Alertas Críticas (Notificación inmediata)
- CPU > 90% por 5 minutos
- RAM > 95%
- Disco < 10% libre
- Base de datos caída
- Backend no responde

### Alertas Warning (Notificación diaria)
- CPU > 70% por 1 hora
- Disco < 20% libre
- Queries lentas (>2 segundos)

### Cómo se Notifica
- Email
- Slack (si configurado)
- Discord (si configurado)
- Webhook custom

---

## 🛠️ Comandos Útiles

```bash
# Ver estado de Observability
docker-compose ps prometheus loki grafana

# Ver logs de Prometheus
docker-compose logs -f prometheus

# Reiniciar Grafana
docker-compose restart grafana

# Verificar que Prometheus está recolectando
curl http://localhost:9090/api/v1/targets

# Verificar métricas de un servidor
curl http://localhost:9100/metrics  # Node Exporter

# Backup de dashboards de Grafana
docker-compose exec grafana grafana-cli admin export-dashboard
```

---

## 💼 Valor de Negocio

### Para Inversionistas

**Este módulo representa**:
- **15% del valor técnico** de Sentinel
- **Reducción de downtime**: 99.95% uptime (vs 99% sin observability)
- **Ahorro en costos**: Previene problemas antes de que sean caros

**ROI**:
```
Sin Observability:
- Downtime: 3.65 días/año (99% uptime)
- Costo de downtime: $10K/hora
- Pérdida anual: $876K

Con Observability:
- Downtime: 4.5 horas/año (99.95% uptime)
- Costo de downtime: $10K/hora
- Pérdida anual: $45K

Ahorro: $831K/año
```

### Comparación con Competidores

| Feature | Sentinel | Datadog | Grafana Cloud |
|---------|----------|---------|---------------|
| **Costo** | $0/mes | $15/host/mes | $8/host/mes |
| **Retención** | 15 días | 15 días | 13 días |
| **Self-hosted** | ✅ | ❌ | ❌ |
| **Privacy** | ✅ | ❌ | ❌ |

---

## 🎓 Para Nuevos Desarrolladores

### Onboarding (10 minutos)

1. **Abrir Grafana**: http://localhost:3001
2. **Explorar dashboards**: Click en "Dashboards" → "Browse"
3. **Ver métricas en vivo**: Dashboard "System Overview"
4. **Crear alerta**: Dashboard → Panel → Alert

### Crear Tu Primer Dashboard

**Paso 1**: Grafana → "+" → "Dashboard"

**Paso 2**: "Add visualization"

**Paso 3**: Query:
```promql
rate(http_requests_total[5m])
```

**Paso 4**: Guardar

¡Listo! Ya tienes un gráfico de requests por segundo.

---

## 🌟 Features Destacadas

### 1. Dashboards Pre-configurados
No necesitas configurar nada, ya vienen listos.

### 2. Retención de 15 Días
Puedes investigar problemas de hace 2 semanas.

### 3. Alertas Inteligentes
Solo te notifica cuando es importante (no spam).

### 4. Exportación de Reportes
Genera PDFs para mostrar a jefes/clientes.

---

## 📚 Documentación Relacionada

- **Configuración de Alertas**: `/docs/OBSERVABILITY_SETUP.md`
- **Dashboards Custom**: `/docs/OBSERVABILITY.md`
- **Troubleshooting**: `/docs/OBSERVABILITY-STATUS.md`

---

**Última actualización**: Diciembre 2024  
**Mantenedor**: Equipo Observability  
**Contacto**: observability@sentinel.dev

---

## ❓ Preguntas Frecuentes

**P: ¿Cuánto espacio en disco usa Observability?**  
R: ~10 GB para 15 días de retención (100 servidores).

**P: ¿Puedo ver métricas de hace 1 mes?**  
R: No, retención es 15 días. Para más, aumentar en `prometheus.yml`.

**P: ¿Las métricas afectan performance?**  
R: Mínimo, <1% CPU overhead.

**P: ¿Puedo integrar con Slack?**  
R: Sí, configurar en Grafana → Alerting → Contact points.
