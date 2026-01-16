# MycNet: Adaptación 4 Nodos (PCs)

## Cambios Realizados

### ✅ Scripts Actualizados
- [x] `minio_deploy.sh` - Cambiado de 6 a 4 nodos
- [x] `mesh_setup.sh` - Compatible con 4-6+ nodos
- [x] `mycnet_s60_monitor.py` - Compatible con cualquier número de nodos

### ✅ Documentación Creada
- [x] `4_NODE_QUICKSTART.md` - Guía completa de instalación
- [x] `README.md` - Actualizado con specs de PCs

### ✅ Configuración Ajustada

**Topología 4 nodos**:
```
n1 ---- n2
|  \  /  |
|   \/   |
|   /\   |
|  /  \  |
n3 ---- n4
```

**MinIO EC**: 2+2 (tolera 2 nodos muertos)

**Costo total**: $30-40 USD (switch + cables)

---

## Próximos Pasos

1. ⏸️ Instalar Ubuntu Server 22.04 en 4 PCs
2. ⏸️ Configurar red (IPs estáticas)
3. ⏸️ Ejecutar `mesh_setup.sh` en cada nodo
4. ⏸️ Ejecutar `minio_deploy.sh` en todos
5. ⏸️ Correr pruebas de resiliencia
6. ⏸️ Generar reporte con métricas S60

---

## Escalado Futuro

Cuando consigas más PCs (6-8):
- Agregar nodos nuevos (auto-discovery)
- Actualizar MinIO a 6+ nodos
- Migrar a Ceph (replicación 3x)
