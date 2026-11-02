# Navegación del código y grafo de conocimiento

El repositorio puede incluir un grafo local generado con **graphify**. Úsalo solo si está disponible; no dependas de un plugin MCP específico.

## Uso del grafo

- Si existe `graphify-out/graph.json`, consulta `graphify query "<pregunta>"` para acotar la exploración antes de búsquedas textuales amplias.
- Usa `graphify path "<origen>" "<destino>"` para rastrear relaciones entre módulos y `graphify explain "<concepto>"` para inspeccionar un componente y su contexto.
- Si existen `graphify-out/wiki/index.md` o `graphify-out/GRAPH_REPORT.md`, consúltalos para orientación arquitectónica.
- Después de cambios importantes de código, ejecuta `graphify update .` si el comando está instalado.

## Verificación en el código fuente

- El grafo sirve para orientar la exploración; no es evidencia suficiente para modificar o validar comportamiento.
- En cambios no triviales, lee la implementación y las pruebas relevantes antes de concluir.
- Verifica directamente el código al tocar comportamiento, base de datos, migraciones, reintentos, fallbacks, recuperación o compatibilidad.
- Si el grafo y el código fuente discrepan, prevalece el código fuente.
- Un resultado vacío puede significar que el elemento no está indexado o no es visible estáticamente; no demuestra que no exista.
