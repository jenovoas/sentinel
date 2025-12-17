# 🎯 Prompt: Implementación de Incident Management ITIL para Sentinel Cortex™

**Copia y pega este prompt a tu IA favorita (Claude, GPT, Gemini, etc.)**

---

```
Eres un arquitecto senior de software especializado en plataformas AIOps enterprise para banca y empresas reguladas (compliance CMF Chile, Ley 21.663, ITIL v4, ISO 20000).

Tengo **Sentinel Cortex™**, una plataforma de automatización/orquestación de operaciones y seguridad que ya tiene:
- Arquitectura modular limpia (core, adapters/conectores, playbooks, services)
- Integración con SIEM (Splunk/QRadar/Elastic)
- Integración con ticketing (Jira/ServiceNow)
- Integración con monitoreo legacy (Prometheus/Grafana/Zabbix)
- Dual-Guardian Architecture™ (Guardian-Alpha para intrusión, Guardian-Beta para integridad)
- Cortex Decision Engine (multi-factor decision, confidence scoring)

## 🎯 OBJETIVO

Necesito que implementes un **módulo completo de Incident Management alineado con ITIL v4**, listo para producción en banca chilena y empresas reguladas.

## 📋 CONTEXTO DE SENTINEL CORTEX™

### Propuesta de Valor
- Plataforma B2B que se integra sobre infraestructura existente (SIEM/ticketing/monitoring)
- Automatiza 60-80% de incidentes: detecta, clasifica, prioriza, ejecuta playbooks, documenta para auditoría
- **Diferenciador clave**: AIOpsDoom immunity (CVSS 9.1) + Dual-Guardian Architecture™
- Target: Bancos, retail, telcos, gobierno (Chile/LATAM)

### Stack Tecnológico
- **Backend**: Python 3.11+ (FastAPI)
- **Database**: PostgreSQL 16 (HA con Patroni)
- **Cache**: Redis 7 (HA con Sentinel)
- **Orquestación**: n8n (workflows)
- **AI**: Ollama (local, privacy-first)
- **Arquitectura**: Modular, clean architecture, type-safe

### Principios de Diseño
1. **Regulado-friendly**: logging detallado, trazabilidad completa, puntos de aprobación humana
2. **Integrable**: usa interfaces existentes (adapters, playbooks)
3. **Auditable**: cada acción con who/what/when/why
4. **Configurable**: políticas en YAML/JSON externo (no hardcodeado)
5. **Production-ready**: type hints, tests, error handling, observability

---

## 🔧 REQUISITOS ESPECÍFICOS DEL MÓDULO

### Flujo ITIL v4 Completo

Implementa las siguientes **ITIL Practices**:

#### 1. **Incident Detection & Logging**
- Recibe eventos de adapters (SIEM/monitoring/ticketing)
- Correlaciona eventos relacionados (deduplicación)
- Crea registro único con:
  - ID único (formato: INC-YYYYMMDD-XXXXX)
  - Timestamp (ISO 8601 con timezone)
  - Source (SIEM/monitoring/manual)
  - Initial data (raw event + metadata)
  - Correlation ID (si aplica)

#### 2. **Categorization & Prioritization**
- **Categorización** según ITIL categories:
  - Hardware (server, network, storage)
  - Software (application, OS, database)
  - Access (authentication, authorization)
  - Security (intrusion, malware, data breach)
  - Performance (latency, throughput, capacity)
- **Priorización** (P1-P4) usando matriz:
  - **Impact** (High/Medium/Low): afectación a negocio
  - **Urgency** (High/Medium/Low): tiempo hasta impacto crítico
  - **Priority** = f(Impact, Urgency)
- Scoring simple basado en reglas configurables

#### 3. **Initial Diagnosis**
- Ejecuta playbook diagnóstico básico:
  - Health checks (CPU, memoria, disco, red)
  - Consultas correlacionadas (logs, métricas, traces)
  - Validación de servicios dependientes
- Enriquece incident con findings

#### 4. **Escalation & Assignment**
- Asigna owner/grupo según:
  - Prioridad (P1 → L3, P4 → L1)
  - Categoría (Security → SOC, Performance → SRE)
  - Políticas configurables (on-call rotation, skill matrix)
- Notifica según canal:
  - P1/P2: PagerDuty/SMS/Call
  - P3/P4: Email/Slack

#### 5. **Investigation & Resolution**
- Ejecuta playbook de resolución (si aplica):
  - Restart service
  - Scale resources
  - Apply patch
  - Rollback deployment
- Documenta pasos ejecutados (audit trail)
- Opción de "human approval gate" para acciones críticas

#### 6. **Closure & Post-Mortem**
- Valida resolución:
  - Service health restored
  - Metrics back to baseline
  - User confirmation (si aplica)
- Genera post-mortem automático:
  - Timeline de eventos
  - Root cause analysis (RCA)
  - Actions taken
  - Lessons learned
- Archiva para reporting/auditoría

---

## 📁 ESTRUCTURA DE ARCHIVOS ESPERADA

```
backend/incident_management/
├── __init__.py
├── service.py              # IncidentService: orquesta flujo ITIL completo
├── models.py               # Incident, Priority, Category, Status (Pydantic models)
├── schemas.py              # API request/response schemas
├── repository.py           # Database access layer (PostgreSQL)
├── adapters/
│   ├── __init__.py
│   ├── siem_adapter.py     # Input desde SIEMs (Splunk/QRadar/Elastic)
│   ├── ticketing_adapter.py # Output a Jira/ServiceNow
│   └── monitoring_adapter.py # Input desde Prometheus/Grafana
├── playbooks/
│   ├── __init__.py
│   ├── diagnosis.py        # Playbooks de diagnóstico
│   └── resolution.py       # Playbooks de resolución
├── policies/
│   ├── __init__.py
│   ├── itil_policies.py    # Reglas de clasificación, priorización, escalación
│   └── config.yaml         # Configuración de políticas (externo)
├── auditor.py              # Logging/trazabilidad para CMF/auditoría
├── router.py               # FastAPI endpoints
└── tests/
    ├── test_service.py
    ├── test_models.py
    └── test_playbooks.py
