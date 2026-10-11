# Workflow POC - Implementation Plan

## Objetivo
Demo funcional HOY mostrando "8,320 workflows disponibles" con rankings inteligentes

## Fase 1: Workflow Scanner (30-45 min)

### Script: `scripts/analyze_workflows.py`
- Escanea 5 repositorios de workflows
- Extrae metadata de cada JSON
- Identifica keywords de seguridad/AI
- Genera rankings por relevancia
- Output: `workflow_index.json`

### Metadata a Extraer:
- name, description, tags
- nodes (tipos de integraciones)
- category (security, ai, automation, etc)
- complexity score
- security relevance score

## Fase 2: API Endpoint (30 min)

### Endpoint: `/api/workflows/recommend`
- Input: incident description
- Output: Top 5 workflows recomendados
- Lógica: Keyword matching + scoring

## Fase 3: Frontend Component (45 min)

### Component: `WorkflowSuggestions.tsx`
- Muestra workflows recomendados
- Badge "8,320 workflows disponibles"
- Botón "Execute" (placeholder)

## Fase 4: Demo Validation (15 min)

### Scenario: Phishing Incident
- Input: "Suspicious phishing email reported"
- Expected: Workflows relacionados con phishing, email analysis, IOC enrichment

---

**Timeline Total**: 2-2.5 horas
**Deliverable**: Demo funcional con datos reales
