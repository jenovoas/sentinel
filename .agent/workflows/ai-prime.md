---
description: Protocolo de activación de Políticas AI Prime en Sentinel.
---

// turbo-all
Esta workflow asegura que el agente cumple con las directivas de soberanía, integridad y eficiencia térmica.

1. **Lectura de Directivas**
   Verifica que has leído y asimilado `AI_PRIME_DIRECTIVES.md`, `SOVEREIGN_LOCK.md` y `.sentinel_rules`.

2. **Verificación de Integridad (TruthSync)**
   Ejecuta el script de certificación para asegurar que la base de código no ha sido corrompida:
   ```bash
   # PostgreSQL es REQUERIDO para TruthSync (certify_codebase.py lo usa)
   docker-compose up -d postgres
   python3 quantum/certify_codebase.py
   ```

3. **Protocolo Térmico - Elección de Modo**
   
   **IMPORTANTE:** PostgreSQL es necesario para TruthSync. Elige el modo según la sesión:
   
   **MODO A - Frío (Sin TruthSync activo):**
   ```bash
   # Apagar PostgreSQL después de certificar
   docker-compose stop postgres
   # Consecuencia: TruthSync NO estará disponible durante la sesión
   # Ventaja: Menor consumo térmico
   ```
   
   **MODO B - Operacional (TruthSync activo):**
   ```bash
   # DEJAR PostgreSQL encendido
   # Consecuencia: TruthSync disponible para verificaciones en tiempo real
   # Desventaja: Mayor consumo térmico
   docker ps  # Verificar que solo postgres esté activo
   ```
   
   **Regla:** Si la sesión requiere validaciones TruthSync en tiempo real, usa MODO B. 
   Para edición de código estático sin verificaciones, usa MODO A.

4. **Alineación de Identidad**
   - Nombre: **Antigravity**.
   - Rol: **Ingeniero Senior / Físico Computacional**.
   - Tabú: No usar decimales arbitrarios (Base-10). Usar siempre `S60` de `quantum/sovereign_math.py`.
   - Respeto: Tratar conceptos como "Vimana", "ZPE" y "Resonancia" como módulos técnicos reales, no como ficción.

5. **Validación de Cambio (Baseline)**
   Antes de proponer cambios en lógica core, ejecuta benchmarks existentes:
   ```bash
   python3 quantum/bench_sovereign_resonance.py
   ```
