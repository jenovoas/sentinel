# Sentinel - Guía para Nuevos Contributors

**Bienvenido al equipo Sentinel!** 🎉

Esta guía te ayudará a empezar a contribuir, sin importar tu nivel de experiencia.

---

## 🎯 Niveles de Contribución

### Nivel 1: Principiante (No requiere experiencia)
**Tiempo estimado**: 1-2 horas por tarea

### Nivel 2: Intermedio (Conocimientos básicos)
**Tiempo estimado**: 3-5 horas por tarea

### Nivel 3: Avanzado (Experiencia en desarrollo)
**Tiempo estimado**: 1-2 días por tarea

---

## 📋 Tareas Nivel 1 (Principiantes)

### Tarea 1.1: Mejorar Documentación
**Objetivo**: Agregar ejemplos y aclaraciones a README.md

**Pasos**:
1. Lee `README.md`
2. Identifica secciones confusas
3. Agrega ejemplos o aclaraciones
4. Crea Pull Request

**Ejemplo**:
```markdown
# Antes
## Installation
Run `npm install`

# Después
## Installation
1. Asegúrate de tener Node.js 18+ instalado
2. Clona el repositorio: `git clone ...`
3. Instala dependencias: `npm install`
4. Verifica instalación: `npm run dev`
```

**Archivos**: `README.md`, `frontend/README.md`, `backend/README.md`

---

### Tarea 1.2: Agregar Comentarios al Código
**Objetivo**: Documentar funciones existentes

**Pasos**:
1. Elige un archivo de `frontend/src/components/`
2. Agrega comentarios JSDoc a funciones
3. Explica qué hace cada parámetro
4. Crea Pull Request

**Ejemplo**:
```typescript
// Antes
function MetricCard({ metric }) {
  return <div>...</div>
}

// Después
/**
 * Muestra una tarjeta con información de una métrica
 * @param {Object} metric - Datos de la métrica
 * @param {string} metric.name - Nombre de la métrica
 * @param {number} metric.value - Valor actual
 * @param {string} metric.unit - Unidad de medida (ej: "ms", "%")
 * @returns {JSX.Element} Componente de tarjeta de métrica
 */
function MetricCard({ metric }) {
  return <div>...</div>
}
```

**Archivos sugeridos**:
- `frontend/src/components/MiniChart.tsx`
- `frontend/src/components/StorageCard.tsx`
- `frontend/src/components/WiFiCard.tsx`

---

### Tarea 1.3: Crear Ejemplos de Uso
**Objetivo**: Documentar cómo usar componentes

**Pasos**:
1. Elige un componente
2. Crea archivo `examples/[componente]-example.tsx`
3. Muestra 2-3 casos de uso
4. Crea Pull Request

**Ejemplo**:
```typescript
// examples/metric-card-example.tsx
import { MetricCard } from '@/components/MetricCard';

// Ejemplo 1: Métrica de CPU
<MetricCard 
  metric={{
    name: "CPU Usage",
    value: 45.2,
    unit: "%"
  }}
/>

// Ejemplo 2: Métrica de memoria
<MetricCard 
  metric={{
    name: "Memory",
    value: 2048,
    unit: "MB"
  }}
/>
```

---

### Tarea 1.4: Traducir Documentación
**Objetivo**: Hacer documentación accesible en español

**Pasos**:
1. Copia `README.md` a `README.es.md`
2. Traduce sección por sección
3. Mantén código sin traducir
4. Crea Pull Request

**Archivos**: Cualquier `.md` en el repo

---

### Tarea 1.5: Reportar Bugs con Detalle
**Objetivo**: Ayudar a identificar problemas

**Template**:
```markdown
## Bug Report

**Descripción**: [Qué pasó]

**Pasos para reproducir**:
1. Ir a ...
2. Hacer click en ...
3. Ver error ...

**Comportamiento esperado**: [Qué debería pasar]

**Screenshots**: [Si aplica]

**Ambiente**:
- OS: [ej: Ubuntu 22.04]
- Browser: [ej: Chrome 120]
- Node: [ej: 18.17.0]
```

---

## 📋 Tareas Nivel 2 (Intermedios)

### Tarea 2.1: Crear Componente Simple
**Objetivo**: Componente de loading spinner

**Requisitos**:
- Mostrar spinner animado
- Prop para tamaño (small, medium, large)
- Prop para color
- TypeScript types

**Archivo**: `frontend/src/components/LoadingSpinner.tsx`

**Ejemplo**:
```typescript
interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
}

export function LoadingSpinner({ size = 'medium', color = 'cyan' }: LoadingSpinnerProps) {
  // TODO: Implementar
}
```

---

### Tarea 2.2: Agregar Tests Básicos
**Objetivo**: Tests para componentes existentes

**Pasos**:
1. Instalar `@testing-library/react`
2. Crear `[componente].test.tsx`
3. Testear render básico
4. Testear props

