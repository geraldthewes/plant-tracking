# FastAPI Backend to support home page Implementation Plan

## Overview

Implement a minimal FastAPI service with a single endpoint `/api/plants/care-needed` that returns plants needing care attention today. This service will leverage the existing `plant_service` package for all data access, following the established Ports & Adapters architecture. For now, the endpoint will return mock data or an empty response as care threshold specifications need further definition.

## Current State Analysis

The plant tracking system currently has:
- A well-structured `plant_service` package (`packages/plant_service/`) with domain models, service layer, and SQLAlchemy adapters
- No existing web backend API - the `entrypoints/` directory in plant_service is empty
- Established patterns for UnitOfWork, repository pattern, and service layer functions
- Project configuration using Justfile, uv, and Alembic for migrations
- Architecture decisions documented in `/knowledge/architecture/` showing a move toward Ports & Adapters single-service approach

The `plant_service` package provides:
- Domain models: Plant, PlantLogEntry, SeedPacket, Genus
- Service layer: PlantService, LogService, etc. with CRUD operations
- UnitOfWork pattern via `SqlAlchemyUnitOfWork` for transaction management
- Repository implementations for each domain model
- Bootstrap functions for creating UnitOfWork instances

## Desired End State

A minimal FastAPI service that:
1. Can be started and responds to health checks
2. Provides a `/api/plants/care-needed` endpoint returning JSON with count and plants array
3. Uses the existing `plant_service` package for all data access (no duplication)
4. Follows the established Ports & Adapters architecture patterns
5. Is containerizable and deployable using existing project patterns
6. Has automated tests covering the endpoint functionality
7. Passes linting and type checking

### Key Discoveries:
- The `plant_service` package uses a UnitOfWork pattern (`src/plant_service/adapters/repository/uow.py:20-81`) that manages SQLAlchemy sessions
- Service layer functions are accessed via UnitOfWork properties (e.g., `uow.plants`, `uow.logs`) (`src/plant_service/service_layer/`)
- Domain models are pure Python dataclasses with factory methods (`src/plant_service/domain/`)
- The project uses Justfile for task running (`Justfile`) with commands for test, lint, format, etc.
- Database configuration is read from DATABASE_URL environment variable via config.py
- Architecture decisions show movement toward Ports & Adapters single-service approach (`knowledge/architecture/architecture-decisions.md`)

## What We're NOT Doing

- Creating duplicate data access logic - we will reuse existing `plant_service` package
- Implementing complex care threshold logic - endpoint will return mock/empty data for now
- Adding authentication/authz - no auth required for this iteration per ticket
- Creating plant detail, activity log, or other endpoints - deferred to future tickets
- Implementing frontend/UI components - backend only
- Adding Dockerfile or deployment configs - will follow existing project patterns when needed

## Implementation Approach

We'll create a new FastAPI application that:
1. Creates a new directory for the backend service (outside plant_service to avoid coupling)
2. Uses the existing `plant_service` package as a dependency
3. Implements a UnitOfWork dependency for FastAPI that creates per-request UnitOfWork instances
4. Implements the `/api/plants/care-needed` endpoint that uses the plant_service to query data
5. Returns mock data or empty response until care thresholds are specified
6. Includes proper error handling and logging
7. Follows the project's existing patterns for testing, linting, and configuration

## Phase 1: Project Setup and Health Check Endpoint

### Overview
Set up the FastAPI project structure, install dependencies, and create a basic health check endpoint to verify the service is running.

### Changes Required:

#### 1. Create backend service directory
**File**: `backend/fastapi/`
**Changes**: Create new directory for the FastAPI service

#### 2. Initialize Python package
**File**: `backend/fastapi/pyproject.toml`
**Changes**: Define package configuration with dependencies on plant_service and FastAPI

```toml
[build-system]
requires = ["hatchling>=1.20.0"]
build-backend = "hatchling.build"

[project]
name = "plant-tracking-api"
version = "0.1.0"
description = "FastAPI backend for plant tracking home page"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.25.0",
    "plant_service @ file:../../packages/plant_service",
    "python-dateutil>=2.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-mock>=3.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[tool.hatch.build.targets.wheel]
sources = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*"
python_classes = "Test*"
python_functions = "test_*"

[tool.ruff]
line-length = 100
target-version = "py310"
```

#### 3. Create main application entrypoint
**File**: `backend/fastapi/src/plant_tracking_api/main.py`
**Changes**: Create FastAPI app with health check endpoint

```python
from fastapi import FastAPI
from plant_tracking_api.routes import health

app = FastAPI(
    title="Plant Tracking API",
    description="Backend API for plant tracking home page",
    version="0.1.0",
)

app.include_router(health.router, tags=["health"])
```

