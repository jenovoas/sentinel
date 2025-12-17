# n8n Workflow Review Scripts

Scripts para revisar workflows de n8n de forma manual y automatizada.

---

## Scripts Disponibles

### 1. `scan_n8n_workflows.py` - Security Scanner
**Propósito**: Escanear workflows por vulnerabilidades de seguridad

**Uso**:
```bash
python scripts/scan_n8n_workflows.py ultimate-n8n-ai-workflows
```

**Output**:
- `n8n_security_report.md` - Reporte completo
- Detecta: credenciales hardcodeadas, ejecución de código, URLs sospechosas

---

### 2. `review_workflow.py` - Manual Review Tool
**Propósito**: Revisar workflows uno por uno de forma interactiva

**Uso**:
```bash
# Revisar un workflow específico
python scripts/review_workflow.py workflow.json

# Revisar toda una categoría
python scripts/review_workflow.py --category AI-LLM

# Especificar directorio de salida
python scripts/review_workflow.py --category AI-LLM --output my-reviews
```

**Opciones durante revisión**:
- `[a]` Approve - Aprobar para Sentinel
- `[r]` Reject - Rechazar (pedir razón)
- `[f]` Flag - Marcar para modificación
- `[s]` Skip - Revisar después
- `[q]` Quit - Salir

**Output**:
- `workflow-reviews/approved/list.txt` - Workflows aprobados
- `workflow-reviews/rejected.txt` - Workflows rechazados con razones
- `workflow-reviews/flagged.txt` - Workflows que necesitan modificación
- `workflow-reviews/summary.txt` - Resumen de la revisión

---

### 3. `auto_review_workflows.py` - Automated Analysis
**Propósito**: Analizar y puntuar workflows automáticamente

**Uso**:
```bash
python scripts/auto_review_workflows.py --input n8n-workflows-safe --output workflow-analysis
```

**Scoring System** (0-100):
- Keywords SIEM (alert, incident, threat): +10 cada uno
- Nodos relevantes:
  - Webhook: +8 (event-driven)
  - PostgreSQL: +7
  - Schedule: +7
  - Slack/Discord: +6
  - HTTP Request: +5
  - Email: +5
- Bonus webhook: +15

**Categorías de Uso**:
- Incident Response
- Monitoring & Detection
- Threat Intelligence
- Compliance & Reporting
- Event Automation
- Scheduled Tasks
- General Automation

**Output**:
- `workflow-analysis/analysis_report.md` - Reporte completo
- `workflow-analysis/top_candidates.json` - Top 50 workflows para Sentinel

---

## Workflow Recomendado

### Paso 1: Security Scan (OBLIGATORIO)
```bash
python scripts/scan_n8n_workflows.py ultimate-n8n-ai-workflows
```
- Revisa `n8n_security_report.md`
- Identifica workflows CRITICAL/HIGH
- Solo usa workflows LOW-risk

### Paso 2: Automated Analysis
```bash
python scripts/auto_review_workflows.py --input n8n-workflows-safe
```
- Genera scoring automático
- Identifica top 50 candidatos
- Categoriza por caso de uso

### Paso 3: Manual Review (Top Candidates)
```bash
# Revisar top 50 manualmente
python scripts/review_workflow.py --category AI-LLM
```
- Aprobar workflows útiles
- Rechazar workflows no relevantes
- Marcar workflows que necesitan modificación

### Paso 4: Integration
- Copiar workflows aprobados a `sentinel/workflows/`
- Adaptar credenciales (usar n8n credentials system)
- Probar en ambiente aislado
- Integrar con ITIL Incident Management

---

## Ejemplos de Uso

### Ejemplo 1: Revisar workflows de IA
```bash
# Análisis automatizado
python scripts/auto_review_workflows.py --input n8n-workflows-safe

# Ver top candidates en AI-LLM
cat workflow-analysis/analysis_report.md | grep -A 10 "AI-LLM"

# Revisar manualmente los mejores
python scripts/review_workflow.py --category AI-LLM
```

### Ejemplo 2: Buscar workflows de incident response
```bash
# Análisis automatizado
python scripts/auto_review_workflows.py --input n8n-workflows-safe

# Filtrar por caso de uso
grep -A 5 "Incident Response" workflow-analysis/analysis_report.md
```

### Ejemplo 3: Workflow completo desde cero
```bash
# 1. Escanear seguridad
python scripts/scan_n8n_workflows.py ultimate-n8n-ai-workflows

# 2. Extraer workflows seguros (ya hecho)
# n8n-workflows-safe/ contiene 1,919 workflows seguros

# 3. Análisis automatizado
python scripts/auto_review_workflows.py

# 4. Revisar top 20 manualmente
python scripts/review_workflow.py --category AI-LLM | head -20

# 5. Ver resultados
cat workflow-reviews/summary.txt
```

---

## Estructura de Directorios

```
sentinel/
├── ultimate-n8n-ai-workflows/     # Original (2,772 workflows)
├── n8n-workflows-safe/            # Seguros (1,919 workflows)
│   ├── AI-LLM/                    # 469 workflows
│   ├── Google/                    # 280 workflows
│   ├── Webhooks/                  # 137 workflows
│   ├── Communication/             # 100 workflows
│   ├── Automation/                # 65 workflows
│   └── Other/                     # 868 workflows
├── workflow-reviews/              # Revisiones manuales
│   ├── approved/
│   ├── rejected.txt
│   ├── flagged.txt
│   └── summary.txt
└── workflow-analysis/             # Análisis automatizado
    ├── analysis_report.md
    └── top_candidates.json
```

---

## Tips de Seguridad

### Antes de Usar Cualquier Workflow:
1. ✅ Revisar código manualmente
2. ✅ Reemplazar credenciales hardcodeadas
3. ✅ Validar todas las URLs externas
4. ✅ Probar en ambiente aislado
5. ✅ Habilitar audit logging
6. ✅ Aplicar principio de menor privilegio

### Red Flags:
- 🚩 Credenciales en texto plano
- 🚩 Ejecución de código JavaScript/shell
- 🚩 Conexiones SSH/FTP
- 🚩 URLs acortadas (bit.ly, tinyurl)
- 🚩 Dominios sospechosos (.tk, .ml, .ga)
- 🚩 HTTP en lugar de HTTPS

---

## Próximos Pasos

1. **Revisar top 50 workflows** del análisis automatizado
2. **Identificar 10-20 workflows** más útiles para Sentinel
3. **Adaptar workflows** (credenciales, URLs, lógica)
4. **Integrar con ITIL** Incident Management
5. **Probar en sandbox** antes de producción
6. **Documentar workflows** aprobados

---

**Última actualización**: 2025-12-16  
**Workflows escaneados**: 2,772  
**Workflows seguros**: 1,919  
**Status**: ✅ Listo para revisión manual
