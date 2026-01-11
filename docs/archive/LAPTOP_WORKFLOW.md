# ⚡ Workflow de Desarrollo en Laptop

## 🔋 Filosofía: Batería Primero

**Por defecto:** Todos los pods APAGADOS  
**Encender:** Solo cuando sea estrictamente necesario  
**Apagar:** Inmediatamente después de usar

---

## 📋 Workflows Comunes

### 1. Desarrollo de Código (Sin Servicios)
**Batería:** ✅ Mínimo consumo

```bash
# Solo editar código, no necesitas servicios
code .
# Trabajar normalmente en archivos Python/Rust/etc
```

**Cuándo usar:** 
- Escribir código nuevo
- Refactorización
- Documentación
- Lectura de código

---

### 2. Certificación TruthSync (Minimal)
**Batería:** ⚠️ Consumo moderado (~1.5GB RAM)

```bash
# 1. Encender solo DB
./scripts/pod-manager.sh start minimal

# 2. Certificar código
python3 quantum/certify_codebase.py

# 3. APAGAR INMEDIATAMENTE
./scripts/pod-manager.sh stop
```

**Duración recomendada:** 5-10 minutos máximo

---

### 3. Testing de APIs (Backend)
**Batería:** 🔥 Consumo alto (~3.5GB RAM)

```bash
# 1. Encender backend
./scripts/pod-manager.sh start backend

# 2. Probar APIs
curl http://localhost:8000/health
# Hacer tus pruebas

# 3. APAGAR INMEDIATAMENTE
./scripts/pod-manager.sh stop
```

**Duración recomendada:** 15-20 minutos máximo

---

### 4. Debugging Full Stack (Full)
**Batería:** 🔥🔥🔥 Consumo crítico (~8GB RAM)

```bash
# ⚠️ SOLO USAR CONECTADO A CORRIENTE

# 1. Encender full stack
./scripts/pod-manager.sh start full

# 2. Debugging/testing
# Grafana: http://localhost:3001
# n8n: http://localhost:5678

# 3. APAGAR INMEDIATAMENTE
./scripts/pod-manager.sh stop
```

**Duración recomendada:** Solo con laptop enchufado

---

## 🎯 Reglas de Oro para Laptop

### ✅ HACER
- Apagar servicios inmediatamente después de usar
- Usar `minimal` para tareas rápidas
- Monitorear batería con `./scripts/pod-manager.sh stats`
- Trabajar sin servicios siempre que sea posible

### ❌ NO HACER
- Dejar servicios corriendo en background
- Usar perfil `full` con batería
- Olvidar apagar después de usar
- Iniciar servicios "por si acaso"

---

## 📊 Verificación Rápida

### ¿Hay algo corriendo?
```bash
podman ps
# Si sale vacío = ✅ Todo apagado
# Si sale algo = ⚠️ Apagar con: ./scripts/pod-manager.sh stop
```

### ¿Cuánto consume?
```bash
./scripts/pod-manager.sh stats
```

---

## 🔧 Comandos Rápidos

```bash
# Ver estado (sin encender nada)
podman ps

# Encender minimal
./scripts/pod-manager.sh start minimal

# Apagar TODO
./scripts/pod-manager.sh stop

# Ver logs (si algo está corriendo)
./scripts/pod-manager.sh logs sentinel-postgres
```

---

## 💡 Tips de Batería

1. **Desarrollo sin servicios:** 90% del tiempo no necesitas pods corriendo
2. **Tests unitarios:** Corren sin necesidad de PostgreSQL/Redis
3. **Certificación:** Solo encender `minimal` cuando vayas a certificar
4. **APIs:** Solo encender `backend` cuando necesites probar endpoints
5. **Siempre apagar:** Nunca dejes servicios corriendo al cerrar laptop

---

## 🚨 Checklist Antes de Cerrar Laptop

```bash
# 1. Verificar que no hay nada corriendo
podman ps

# 2. Si hay algo, apagar
./scripts/pod-manager.sh stop

# 3. Verificar de nuevo
podman ps
# Debe estar vacío

# 4. Cerrar laptop tranquilo ✅
```

---

## 📝 Resumen

**Estado por defecto:** TODO APAGADO  
**Encender:** Solo cuando necesites  
**Apagar:** Inmediatamente después  
**Verificar:** `podman ps` antes de cerrar laptop
