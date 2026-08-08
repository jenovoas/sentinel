# 👋 Bienvenido a Sentinel - Guía para Nuevos Desarrolladores

**¡Hola! No te asustes.** 😊

Sí, hay 913,087 líneas de código y 145+ documentos. Pero no necesitas leerlo todo.

---

##  Empieza Aquí (5 minutos)

### Lo Básico
Sentinel es un sistema de monitoreo con IA que detecta ataques y optimiza rendimiento.

**Stack**:
- **Backend**: Python + FastAPI
- **Frontend**: TypeScript + Next.js
- **Base de datos**: PostgreSQL + Redis
- **Logs**: Loki

**Eso es todo lo que necesitas saber para empezar.**

---

## 📁 Estructura Simplificada

```
sentinel/
├── backend/          # API en Python (aquí trabajarás 80% del tiempo)
├── frontend/         # Dashboard en React/Next.js
├── tests/            # Tests (11 archivos, todos pasan)
└── docs/
    ├── proven/       # ✅ Código que funciona
    └── research/     # 🔬 Ideas teóricas (ignora por ahora)
```

---

##  Setup Rápido (15 minutos)

```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Base de datos
docker-compose up -d

# 3. Ejecutar
python -m uvicorn app.main:app --reload

# 4. Ver en navegador
http://localhost:8000
```

**¿Funcionó?** ✅ Estás listo.

---

## 📚 Documentos Importantes (solo estos)

### Para Empezar
1. **README.md** - Overview del proyecto
2. **CONTRIBUTING.md** - Cómo contribuir
3. **backend/README.md** - API docs

### Si Tienes Curiosidad
4. **docs/proven/BENCHMARKS_VALIDADOS.md** - Qué tan rápido es
5. **docs/proven/AIOPS_SHIELD.md** - Cómo detectamos ataques

### Ignora Por Ahora
- ❌ Todo en `docs/research/` (teoría, no código)
- ❌ Documentos con "VISION" o "PLANETARY" en el nombre
- ❌ Cualquier cosa que mencione "resonancia" o "háptica"

---

##  Tu Primera Tarea (30 minutos)

### Opción 1: Backend
```bash
cd backend
python test_dual_lane.py
```
**Objetivo**: Ver que los tests pasan. Luego lee el código del test.

### Opción 2: Frontend
```bash
cd frontend
npm install
npm run dev
```
**Objetivo**: Ver el dashboard funcionando.

### Opción 3: Explorar
```bash
cd backend/app/services
ls -la
```
**Objetivo**: Ver los servicios principales. Empieza por `aiops_shield.py`.

---

## 💡 Preguntas Frecuentes

### "¿Qué es AIOpsDoom?"
Un tipo de ataque donde inyectan comandos maliciosos en logs para engañar a la IA.

### "¿Qué es TruthSync?"
Un sistema que verifica si la información es verdadera o falsa. Es 90x más rápido que la versión anterior.

### "¿Qué es eBPF?"
Código que corre en el kernel de Linux. Es avanzado, no te preocupes por ahora.

### "¿Qué es Planetary Resonance?"
Una idea teórica. **Ignórala completamente** por ahora.

### "¿Por qué hay tantos documentos?"
Porque el creador documenta TODO. Solo lee los que necesites.

---

## 🆘 Si Te Pierdes

### Paso 1: Respira
No necesitas entender todo. Nadie lo entiende todo.

### Paso 2: Pregunta
- Slack: [[sentinel-dev]]
- Email: jaime.novoase@gmail.com
- Issues: GitHub

### Paso 3: Enfócate
Elige UNA cosa:
- Backend API
- Frontend UI
- Tests
- Documentación

---

## 🎓 Niveles de Conocimiento

### Nivel 1: Junior (Tú estás aquí)
- ✅ Ejecutar el proyecto
- ✅ Leer código de servicios
- ✅ Ejecutar tests
- ✅ Hacer cambios pequeños

**Tiempo**: 1-2 semanas

### Nivel 2: Intermedio
- ✅ Entender arquitectura completa
- ✅ Agregar nuevos servicios
- ✅ Optimizar rendimiento
- ✅ Escribir tests

**Tiempo**: 1-2 meses

### Nivel 3: Avanzado
- ✅ Entender eBPF
- ✅ Modificar kernel modules
- ✅ Diseñar nuevas features
- ✅ Revisar código de otros

**Tiempo**: 3-6 meses

### Nivel 4: Arquitecto (Jaime)
- ✅ Entender TODO
- ✅ Visión completa
- ✅ Decisiones de arquitectura
- ✅ Teorías locas en docs/research/

**Tiempo**: Años

---

##  Tu Objetivo (Primeras 2 Semanas)

1. ✅ Ejecutar el proyecto localmente
2. ✅ Entender backend/app/services/
3. ✅ Hacer tu primer PR (fix typo, mejorar docs, etc.)
4. ✅ Ejecutar y entender 1-2 tests

**Eso es TODO.**

No necesitas:
- ❌ Leer 145 documentos
- ❌ Entender eBPF
- ❌ Saber qué es "Planetary Resonance"
- ❌ Leer teorías en docs/research/

---

##  Siguiente Paso

**Ahora mismo**:
```bash
cd /home/jnovoas/sentinel/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test_dual_lane.py
```

**Si funciona**: ✅ Estás listo para trabajar.  
**Si no funciona**: 🆘 Pide ayuda en Slack.

---

##  Mensaje Final

**No te asustes por el tamaño del proyecto.**

Todos empezamos sin entender nada. Es normal.

Enfócate en UNA cosa a la vez. Pregunta cuando te pierdas.

**Bienvenido al equipo.** 🎉

---

**Creado**: 21 de Diciembre de 2025  
**Para**: Nuevos desarrolladores que no quieren salir corriendo 😂  
**Actualizado**: Cuando sea necesario
