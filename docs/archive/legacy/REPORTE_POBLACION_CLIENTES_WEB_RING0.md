# 🌐 Reporte de Población de Aplicaciones Web de Clientes en Whitelist eBPF Ring-0
> ⚠️ **FAN (157.254.174.40) DECOMISIONADO 2026-08-28** — Este es un reporte histórico que menciona `fan`. Producción actual `kingu` (68.211.176.190:4222), desarrollo `fenix` (20.226.112.222). No usar `fan` como target.


> **Servidor:** Fan (`10.88.0.1`)  
> **Servicio Auditado:** `laespiguita_web` (`bakery-api.service`)  
> **Mapas BPF Target:** `whitelist_map` (ID 25 y ID 48)  
> **Fecha:** 29 de Julio, 2026  
> **Estado:** 🟢 **AÑADIDAS Y INMUNIZADAS EN RING-0 CON ÉXITO**

---

## 🔬 Rutas Absolutas Inyectadas para Servicios Web de Clientes

Agregamos los binarios y motores del stack de clientes a ambos mapas de kernel (`whitelist_map` ID 25 y ID 48):

```text
1. /home/jnovoas/laespiguita_web/services/target/release/bakery-api
2. /usr/bin/postgres
3. /usr/libexec/postgres
4. /usr/bin/nginx
```

---

## 🛡️ Garantía de Continuidad de Operaciones:
Con la adición de `bakery-api` y los motores de base de datos/web (`postgres`, `nginx`) a las listas blancas del Ring-0, **las aplicaciones web de clientes quedan 100% protegidas e inmunizadas** contra intercepciones accidentales o bloqueos de ejecución una vez que Sentinel active el enforzamiento estricto.
