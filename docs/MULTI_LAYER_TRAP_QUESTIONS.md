# 🎯 Preguntas Técnicas Trampa - Multi-Layer Bugs

## Filosofía

**Objetivo**: Código con bugs en múltiples capas de profundidad.

**Niveles de dificultad**:
1. **Obvio** (30 segundos) - Syntax errors, typos
2. **Intermedio** (2-5 minutos) - Logic errors, edge cases
3. **Sutil** (5-15 minutos) - Performance, security, race conditions
4. **Experto** (15+ minutos) - Architecture, scalability, subtle bugs

**Scoring**:
- Encuentra bugs nivel 1-2: Junior (no contratar)
- Encuentra bugs nivel 1-3: Mid-level (tal vez)
- Encuentra bugs nivel 1-4: Senior (contratar)

---

## 🐛 Ejemplo 1: User Authentication (10 bugs)

```python
# "AI-generated" user authentication endpoint

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
import jwt
from datetime import datetime, timedelta

app = FastAPI()

SECRET_KEY = "my-secret-key"  # Bug 1

async def authenticate_user(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    # Find user
    user = db.query(User).filter(User.email == email).first()  # Bug 2
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check password
    if bcrypt.checkpw(password, user.password):  # Bug 3
        # Generate token
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=30)  # Bug 4
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
        
        # Update last login
        user.last_login = datetime.now()  # Bug 5
        db.commit()  # Bug 6
        
        return {"token": token, "user": user}  # Bug 7
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):  # Bug 8
    user = await authenticate_user(email, password, db)
    return user

# Cache for performance
login_cache = {}  # Bug 9

@app.post("/login-cached")
async def login_cached(email: str, password: str):
    cache_key = f"{email}:{password}"  # Bug 10
    if cache_key in login_cache:
        return login_cache[cache_key]
    
    result = await login(email, password)
    login_cache[cache_key] = result
    return result
```

### Los 10 Bugs (Ordenados por Dificultad)

**Nivel 1: Obvio (2 bugs)**

1. **Bug 1: Hardcoded SECRET_KEY**
   - Severidad: CRITICAL
   - Por qué: Secret key en código fuente
   - Fix: `SECRET_KEY = os.getenv("SECRET_KEY")`
   - Tiempo: 30 segundos

2. **Bug 8: Parámetros en URL (GET-like)**
   - Severidad: HIGH
   - Por qué: Passwords en query params (logs, history)
   - Fix: Usar `Pydantic` model en body
   - Tiempo: 1 minuto

**Nivel 2: Intermedio (3 bugs)**

3. **Bug 2: SQL Injection vulnerable**
   - Severidad: CRITICAL
   - Por qué: `.filter(User.email == email)` es seguro, PERO...
   - Si cambias a raw SQL sería vulnerable
   - Fix: Ya está bien con ORM, pero falta validación de email
   - Tiempo: 2 minutos

4. **Bug 4: Token expiration muy largo**
   - Severidad: MEDIUM
   - Por qué: 30 días es demasiado para JWT
   - Fix: `timedelta(hours=1)` + refresh token
   - Tiempo: 3 minutos

5. **Bug 7: Retorna objeto User completo**
   - Severidad: HIGH
   - Por qué: Expone password hash, datos sensibles
   - Fix: Retornar solo campos públicos
   - Tiempo: 2 minutos

**Nivel 3: Sutil (3 bugs)**

6. **Bug 3: Password check es blocking**
   - Severidad: HIGH
   - Por qué: `bcrypt.checkpw()` bloquea event loop
   - Fix: `await run_in_executor(bcrypt.checkpw, ...)`
   - Tiempo: 5 minutos

7. **Bug 5: datetime.now() sin timezone**
   - Severidad: MEDIUM
   - Por qué: `datetime.now()` es naive (no timezone)
   - Fix: `datetime.utcnow()` o `datetime.now(timezone.utc)`
   - Tiempo: 5 minutos

8. **Bug 6: Commit sin await**
   - Severidad: HIGH
   - Por qué: `db.commit()` debería ser `await db.commit()` si es async
   - Fix: `await db.commit()`
   - Tiempo: 3 minutos

**Nivel 4: Experto (2 bugs)**

9. **Bug 9: Cache global sin TTL**
   - Severidad: CRITICAL
   - Por qué: Cache crece infinitamente (memory leak)
   - Fix: Usar Redis con TTL o LRU cache
   - Tiempo: 10 minutos

