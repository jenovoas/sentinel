# 🧠 Prompts de Ingeniería para Gemini - Protocolo Sentinel/YATRA

**Objetivo:** Colección de prompts de alta calidad para interactuar con el ecosistema Sentinel, optimizados para el modelo Gemini y en cumplimiento con los axiomas del proyecto.

---

## 1. Auditoría y Salud del Sistema

### Prompt 1.1: Health Check Completo del Nodo Fenix

```
Realiza un health check completo del nodo Fenix. Analiza el `docker-compose.fenix.yml`, el `inventory.yaml` y los logs recientes de Podman. Genera un reporte en markdown que incluya:
1.  Estado de cada contenedor (running, degraded, stopped).
2.  Consumo de recursos (CPU/RAM) por contenedor.
3.  Alertas activas en Prometheus (`prometheus.fenix.yml`).
4.  Discrepancias entre el estado deseado (`inventory.yaml`) y el estado real.
5.  Recomendaciones para optimizar la estabilidad.
```

### Prompt 1.2: Auditoría de Seguridad Rápida

```
Actúa como un analista de seguridad. Revisa la configuración de `firewalld` en `CONTEXTO_REINICIO.md` y las labels de Traefik en `docker-compose.fenix.yml`. Identifica y lista posibles vectores de ataque o configuraciones inseguras, y sugiere mitigaciones específicas para un entorno de producción en Rocky Linux 9.
```

---

## 2. Refactorización y Migración de Código (Protocolo YATRA)

### Prompt 2.1: Migración de Python a Rust (YATRA-Compliant)

```
Toma el siguiente script de Python [pegar script aquí]. Tu tarea es refactorizarlo a un binario de Rust de alto rendimiento.

**Reglas estrictas:**
1.  **Axioma YATRA:** No se permite el uso de `f32` o `f64`. Toda la aritmética debe ser reemplazada por la implementación de `S60` (Base-60) del proyecto o enteros nativos.
2.  **Zero-Copy:** Evita clonaciones innecesarias. Usa `&str`, `Cow`, `Rc`/`Arc` donde sea apropiado.
3.  **Manejo de Errores:** No uses `unwrap()` o `expect()`. Usa `Result` y el crate `anyhow` o `thiserror`.
4.  **Logging:** Integra el crate `tracing` para logging estructurado.

Proporciona el código Rust completo y una breve explicación de las decisiones de refactorización.
```

### Prompt 2.2: Optimización de Script Bash

```
Analiza el script `nuevo-cliente.sh`. Propón una versión refactorizada que mejore la seguridad y la idempotencia. Específicamente, enfócate en:
1.  Prevenir ataques de path traversal en los argumentos.
2.  Validar que los comandos externos (`pdnsutil`, `podman-compose`) existan antes de usarlos.
3.  Mejorar el manejo de errores con `set -euo pipefail` y traps.
4.  Asegurar que se pueda ejecutar múltiples veces sin efectos secundarios no deseados.
```

---

## 3. Investigación y Documentación Técnica

### Prompt 3.1: Generar Dossier Técnico

```
Actúa como el agente `sentinel_research`. Lee los siguientes documentos: `RESEARCH.md`, `ARCHITECTURE.md` y `AI_PRIME_DIRECTIVES.md`.

Sintetiza la información en un dossier técnico de 2 páginas (`DOSSIER_TECNICO.md`) dirigido a un nuevo arquitecto de software. El dossier debe explicar de forma concisa:
1.  La motivación científica detrás de la aritmética Base-60 (YATRA).
2.  La arquitectura de 3 Guardianes (Beta, Alpha, Gamma).
3.  El rol del `Neural Guard` y el `Octomechanical Coupling`.
4.  La importancia de los Axiomas Inmutables.
```

### Prompt 3.2: Crear Plan de Implementación

```
Basado en el plan `PLAN_SMTP_N8N_MARKETING.md`, crea un nuevo plan llamado `PLAN_CLIENT_PORTAL.md`. El objetivo es diseñar un portal de clientes seguro donde puedan ver el estado de sus servicios, métricas de monitoreo y facturas.

El plan debe incluir:
1.  **Arquitectura:** ¿Qué componentes se necesitan (Next.js, API en Rust, etc.)?
2.  **Seguridad:** ¿Cómo se manejará la autenticación y autorización multi-tenant?
3.  **Integración:** ¿Cómo se conectará con Grafana y Prometheus de forma segura?
4.  **Fases de implementación:** Desglosa el proyecto en 4 fases manejables.
```

---

## 4. Troubleshooting y Reparación

### Prompt 4.1: Diagnóstico de Falla de Despliegue

```
He intentado desplegar un nuevo servicio y ha fallado. Aquí están los logs de `podman-compose up -d`:

[pegar logs de error aquí]

Analiza los logs, compáralos con el `docker-compose.fenix.yml` y el `inventory.yaml`, y dame un diagnóstico preciso del problema y los comandos exactos para solucionarlo.
```

### Prompt 4.2: Simulación de Desastre y Plan de Recuperación

```
Simula un escenario de desastre: el volumen `postgres_data` se ha corrompido y es irrecuperable.

Basado en los scripts de backup y la arquitectura (`BACKUP_SYSTEM_INVESTOR_SUMMARY.md`), escribe un plan de recuperación de desastres (DRP) paso a paso. El plan debe incluir:
1.  Comandos para detener los servicios dependientes.
2.  Comandos para identificar y usar el último backup válido.
3.  Comandos para restaurar la base de datos en un nuevo volumen.
4.  Pasos de verificación post-restauración.
```

---

## 5. Prompts Cuánticos y de Simulación (Avanzado)

### Prompt 5.1: Explicación de Concepto YATRA

```
Explica el concepto de "Octomechanical Coupling" y "Computational Mass" como se describe en `ARCHITECTURE.md` y `README.md`. Utiliza una analogía del mundo real para que un ingeniero de software sin experiencia en física teórica pueda entender cómo la temperatura de la CPU afecta la sensibilidad de las alertas en el `neural-guard`.
```

### Prompt 5.2: Generar Código de Simulación

```
Basado en los principios de `RESEARCH.md`, escribe un script en Python que simule una versión simplificada de la `Resonant Memory (Liquid Lattice)`.

El script debe:
1.  Usar una clase `ResonantCrystal` que tenga `phase` y `amplitude`.
2.  Crear una red (lattice) de 10 cristales.
3.  Simular la propagación de una perturbación de fase a través de la red.
4.  Usar `matplotlib` para visualizar la coherencia de la red a lo largo del tiempo.

**Restricción:** No uses `float` para los cálculos de fase, simula la aritmética de punto fijo.
```