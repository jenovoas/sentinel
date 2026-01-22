# 🎨 AGENTE FRONTEND: VISUALIZACIÓN E INTERFAZ

> **CONTEXTO:** Este directorio (`/frontend`) es la cara del sistema hacia el Operador Humano.

## 1. 🛡️ DIRECTIVAS CRÍTICAS

### 👁️ VISUALIZACIÓN S60
- **DATOS:** Recibes datos S60 del backend.
- **DISPLAY:** Intenta mostrar el formato S60 (ej: `01:30:00`) en lugar de convertir a decimal (`1.5`), a menos que sea una gráfica estándar que requiera float (en cuyo caso, la conversión es SOLO visual).
- **LÓGICA:** EL FRONTEND NO PIENSA. Solo muestra. No recalcules física aquí.

### 🎨 DISEÑO Y UX
- **Estilo:** Moderno, limpio, "Sci-Fi Industrial" (conforme a `BRAND_GUIDE.md` si existe).
- **Responsive:** Debe funcionar en el dashboard del operador.

## 2. ⚙️ REGLAS TÉCNICAS (Next.js)

1. **Framework:** Next.js + Tailwind CSS.
2. **Estado:** React Query o similar para manejo de estado de servidor.
3. **Performance:** Carga rápida. El dashboard es de misión crítica.
4. **Wasm:** Permitido SOLO para visualización avanzada, nunca para lógica de negocio.

## 3. 📂 MAPA DE CONOCIMIENTO

- **Componentes:** `src/components/`
- **Páginas:** `src/app/` o `src/pages/`
- **Estilos:** `tailwind.config.js`

---
**OBJETIVO:** Claridad total. El operador debe entender el estado del sistema en < 1 segundo.
