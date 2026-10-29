# Vulnerabilidades de Seguridad — Registro y Manual

> **¿Qué es esto?** GitHub escanea tus dependencias automáticamente (Dependabot).
> Cuando encuentra librerías con fallos de seguridad conocidos, te avisa.
> Este documento explica qué se arregló, qué no se puede arreglar (aún), y por qué.

---

## ¿Qué se arregló? (2026-04-06)

### 1. `python-jose` → eliminada (CRÍTICO)

| Campo | Detalle |
|-------|---------|
| **Librería** | `python-jose==3.5.0` (Python) |
| **CVEs** | CVE-2024-33664, CVE-2024-33663 |
| **Gravedad** | Crítica / Alta |
| **El problema** | Permitía ataques de "confusión de algoritmo": un atacante podía fabricar tokens JWT válidos sin conocer la clave secreta. |
| **La solución** | Migrar a `PyJWT` (que ya estaba en el proyecto). Se eliminó `python-jose` de `requirements.txt` y se actualizó `backend/app/security/auth.py`. |

**Antes (vulnerable):**
```python
from jose import JWTError, jwt
jwt.encode(data, secret, algorithm="HS256")
```

**Después (seguro):**
```python
import jwt
from jwt.exceptions import InvalidTokenError as JWTError
jwt.encode(data, secret, algorithm="HS256")
```

---

### 2. `reqwest 0.11` → `0.12` (MODERADO)

| Campo | Detalle |
|-------|---------|
| **Librería** | `reqwest 0.11` (Rust) |
| **Advisory** | RUSTSEC-2025-0134 |
| **El problema** | `reqwest 0.11` depende de `rustls-pemfile 1.x`, librería abandonada por su autor. |
| **La solución** | Actualizar a `reqwest 0.12` que usa versiones mantenidas activamente. |
| **Archivos modificados** | `sentinel-cortex/Cargo.toml`, `services/neural-guard/Cargo.toml` |

---

## ¿Qué NO se puede arreglar aún?

### 3. `rsa` en `sqlx` (MODERADO — sin fix disponible)

| Campo | Detalle |
|-------|---------|
| **Librería** | `rsa 0.9.x` (dependencia interna de `sqlx-mysql`) |
| **Advisory** | RUSTSEC-2023-0071 |
| **El problema** | Vulnerabilidad de timing en operaciones RSA. |
| **Por qué no se arregla** | El equipo de `sqlx` aún no ha liberado una versión que cambie esta dependencia. No hay versión parcheada disponible. |
| **Acción** | Monitorear actualizaciones de `sqlx`. Cuando salga una versión que lo resuelva, actualizar `sqlx` en `sentinel-cortex/Cargo.toml`. |

### 4. `paste` y `lru` en `ratatui` (BAJO — en repo externo)

| Campo | Detalle |
|-------|---------|
| **Librería** | `paste 1.0.15`, `lru 0.12.5` (dependencias de `ratatui 0.26`) |
| **Advisory** | RUSTSEC-2024-0436, RUSTSEC-2026-0002 |
| **El problema** | `paste` está abandonado; `lru` tiene un bug de memoria (unsound). |
| **Por qué no se arregla aquí** | Estas dependencias vienen de `me-60os` (repo separado). Hay que actualizar `ratatui` allí. |
| **Acción** | En el repo `me-60os`, cambiar `ratatui = "0.26"` a `ratatui = "0.29"` o superior y verificar que compile. |

---

## ¿Cómo verificar el estado actual?

```bash
# Ver vulnerabilidades en dependencias Rust
cargo audit

# Ver alertas activas en GitHub (requiere gh CLI)
gh api repos/jenovoas/sentinel/dependabot/alerts --jq '.[].security_advisory.summary'
```

---

## Glosario rápido

| Término | Significado simple |
|---------|-------------------|
| **CVE** | Número de identificación de una vulnerabilidad conocida (ej: CVE-2024-33664) |
| **Dependabot** | Bot de GitHub que revisa tus dependencias automáticamente |
| **Advisory** | Aviso oficial de seguridad sobre una librería |
| **No fix available** | El problema existe pero nadie ha sacado una versión que lo arregle todavía |
| **Unmaintained** | La librería está abandonada, nadie la mantiene ni saca parches |
| **Unsound (Rust)** | Código que viola las garantías de seguridad de memoria que Rust promete |
