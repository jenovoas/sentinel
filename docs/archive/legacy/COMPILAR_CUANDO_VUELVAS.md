#  Guía Rápida: Compilar eBPF LSM

**Cuando vuelvas de la batería, ejecuta esto:**

---

## ⚡ OPCIÓN 1: Script Automático (Recomendado)

```bash
cd /home/jnovoas/sentinel/ebpf
./compilar_ebpf.sh
```

Este script hace TODO automáticamente:
1. ✅ Instala toolchain (clang, llvm, bpftool)
2. ✅ Compila guardian_alpha_lsm.c
3. ✅ Verifica archivos generados
4. ✅ Documenta resultado en VALIDATION_LOG.md

**Tiempo**: 5-10 minutos (dependiendo de descarga de paquetes)

---

## ⚡ OPCIÓN 2: Manual (Paso a Paso)

### Paso 1: Instalar toolchain (2-3 min)
```bash
sudo pacman -S clang llvm bpf libbpf bpftool
```

### Paso 2: Compilar (1 min)
```bash
cd /home/jnovoas/sentinel/ebpf
make clean
make
```

### Paso 3: Verificar (30 seg)
```bash
ls -lh guardian_alpha_lsm.o
```

Si ves el archivo .o, ¡compiló exitosamente! ✅

---

##  SIGUIENTE PASO (Después de compilar)

### Cargar en kernel (requiere sudo)
```bash
sudo ./load.sh
```

O manualmente:
```bash
sudo bpftool prog load guardian_alpha_lsm.o /sys/fs/bpf/guardian
sudo bpftool prog list | grep guardian
```

---

## ⚠ Si Hay Errores

### Error: "clang: command not found"
**Solución**: Ejecuta `sudo pacman -S clang`

### Error: "bpf/libbpf.h: No such file"
**Solución**: Ejecuta `sudo pacman -S libbpf`

### Error: "Permission denied"
**Solución**: Usa `sudo` para cargar en kernel

### Error: "Invalid BPF program"
**Solución**: Verifica versión de kernel con `uname -r` (debe ser >5.7)

---

## ✅ Criterio de Éxito

Después de compilar, deberías ver:
```
✅ guardian_alpha_lsm.o generado (tamaño ~2-5 KB)
✅ Sin errores de compilación
✅ Listo para cargar en kernel
```

---

**Cuando vuelvas, ejecuta**: `./compilar_ebpf.sh` y listo! 

---

**Fecha**: 21 de Diciembre de 2025, 10:15 AM  
**Status**: ⏸ Esperando que vuelvas de la batería  
**Siguiente**: Ejecutar compilar_ebpf.sh