10. **Bug 10: Cachea passwords en plaintext**
    - Severidad: CRITICAL
    - Por qué: `f"{email}:{password}"` guarda password en memoria
    - Fix: Nunca cachear con password, usar session token
    - Tiempo: 15 minutos

---

## 🐛 Ejemplo 2: Data Processing Pipeline (12 bugs)

```python
# "AI-generated" data processing for metrics

import asyncio
from typing import List
import pandas as pd

class MetricsProcessor:
    def __init__(self):
        self.cache = {}  # Bug 1
        self.processed_count = 0  # Bug 2
    
    async def process_metrics(self, metrics: List[dict]):
        results = []
        
        # Process in parallel
        for metric in metrics:  # Bug 3
            result = await self.process_single_metric(metric)
            results.append(result)
        
        return results
    
    async def process_single_metric(self, metric: dict):
        # Check cache
        cache_key = str(metric)  # Bug 4
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Validate
        if metric["value"] < 0:  # Bug 5
            raise ValueError("Negative value")
        
        # Calculate statistics
        df = pd.DataFrame([metric])  # Bug 6
        mean = df["value"].mean()
        std = df["value"].std()
        
        # Store in cache
        result = {
            "mean": mean,
            "std": std,
            "timestamp": metric["timestamp"]
        }
        self.cache[cache_key] = result  # Bug 7
        
        # Update counter
        self.processed_count += 1  # Bug 8
        
        return result
    
    def get_stats(self):
        return {
            "processed": self.processed_count,
            "cache_size": len(self.cache)
        }

# Usage
processor = MetricsProcessor()  # Bug 9

async def handle_metrics_batch(metrics: List[dict]):
    # Split into chunks
    chunk_size = 1000
    chunks = [metrics[i:i+chunk_size] for i in range(0, len(metrics), chunk_size)]
    
    # Process chunks in parallel
    tasks = [processor.process_metrics(chunk) for chunk in chunks]  # Bug 10
    results = await asyncio.gather(*tasks)
    
    # Flatten results
    flat_results = []
    for result in results:
        flat_results.extend(result)  # Bug 11
    
    # Save to database
    save_to_db(flat_results)  # Bug 12
    
    return flat_results
```

### Los 12 Bugs

**Nivel 1: Obvio (2 bugs)**

1. **Bug 5: KeyError si falta "value"**
   - Severidad: HIGH
   - Por qué: No valida que "value" existe
   - Fix: `metric.get("value")` + validación
   - Tiempo: 1 minuto

2. **Bug 12: save_to_db es blocking**
   - Severidad: HIGH
   - Por qué: Función sync en contexto async
   - Fix: `await save_to_db()` o `run_in_executor`
   - Tiempo: 2 minutos

**Nivel 2: Intermedio (4 bugs)**

3. **Bug 3: No usa asyncio.gather**
   - Severidad: MEDIUM
   - Por qué: Procesa secuencialmente, no en paralelo
   - Fix: `await asyncio.gather(*[process_single_metric(m) for m in metrics])`
   - Tiempo: 3 minutos

4. **Bug 4: Cache key es str(dict)**
   - Severidad: MEDIUM
   - Por qué: `str(dict)` no es determinista (orden de keys)
   - Fix: `json.dumps(metric, sort_keys=True)`
   - Tiempo: 5 minutos

5. **Bug 6: Pandas para 1 row**
   - Severidad: LOW
   - Por qué: Overhead enorme para 1 valor
   - Fix: Calcular directamente sin pandas
   - Tiempo: 3 minutos

6. **Bug 11: extend() modifica lista**
   - Severidad: LOW
   - Por qué: Funciona pero ineficiente
   - Fix: List comprehension `[item for sublist in results for item in sublist]`
   - Tiempo: 2 minutos

**Nivel 3: Sutil (4 bugs)**

7. **Bug 1: Cache sin límite**
   - Severidad: CRITICAL
   - Por qué: Memory leak (crece infinitamente)
   - Fix: LRU cache con maxsize
   - Tiempo: 5 minutos

8. **Bug 2: Counter no es thread-safe**
   - Severidad: HIGH
   - Por qué: Race condition en `processed_count += 1`
   - Fix: `asyncio.Lock()` o `atomic counter`
   - Tiempo: 10 minutos

9. **Bug 7: Cache crece sin control**
   - Severidad: CRITICAL
   - Por qué: Mismo que Bug 1, pero específico a esta función
   - Fix: TTL o maxsize
   - Tiempo: 5 minutos

