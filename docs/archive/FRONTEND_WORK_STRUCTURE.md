# Sentinel Frontend - Estructura de Trabajo

**Objetivo**: Implementación modular para delegar trabajo a diferentes personas

---

## 📋 Estructura General

```
sentinel/
├── frontend/                    # Next.js + React
│   ├── src/
│   │   ├── app/                # Pages (Next.js 14 App Router)
│   │   ├── components/         # React components
│   │   ├── lib/                # Utilities & helpers
│   │   └── store/              # Zustand state management
│   └── package.json
│
├── sentinel-wasm/              # Rust → WASM modules
│   ├── src/
│   │   └── lib.rs             # WASM functions
│   ├── Cargo.toml
│   └── pkg/                   # Built WASM (generated)
│
└── backend/                    # FastAPI (Python)
    └── app/
```

---

##  Módulos Independientes (Para Delegar)

### Módulo 1: WASM Performance Layer
**Responsable**: Developer con Rust
**Archivos**: `sentinel-wasm/`
**Tareas**:
- [ ] AIOpsDoom detection (✅ HECHO)
- [ ] Anomaly calculations
- [ ] Crypto operations (HMAC, signatures)
- [ ] Log parsing optimizado

**Interfaz definida**: `frontend/src/lib/wasm-loader.ts`

---

### Módulo 2: Design System
**Responsable**: Frontend Developer
**Archivos**: `frontend/src/lib/design-system.ts`
**Tareas**:
- [ ] Definir colores consistentes
- [ ] Definir spacing system
- [ ] Definir typography
- [ ] Crear theme tokens

**Output**: Sistema de diseño reutilizable

---

### Módulo 3: Estado Global (Zustand)
**Responsable**: Frontend Developer
**Archivos**: `frontend/src/store/`
**Tareas**:
- [ ] `sentinelStore.ts` - Estado principal
- [ ] `metricsStore.ts` - Métricas en tiempo real
- [ ] `securityStore.ts` - Alertas de seguridad
- [ ] `aiStore.ts` - AI insights

**Interfaz**: Hooks de Zustand

---

### Módulo 4: Componentes Unificados
**Responsable**: UI Developer
**Archivos**: `frontend/src/components/unified/`
**Tareas**:
- [ ] `UnifiedCard.tsx` - Card reutilizable
- [ ] `UnifiedChart.tsx` - Charts consistentes
- [ ] `UnifiedWidget.tsx` - Widgets modulares
- [ ] `UnifiedModal.tsx` - Modals estandarizados

**Basado en**: shadcn/ui + TailwindCSS

---

### Módulo 5: Real-time Provider
**Responsable**: Backend/Frontend Developer
**Archivos**: `frontend/src/components/providers/`
**Tareas**:
- [ ] `RealtimeProvider.tsx` - WebSocket/SSE
- [ ] Conexión con backend
- [ ] Auto-reconnect
- [ ] Event handling

**Integración**: FastAPI WebSocket

---

### Módulo 6: Command Palette
**Responsable**: UI Developer
**Archivos**: `frontend/src/components/CommandPalette.tsx`
**Tareas**:
- [ ] Cmd+K shortcut
- [ ] Búsqueda de páginas
- [ ] Acciones rápidas
- [ ] Navegación

**Inspiración**: VS Code Command Palette

---

### Módulo 7: Control Center Page
**Responsable**: Full-stack Developer
**Archivos**: `frontend/src/app/control-center/`
**Tareas**:
- [ ] Layout principal
- [ ] Integrar widgets existentes
- [ ] Drag-and-drop (opcional)
- [ ] Responsive design

**Dependencias**: Módulos 2, 3, 4

---

### Módulo 8: Analytics Page Enhancement
**Responsable**: Data Visualization Developer
**Archivos**: `frontend/src/app/analytics/`
**Tareas**:
- [ ] Gráficos interactivos (Recharts)
- [ ] Filtros de tiempo
- [ ] Export data (CSV/JSON)
- [ ] Comparación histórica

**Integración**: Backend API

---

## 📐 Interfaces Definidas

### 1. WASM Interface
```typescript
// frontend/src/lib/wasm-loader.ts
export interface TelemetryEvent {
  message: string;
  source: string;
  timestamp: number;
}

export function detectAIOpsD(message: string): boolean;
export function detectAIOpsDoomBatch(events: TelemetryEvent[]): boolean[];
export function calculateAnomalyScore(values: number[], threshold: number): number;
```

