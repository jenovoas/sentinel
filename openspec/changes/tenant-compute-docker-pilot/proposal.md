# Proposal

## Why

T4 tiene preparación local parcial: el módulo Docker, el preflight y el aprovisionador de imagen ext4 loop están escritos. Una imagen temporal real y la unidad systemd generada se validaron localmente, pero no se ha probado montaje, cuota por llenado o persistencia en VM; Terraform/OpenTofu no están instalados y el módulo no se validó. No existe runner operativo y el checkout no declara backend remoto; el inventario fuera del repositorio sigue pendiente. El piloto temporal en Kingu debe usar los recursos actuales, pero no puede aplicarse hasta demostrar aislamiento por tenant y una cuota de disco realmente dura. La plantilla inicial se aplaza por decisión del dueño y no se habilitará una carga por inferencia.

## What Changes

- Añadir la capacidad de aprovisionar cómputo Docker aislado por tenant mediante IaC y un ejecutor separado del proceso web.
- Exigir límites verificables de CPU y memoria, almacenamiento persistente con cuota dura y ausencia de puertos públicos.
- Rechazar el `apply` si el host no demuestra los controles requeridos o si falta autorización operativa.
- Mantener el piloto de La Espiguita en Kingu con recursos actuales; evaluar ampliación o segundo host solo cuando existan clientes reales.
- No declarar DNS, métricas, inventario ni ACL Guacamole integrados hasta probar sus interfaces reales.

## Capabilities

### New Capabilities
- `tenant-compute-provisioning`: Aprovisionamiento Docker aislado, con cuotas duras y ciclo de vida limitado al tenant autorizado.

### Modified Capabilities

## Impact

Afecta el módulo `modules/tenant-compute/`, el runner de despliegue, sus pruebas y la documentación contractual de T4. Requiere Terraform y Docker; no modifica servicios activos ni ejecuta recursos durante esta fase local. El `apply` permanece bloqueado mientras no haya identidad piloto y cuota dura compatible demostrada.