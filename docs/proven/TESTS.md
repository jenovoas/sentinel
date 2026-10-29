# Pruebas Verificadas — Sentinel Core

**Fecha de verificación**: 2026-10-05  
**Entorno**: Nodo Fenix (Alpine Linux v3.24, Kernel 6.18.40-0-virt, arquitectura x86_64)  
**Rama**: `alpine_fenix`  
**Estado**: ✅ 173 pruebas de Rust en verde (100% éxito)

---

## 1. Suite Oficial Rust (Workspace)

Ejecución verificada con `cargo test --workspace`:

| Crates | Pruebas | Resultado | Componentes probados |
| :--- | :--- | :--- | :--- |
| `me-60os-core` (`me60os`) | 105 | ✅ 105 pasadas, 0 fallos | Aritmética SPA, lógica armónica S60, S60PID, matrices resonantes, atlantean, verificadores Plimpton 322 y Meijer |
| `sentinel-cortex` | 47 | ✅ 47 pasadas, 0 fallos | Intercepción TruthClaim, WAL de seguridad, filtrado de respaldos, tick térmico, clientes QHC y endpoints HTTP |
| `truthsync-core` | 17 | ✅ 17 pasadas, 0 fallos | Detección de patrones críticos, penalización SPA, caché de digest SHA3-512, paralelismo Rayon |
| `services/neural-guard` | 4 | ✅ 4 pasadas, 0 fallos | Detección de caída de tráfico, multiplicador térmico S60 entero, análisis de temperatura sin floats |
| **Total Workspace** | **173** | **✅ 100% Exitoso** | Cero advertencias críticas, cero errores |

---

## 2. Pruebas de Humo en Vivo (Servicios Nativos OpenRC)

Verificadas mediante peticiones directas en el host contra `sentinel-cortex` (puerto 8000):

* **`/health`**: Retorna `status: "OK"`, eficiencia 95%, QHC conectado vía `/run/soma/qhc.sock` con tick activo.
* **`/api/v1/truth_claim` (Ataque malicioso)**:
  * Payload: `rm -rf /`
  * Respuesta: HTTP 403 Forbidden, `security_blocked: true`, `claim_valid: false`, `sentinel_score: 0.01`.
  * Verificación forense: Registro persistido en `/tmp/sentinel_security_wal.log`.
* **`/api/v1/truth_claim` (Texto limpio)**:
  * Payload: `"El sistema opera con normalidad."`
  * Respuesta: HTTP 200 OK, `claim_valid: true`, `sentinel_score: 0.94`, latencia de verificación: 70 microsegundos.
* **`/api/v1/backup/status`**: Filtra correctamente artefactos con formato `sentinel_backup_*.sql.gz` excluyendo archivos temporales.

---

## 3. Estado de la Suite de Estudio Python (`quantum/`)

* **Ubicación**: `quantum/`
* **Naturaleza**: Prototipos matemáticos preliminares de la fase de estudio antes de la migración a Rust.
* **Estado actual**: 2 de 5 módulos pasando en `test_all.py`. Los módulos restantes fallan por atributos no expuestos en PyO3 y sombras de nombres de librerías locales.
* **Directiva**: La lógica de negocio y seguridad crítica reside al 100% en los crates de Rust; el código de `quantum/` es material de estudio y no forma parte del pipeline de producción.
