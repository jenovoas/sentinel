# PLAN DE TRABAJO ESTRATÉGICO Q1 2026 - SENTINEL

**Objetivo:** Organizar la documentación para reflejar las distintas fases del proyecto (Desarrollo, Producción Actual y Arquitectura Futura), alinear la configuración con la realidad de producción (Fenix), y planificar los próximos pasos estratégicos post-congelamiento.

---

## Sección 1: Organización y Clarificación de la Documentación

* **Tarea 1.1: Reestructurar el directorio `docs/`.**
* **Problema:** La documentación de diferentes fases (desarrollo, producción, futuro) está mezclada, causando confusión.
* **Acción:** Crear una nueva estructura de carpetas y mover los documentos existentes para reflejar el estado real del proyecto.
    *`docs/00_vision_y_arquitectura_global/`: Para documentos de alto nivel, como la visión del producto y la arquitectura objetivo final (multi-nodo).
    *   `docs/01_produccion_actual_fenix/`: Para guías de despliegue, configuración y operación específicas del nodo Fenix.
    *`docs/02_entorno_desarrollo_local/`: Para la documentación relacionada con el stack original de Python/FastAPI.
    *   `docs/historico/`: Solo para documentos explícitamente reemplazados o que ya no aplican de ninguna forma.

* **Tarea 1.2: Actualizar `README.md` principal.**
* **Problema:** El README actual no explica el estado multifase del proyecto.
* **Acción:** Añadir una sección al inicio que aclare los tres contextos:
        1. **Entorno de Desarrollo Local:** El PoC con Python/FastAPI.
        2. **Producción Fase 1 (Nodo Fenix):** El estado actual con Rust/Cortex en un solo servidor.
        3. **Arquitectura Objetivo Fase 2:** El plan a futuro para un cluster multi-nodo.

* **Tarea 1.3: Actualizar `ARCHITECTURE.md`.**
* **Problema:** El documento de arquitectura puede ser ambiguo.
* **Acción:** Estructurar el documento con títulos claros: "Arquitectura de Producción Actual (Fenix)" y "Arquitectura Objetivo (Cluster Multi-Nodo)", moviendo los diagramas y textos existentes a la sección que corresponda.

---

## Sección 2: Alineación y Planificación Técnica (Post-Congelamiento)

* **Tarea 2.1: Depurar `docker-compose.fenix.yml`.**
* **Problema:** Contiene servicios (`celery_worker`) que no corresponden al stack de Rust.
* **Acción:** Eliminar el servicio `celery_worker` del compose de Fenix para alinearlo con la realidad del backend de Rust.

* **Tarea 2.2: Implementar Health-Check y Métricas en `sentinel-cortex`.**
* **Problema:** `sentinel-cortex` es una caja negra para Prometheus.
* **Acción:** Planificar la adición de dos rutas en el servidor Axum (Rust): `/health` y `/metrics` (formato Prometheus) para una correcta monitorización y observabilidad.

* **Tarea 2.3: Planificar la Integración de Google AI en `sentinel-cortex`.**
* **Problema:** La capacidad de IA del PoC de Python no ha sido portada al nuevo backend de Rust.
* **Acción:** Investigar y diseñar la implementación de un cliente de Google AI (Gemini) en el servicio `cortex`.

* **Tarea 2.4: Diseño de Hitos Futuros.**
* **Problema:** Los próximos pasos estratégicos (`SOMA`, `Inercia Cuántica`) están mencionados pero no diseñados.
* **Acción:** Crear documentos de diseño técnico para estos hitos, enmarcándolos como parte de la "Fase 2" de la arquitectura.

---
