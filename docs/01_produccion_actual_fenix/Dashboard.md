# 🔱 SENTINEL CORTEX - Dashboard

> [!info] **Status del Proyecto**
> Proyecto de arquitectura híbrida Rust/GPU/Bio. Sincronizado desde `~/dev/sentinel`.

---

## 🏛️ Núcleo del Sistema
| Documento | Descripción |
| --------- | ----------- |
| [[AI_PRIME_DIRECTIVES]] | Axiomas inmutables y reglas de seguridad. |
| [[ARCHITECTURE]] | Mapa de capas y diseño del sistema. |
| [[COGNITIVE_DESIGN]] | Lógica de la NPU Sumeria y Tetra-Logic. |
| [[CHECKLIST]] | Pasos críticos antes de cada despliegue. |

---

## 🕒 Actividad Reciente (Docs & Notas)
```dataview
TABLE file.mday as "Modificado"
FROM "Sentinel"
WHERE file.name != this.file.name
SORT file.mday DESC
LIMIT 10
```

---

## 🔬 Módulos y Código
- **Backend:** [[backend/README|Documentación del Backend]]
- **BCI:** [[bci/README|Brain-Computer Interface]]
- **Docker:** [[docker-compose.yml|Configuración de Orquestación]]

---

## 📋 Tareas Pendientes
```dataview
TASK FROM "Sentinel"
WHERE !completed
```