10. **Bug 10: Shared state race condition**
    - Severidad: CRITICAL
    - Por qué: Múltiples tasks modifican `self.cache` simultáneamente
    - Fix: `asyncio.Lock()` alrededor de cache access
    - Tiempo: 15 minutos

**Nivel 4: Experto (2 bugs)**

11. **Bug 9: Singleton global**
    - Severidad: MEDIUM
    - Por qué: `processor` es global, compartido entre requests
    - Fix: Dependency injection, crear por request
    - Tiempo: 10 minutos

12. **Bug 8: Race condition en counter**
    - Severidad: HIGH
    - Por qué: `+=` no es atómico en async
    - Fix: `async with lock: self.processed_count += 1`
    - Tiempo: 15 minutos

---

## 🐛 Ejemplo 3: WebSocket Real-Time Updates (15 bugs)

```python
# "AI-generated" WebSocket server for real-time metrics

from fastapi import FastAPI, WebSocket
from typing import Dict, Set
import asyncio
import json

app = FastAPI()

# Global state
active_connections: Set[WebSocket] = set()  # Bug 1
user_subscriptions: Dict[int, Set[str]] = {}  # Bug 2
metrics_buffer = []  # Bug 3

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections.add(websocket)  # Bug 4
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()  # Bug 5
            message = json.loads(data)
            
            # Handle subscription
            if message["type"] == "subscribe":  # Bug 6
                topic = message["topic"]
                if user_id not in user_subscriptions:
                    user_subscriptions[user_id] = set()
                user_subscriptions[user_id].add(topic)
                
                # Send confirmation
                await websocket.send_text(json.dumps({  # Bug 7
                    "type": "subscribed",
                    "topic": topic
                }))
    
    except Exception as e:  # Bug 8
        print(f"Error: {e}")
    
    finally:
        active_connections.remove(websocket)  # Bug 9

# Background task to broadcast metrics
async def broadcast_metrics():
    while True:
        if metrics_buffer:  # Bug 10
            metric = metrics_buffer.pop(0)
            
            # Broadcast to all connections
            for connection in active_connections:  # Bug 11
                try:
                    await connection.send_text(json.dumps(metric))  # Bug 12
                except:
                    pass  # Bug 13
        
        await asyncio.sleep(0.1)  # Bug 14

# API endpoint to add metrics
@app.post("/metrics")
async def add_metric(metric: dict):
    metrics_buffer.append(metric)  # Bug 15
    return {"status": "queued"}

@app.on_event("startup")
async def startup():
    asyncio.create_task(broadcast_metrics())
```

### Los 15 Bugs

**Nivel 1: Obvio (3 bugs)**

1. **Bug 5: No timeout en receive**
   - Severidad: MEDIUM
   - Por qué: Bloquea indefinidamente
   - Fix: `asyncio.wait_for(websocket.receive_text(), timeout=60)`
   - Tiempo: 2 minutos

2. **Bug 6: KeyError si falta "type"**
   - Severidad: HIGH
   - Por qué: No valida estructura del mensaje
   - Fix: `message.get("type")` + validación
   - Tiempo: 1 minuto

3. **Bug 8: Catch-all exception**
   - Severidad: MEDIUM
   - Por qué: Oculta errores reales
   - Fix: Catch específico + logging
   - Tiempo: 2 minutos

**Nivel 2: Intermedio (5 bugs)**

4. **Bug 4: No cleanup en error**
   - Severidad: HIGH
   - Por qué: Si `accept()` falla, no se limpia
   - Fix: Mover `add` después de `accept`
   - Tiempo: 3 minutos

5. **Bug 7: No await en send**
   - Severidad: CRITICAL
   - Por qué: `send_text` es async pero no tiene await... espera, SÍ tiene await
   - Esto es una trampa - está correcto
   - Tiempo: 5 minutos (para darse cuenta que NO es bug)

6. **Bug 9: Race condition en remove**
   - Severidad: HIGH
   - Por qué: `remove()` puede fallar si ya fue removido
   - Fix: `discard()` en vez de `remove()`
   - Tiempo: 5 minutos

7. **Bug 13: Silent failure**
   - Severidad: MEDIUM
   - Por qué: `pass` oculta errores de envío
   - Fix: Log error + remove connection
   - Tiempo: 3 minutos

