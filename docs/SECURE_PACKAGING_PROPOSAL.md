# 📦 SIP: Sentinel Installation Protocol (Propuesta)

## Visión
En un SO "Hardened", la instalación de software es el vector de ataque #1. Los gestores tradicionales (`apt`, `npm`) verifican **quién** hizo el paquete (firmas), pero no **qué** hace.

**SIP** añade la validación de **INTENCIÓN**.

## Estructura del Paquete (`.sip`)
Es un archivo ZIP renombrado con estructura estricta:
```text
myapp.sip
├── bin/              # Binarios compilados
├── assets/           # Recursos
├── intent.json       # Manifiesto Semántico
└── signature.sig     # Firma Ed25519 del hash del ZIP (sin sig)
```

### El Archivo `intent.json`
```json
{
  "name": "net-monitor",
  "version": "1.0.0",
  "description": "Monitor de tráfico de red pasivo.",
  "permissions": ["NET_RAW", "READ_LOGS"],
  "semantic_hash": "a1b2..."
}
```

## Flujo de Instalación (`sip install`)

1. **Verificación Física**:
   - ¿Es válida la firma criptográfica? (Previene tampering).

2. **Juicio Cognitivo (The Novelty)**:
   - El instalador extrae `intent.json` y metadatos de los binarios.
   - Envía un prompt a `SemSH`:
     > "El paquete 'net-monitor' pide permisos RAW_SOCKET. Su descripción es 'Monitor pasivo'. ¿Es coherente?"
   - La IA responde: **APPROVED** o **FLAGGED**.

3. **Ejecución (Kernel)**:
   - Si Approved: Se descomprime en `/opt/sentinel/apps/`.
   - Se notifica al **LSM Whitelist** para permitir la ejecución de los nuevos binarios.

## Herramientas (`tools/sip`)
- `sip build <dir>`: Crea un paquete `.sip` firmado.
- `sip install <file>`: Valida, consulta a la IA e instala.
- `sip verify <file>`: Solo chequeo.
