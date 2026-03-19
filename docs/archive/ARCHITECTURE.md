# Dashboard Refactored - SOLID Architecture

## Estructura Modular

```
src/
├── app/dash-op/
│   └── page.tsx              # Main dashboard (thin, focused)
├── components/
│   ├── StorageCard.tsx       # Reusable storage stats card
│   └── DetailModal.tsx       # Modal with extensible content
├── hooks/
│   └── useAnalytics.ts       # Custom hook for analytics logic
├── lib/
│   ├── types.ts              # Shared type definitions
│   └── api.ts                # API service (data layer)
```

## Principios SOLID Aplicados

### 1. **Single Responsibility Principle (SRP)**
- **`AnalyticsAPI`**: Solo responsable de fetches de datos
- **`useAnalytics`**: Solo maneja estado y lógica de analytics
- **`StorageCard`**: Solo renderiza una tarjeta de almacenamiento
- **`DetailModal`**: Solo maneja la presentación del modal
- **`page.tsx`**: Solo orquesta componentes, no contiene lógica compleja

### 2. **Open/Closed Principle (OCP)**
- **`StorageCard`**: Abierta para extensión (props color personalizables)
- **`DetailModal`**: Abierta para agregar nuevos tipos sin modificar el código existente
- **`DetailContent`**: Switch extensible para nuevos tipos de detalle

```tsx
// Fácil agregar nuevo tipo sin modificar componente
case "newType":
  return <NewContent />;
```

### 3. **Liskov Substitution Principle (LSP)**
- Componentes siguen interfaces consistentes
- `StorageCard` siempre renderiza el mismo formato
- Los hooks retornan estructuras predecibles

### 4. **Interface Segregation Principle (ISP)**
- Componentes reciben solo props necesarios
- `StorageCard` no necesita conocer sobre anomalías
- `DetailModal` no depende de componentes innecesarios

```tsx
// StorageCard: minimal props
<StorageCard 
  label={string}
  value={ReactNode}
  onClick={() => void}
  color={colors}
/>
```

### 5. **Dependency Inversion Principle (DIP)**
- `page.tsx` depende de abstracciones (hooks, componentes)
- No depende de implementaciones concretas
- `AnalyticsAPI` abstrae los endpoints

```tsx
// page.tsx depende del hook, no de fetch directo
const { history, anomalies, storage } = useAnalytics();
```

## Ventajas de Esta Arquitectura

### 🔧 **Mantenibilidad**
- Cada archivo tiene una responsabilidad clara
- Cambios localizados, sin efectos secundarios

### 🧩 **Reutilizabilidad**
- `StorageCard` usable en otros dashboards
- `useAnalytics` usable en otros componentes
- `AnalyticsAPI` usable en cualquier contexto

### 📦 **Testabilidad**
- Hooks pueden ser testeados aisladamente
- Componentes son puros
- API service es mockeable

###  **Escalabilidad**
- Agregar nuevas tarjetas: copiar `StorageCard`
- Agregar nuevo modal: extender `DetailModal`
- Agregar fetch: agregar método en `AnalyticsAPI`

###  **Claridad**
- El flujo de datos es explícito
- Fácil ver qué depende de qué
- Nombres descriptivos

## Flujo de Datos

```
page.tsx (Orquestación)
    ↓
useAnalytics() (Lógica de estado)
    ↓
AnalyticsAPI (Fetches)
    ↓
Backend API

page.tsx
    ↓
<StorageCard /> (Presentación)
    ↓
<DetailModal /> (Presentación extendida)
```

## Ejemplo: Agregar Nueva Funcionalidad

### Agregar Nueva Tarjeta

1. **Sin refactorización**: Copiar 100+ líneas de código, modificar nombres, duplicar estilos

2. **Con refactorización**:
```tsx
<StorageCard
  label="New Metric"
  value={newValue}
  onClick={() => open("new")}
  color={{...}}
/>
```

### Agregar Nuevo Tipo de Detalle

1. **En `DetailModal.tsx`** - agregar case:
```tsx
case "newType":
  return <NewDetailContent {...} />;
```

2. **Eso es todo** - No necesitas tocar `page.tsx`