8. **Bug 14: Busy wait**
   - Severidad: LOW
   - Por qué: `sleep(0.1)` es demasiado frecuente
   - Fix: Event-driven o `sleep(1)`
   - Tiempo: 5 minutos

**Nivel 3: Sutil (4 bugs)**

9. **Bug 1: Set no es thread-safe**
   - Severidad: CRITICAL
   - Por qué: Múltiples coroutines modifican `set()` simultáneamente
   - Fix: `asyncio.Lock()` o usar estructura thread-safe
   - Tiempo: 10 minutos

10. **Bug 2: Dict no es thread-safe**
    - Severidad: CRITICAL
    - Por qué: Race condition en modificación
    - Fix: `asyncio.Lock()`
    - Tiempo: 10 minutos

11. **Bug 3: List no es thread-safe**
    - Severidad: CRITICAL
    - Por qué: `append()` y `pop()` simultáneos
    - Fix: `asyncio.Queue()`
    - Tiempo: 10 minutos

12. **Bug 11: Iterating while modifying**
    - Severidad: CRITICAL
    - Por qué: Si connection se remueve durante iteración, crash
    - Fix: `for connection in list(active_connections):`
    - Tiempo: 15 minutos

**Nivel 4: Experto (3 bugs)**

13. **Bug 10: No atomic check-and-pop**
    - Severidad: HIGH
    - Por qué: Entre `if metrics_buffer` y `pop()`, puede vaciarse
    - Fix: Try/except o lock
    - Tiempo: 15 minutos

14. **Bug 15: No backpressure**
    - Severidad: CRITICAL
    - Por qué: Buffer crece infinitamente si broadcast es lento
    - Fix: Bounded queue con maxsize
    - Tiempo: 20 minutos

15. **Bug 12: No selective broadcast**
    - Severidad: MEDIUM
    - Por qué: Envía a todos, ignora subscriptions
    - Fix: Filtrar por `user_subscriptions`
    - Tiempo: 10 minutos

---

## 📊 Sistema de Scoring

### Por Cantidad de Bugs

| Bugs Encontrados | Score | Nivel |
|------------------|-------|-------|
| 15/15 | 100% | Experto (instant hire) |
| 12-14/15 | 85-95% | Senior (hire) |
| 9-11/15 | 65-80% | Mid-Senior (maybe) |
| 6-8/15 | 45-60% | Mid-level (no hire) |
| <6/15 | <40% | Junior (reject) |

### Por Profundidad

| Nivel | Bugs | Puntos | Descripción |
|-------|------|--------|-------------|
| **Nivel 1** | 2-3 | 5 pts c/u | Obvios (syntax, typos) |
| **Nivel 2** | 4-5 | 10 pts c/u | Intermedios (logic, edge cases) |
| **Nivel 3** | 4-5 | 20 pts c/u | Sutiles (performance, security) |
| **Nivel 4** | 2-3 | 30 pts c/u | Expertos (architecture, race conditions) |

**Total**: 100-150 puntos posibles

**Pass threshold**: 85+ puntos (encuentra bugs nivel 1-3 + algunos nivel 4)

---

## 🎯 Uso en Assessment

### Challenge 6 Actualizado

**Tiempo**: 45 minutos (aumentado de 30)

**Instrucciones**:
```
Revisa estos 3 códigos "generados por IA".
Cada uno tiene 10-15 bugs de diferentes niveles.

Encuentra TODOS los bugs que puedas en 45 minutos.

Para cada bug:
1. Línea número
2. Descripción del bug
3. Por qué es un problema
4. Cómo lo arreglarias
5. Severidad (LOW/MEDIUM/HIGH/CRITICAL)

NO uses IA para encontrar bugs.
```

**Scoring**:
- 30+ bugs encontrados (de 37 totales): 100% (instant hire)
- 25-29 bugs: 85-95% (hire)
- 20-24 bugs: 70-80% (maybe)
- <20 bugs: FAIL

---

## 💡 Por Qué Esto Funciona

1. **Múltiples capas**: No pueden "tener suerte" encontrando 1-2 bugs
2. **Diferentes tipos**: Testing conocimiento amplio (async, security, performance)
3. **Realista**: Bugs que IA realmente genera
4. **Auto-gradeable**: Cada bug tiene línea específica
5. **Diferencia niveles**: Junior encuentra 5, Senior encuentra 25+

---

**¿Quieres que agregue estos ejemplos al assessment automatizado?**
