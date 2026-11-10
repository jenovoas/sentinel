# Verificación CI de Python y el puente Rust

El flujo `Backend Python verification` protege el límite Rust/Python del backend. Se ejecuta en solicitudes de integración cuando cambian requisitos, código/pruebas del backend, el puente `quantum`, la extensión Rust o el propio flujo.

El trabajo usa Python 3.11, instala `backend/requirements.txt` y compila `me60os_core` con ese mismo intérprete. Copia el artefacto construido a `quantum/me60os_core.so` únicamente en el directorio efímero del ejecutor; no reemplaza el binario versionado del repositorio. Después verifica la importación del puente, ejecuta `quantum/test_bridge_integrity.py` y comprueba que las pruebas del backend se puedan recolectar.

Esto detecta incompatibilidades de ABI de CPython y errores de importación/colección. **No ejecuta el cuerpo de toda la suite del backend ni valida servicios externos** como PostgreSQL, Redis u Ollama; una colección correcta no equivale a pruebas funcionales aprobadas. La suite completa debe convertirse en una comprobación estable por separado antes de usarla como bloqueo de integración.

El flujo se añadió después de que el PR #142 verificara únicamente la instalación de dependencias. La causa concreta del fallo local era reutilizar un `.so` compilado para otra versión de CPython en pruebas con Python 3.11; construir la extensión para el intérprete del ejecutor hizo que la importación y la colección funcionaran.
