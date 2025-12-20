# Plan de Trabajo - 2 Contributors Nuevos

**Equipo**: 2 personas (principiantes)  
**Objetivo**: Onboarding productivo y aprendizaje gradual  
**Duración**: 2-4 semanas

---

## 👥 Asignación de Roles

### Persona 1: "Documentation Lead"
**Enfoque**: Documentación, ejemplos, guías

### Persona 2: "UI/Testing Lead"  
**Enfoque**: Componentes visuales, tests, estilos

---

## 📅 Plan Semanal

### Semana 1: Familiarización

#### Persona 1 - Tasks
**Día 1-2**: Setup y exploración
- [ ] Clonar repo y hacer setup
- [ ] Leer `README.md` completo
- [ ] Explorar estructura de carpetas
- [ ] Ejecutar `npm run dev` y ver el sistema

**Día 3-4**: Primera contribución
- [ ] **Tarea 1.1**: Mejorar `README.md`
  - Agregar sección "Quick Start"
  - Agregar troubleshooting común
  - Mejorar ejemplos de instalación

**Día 5**: Segunda contribución
- [ ] **Tarea 1.3**: Crear `examples/metric-card-example.tsx`
  - 3 ejemplos de uso del componente
  - Comentarios explicativos

**Entregable Semana 1**: 2 Pull Requests

---

#### Persona 2 - Tasks
**Día 1-2**: Setup y exploración
- [ ] Clonar repo y hacer setup
- [ ] Leer `CONTRIBUTING.md`
- [ ] Explorar componentes en `frontend/src/components/`
- [ ] Identificar componentes sin tests

**Día 3-4**: Primera contribución
- [ ] **Tarea 1.2**: Agregar comentarios a `StorageCard.tsx`
  - JSDoc para todas las funciones
  - Explicar props
  - Comentarios inline donde sea necesario

**Día 5**: Segunda contribución
- [ ] **Tarea 2.3**: Mejorar estilos de `WiFiCard.tsx`
  - Mejores colores
  - Hover effects
  - Animaciones suaves

**Entregable Semana 1**: 2 Pull Requests

---

### Semana 2: Contribuciones Reales

#### Persona 1 - Tasks
**Objetivo**: Crear documentación de componentes

- [ ] **Tarea A**: Documentar `MiniChart.tsx`
  - Props y tipos
  - Ejemplos de uso
  - Screenshots

- [ ] **Tarea B**: Crear guía "Cómo agregar un componente nuevo"
  - Template de componente
  - Checklist de pasos
  - Ejemplos

- [ ] **Tarea C**: Traducir `CONTRIBUTING.md` a español
  - `CONTRIBUTING.es.md`
  - Mantener formato

**Entregable Semana 2**: 3 Pull Requests

---

#### Persona 2 - Tasks
**Objetivo**: Tests y componente simple

- [ ] **Tarea A**: Tests para `StorageCard.tsx`
  - Setup testing library
  - 3-5 tests básicos
  - Documentar cómo correr tests

- [ ] **Tarea B**: Crear `LoadingSpinner.tsx`
  - Componente simple
  - Props: size, color
  - Animación CSS

- [ ] **Tarea C**: Tests para `LoadingSpinner.tsx`
  - Test de render
  - Test de props
  - Test de animación

**Entregable Semana 2**: 3 Pull Requests

---

### Semana 3-4: Proyectos Más Grandes

#### Persona 1 - Proyecto
**Crear página de documentación**

**Archivo**: `frontend/src/app/docs/page.tsx`

**Features**:
- Lista de todos los componentes
- Links a ejemplos
- Búsqueda simple
- Categorías (UI, Data, Layout)

**Tiempo**: 1-2 semanas

---

#### Persona 2 - Proyecto
**Crear biblioteca de componentes UI**

**Componentes a crear**:
1. `Button.tsx` (si no existe)
2. `Input.tsx`
3. `Select.tsx`
4. `Checkbox.tsx`

**Cada uno con**:
- TypeScript types
- Variantes (primary, secondary, etc.)
- Tests básicos
- Ejemplos de uso

