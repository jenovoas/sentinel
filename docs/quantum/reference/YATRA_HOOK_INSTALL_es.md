# 🛡️ Guía de Instalación: Hook Pre-Commit YatraGuard

## Instalación Automática (Recomendada)

```bash
cd /home/jnovoas/dev/sentinel
python3 quantum/install_yatra_hook.py
```

El script instalador:
- ✅ Copia `yatra_guard_precommit.py` a `.git/hooks/pre-commit`
- ✅ Lo hace ejecutable automáticamente
- ✅ Crea backup del hook anterior si existe

## Instalación Manual

```bash
cp quantum/yatra_guard_precommit.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Funcionamiento

El hook se ejecuta **automáticamente** antes de cada commit y:

1. 🔍 Detecta archivos protegidos en el *staging area*
2. 🛡️ Valida cada archivo con YatraGuard
3. ✅ Aprueba el commit si todos los archivos son puros
4. 🚫 **BLOQUEA** el commit si detecta:
   - `import math` (excepto `yatra_math`)
   - `import random`, `numpy`, `scipy`, `matplotlib`
   - Literales float (excepto `0.0` y `1.0`)
   - Llamadas a `.to_float()`

## Uso

### Commit Normal
```bash
git add quantum/yatra_core.py
git commit -m "Refactor: mejorar S60"
# El hook se ejecuta automáticamente
```

### Bypass Temporal (NO RECOMENDADO)
```bash
git commit --no-verify -m "WIP: trabajo en progreso"
```

## Desinstalación

```bash
rm .git/hooks/pre-commit
# O restaurar backup
mv .git/hooks/pre-commit.backup .git/hooks/pre-commit
```

## Ejemplo de Salida

### ✅ Commit Aprobado
```
🛡️ YATRA-GUARD PRE-COMMIT VALIDATION
============================================================

📋 Validando 1 archivo(s) protegido(s)...

🔍 Verificando: quantum/yatra_core.py
   ✅ PURO

============================================================
✅ COMMIT APROBADO: Pureza Yatra verificada
```

### 🚫 Commit Bloqueado
```
🛡️ YATRA-GUARD PRE-COMMIT VALIDATION
============================================================

📋 Validando 1 archivo(s) protegido(s)...

🔍 Verificando: quantum/yatra_core.py
   🚨 CONTAMINACIÓN: quantum/yatra_core.py
      Línea 25: 'import math' prohibido (usa yatra_math).
   ❌ VIOLACIÓN DETECTADA

============================================================
🚫 COMMIT BLOQUEADO: 1 violación(es) Yatra detectada(s)

Para corregir:
1. Elimina floats y reemplaza con S60
2. Elimina import math/random/numpy (usa yatra_math)
3. Elimina llamadas a .to_float()

O usa: git commit --no-verify (NO RECOMENDADO)
```

## Archivos Protegidos

El hook protege todos los archivos listados en `YatraGuard.PROTECTED_FILES`:
- `quantum/yatra_core.py`
- `quantum/yatra_math.py`
- `quantum/core_simulator.py`
- `quantum/sentinel_quantum_core.py`
- Y más... (ver `yatra_guard.py` para lista completa)

## Solución de Problemas

### "No se pudo obtener archivos staged"
- Verifica que estás en un repositorio git
- Asegúrate de tener archivos en staging: `git status`

### "ModuleNotFoundError: No module named 'quantum'"
- El hook necesita ejecutarse desde la raíz del repo
- Verifica que `quantum/yatra_guard.py` existe

### El hook no se ejecuta
- Verifica permisos: `ls -l .git/hooks/pre-commit`
- Debe ser ejecutable: `chmod +x .git/hooks/pre-commit`