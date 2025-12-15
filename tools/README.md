# Watchdog Loader (n8n)

Monitorea el directorio `docker/n8n/workflows` y crea/inyecta automáticamente cualquier archivo `.json` nuevo en la API de n8n.

## Uso rápido

1. Exporta tu API Key de n8n (opcional si desactivaste el requirement):

```bash
export N8N_API_KEY="<tu_api_key>"
```

2. Instala dependencias (usa el entorno del backend o tu venv):

```bash
pip install -r backend/requirements.txt
```

3. Ejecuta el monitor:

```bash
python tools/watchdog_loader.py
```

4. Copia un workflow al directorio observado y mira el log:

```bash
cp docker/n8n/workflows/slo-alert.json docker/n8n/workflows/slo-alert-copy.json
```

## Variables de entorno
- `N8N_URL` (default: http://localhost:5678)
- `N8N_API_KEY` (default: vacío)
- `WORKFLOWS_DIR` (default: docker/n8n/workflows)

## Nota
- Si n8n responde `"request/body must have required property 'settings'"`, asegúrate de que el JSON incluya al menos `name`, `nodes`, `connections` y `settings`.
- No envíes `active` en el POST inicial; es de solo lectura.