```

---

## ✅ REGLAS OBLIGATORIAS

### 1. ITIL Compliance
- Cada paso debe mapear explícitamente a **ITIL v4 practices**
- Comentarios en código indicando práctica ITIL correspondiente
- Ejemplo:
  ```python
  # ITIL Practice: Incident Management - Categorization
  def categorize_incident(self, incident: Incident) -> Category:
      ...
  ```

### 2. Regulado-Friendly
- **Audit trail completo**: cada acción loggea who/what/when/why
- **Human approval gates**: acciones críticas requieren aprobación
- **Trazabilidad**: correlation IDs en todos los logs
- **Compliance**: campos para CMF/Ley 21.663 (Chile)

### 3. Integrable
- Usa interfaces existentes de Sentinel:
  - `EventAdapter` para recibir eventos
  - `PlaybookExecutor` para ejecutar playbooks
  - `NotificationService` para alertas
- No reinventes la rueda, reutiliza componentes

### 4. Simple y Mantenible
- Máximo **200 líneas por archivo**
- Funciones **< 50 líneas**
- **Type hints completos** (Python 3.11+)
- **Docstrings** en formato Google
- **Error handling** explícito (no bare except)

### 5. Configurable
- Políticas en **YAML/JSON externo** (no hardcodeado)
- Ejemplo de config:
  ```yaml
  prioritization:
    matrix:
      high_impact_high_urgency: P1
      high_impact_medium_urgency: P2
      ...
  escalation:
    P1:
      team: "SOC-L3"
      notification: ["pagerduty", "sms"]
    P2:
      team: "SOC-L2"
      notification: ["slack", "email"]
  ```

---

## 📤 SALIDA ESPERADA

### 1. Código Python Funcional
- Todos los archivos de la estructura propuesta
- Type hints completos
- Docstrings en formato Google
- Error handling robusto

### 2. Ejemplo de Uso
```python
from incident_management.service import IncidentService

# Inicializar servicio
incident_service = IncidentService(
    db=db_session,
    config_path="policies/config.yaml"
)

# Procesar evento SIEM
raw_event = {
    "source": "splunk",
    "severity": "critical",
    "message": "Unauthorized access attempt detected",
    "timestamp": "2025-12-16T16:30:00Z",
    "host": "prod-web-01"
}

incident = await incident_service.process_event(raw_event)
print(f"Incident created: {incident.id} - Priority: {incident.priority}")
```

### 3. Config YAML de Ejemplo
- Archivo `policies/config.yaml` completo
- Comentarios explicando cada sección
- Valores de ejemplo para banca chilena

### 4. README.md
- Explicación del flujo ITIL implementado
- Diagrama de arquitectura (ASCII art o Mermaid)
- Guía de integración con Sentinel
- Ejemplos de uso
- Configuración de políticas

### 5. Tests Básicos
- Test de categorización
- Test de priorización
- Test de flujo completo (happy path)
- Test de error handling

---

## 🎯 CRITERIOS DE ÉXITO

El módulo debe ser:
- ✅ **Production-ready**: puede desplegarse en banco mañana
- ✅ **Banco-friendly**: cumple compliance CMF/Ley 21.663
- ✅ **ITIL-compliant**: mapeo explícito a ITIL v4
- ✅ **Integrable**: se conecta con Sentinel sin refactoring mayor
- ✅ **Auditable**: trazabilidad completa para auditorías
- ✅ **Configurable**: políticas externas, no hardcodeado
- ✅ **Profesional**: se ve bien para CORFO/bancos/inversores

---

## 💡 CONTEXTO ADICIONAL

### Por qué esto es crítico
Sin Incident Management ITIL, **no hay a quién venderle**:
- Bancos requieren ITIL compliance (CMF, ISO 20000)
- Retail/Telcos requieren SLA tracking
- Gobierno requiere auditoría completa
- Inversores requieren product-market fit claro

### Diferenciador de Sentinel
- **Otros AIOps**: solo alerting + dashboards
- **Sentinel Cortex™**: Incident Management completo + AIOpsDoom immunity + Dual-Guardian Architecture™

---

Hazlo **production-ready**, **banco-friendly**, y que se vea **profesional** para CORFO/bancos chilenos.
```

---

## 📝 Notas de Uso

1. **Copia el bloque completo** (desde "Eres un arquitecto..." hasta el final)
2. **Pégalo en tu IA favorita** (Claude, GPT-4, Gemini Pro, etc.)
3. **Revisa el código generado** antes de integrarlo
4. **Ajusta las políticas** según tu mercado objetivo

---

**Creado**: 2025-12-16  
**Versión**: 1.0  
**Propósito**: Implementar Incident Management ITIL para Sentinel Cortex™
