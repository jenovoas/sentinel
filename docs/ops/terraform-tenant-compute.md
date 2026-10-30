# Terraform `tenant-compute` — VMs (contenedores) por tenant desde el portal

> Ejecuta `agente:iac`. Prerrequisitos: T1 (OUs, grupos `SP-VM-Server/Desktop`), T3 parcial (`/api/portal/deploy` operativo).
> Restricción física verificada 2026-10-30: **ni fenix ni kingu exponen `/dev/kvm`** (0 flags vmx/svm, VMs Azure sin anidado). No KVM/libvirt: contenedores Podman rootless aislados.

## 1. Módulo `modules/tenant-compute/`

Variables: `tenant_rut`, `tenant_subnet` (única por tenant, p. ej. `10.201.<n>.0/24`), `vm_type` (`server|desktop`), `cpu`, `ram_mb`, `disk_gb`, `admin_objectguid`.

Recursos por `apply` (un contenedor = un "servidor/escritorio" del cliente):

1. Red Podman dedicada `tn-<rut>` (aislamiento L3 por tenant; firewalld rich rules por subnet equivalen a NetworkPolicy).
2. Volumen disco con cuota (`disk_gb`).
3. Contenedor:
   - `server`: imagen mínima + SSH en puerto dedicado `22<nn>` (solo escucha en WG `10.88.0.0/24`, nunca público).
   - `desktop`: XFCE + xRDP (puerto interno) o noVNC; acceso solo vía Guacamole, sin puerto expuesto.
4. `node-exporter` sidecar o job → scrape en Marte (observabilidad por tenant).
5. Registro DNS interno del tenant + entrada en inventario (para Guacamole y monitoreo).

## 2. Guacamole automático (hoy es manual)

Al `apply`: crear conexión (SSH/RDP/VNC) por API de Guacamole y asignarla **solo** al `objectGUID` del usuario (grupo `SP-Guacamole-Remote` como condición previa). Al `destroy`/quitar grupo: revocar conexión + detener contenedor. Nunca conexiones huérfanas visibles a otros tenants.

**Gate de identidad:** la instancia actual combina LDAP + PostgreSQL y su ACL Guacamole se resuelve con nombres canónicos de usuario/grupo LDAP. No se ha validado que la API pueda autorizar directamente un `objectGUID`. Antes de implementar la línea anterior, probar y documentar la traducción `objectGUID` → UPN/grupo AD → entidad ACL Guacamole, incluido renombre, baja y grupos anidados. No escribir el GUID en `guacamole_entity` como si Guacamole lo asociara automáticamente. El modelo de protocolos, grupos y aislamiento está en [`guacamole-servicios-remotos-plan-2026-10-30.md`](guacamole-servicios-remotos-plan-2026-10-30.md).

## 3. Packs (vault `ESTRATEGIA_NEGOCIO_IA_SOBERANA` §5)

- *Pack Teletrabajo* = `SP-VPN-Access` + `SP-Guacamole-Remote` + 1× `vm-desktop`.
- *Pack Comercio* = Odoo + Chatwoot (cuando existan sus módulos) sobre 1× `vm-server`.
- *Nivel 1 IA* = `SP-AI-Node` + Ollama/`llama.cpp` (Llama 3.1 8B GGUF) en la VM del tenant, `:11434` solo por WireGuard. Sin GPU, $0 hardware adicional.

## 4. Límites y cuotas

- Cuotas en Postgres del portal (`tenants.max_vms/max_ram_mb/max_disk_gb`); el ejecutor Terraform rechaza `apply` que exceda.
- Un `apply` = un recurso facturable; registrar `deployment_request_id` (idempotency-key del endpoint) como tag.
- Imágenes pineadas por digest. `terraform plan` obligatorio antes de `apply`; estado remoto con lock (no local).

## 5. Criterios de aceptación

- `plan`+`apply` de un `vm-desktop` piloto crea red, contenedor, conexión Guacamole visible solo para su usuario, métricas en Marte.
- Usuario de otro tenant no ve la conexión ni alcanza la subnet (test de aislamiento L3 + API Guacamole).
- `destroy` deja cero restos (red, volumen, conexión, DNS).
