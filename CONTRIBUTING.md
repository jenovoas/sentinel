# Contribuir a Sentinel

Guía para el equipo de desarrollo que mantiene la calidad y la consistencia del código.

## Estándares de Código

### Python (Backend)

**Todo el código Python debe:**
- Seguir la guía de estilo **PEP 8**
- Incluir *type hints* en parámetros y valores de retorno
- Tener *docstrings* exhaustivas (estilo Google)
- Comentar donde la lógica no sea obvia
- Pasar el *linting* sin advertencias

**Formato de docstring:**
```python
def crear_usuario(email: str, password: str, tenant_id: str) -> User:
    """
    Crea un nuevo usuario en un tenant.

    Esta función maneja la creación de usuarios con hash de contraseña y
    asocia el usuario al tenant especificado.

    Args:
        email: Correo del usuario (debe ser único dentro del tenant)
        password: Contraseña en texto plano (se hasheará)
        tenant_id: ID del tenant al que pertenece el usuario

    Returns:
        User: El objeto usuario creado

    Raises:
        ValueError: Si el email ya existe en el tenant

    Example:
        user = crear_usuario("juan@ejemplo.com", "password123", tenant_id)
    """
    pass
```

**Guía de comentarios:**
```python
# ✅ Bueno: Explica el POR QUÉ
# Usamos connection pooling con recycle para evitar errores "connection lost"
# tras reinicios de la BD o timeouts de inactividad

# ❌ Malo: Explica el QUÉ (el código ya lo hace)
# conn_pool = get_connection_pool()
```

### TypeScript/JavaScript (Frontend)

**Todo el código frontend debe:**
- Usar **TypeScript** (nada de JS plano)
- Incluir definiciones de tipos
- Tener comentarios JSDoc en componentes
- Usar *functional components*
- Seguir *best practices* de React

**Formato de componente:**
```typescript
/**
 * Componente UserCard.
 *
 * Muestra la información del usuario en una tarjeta con acciones de editar y borrar.
 *
 * @param user - Objeto usuario a mostrar
 * @param onEdit - Callback al hacer clic en editar
 * @param onDelete - Callback al hacer clic en borrar
 * @returns Componente React
 *
 * @example
 * <UserCard
 *   user={userData}
 *   onEdit={handleEdit}
 *   onDelete={handleDelete}
 * />
 */
export function UserCard({
  user,
  onEdit,
  onDelete,
}: UserCardProps): JSX.Element {
  return <div>...</div>;
}
```

### SQL y Base de Datos

**Los cambios en BD deben:**
- Incluir explicación de la migración
- Ser retrocompatibles cuando sea posible
- Comentar políticas RLS
- Documentar la lógica de negocio

## Flujo de Trabajo Git

### Ramas
- `main` — Solo código listo para producción
- `develop` — Rama de integración
- *Feature branches*: `feature/descripcion`
- *Bugfix branches*: `bugfix/numero-issue`
- *Hotfix branches*: `hotfix/issue-urgente`

### Commits
```bash
# Buenos mensajes de commit
git commit -m "feat: añadir autenticación de usuario con JWT"
git commit -m "fix: resolver timeout de conexión a base de datos"
git commit -m "docs: actualizar documentación de API para endpoint usuarios"

# Formato: [tipo]: [descripción corta]
# Tipos: feat, fix, docs, style, refactor, perf, test, chore
```

### Pull Requests

**Antes de crear un PR:**
1. Crear rama feature desde `develop`
2. Hacer cambios con buenos commits
3. Probar localmente con `podman-compose`
4. Actualizar documentación si es necesario

**Plantilla de PR:**
```markdown
## Descripción
¿Qué cambios hace este PR?

## Tipo de Cambio
- [ ] Nueva funcionalidad
- [ ] Corrección de bug
- [ ] Actualización de documentación
- [ ] Mejora de rendimiento

## Pruebas
¿Cómo se probó esto?

## Lista de verificación
- [ ] El código sigue los estándares del proyecto
- [ ] La documentación está actualizada
- [ ] Se añadieron/actualizaron tests
- [ ] Sin errores/advertencias en consola
```

## Requisitos de Pruebas

### Tests Backend
```python
# Usar pytest para todos los tests
# Ubicación: directorio tests/
# Ejecutar: podman-compose exec backend pytest

import pytest
from app.models import User

def test_crear_usuario(db_session):
    """Test creación de usuario con datos válidos."""
    user = User(email="test@ejemplo.com", username="testuser")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "test@ejemplo.com"
```

### Tests Frontend
```typescript
// Usar vitest/jest para test de componentes
// Ubicación: __tests__/ o adyacente al componente
// Ejecutar: podman-compose exec frontend npm test

import { render, screen } from '@testing-library/react';
import { UserCard } from '@/components/UserCard';

describe('UserCard', () => {
  it('muestra la información del usuario correctamente', () => {
    render(<UserCard user={mockUser} />);
    expect(screen.getByText(mockUser.email)).toBeInTheDocument();
  });
});
```

## Documentación

### README.md
- Mantener actualizado con cambios mayores
- Incluir nuevos endpoints
- Documentar nuevas funcionalidades
- Actualizar ejemplos de comandos si cambian

