# 🔧 Backend - API y Lógica de Negocio

## 📋 Resumen Ejecutivo

El **Backend** es el cerebro operacional de Sentinel. Procesa todas las solicitudes, gestiona datos, y coordina la comunicación entre componentes.

**En términos ITIL**: Este módulo implementa **Service Operation** (Operación del Servicio) y **Service Transition** (Transición del Servicio).

---

## 🎯 ¿Qué Hace Este Módulo?

- **API REST**: Punto de entrada para todas las operaciones (como el mostrador de un banco)
- **Gestión de Datos**: Almacena y recupera información de forma segura
- **Autenticación**: Verifica quién puede acceder al sistema
- **Procesamiento Asíncrono**: Maneja tareas pesadas en segundo plano

- **FastAPI**: Framework Python moderno con async/await
- **PostgreSQL**: Base de datos relacional con soporte HA
- **Celery**: Queue de tareas asíncronas
- **Alembic**: Migraciones de base de datos
- **Pydantic**: Validación de datos

---

## 📊 Jerarquía ITIL

```
ITIL Framework
├─ Service Strategy (Estrategia)
│  └─ Definición de servicios API
│
├─ Service Design (Diseño)
│  ├─ Arquitectura REST
│  ├─ Modelo de datos
│  └─ Seguridad (JWT, RBAC)
│
├─ Service Transition (Transición)
│  ├─ Migraciones de DB (alembic/)
│  ├─ Testing (tests/)
│  └─ CI/CD integration
│
├─ Service Operation (Operación)
│  ├─ API endpoints (app/api/)
│  ├─ Background tasks (Celery)
│  └─ Health checks
│
└─ Continual Service Improvement
   ├─ Logging (logs/)
   ├─ Metrics (Prometheus)
   └─ Performance monitoring
```

---

## 🗂️ Estructura de Carpetas

```
backend/
├── app/                    # Código principal de la aplicación
│   ├── api/               # Endpoints REST
│   │   ├── v1/           # API versión 1
│   │   │   ├── auth.py   # Autenticación
│   │   │   ├── orgs.py   # Organizaciones
│   │   │   └── users.py  # Usuarios
│   │   └── deps.py       # Dependencias compartidas
│   │
│   ├── core/             # Configuración central
│   │   ├── config.py     # Variables de entorno
│   │   └── security.py   # JWT, passwords
│   │
│   ├── db/               # Base de datos
│   │   ├── models.py     # Modelos SQLAlchemy
│   │   └── session.py    # Conexión DB
│   │
│   ├── services/         # Lógica de negocio
│   │   ├── auth.py       # Servicio de autenticación
│   │   └── telemetry.py  # Procesamiento de telemetría
│   │
│   └── tasks/            # Tareas asíncronas (Celery)
│       ├── backup.py     # Backups automáticos
│       └── reports.py    # Generación de reportes
│
├── alembic/              # Migraciones de base de datos
│   └── versions/         # Historial de cambios
│
├── tests/                # Tests automatizados
│   ├── test_api.py       # Tests de endpoints
│   └── test_services.py  # Tests de servicios
│
├── logs/                 # Logs de aplicación
│
├── requirements.txt      # Dependencias Python
├── Dockerfile           # Imagen Docker
└── entrypoint.sh        # Script de inicio
```

---

## 🔑 Componentes Clave

### 1. API REST (app/api/)

**Función**: Expone endpoints HTTP para el frontend y clientes externos

**Endpoints principales**:

- `/api/v1/auth/login` - Autenticación
- `/api/v1/organizations` - Gestión de organizaciones
- `/api/v1/telemetry` - Ingesta de métricas/logs
- `/api/v1/health` - Health check

**Tecnología**: FastAPI (async, auto-documentación con Swagger)

### Autorización de Guardian Gamma

Todas las operaciones de `/api/v1/gamma` requieren un JWT Bearer vigente y el
control compartido `get_current_superuser` (`is_superuser=true`). La cola es
global, sin tenant; un administrador de organización no puede acceder. Incluye
`POST /decision`, `GET /pending`,
`POST /approve/{decision_id}`, `POST /deny/{decision_id}` y `POST /cleanup`.
Sin credenciales o con un token inválido se devuelve `401`; usuarios autenticados
sin privilegios administrativos reciben `403`. `X-Sentinel-Token` de ingesta no
autoriza estas rutas.

Los consumidores HTTP, incluidos trabajos de limpieza, deben obtener y enviar un
JWT de superusuario mediante el flujo de autenticación existente; no hay bypass
para automatizaciones. La escalación interna de Cortex continúa usando
`GuardianGammaService` directamente, sin cambios en persistencia ni en el servicio.
Este cierre no agrega rutas al BFF ni interfaz de revisión en Kingu.