**Ejemplo**:
```typescript
// MetricCard.test.tsx
import { render, screen } from '@testing-library/react';
import { MetricCard } from './MetricCard';

test('renders metric name', () => {
  render(<MetricCard metric={{ name: 'CPU', value: 50, unit: '%' }} />);
  expect(screen.getByText('CPU')).toBeInTheDocument();
});

test('renders metric value', () => {
  render(<MetricCard metric={{ name: 'CPU', value: 50, unit: '%' }} />);
  expect(screen.getByText('50')).toBeInTheDocument();
});
```

---

### Tarea 2.3: Mejorar Estilos CSS
**Objetivo**: Hacer componentes más bonitos

**Pasos**:
1. Elige un componente
2. Mejora colores, espaciado, animaciones
3. Mantén consistencia con design system
4. Crea Pull Request

**Componentes sugeridos**:
- `StorageCard.tsx` - Agregar gradientes
- `WiFiCard.tsx` - Mejorar iconos
- `MiniChart.tsx` - Animaciones suaves

---

### Tarea 2.4: Crear Página de Documentación
**Objetivo**: Página `/docs` con guías

**Pasos**:
1. Crear `frontend/src/app/docs/page.tsx`
2. Listar todas las guías disponibles
3. Links a documentación
4. Búsqueda simple

---

### Tarea 2.5: Agregar Validación de Forms
**Objetivo**: Validar inputs de usuario

**Ejemplo**:
```typescript
function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

function validatePort(port: string): boolean {
  const num = parseInt(port);
  return num >= 1 && num <= 65535;
}
```

---

## 📋 Tareas Nivel 3 (Avanzados)

### Tarea 3.1: Implementar Design System
**Objetivo**: Sistema de diseño unificado

**Ver**: `FRONTEND_WORK_STRUCTURE.md` - Módulo 2

---

### Tarea 3.2: Estado Global con Zustand
**Objetivo**: Stores para métricas, seguridad, AI

**Ver**: `FRONTEND_WORK_STRUCTURE.md` - Módulo 3

---

### Tarea 3.3: Real-time Provider
**Objetivo**: WebSocket/SSE para datos en tiempo real

**Ver**: `FRONTEND_WORK_STRUCTURE.md` - Módulo 5

---

## 🚀 Cómo Empezar

### 1. Setup Inicial
```bash
# Clonar repo
git clone https://github.com/jenovoas/sentinel.git
cd sentinel

# Frontend
cd frontend
npm install
npm run dev

# Backend (opcional)
cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Elegir Tarea
- Nivel 1: No requiere programar
- Nivel 2: Programación básica
- Nivel 3: Experiencia requerida

### 3. Crear Branch
```bash
git checkout -b feature/tu-nombre-tarea
```

### 4. Hacer Cambios
- Sigue las guías de estilo
- Agrega comentarios
- Testea localmente

### 5. Pull Request
```bash
git add .
git commit -m "feat: descripción clara"
git push origin feature/tu-nombre-tarea
```

Luego crea PR en GitHub con:
- Descripción de cambios
- Screenshots (si aplica)
- Checklist de testing

---

## ✅ Checklist de PR

Antes de crear Pull Request:

- [ ] Código funciona localmente
- [ ] Sin errores en consola
- [ ] Comentarios agregados
- [ ] README actualizado (si aplica)
- [ ] Tests pasan (si aplica)
- [ ] Screenshots incluidos (si es UI)

---

## 💡 Tips para Principiantes

### 1. Empieza Pequeño
- No intentes tareas grandes al inicio
- Completa 2-3 tareas Nivel 1 primero
- Familiarízate con el código

### 2. Pregunta
- Usa GitHub Discussions
- Crea issues para dudas
- Pide code review

### 3. Aprende del Código
- Lee código existente
- Copia patrones que veas
- Pregunta por qué se hace algo

### 4. Documenta Todo
- Agrega comentarios
- Actualiza README
- Crea ejemplos

---

## 📚 Recursos de Aprendizaje

### React + TypeScript
- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Next.js
- [Next.js Tutorial](https://nextjs.org/learn)

### Git
- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)

### Testing
- [Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

---

## 🎯 Progresión Sugerida

### Semana 1-2: Nivel 1
- Tarea 1.1: Documentación
- Tarea 1.2: Comentarios
- Tarea 1.3: Ejemplos

### Semana 3-4: Nivel 2
- Tarea 2.1: Componente simple
- Tarea 2.2: Tests básicos

### Mes 2+: Nivel 3
- Elegir módulo de `FRONTEND_WORK_STRUCTURE.md`
- Implementar feature completa

---

## 🏆 Reconocimiento

Contributors destacados:
- Aparecen en README.md
- Crédito en releases
- Posibilidad de rol de maintainer

---

## 📞 Contacto

- **GitHub Issues**: Para bugs y features
- **GitHub Discussions**: Para preguntas
- **Email**: [tu-email] (para temas urgentes)

---

**¡Gracias por contribuir a Sentinel!** 🚀

Tu ayuda hace la diferencia, sin importar tu nivel de experiencia.
