# Contributing to Sentinel

Guidelines for the development team to maintain code quality and consistency.

## Code Standards

### Python (Backend)

**All Python code must:**
- Follow PEP 8 style guide
- Include type hints for function parameters and returns
- Have comprehensive docstrings (Google style)
- Be commented where logic is not obvious
- Pass linting without warnings

**Docstring Format:**
```python
def create_user(email: str, password: str, tenant_id: str) -> User:
    """
    Create a new user in a tenant.
    
    This function handles user creation with password hashing and
    associates the user with the specified tenant.
    
    Args:
        email: User's email address (must be unique within tenant)
        password: Plain text password (will be hashed)
        tenant_id: ID of the tenant this user belongs to
        
    Returns:
        User: The created user object
        
    Raises:
        ValueError: If email already exists in tenant
        
    Example:
        user = create_user("john@example.com", "password123", tenant_id)
    """
    pass
```

**Comment Guidelines:**
```python
# ✅ Good: Explains WHY
# We use connection pooling with recycle to avoid "connection lost" errors
# after database restarts or idle timeouts

# ❌ Bad: Explains WHAT (code already does this)
# conn_pool = get_connection_pool()
```

### TypeScript/JavaScript (Frontend)

**All frontend code must:**
- Use TypeScript (no plain JS)
- Include type definitions
- Have JSDoc comments for components
- Use functional components
- Follow React best practices

**Component Format:**
```typescript
/**
 * UserCard component.
 * 
 * Displays user information in a card layout with edit and delete actions.
 * 
 * @param user - The user object to display
 * @param onEdit - Callback when edit button is clicked
 * @param onDelete - Callback when delete button is clicked
 * @returns React component
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

### SQL & Database

**Database changes must:**
- Include migration explanation
- Be backwards compatible when possible
- Include comments for RLS policies
- Document the business logic

## Git Workflow

### Branches
- `main` - Production-ready code only
- `develop` - Integration branch
- Feature branches: `feature/description`
- Bugfix branches: `bugfix/issue-number`
- Hotfix branches: `hotfix/urgent-issue`

### Commits
```bash
# Good commit messages
git commit -m "feat: add user authentication with JWT"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update API documentation for users endpoint"

# Format: [type]: [short description]
# Types: feat, fix, docs, style, refactor, perf, test, chore
```

### Pull Requests

**Before creating a PR:**
1. Create feature branch from `develop`
2. Make your changes with good commits
3. Test locally with `docker-compose`
4. Update documentation if needed

**PR Template:**
```markdown
## Description
What changes does this PR make?

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance improvement

## Testing
How was this tested?

## Checklist
- [ ] Code follows project standards
- [ ] Documentation is updated
- [ ] Tests are added/updated
- [ ] No console errors/warnings
```

## Testing Requirements

### Backend Tests
```python
# Use pytest for all tests
# Location: tests/ directory
# Run: docker-compose exec backend pytest

import pytest
from app.models import User

def test_create_user(db_session):
    """Test user creation with valid data."""
    user = User(email="test@example.com", username="testuser")
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"
```

### Frontend Tests
```typescript
// Use vitest/jest for component testing
// Location: __tests__/ or adjacent to component
// Run: docker-compose exec frontend npm test

import { render, screen } from '@testing-library/react';
import { UserCard } from '@/components/UserCard';