**Tiempo**: 1-2 semanas

---

## 📊 Tracking de Progreso

### Checklist General

**Persona 1**:
- [ ] Semana 1: 2 PRs (Documentación)
- [ ] Semana 2: 3 PRs (Guías y ejemplos)
- [ ] Semana 3-4: Página de docs

**Persona 2**:
- [ ] Semana 1: 2 PRs (Comentarios y estilos)
- [ ] Semana 2: 3 PRs (Tests y componente)
- [ ] Semana 3-4: Biblioteca de componentes

---

## 🎯 Objetivos de Aprendizaje

### Persona 1 aprenderá:
- Git workflow (branches, PRs)
- Markdown y documentación técnica
- Estructura de proyectos React
- TypeScript básico
- Next.js routing

### Persona 2 aprenderá:
- React components
- TypeScript
- CSS/TailwindCSS
- Testing con Jest/Testing Library
- Component design patterns

---

## 📞 Comunicación

### Daily Standup (Async)
Cada persona reporta diariamente:
- ✅ Qué hice ayer
- 🎯 Qué haré hoy
- 🚧 Blockers

**Formato**: GitHub Discussion o Slack

### Code Review
- Tú revisas todos los PRs
- Feedback constructivo
- Aprobar cuando esté listo

### Weekly Sync
- 30 min cada viernes
- Revisar progreso
- Planear siguiente semana
- Resolver dudas

---

## 🚀 Quick Start para Cada Persona

### Persona 1: Setup
```bash
# 1. Fork y clone
git clone https://github.com/[tu-usuario]/sentinel.git
cd sentinel

# 2. Crear branch
git checkout -b docs/improve-readme

# 3. Hacer cambios
# Editar README.md

# 4. Commit y push
git add README.md
git commit -m "docs: improve README quick start section"
git push origin docs/improve-readme

# 5. Crear PR en GitHub
```

### Persona 2: Setup
```bash
# 1. Fork y clone
git clone https://github.com/[tu-usuario]/sentinel.git
cd sentinel/frontend

# 2. Install
npm install

# 3. Run dev server
npm run dev

# 4. Crear branch
git checkout -b feat/add-comments-storage-card

# 5. Hacer cambios y PR
```

---

## ✅ Criterios de Éxito

### Semana 1
- [ ] Ambos hicieron setup exitosamente
- [ ] Ambos crearon su primer PR
- [ ] Ambos entienden el workflow de Git

### Semana 2
- [ ] Ambos tienen 5+ PRs merged
- [ ] Ambos pueden trabajar independientemente
- [ ] Código de calidad aceptable

### Semana 3-4
- [ ] Proyectos grandes en progreso
- [ ] Menos supervisión necesaria
- [ ] Pueden ayudarse entre ellos

---

## 💡 Tips de Mentoría

### Para Ti
1. **Paciencia**: Son principiantes
2. **Feedback rápido**: Revisa PRs en <24h
3. **Celebra wins**: Cada PR merged es un logro
4. **Enseña, no hagas**: Guía, no resuelvas todo

### Para Ellos
1. **No tengan miedo**: Todos empezamos así
2. **Pregunten**: No hay preguntas tontas
3. **Lean código**: La mejor forma de aprender
4. **Experimenten**: El código no se rompe fácil

---

## 📚 Recursos Compartidos

### Para Ambos
- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Git Basics](https://git-scm.com/book/en/v2)

### Para Persona 1
- [Markdown Guide](https://www.markdownguide.org/)
- [Technical Writing](https://developers.google.com/tech-writing)

### Para Persona 2
- [Testing Library](https://testing-library.com/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)

---

## 🎉 Celebraciones

### Milestones
- 🥇 Primer PR merged
- 🥈 5 PRs merged
- 🥉 10 PRs merged
- 🏆 Proyecto grande completado

**Reconocimiento**: Agregar a `CONTRIBUTORS.md`

---

**¡Éxito con tu nuevo equipo!** 🚀
