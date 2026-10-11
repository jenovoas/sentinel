# 🤖 Configuración de Proveedores de IA - Sentinel TUI

## Proveedores Disponibles

Sentinel TUI soporta múltiples proveedores de IA:

1. **Ollama** (Local, GPU-enabled) - Por defecto
2. **Antigravity** (Google AI Studio / Gemini) - Remoto

---

## 🔧 Configuración

### Opción 1: Ollama Local (Por Defecto)

**Sin configuración adicional** - Usa el modelo local `llama3.2:3b`

```bash
# Simplemente ejecuta:
./sentinel_tui.py
```

**Modelos disponibles:**
- `llama3.2:3b` (2GB) - Por defecto
- `phi3:mini` (2.2GB) - Más rápido
- `qwen2.5-coder:3b` (1.9GB) - Especializado en código

---

### Opción 2: Antigravity (Google Gemini)

#### A. Con API Key de Google AI Studio

1. **Obtén tu API Key:**
   - Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Crea una API key

2. **Configura las variables de entorno:**

```bash
# En ~/.bashrc o ~/.zshrc:
export SENTINEL_AI_PROVIDER="antigravity"
export GOOGLE_AI_API_KEY="tu-api-key-aqui"
export ANTIGRAVITY_MODEL="gemini-1.5-flash"  # Opcional
```

3. **Ejecuta el TUI:**

```bash
source ~/.bashrc  # Recargar variables
./sentinel_tui.py
```

#### B. Con HTTP Basic Auth (Antigravity Proxy)

Si tienes un proxy de Antigravity con autenticación HTTP:

```bash
# En ~/.bashrc o ~/.zshrc:
export SENTINEL_AI_PROVIDER="antigravity"
export ANTIGRAVITY_URL="https://tu-proxy.com"
export ANTIGRAVITY_USERNAME="tu-usuario"
export ANTIGRAVITY_PASSWORD="tu-password"
export ANTIGRAVITY_MODEL="gemini-1.5-flash"
```

---

## 🎯 Modelos de Gemini Disponibles

| Modelo | Descripción | Velocidad | Capacidad |
|--------|-------------|-----------|-----------|
| `gemini-1.5-flash` | Rápido y eficiente | ⚡⚡⚡ | 🧠🧠 |
| `gemini-1.5-pro` | Más capaz | ⚡⚡ | 🧠🧠🧠 |
| `gemini-pro` | Balanceado | ⚡⚡ | 🧠🧠 |

**Recomendado**: `gemini-1.5-flash` (rápido y gratis con límites)

---

## 🛡️ Seguridad con Antigravity

### Capas de Seguridad Aplicadas:

✅ **TruthSync Verification** - Todas las respuestas verificadas con Base-60  
✅ **Conversation Tracking** - Todo registrado con timestamps  
✅ **Metadata Tagging** - Provider, modelo, y threat level  
✅ **History Persistence** - Guardado en `~/.sentinel/tui_history.json`  

### Lo que Google Maneja:

- Input sanitization
- Content filtering
- Rate limiting (según tu plan)
- Safety settings

---

## 📊 Comparación de Proveedores

| Característica | Ollama | Antigravity |
|----------------|--------|-------------|
| **Velocidad** | Depende de GPU | Rápido (cloud) |
| **Privacidad** | 100% local | Datos a Google |
| **Costo** | Gratis | Gratis con límites |
| **Capacidad** | Limitada (3B params) | Alta (Gemini) |
| **Offline** | ✅ Sí | ❌ No |
| **TruthSync** | ✅ Sí | ✅ Sí |
| **AIOpsShield** | ✅ Sí | ❌ No (Google lo maneja) |

---

## 🚀 Ejemplos de Uso

### Con Ollama (Local):

```bash
# Sin configuración adicional
./sentinel_tui.py
```

### Con Gemini Flash (Rápido):

```bash
export SENTINEL_AI_PROVIDER="antigravity"
export GOOGLE_AI_API_KEY="AIza..."
export ANTIGRAVITY_MODEL="gemini-1.5-flash"
./sentinel_tui.py
```

### Con Gemini Pro (Más Capaz):

```bash
export SENTINEL_AI_PROVIDER="antigravity"
export GOOGLE_AI_API_KEY="AIza..."
export ANTIGRAVITY_MODEL="gemini-1.5-pro"
./sentinel_tui.py
```

---

## 🔍 Verificación

Para verificar qué proveedor está usando:

```bash
# Dentro del TUI, las respuestas mostrarán:
# [provider: antigravity] [model: gemini-1.5-flash]
```

O revisa el historial:

```bash
cat ~/.sentinel/tui_history.json | grep provider
```

---

## ⚠️ Límites de Google AI Studio

**Gratis:**
- 15 requests/minuto
- 1,500 requests/día
- 1 millón tokens/mes

**Recomendación**: Usa Gemini Flash para maximizar el free tier.

---

## 🐛 Troubleshooting

### Error: "Antigravity client not available"

```bash
# Verifica que el archivo existe:
ls backend/app/services/antigravity_client.py

# Reinstala dependencias:
source .venv/bin/activate
pip install httpx
```

### Error: "Invalid API Key"

```bash
# Verifica tu API key:
echo $GOOGLE_AI_API_KEY

# Regenera en: https://makersuite.google.com/app/apikey
```

### Error: "Rate limit exceeded"

```bash
# Cambia a Ollama temporalmente:
export SENTINEL_AI_PROVIDER="ollama"
./sentinel_tui.py
```

---

## 📝 Configuración Recomendada

Para **desarrollo** (privacidad):
```bash
export SENTINEL_AI_PROVIDER="ollama"
```

Para **producción** (capacidad):
```bash
export SENTINEL_AI_PROVIDER="antigravity"
export GOOGLE_AI_API_KEY="tu-key"
export ANTIGRAVITY_MODEL="gemini-1.5-flash"
```

---

**Última actualización**: 2026-01-04  
**Versión**: 1.0