### 2. Store Interface
```typescript
// frontend/src/store/sentinelStore.ts
interface SentinelState {
  systemHealth: SystemHealth;
  metrics: MetricsData;
  aiInsights: AIInsight[];
  securityAlerts: SecurityAlert[];
}
```

### 3. Component Interface
```typescript
// frontend/src/components/unified/UnifiedCard.tsx
interface UnifiedCardProps {
  variant: 'metric' | 'ai' | 'security' | 'action';
  title: string;
  data: any;
  actions?: Action[];
}
```

---

## 🔄 Workflow de Integración

### 1. Developer trabaja en módulo independiente
```bash
# Ejemplo: Trabajar en WASM
cd sentinel-wasm
cargo build --release
wasm-pack build --target bundler
```

### 2. Prueba su módulo aisladamente
```bash
# Tests unitarios
cargo test

# Tests de integración
npm run test
```

### 3. Integra con interfaz definida
```typescript
// Usa la interfaz en wasm-loader.ts
import { detectAIOpsD } from '@/lib/wasm-loader';
```

### 4. Pull Request con documentación
- Código
- Tests
- Documentación de uso
- Ejemplos

---

## 📚 Documentación Requerida por Módulo

Cada módulo debe incluir:

### README.md
```markdown
# [Nombre del Módulo]

## Propósito
[Qué hace este módulo]

## Uso
[Ejemplos de código]

## API
[Funciones/componentes exportados]

## Tests
[Cómo ejecutar tests]

## Dependencias
[Qué otros módulos necesita]
```

### Ejemplos
```typescript
// examples/[modulo]-example.tsx
// Código de ejemplo funcional
```

### Tests
```typescript
// __tests__/[modulo].test.ts
// Tests unitarios
```

---

##  Prioridades de Implementación

### Fase 1: Fundamentos (Semana 1)
1. ✅ WASM Module (AIOpsDoom) - HECHO
2. Design System
3. Zustand Stores

### Fase 2: Componentes (Semana 2)
4. Componentes Unificados
5. Real-time Provider
6. Command Palette

### Fase 3: Pages (Semana 3)
7. Control Center
8. Analytics Enhancement

---

## 👥 Asignación Sugerida

### Developer 1 (Rust/WASM)
- Módulo 1: WASM Performance Layer
- Tiempo: 1 semana
- Entregable: 4 funciones WASM optimizadas

### Developer 2 (Frontend/Design)
- Módulo 2: Design System
- Módulo 4: Componentes Unificados
- Tiempo: 1.5 semanas
- Entregable: Sistema de diseño + 4 componentes

### Developer 3 (Frontend/State)
- Módulo 3: Estado Global
- Módulo 5: Real-time Provider
- Tiempo: 1 semana
- Entregable: 4 stores + WebSocket provider

### Developer 4 (Full-stack)
- Módulo 7: Control Center
- Módulo 8: Analytics
- Tiempo: 2 semanas
- Entregable: 2 páginas completas

### Developer 5 (UI/UX)
- Módulo 6: Command Palette
- Polish general
- Tiempo: 1 semana
- Entregable: Command Palette + mejoras UI

---

## ✅ Checklist de Entrega

Cada developer debe entregar:

- [ ] Código funcional
- [ ] Tests (coverage > 80%)
- [ ] Documentación (README.md)
- [ ] Ejemplos de uso
- [ ] TypeScript types completos
- [ ] Sin errores de linting
- [ ] Build exitoso

---

##  Cómo Empezar (Para Nuevos Developers)

### 1. Setup
```bash
git clone [repo]
cd sentinel

# Frontend
cd frontend
npm install

# WASM (si trabajas en Rust)
cd ../sentinel-wasm
cargo build
```

### 2. Elegir Módulo
Ver sección "Módulos Independientes"

### 3. Leer Interfaz
Ver `frontend/src/lib/` para interfaces definidas

### 4. Desarrollar
Trabajar en tu módulo aisladamente

### 5. Integrar
Usar las interfaces definidas

### 6. PR
Pull request con documentación

---

## 📊 Métricas de Éxito

- [ ] Todos los módulos tienen tests
- [ ] Coverage > 80%
- [ ] Build time < 30s
- [ ] Bundle size < 500KB
- [ ] Lighthouse score > 90
- [ ] Zero TypeScript errors

---

**Status**: ✅ Estructura definida  
**Listo para**: Asignar trabajo  
**Próximo paso**: Documentar módulo WASM completado