#### 4. Create health check route
**File**: `backend/fastapi/src/plant_tracking_api/routes/health.py`
**Changes**: Create health check endpoint

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Plant Tracking API"}
```

#### 5. Create package init files
**File**: `backend/fastapi/src/plant_tracking_api/__init__.py`
**Changes**: Make src a Python package

```python
"""Plant Tracking API package."""
```

**File**: `backend/fastapi/src/plant_tracking_api/routes/__init__.py`
**Changes**: Make routes a Python package

```python
"""API routes package."""
```

### Success Criteria:

#### Automated Verification:
- [ ] Package installs successfully: `uv pip install -e backend/fastapi`
- [ ] FastAPI server starts: `uvicorn plant_tracking_api.main:app --reload`
- [ ] Health check endpoint responds: `curl http://localhost:8000/health` returns `{"status":"healthy"}`
- [ ] Root endpoint responds: `curl http://localhost:8000/` returns `{"message":"Plant Tracking API"}`
- [ ] All automated tests pass: `uv run pytest backend/fastapi/tests/`
- [ ] Linting passes: `ruff check backend/fastapi/src/`
- [ ] Type checking passes: `mypy backend/fastapi/src/`

#### Manual Verification:
- [ ] Server starts without errors and binds to port 8000
- [ ] Health check endpoint returns expected JSON response
- [ ] API documentation is available at `/docs` endpoint

---

## Phase 2: UnitOfWork Dependency and Plant Service Integration

### Overview
Create a UnitOfWork dependency for FastAPI that integrates with the existing plant_service package, and implement the care-needed endpoint skeleton.

### Changes Required:

#### 1. Create UnitOfWork dependency
**File**: `backend/fastapi/src/plant_tracking_api/dependencies.py`
**Changes**: Create dependency that provides UnitOfWork instances

```python
from typing import Generator
from fastapi import Depends
from plant_service.bootstrap import create_unit_of_work
from plant_service.adapters.repository.uow import SqlAlchemyUnitOfWork


def get_uow() -> Generator[SqlAlchemyUnitOfWork, None, None]:
    """Dependency that provides a UnitOfWork instance per request."""
    uow = create_unit_of_work()  # reads DATABASE_URL from environment
    try:
        yield uow
    finally:
        # UnitOfWork context manager handles session cleanup
        # but we need to ensure it's properly exited
        pass  # The caller should use 'with uow:' pattern
```

#### 2. Update main app to include plant routes
**File**: `backend/fastapi/src/plant_tracking_api/main.py`
**Changes**: Import and include plant routes

```python
from fastapi import FastAPI
from plant_tracking_api.routes import health, plants

app = FastAPI(
    title="Plant Tracking API",
    description="Backend API for plant tracking home page",
    version="0.1.0",
)

app.include_router(health.router, tags=["health"])
app.include_router(plants.router, prefix="/api/plants", tags=["plants"])
```

#### 3. Create plants route with care-needed endpoint
**File**: `backend/fastapi/src/plant_tracking_api/routes/plants.py`
**Changes**: Create endpoint for care-needed plants

```python
from fastapi import APIRouter, Depends
from plant_service.adapters.repository.uow import SqlAlchemyUnitOfWork
from plant_tracking_api.dependencies import get_uow

router = APIRouter()


@router.get("/care-needed")
async def get_plants_needing_care(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    """
    Get plants needing care attention today.
    
    Returns mock data or empty response until care threshold logic is defined.
    """
    # TODO: Implement actual care logic once thresholds are defined
    # For now, return empty response as specified
    
    return {
        "count": 0,
        "plants": []
    }
```

#### 4. Create route init file
**File**: `backend/fastapi/src/plant_tracking_api/routes/__init__.py`
**Changes**: Update to export both routers

```python
"""API routes package."""
from .health import router as health_router
from .plants import router as plants_router

__all__ = ["health_router", "plants_router"]
```

#### 5. Add tests for the new endpoint
**File**: `backend/fastapi/tests/test_plants.py`
**Changes**: Create test file for plants endpoint

```python
from fastapi.testclient import TestClient
from plant_tracking_api.main import app


def test_get_plants_needing_care_returns_empty():
    """Test that care-needed endpoint returns empty response."""
    client = TestClient(app)
    response = client.get("/api/plants/care-needed")
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["plants"] == []


def test_health_check_endpoint():
    """Test that health check endpoint works."""
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### Success Criteria:

#### Automated Verification:
- [ ] Package installs successfully with new dependencies
- [ ] Care-needed endpoint responds: `curl http://localhost:8000/api/plants/care-needed` returns `{"count":0,"plants":[]}`
- [ ] Health check endpoint still works
- [ ] All automated tests pass including new plant tests
- [ ] Linting passes
- [ ] Type checking passes

#### Manual Verification:
- [ ] Server starts with both health and plant routes available
- [ ] Care-needed endpoint returns properly formatted JSON
- [ ] OpenAPI docs show the new endpoint at `/docs`

---

## Phase 3: Testing, Configuration, and Project Integration

### Overview
Add proper configuration management, integrate with project's Justfile for testing, and ensure the service follows project conventions.

### Changes Required:

#### 1. Create configuration module
**File**: `backend/fastapi/src/plant_tracking_api/config.py`
**Changes**: Handle configuration from environment variables