describe('UserCard', () => {
  it('displays user information correctly', () => {
    render(<UserCard user={mockUser} />);
    expect(screen.getByText(mockUser.email)).toBeInTheDocument();
  });
});
```

## Documentation

### README.md
- Keep updated with major changes
- Include new endpoints
- Document new features
- Update command examples if they change

### Code Comments
- Explain business logic and decisions
- Document non-obvious algorithms
- Note workarounds with reasons
- Link to related issues or docs

### Docstrings
- Every public function/class must have docstrings
- Include parameters, returns, raises
- Add examples for complex usage

## Performance Considerations

### Backend
- Use `pool_pre_ping=True` for connections
- Implement pagination for list endpoints
- Cache frequently accessed data in Redis
- Use Celery for long-running tasks
- Monitor query performance with `echo=True` in dev

### Frontend
- Use React.memo for expensive components
- Implement lazy loading for routes
- Optimize images with next/image
- Minimize bundle size
- Use Suspense for async components

## Security Checklist

### Before Each Release
- [ ] No hardcoded secrets in code
- [ ] All user inputs validated
- [ ] SQL injection protection via ORM
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Passwords hashed (never stored plain)
- [ ] JWT secrets rotated if needed
- [ ] Dependencies updated
- [ ] No debug mode in production
- [ ] HTTPS enforced in production

## Local Development Setup

```bash
# First time setup
cd /home/jnovoas/sentinel
docker-compose build
docker-compose up -d

# Backend development
docker-compose exec backend bash
pip install -r requirements.txt
pytest

# Frontend development
docker-compose exec frontend bash
npm install
npm run dev

# Check code quality
docker-compose exec backend black app/
docker-compose exec backend mypy app/
docker-compose exec frontend npm run lint
```

## Debugging

### Backend
```bash
# View logs
docker-compose logs -f backend

# Shell access
docker-compose exec backend bash

# Python debugger
docker-compose exec backend python -m pdb app/main.py

# Query database
docker-compose exec postgres psql -U sentinel_user -d sentinel_db
```

### Frontend
```bash
# View logs
docker-compose logs -f frontend

# Node shell
docker-compose exec frontend bash

# Browser DevTools (automatic in development)
```

### Database
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U sentinel_user -d sentinel_db

# Common queries
\dt                    # List tables
\d+ table_name        # Describe table
SELECT * FROM users;  # Query data
```

## Common Tasks

### Adding an API Endpoint
1. Create schema in `backend/app/schemas/__init__.py`
2. Create router in `backend/app/routers/feature.py`
3. Add route to router with proper docstrings
4. Include router in `backend/app/main.py`
5. Update README.md with endpoint info
6. Write tests for endpoint

### Adding a Database Table
1. Create model in `backend/app/models/__init__.py`
2. Add migration (Alembic when implemented)
3. Update RLS policies if multi-tenant
4. Document in README.md

### Adding Frontend Component
1. Create component in `frontend/src/components/`
2. Add TypeScript types
3. Write tests
4. Document with JSDoc
5. Add to component index/export

## Code Review Guidelines

**Reviewers should check:**
- [ ] Code follows standards
- [ ] Logic is correct
- [ ] Tests are adequate
- [ ] Documentation is complete
- [ ] No security issues
- [ ] Performance is acceptable
- [ ] No breaking changes without discussion

**Comments should be:**
- Constructive and helpful
- Specific with examples
- Positive and encouraging

## Tools & Commands

```bash
# Code formatting
docker-compose exec backend black app/
docker-compose exec frontend npm run format

# Linting
docker-compose exec backend flake8 app/
docker-compose exec frontend npm run lint

# Type checking
docker-compose exec backend mypy app/
docker-compose exec frontend npm run type-check

# Testing
docker-compose exec backend pytest
docker-compose exec frontend npm test

# All checks
docker-compose exec backend black app/ && mypy app/ && flake8 app/
```

## Getting Help

- **Questions?** Ask in the team channel
- **Stuck?** Check existing issues/PRs
- **Bug found?** Create an issue with details
- **Documentation unclear?** Update it!

## Final Reminders

✅ **Do:**
- Write clear, self-documenting code
- Comment business logic, not obvious code
- Test your changes before pushing
- Keep functions small and focused
- Use meaningful variable names
- Document as you code

❌ **Don't:**
- Commit without understanding changes
- Leave debug code or console.log
- Ignore type warnings
- Mix features in one commit
- Hardcode values (use config/env)
- Skip documentation

---

**Questions?** Ask the team. **Ready to contribute?** Start with an issue!