### Comentarios en Código
- Explicar lógica de negocio y decisiones
- Documentar algoritmos no obvios
- Anotar *workarounds* con razones
- Enlazar a issues o docs relacionados

### Docstrings
- Cada función/clase pública debe tener docstrings
- Incluir parámetros, retornos, excepciones
- Añadir ejemplos para uso complejo

## Consideraciones de Rendimiento

### Backend
- Usar `pool_pre_ping=True` para conexiones
- Implementar paginación en endpoints de lista
- Cachear datos frecuentes en Redis
- Usar Celery para tareas largas
- Monitorizar rendimiento de consultas con `echo=True` en dev

### Frontend
- Usar `React.memo` para componentes costosos
- Implementar *lazy loading* para rutas
- Optimizar imágenes con next/image
- Minimizar tamaño de bundle
- Usar Suspense para componentes async

## Lista de Verificación de Seguridad

### Antes de Cada Release
- [ ] Sin secretos hardcodeados en código
- [ ] Todas las entradas de usuario validadas
- [ ] Protección contra inyección SQL vía ORM
- [ ] CORS configurado correctamente
- [ ] Rate limiting habilitado
- [ ] Contraseñas hasheadas (nunca en plano)
- [ ] Secretos JWT rotados si es necesario
- [ ] Dependencias actualizadas
- [ ] Modo debug desactivado en producción
- [ ] HTTPS forzado en producción

## Configuración de Desarrollo Local

```bash
# Primera configuración
cd /home/jnovoas/sentinel
podman-compose build
podman-compose up -d

# Desarrollo backend
podman-compose exec backend bash
pip install -r requirements.txt
pytest

# Desarrollo frontend
podman-compose exec frontend bash
npm install
npm run dev

# Verificar calidad de código
podman-compose exec backend black app/
podman-compose exec backend mypy app/
podman-compose exec frontend npm run lint
```

## Depuración

### Backend
```bash
# Ver logs
podman-compose logs -f backend

# Acceso shell
podman-compose exec backend bash

# Debugger Python
podman-compose exec backend python -m pdb app/main.py

# Consultar base de datos
podman-compose exec postgres psql -U sentinel_user -d sentinel_db
```

### Frontend
```bash
# Ver logs
podman-compose logs -f frontend

# Shell Node
podman-compose exec frontend bash

# DevTools del navegador (automático en desarrollo)
```

### Base de Datos
```bash
# Conectar a PostgreSQL
podman-compose exec postgres psql -U sentinel_user -d sentinel_db

# Consultas comunes
\dt                    # Listar tablas
\d+ nombre_tabla      # Describir tabla
SELECT * FROM users;  # Consultar datos
```

## Tareas Comunes

### Añadir un Endpoint de API
1. Crear schema en `backend/app/schemas/__init__.py`
2. Crear router en `backend/app/routers/feature.py`
3. Añadir ruta al router con docstrings adecuados
4. Incluir router en `backend/app/main.py`
5. Actualizar README.md con info del endpoint
6. Escribir tests para el endpoint

### Añadir una Tabla a la BD
1. Crear modelo en `backend/app/models/__init__.py`
2. Añadir migración (Alembic cuando se implemente)
3. Actualizar políticas RLS si es multi-tenant
4. Documentar en README.md

### Añadir Componente Frontend
1. Crear componente en `frontend/src/components/`
2. Añadir tipos TypeScript
3. Escribir tests
4. Documentar con JSDoc
5. Añadir a índice/exportación de componentes

## Guías de Code Review

**Los revisores deben comprobar:**
- [ ] El código sigue los estándares
- [ ] La lógica es correcta
- [ ] Los tests son adecuados
- [ ] La documentación está completa
- [ ] Sin problemas de seguridad
- [ ] El rendimiento es aceptable
- [ ] Sin breaking changes sin discusión

**Los comentarios deben ser:**
- Constructivos y útiles
- Específicos con ejemplos
- Positivos y alentadores

## Herramientas y Comandos

```bash
# Formateo de código
podman-compose exec backend black app/
podman-compose exec frontend npm run format

# Linting
podman-compose exec backend flake8 app/
podman-compose exec frontend npm run lint

# Type checking
podman-compose exec backend mypy app/
podman-compose exec frontend npm run type-check

# Testing
podman-compose exec backend pytest
podman-compose exec frontend npm test

# Todas las comprobaciones
podman-compose exec backend black app/ && mypy app/ && flake8 app/
```

## Obtener Ayuda

- **¿Preguntas?** Preguntar en el canal del equipo
- **¿Atascado?** Revisar issues/PRs existentes
- **¿Bug encontrado?** Crear issue con detalles
- **¿Documentación poco clara?** ¡Actualízala!

## Recordatorios Finales

✅ **Hacer:**
- Escribir código claro y auto-documentado
- Comentar lógica de negocio, no código obvio
- Probar tus cambios antes de pushear
- Mantener funciones pequeñas y enfocadas
- Usar nombres de variables significativos
- Documentar mientras codificas

❌ **No hacer:**
- Commit sin entender los cambios
- Dejar código de debug o console.log
- Ignorar advertencias de tipos
- Mezclar features en un solo commit
- Hardcodear valores (usar config/env)
- Saltarse la documentación

---

**¿Preguntas?** Pregunta al equipo. **¿Listo para contribuir?** ¡Empieza con un issue!