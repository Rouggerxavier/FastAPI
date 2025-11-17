# FastAPI Order Management System - Copilot Instructions

## Architecture Overview

This is a FastAPI-based order management API with three core entities:
- **Usuario** (Users): User accounts with email-based authentication
- **Pedido** (Orders): Orders linked to users with status tracking
- **ItemPedido** (Order Items): Individual items within orders

**Data Flow**: Users → Orders → Order Items (1:N relationships)

## Project Structure & Key Files

- `main.py`: FastAPI app initialization with router includes
- `models.py`: SQLAlchemy ORM models (Usuario, Pedido, ItemPedido) using declarative_base
- `auth_routes.py`: Authentication endpoints (incomplete - `/auth/login`, `/auth/criar_conta`)
- `order_routes.py`: Order management endpoints (skeleton - `/orders/lista`)
- `alembic/`: Database migration management
- `alembic.ini`: SQLite database configuration (`sqlite:///./meubanco.db`)

## Database & Migrations

**Setup Pattern**: Alembic for schema versioning
- Database: SQLite (configured in `alembic.ini`)
- Migration file: `alembic/versions/e3fa71cb9169_inicial.py` (creates all tables)
- Key concern: `ChoiceType` from `sqlalchemy_utils` is imported in migration file for status enum

**Common Commands**:
```
alembic upgrade head          # Apply all pending migrations
alembic revision --autogenerate -m "description"  # Create new migration
alembic downgrade -1          # Rollback one migration
```

## Routes & Patterns

**Router Pattern** (from `main.py`):
- Use `APIRouter` with `prefix` and `tags` parameters
- Import router and call `app.include_router()`
- Convention: Each route module exports a router (e.g., `auth_router`, `order_router`)

**Status Choices** (from `models.py`):
```python
STATUS_CHOICES = [("aberto", "Aberto"), ("fechado", "Fechado"), ("cancelado", "Cancelado")]
```
Used in `Pedido.status` with `ChoiceType(STATUS_CHOICES)` from `sqlalchemy_utils`

## Known Issues & Incomplete Code

1. **auth_routes.py**: Incomplete syntax - `criar_conta()` function has syntax errors (missing colon, incomplete assignment)
2. **Database session management**: No SessionLocal, no dependency injection for sessions in routes
3. **Authentication**: No password hashing or JWT tokens implemented
4. **Order routes**: Only skeleton implementation exists

## Development Workflow

**Environment**: Uses Python venv (`venv/` directory exists)
**Dependencies**: FastAPI, SQLAlchemy, sqlalchemy_utils, Alembic (inferred from imports and alembic.ini)

When completing incomplete routes:
- Follow router + endpoint pattern established in order_routes.py
- Add proper session management (SessionLocal dependency)
- Implement Pydantic schemas for request validation
- Maintain naming conventions (snake_case for functions/variables, CamelCase for classes)

## Language & Convention Notes

- Portuguese naming in domain models (Usuario, Pedido, ItemPedido) but English in route structure
- Function returns are currently placeholder dicts (e.g., `{"message": "..."}`)
- No error handling or validation currently implemented
