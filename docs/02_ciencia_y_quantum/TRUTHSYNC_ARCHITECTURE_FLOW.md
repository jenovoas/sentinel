# 🛰️ TruthSync: Arquitectura de Flujo (Motor Pesado)

Este diagrama detalla el ciclo de vida de un **Job de Verificación**, desde la captura del claim hasta la sincronización en el Edge Cache.

## 🧜‍♂️ Diagrama de Secuencia UML

```mermaid
sequenceDiagram
    participant C as Cliente (Validator/TUI)
    participant Core as TruthSync Core (Heavy)
    participant Q as Colas de Prioridad (Async)
    participant W as Workers (x4 Slots)
    participant DB as PostgreSQL (Sovereign DB)
    participant R as Redis (Edge Cache)

    C->>Core: submit_job(text, priority)
    Core->>Core: Generar claim_hash (SHA-256)
    Core->>Q: Enqueue Job (Urgent | High | Normal)
    
    Note over Q,W: Los Workers monitorean las colas constantemente
    
    W->>Q: Pull Job (Prioridad De-queue)
    W->>DB: _get_cached_verification(claim_hash)
    
    alt Existe en Cache DB y es Válido
        DB-->>W: Retornar Resultado SQL
    else No existe o Expitado (TTL)
        W->>W: _perform_deep_verification (ML Pipeline)
        W->>DB: _store_verification_result (Persistencia)
    end
    
    W->>R: _sync_to_edge_cache (Set Redis TTL)
    Core-->>C: Notificar Finalización (Async Success)
    
    Note right of R: Disponible para el Backend/API < 1ms
```

## ⚙️ Componentes Críticos

1.  **Prioridad Dinámica**: El sistema utiliza 3 colas paralelas. Los jobs `Urgent` tienen preferencia absoluta sobre los `Normal`, evitando que las validaciones masivas bloqueen el acceso en tiempo real a la API.
2.  **Persistencia Dual**: 
    *   **PostgreSQL**: Registro inmutable histórico de cada claim verificado.
    *   **Redis**: Espejo de alta velocidad para que el Sentinel Edge no tenga que consultar la DB pesada.
3.  **Worker Loop**: Operación no bloqueante que permite procesar miles de archivos con una latencia de ~100ms.

## 📈 Latencia Operacional Observada
- **Queue Overhead**: < 1ms
- **DB Lookup**: ~5-10ms
- **ML Analysis (Sim)**: ~100ms
- **Total Roundtrip**: **~112ms**