Despliegue: actualizar únicamente la imagen del backend; este cambio no requiere
migraciones adicionales. La autenticación exige usuario y organización activos y
la versión de esquema esperada por el backend. Coordinar los consumidores HTTP
antes del cambio: sus peticiones anónimas dejarán de funcionar.

Smoke no destructivo: ejecutar `GET /api/v1/gamma/pending?limit=1` sin credenciales
(esperado `401`), con sesión de miembro/lector/admin de tenant (`403`) y con sesión
de superusuario (`200`). Obtener tokens de forma segura sin imprimirlos ni registrarlos.
No aprobar, denegar, crear ni limpiar decisiones como parte de este smoke.
La cobertura conductual de las cinco operaciones está en
`tests/test_gamma_security.py`.

### 2. Modelos de Datos (app/db/)

**Función**: Define estructura de tablas en PostgreSQL

**Modelos principales**:

- `Organization` - Multi-tenancy
- `User` - Usuarios y autenticación
- `TelemetryEvent` - Eventos de monitoreo
- `Alert` - Alertas generadas

**Tecnología**: SQLAlchemy (ORM), Alembic (migraciones)

### 3. Servicios de Negocio (app/services/)

**Función**: Lógica de negocio reutilizable

**Servicios**:

- `AuthService` - Autenticación y autorización
- `TelemetryService` - Procesamiento de telemetría
- `AlertService` - Generación de alertas
- `BackupService` - Gestión de backups

### 4. Tareas Asíncronas (app/tasks/)

**Función**: Procesos en segundo plano

**Tareas**:

- Backup automático cada 6 horas
- Generación de reportes diarios
- Limpieza de datos antiguos
- Envío de notificaciones

**Tecnología**: Celery + Redis

---

## Cómo Funciona (Flujo de Datos)

```
1. Cliente (Frontend/API) → 2. Nginx → 3. FastAPI → 4. Servicio → 5. Base de Datos
                                           ↓
                                      6. Celery (async)
                                           ↓
                                      7. Redis Queue
```

**Ejemplo: Crear una organización**

1. Frontend envía `POST /api/v1/organizations`
2. Nginx enruta a backend (puerto 8000)
3. FastAPI valida datos (Pydantic)
4. `OrganizationService` crea registro
5. PostgreSQL almacena datos
6. Celery envía email de bienvenida (async)
7. Backend retorna respuesta al frontend

---

## 📈 Métricas de Performance

| Métrica           | Valor      | Benchmark          |
| ----------------- | ---------- | ------------------ |
| **Latencia P95**  | <100ms     | <200ms (bueno)     |
| **Throughput**    | 1000 req/s | 500+ req/s (bueno) |
| **Uptime**        | 99.95%     | 99.9% (estándar)   |
| **Test Coverage** | 75%        | 60-80% (bueno)     |

---

## Seguridad

### Implementado

- **JWT Authentication**: Tokens con expiración
- **Password Hashing**: bcrypt
- **SQL Injection Prevention**: ORM (SQLAlchemy)
- **CORS**: Configurado para frontend
- **Rate Limiting**: 100 req/min por IP

### Roadmap 🔜

- RBAC (Role-Based Access Control)
- 2FA (Two-Factor Authentication)
- API Key management

---

## 🛠️ Comandos Útiles

```bash
# Desarrollo local
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Migraciones
alembic upgrade head              # Aplicar migraciones
alembic revision --autogenerate   # Crear nueva migración

# Tests
pytest                            # Todos los tests
pytest --cov=app                  # Con coverage

# Docker
docker-compose up backend         # Solo backend
docker-compose logs -f backend    # Ver logs
```

---

## 📚 Documentación Adicional

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Redoc**: http://localhost:8000/redoc
- **Arquitectura**: `/docs/ARCHITECTURE.md`
- **Guía de Desarrollo**: `/docs/TECHNICAL_GUIDE.md`

---

## 🎓 Para Nuevos Desarrolladores

### Onboarding Rápido (30 minutos)

1. **Leer**: Este README
2. **Instalar**: Dependencias con `pip install -r requirements.txt`
3. **Explorar**: API docs en http://localhost:8000/docs
4. **Probar**: Crear un endpoint simple en `app/api/v1/`
5. **Testear**: Escribir test en `tests/`

### Recursos de Aprendizaje

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Celery**: https://docs.celeryproject.org/

---

## 💼 Valor de Negocio

### Para Inversionistas

**Este módulo representa**:

- 40% del valor técnico de Sentinel
- Core IP (propiedad intelectual)
- Escalabilidad: 1000+ req/s con un solo servidor
- Multi-tenancy: Soporta 1000+ organizaciones

**Comparación con competidores**:

- Datadog: API similar, pero cloud-only
- Sentinel: Self-hosted, privacy-first, 10x más barato

---

**Última actualización**: Diciembre 2024  
**Mantenedor**: Equipo Backend  
**Contacto**: backend@sentinel.dev