```python
import os
from typing import Optional


class Settings:
    """Application settings."""
    
    def __init__(self):
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.reload: bool = os.getenv("RELOAD", "false").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "info")


settings = Settings()
```

#### 2. Update main app to use configuration
**File**: `backend/fastapi/src/plant_tracking_api/main.py`
**Changes**: Use settings for Uvicorn configuration

```python
import uvicorn
from fastapi import FastAPI
from plant_tracking_api.config import settings
from plant_tracking_api.routes import health, plants

app = FastAPI(
    title="Plant Tracking API",
    description="Backend API for plant tracking home page",
    version="0.1.0",
)

app.include_router(health.router, tags=["health"])
app.include_router(plants.router, prefix="/api/plants", tags=["plants"])


if __name__ == "__main__":
    uvicorn.run(
        "plant_tracking_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level,
    )
```

#### 3. Add Justfile targets for the new service
**File**: `Justfile` (append to existing)
**Changes**: Add targets for testing, linting, and running the API service

```bash
# FastAPI backend service
api-install:
	uv pip install -e backend/fastapi

api-test:
	uv run pytest backend/fastapi/tests/ -v

api-lint:
	ruff check backend/fastapi/src/

api-format:
	black backend/fastapi/src/

api-format-check:
	black --check backend/fastapi/src/

api-type-check:
	mypy backend/fastapi/src/

api-run:
	uv run uvicorn plant_tracking_api.main:app --reload

api-check: api-lint api-format-check api-type-check api-test
```

#### 4. Create test configuration
**File**: `backend/fastapi/tests/conftest.py`
**Changes**: Set up test fixtures and environment

```python
import os
import pytest
from plant_tracking_api.main import app


@pytest.fixture(autouse=True)
def set_test_env():
    """Set test environment variables."""
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test_plant_tracking"
    yield
    # Clean up after test
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]


@pytest.fixture
def client():
    """Create test client."""
    from fastapi.testclient import TestClient
    return TestClient(app)
```

#### 5. Update plants test to use fixture
**File**: `backend/fastapi/tests/test_plants.py`
**Changes**: Use test client fixture

```python
def test_get_plants_needing_care_returns_empty(client):
    """Test that care-needed endpoint returns empty response."""
    response = client.get("/api/plants/care-needed")
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["plants"] == []


def test_health_check_endpoint(client):
    """Test that health check endpoint works."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### Success Criteria:

#### Automated Verification:
- [ ] New Justfile targets work: `just api-install`, `just api-test`, etc.
- [ ] All tests pass with test client fixture
- [ ] Configuration loads from environment variables
- [ ] Service can be run with `just api-run`
- [ ] All linting and type checking passes
- [ ] Project-level `just check` still works (or add API checks to it)

#### Manual Verification:
- [ ] Service starts correctly with `just api-run`
- [ ] Environment variables affect service behavior (port, host, etc.)
- [ ] API documentation accessible at `/docs`
- [ ] Health check and care-needed endpoints work as expected

## Testing Strategy

### Unit Tests:
- Test health check endpoint returns correct response
- Test care-needed endpoint returns expected JSON structure
- Test that UnitOfWork dependency is properly injected
- Test configuration loading from environment variables

### Integration Tests:
- Test that the service can start and accept connections
- Test endpoint responses with actual HTTP calls (using TestClient)
- Test error handling (though minimal for this initial implementation)

### Manual Testing Steps:
1. Install the service: `just api-install`
2. Run tests: `just api-test`
3. Start the service: `just api-run`
4. In another terminal, test endpoints:
   - `curl http://localhost:8000/health`
   - `curl http://localhost:8000/api/plants/care-needed`
5. Verify JSON responses are correctly formatted
6. Check that API docs are available at `http://localhost:8000/docs`
7. Stop the service and verify clean shutdown

## Performance Considerations

- The endpoint currently returns static/mock data, so performance is not a concern
- When actual care logic is implemented, we'll need to:
  - Ensure database queries are efficient with proper indexing
  - Consider pagination if large numbers of plants are expected
  - Monitor response time to ensure it stays under 3 seconds (NFR-PERF-01)
  - Use connection pooling effectively through SQLAlchemy

## Migration Notes

Not applicable for this initial implementation as we're creating a new service. However, the service is designed to:
- Use the existing DATABASE_URL environment variable for configuration
- Leverage existing Alembic migrations through the plant_service package
- Follow the same database connection patterns as the existing CLI service
- Be compatible with existing deployment patterns once containerization is added

## References

- Original ticket: `knowledge/tickets/PROJ-0010.md`
- Plant service package: `packages/plant_service/`
- Project configuration: `pyproject.toml`, `Justfile`
- Architecture decisions: `knowledge/architecture/architecture-decisions.md`
- Backend container architecture: `knowledge/architecture/backend/c2-container.md`
- API design patterns: `https://github.com/geraldthewes/software-backend-wiki/` (referenced in ticket)