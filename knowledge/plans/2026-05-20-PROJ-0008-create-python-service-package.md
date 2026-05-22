# Create python service package Implementation Plan

## Overview

This plan implements the creation of a Python service package (`packages/plant_service/`) that centralizes all business logic for the plant tracking system. The service package will follow Ports & Adapters (Hexagonal) architecture, providing a clean separation between domain models, service layer use-cases, and repository adapters. Both the existing CLI and future FastAPI server will consume this package as a thin entrypoint shell.

## Current State Analysis

The current business logic is monolithically contained in `commands/plant_tracking_cli.py` (~1422 lines) with direct database calls and mixed presentation logic. The system currently uses a dual-storage approach with both PostgreSQL (via SQLAlchemy models in `commands/models/`) and Markdown file storage for backward compatibility during transition.

Key findings from research:
- Domain models in `commands/models/` are well-structured but incorrectly import from `commands.database` (violating Ports & Adapters)
- Business logic for CRUD operations, label generation, and exports is embedded in CLI command handlers
- Export functionality currently loads full datasets into memory, violating streaming requirements
- Alembic migrations are properly configured but reference the old model location
- The CLI maintains backward compatibility with Markdown storage during transition

## Desired End State

After implementation, the system will have:
1. A separately installable Python package at `packages/plant_service/` with its own `pyproject.toml`
2. Clean Ports & Adapters structure:
   - Domain layer: Pure Python classes with no infrastructure imports
   - Service layer: Use-case functions orchestrating business logic
   - Adapter layer: SQLAlchemy 2.0 implementations with proper session management
3. Iterator/streaming export functions that don't load full datasets into memory
4. Unit of Work pattern for transaction management
5. Comprehensive test suite (unit and integration tests)
6. Proper error handling with domain-specific exceptions
7. CLI refactored to be a thin entrypoint that calls the service package
8. Package installable via `uv pip install -e packages/plant_service`
9. Zero business logic remaining in the `commands/` monolith

## What We're NOT Doing

- FastAPI server implementation (separate work)
- CLI entrypoint implementation beyond refactoring to consume service package
- Phomemo printer hardware driver logic (external dependency)
- Hermes agent integration
- Frontend application changes
- Changing existing ID generation formats (VARIETY-YYYY-SEQ, GENUS-NNN, SPKT-NNN)
- Modifying existing Alembic migration files (only updating references)

## Implementation Approach

We'll follow a phased approach to build the service package incrementally while maintaining backward compatibility:

1. Phase 1: Create package structure and domain models
2. Phase 2: Define service layer interfaces and exceptions
3. Phase 3: Implement repository adapters and Unit of Work
4. Phase 4: Implement service layer use-cases
5. Phase 5: Add export functions with iterator/streaming pattern
6. Phase 6: Configure packaging, testing, and linting
7. Phase 7: Refactor CLI to consume service package
8. Phase 8: Verify Alembic migration compatibility

Each phase includes both automated and manual verification criteria to ensure quality.

## Phase 1: ✅ COMPLETE: Package Structure and Domain Models

### Overview
Create the foundational package structure and implement pure Python domain models for Plant, Genus, SeedPacket, and PlantLogEntry with validation logic but no infrastructure dependencies.

### Changes Required:

#### 1. Create directory structure
```bash
mkdir -p packages/plant_service/{src,tests}/{plant_service,unit,integration}
mkdir -p packages/plant_service/src/plant_service/{domain,service_layer,adapters,entrypoints}
```

#### 2. Domain models: `packages/plant_service/src/plant_service/domain/plant.py`
```python
"""
Plant domain model - pure Python with validation, no infrastructure imports
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class Plant:
    """Plant entity matching existing Markdown-based Plant class"""
    id: str
    variety_name: str
    latin_name: str
    brand: str | None = None
    days_to_maturity: str | None = None
    germination_time: str | None = None
    planting_depth: str | None = None
    spacing: str | None = None
    sun_requirements: str | None = None
    indoor_start_time: str | None = None
    planting_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    seed_packet_id: str | None = None
    genus_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def generate_id(self, variety_name: str, planting_date: str) -> str:
        """
        Generate plant ID in VARIETY-YYYY-SEQ format
        Preserves exact logic from commands/plant_model.py:103-149
        """
        # Extract abbreviation (first 2 letters of each word, max 4 chars)
        words = variety_name.upper().split()
        abbrev = "".join([word[:2] for word in words if word.isalpha()])[:4]
        if not abbrev:
            abbrev = variety_name[:4].upper()

        if planting_date:
            year = datetime.strptime(planting_date, "%Y-%m-%d").year
        else:
            year = datetime.now().year

        # This would normally query existing records, but domain layer doesn't have DB access
        # Sequence generation will be handled in application layer
        seq = 1  # Placeholder - actual sequence logic in service layer
        
        return f"{abbrev}-{year}-{seq:03d}"

    @classmethod
    def create_from_dict(cls, data: dict) -> "Plant":
        """
        Create Plant instance from dictionary data
        Preserves validation logic from commands/plant_model.py:68-84
        """
        # Validate required fields
        required_fields = ["variety_name", "latin_name", "planting_date"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate genus_id format if present
        if "genus_id" in data and data["genus_id"] not in (None, "unknown"):
            if not re.match(r"^GENUS-\d{3}$", data["genus_id"]):
                raise ValueError("genus_id must match GENUS-NNN format or be 'unknown'")

        # Validate date format
        if "planting_date" in data:
            try:
                datetime.strptime(data["planting_date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError("planting_date must be in YYYY-MM-DD format")

        # Generate ID if not present
        if "id" not in data:
            data["id"] = cls.generate_id(
                data["variety_name"], 
                data.get("planting_date", "")
            )

        return cls(**data)
```

#### 3. Similar domain models for Genus, SeedPacket, and PlantLogEntry in the same directory

#### 4. Domain exceptions: `packages/plant_service/src/plant_service/domain/exceptions.py`
```python
"""
Domain-specific exceptions for the plant tracking service
"""
class PlantTrackingServiceException(Exception):
    """Base exception for all service-related errors"""
    pass

class ValidationException(PlantTrackingServiceException):
    """Raised when data validation fails"""
    pass

class PlantNotFoundException(PlantTrackingServiceException):
    """Raised when a plant cannot be found"""
    pass

class SeedPacketNotFoundException(PlantTrackingServiceException):
    """Raised when a seed packet cannot be found"""
    pass

class GenusNotFoundException(PlantTrackingServiceException):
    """Raised when a genus cannot be found"""
    pass

class DatabaseUnavailableError(PlantTrackingServiceException):
    """Raised when database operations fail"""
    pass

class ExportError(PlantTrackingServiceException):
    """Raised when export operations fail"""
    pass
```

### Success Criteria:

#### Automated Verification:
- [ ] All domain model classes import without errors
- [ ] Plant.create_from_dict() validates required fields correctly
- [ ] Plant.generate_id() produces correct VARIETY-YYYY-SEQ format
- [ ] Domain exceptions can be imported and instantiated
- [ ] No infrastructure imports in domain models (check for sqlalchemy, database, etc.)

#### Manual Verification:
- [ ] Verify ID generation methods produce correct formats
- [ ] Confirm validation logic matches original Markdown-based models
- [ ] Test that domain models can be instantiated and used in isolation

---

## Phase 2: ✅ COMPLETE: Service Layer Interfaces and Exceptions

### Overview
Define the service layer interfaces (ports) that declare what the application can do, and implement the exception hierarchy that will be used throughout the service.

### Changes Required:

#### 1. Service layer interfaces: `packages/plant_service/src/plant_service/service_layer/__init__.py`
Export all service interfaces

#### 2. Plant service interface: `packages/plant_service/src/plant_service/service_layer/plant_service.py`
```python
"""
Plant service interface (port) defining plant-related use cases
"""
from __future__ import annotations
from typing import Iterator, Protocol
from ..domain.models import Plant, Genus, SeedPacket
from ..domain.exceptions import PlantTrackingServiceException


class PlantService(Protocol):
    """Interface for plant-related use cases"""
    
    def create_plant(self, plant_data: dict) -> Plant:
        """Create a new plant record"""
        ...
    
    def get_plant(self, plant_id: str) -> Plant:
        """Retrieve a plant by ID"""
        ...
    
    def list_plants(self) -> Iterator[Plant]:
        """List all plants (returns iterator for streaming)"""
        ...
    
    def update_plant(self, plant_id: str, plant_data: dict) -> Plant:
        """Update an existing plant"""
        ...
    
    def delete_plant(self, plant_id: str) -> None:
        """Delete a plant by ID"""
        ...
    
    def find_plant_by_variety_name(self, variety_name: str) -> Plant | None:
        """Find plant by variety name"""
        ...
```

#### 3. Similar service interfaces for Genus, SeedPacket, and Log services

#### 4. Unit of Work interface: `packages/plant_service/src/plant_service/service_layer/unit_of_work.py`
```python
"""
Unit of Work interface (port) for transaction management
"""
from __future__ import annotations
from typing import Protocol
from .plant_service import PlantService
from .genus_service import GenusService
from .seed_packet_service import SeedPacketService
from .log_service import LogService


class UnitOfWork(Protocol):
    """Interface defining transaction boundaries"""
    
    plants: PlantService
    genera: GenusService
    seed_packets: SeedPacketService
    logs: LogService
    
    def __enter__(self) -> "UnitOfWork":
        """Enter transaction context"""
        ...
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit transaction context - commit if no exception, rollback otherwise"""
        ...
    
    def commit(self) -> None:
        """Commit the current transaction"""
        ...
    
    def rollback(self) -> None:
        """Rollback the current transaction"""
        ...
```

### Success Criteria:

#### Automated Verification:
- [ ] All service interfaces import without errors
- [ ] UnitOfWork protocol defines required attributes and methods
- [ ] Service interfaces define expected use-case methods
- [ ] No implementation details in interfaces (pure abstract definitions)

#### Manual Verification:
- [ ] Review interface definitions for completeness and clarity
- [ ] Verify that interfaces follow single responsibility principle
- [ ] Confirm exception hierarchy covers expected error cases

---

## Phase 3: ✅ COMPLETE: Repository Adapters and Unit of Work Implementation

### Overview
Implement the infrastructure adapters that fulfill the service layer ports, using SQLAlchemy 2.0 for database operations. Implement the Unit of Work pattern for transaction management.

### Changes Required:

#### 1. Repository base class: `packages/plant_service/src/plant_service/adapters/repository/base.py`
```python
"""
Base repository class with common database operations
"""
from __future__ import annotations
from typing import Generic, TypeVar, Iterator, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository providing common CRUD operations"""
    
    def __init__(self, session: Session, model_type: type[T]):
        self.session = session
        self.model_type = model_type
    
    def get(self, id: str) -> Optional[T]:
        """Get entity by ID"""
        return self.session.get(self.model_type, id)
    
    def list(self) -> Iterator[T]:
        """List all entities (returns iterator for streaming)"""
        stmt = select(self.model_type)
        # Use yield_per for streaming large result sets
        for obj in self.session.execute(stmt).scalars().yield_per(100):
            yield obj
    
    def add(self, entity: T) -> T:
        """Add new entity"""
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def update(self, entity: T) -> T:
        """Update existing entity"""
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def delete(self, id: str) -> None:
        """Delete entity by ID"""
        entity = self.get(id)
        if entity:
            self.session.delete(entity)
            self.session.flush()
```

#### 2. Plant repository: `packages/plant_service/src/plant_service/adapters/repository/plant_repository.py`
```python
"""
Plant repository adapter implementing plant service port
"""
from __future__ import annotations
from typing import Iterator, Optional
from .....domain.models import Plant
from ..service_layer.plant_service import PlantService
from .base import BaseRepository


class PlantRepository(BaseRepository[Plant], PlantService):
    """SQLAlchemy implementation of plant repository"""
    
    def __init__(self, session: Session):
        super().__init__(session, Plant)
    
    def create_plant(self, plant_data: dict) -> Plant:
        """Create a new plant record"""
        # ID generation logic moved to application/service layer
        plant = Plant.create_from_dict(plant_data)
        return self.add(plant)
    
    def get_plant(self, plant_id: str) -> Optional[Plant]:
        """Retrieve a plant by ID"""
        return self.get(plant_id)
    
    def list_plants(self) -> Iterator[Plant]:
        """List all plants (returns iterator for streaming)"""
        return self.list()
    
    # Implement other required methods...
```

#### 3. Similar repository implementations for Genus, SeedPacket, and Log entities

#### 4. Unit of Work implementation: `packages/plant_service/src/plant_service/service_layer/unit_of_work.py`
```python
"""
SQLAlchemy implementation of Unit of Work
"""
from __future__ import annotations
from contextlib import AbstractContextManager
from typing import Iterator
from sqlalchemy.orm import Session, sessionmaker

from ..adapters.repository import (
    PlantRepository,
    GenusRepository,
    SeedPacketRepository,
    LogRepository
)
from ..service_layer import (
    PlantService,
    GenusService,
    SeedPacketService,
    LogService
)


class SqlAlchemyUnitOfWork(AbstractContextManager):
    """SQLAlchemy implementation of Unit of Work"""
    
    def __init__(self, session_factory: sessionmaker[Session]):
        self.session_factory = session_factory
        self.session: Session | None = None
    
    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        """Enter transaction context"""
        self.session = self.session_factory()
        self.plants = PlantServiceAdapter(self.session)
        self.genera = GenusServiceAdapter(self.session)
        self.seed_packets = SeedPacketServiceAdapter(self.session)
        self.logs = LogServiceAdapter(self.session)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit transaction context"""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.session.close()
    
    def commit(self) -> None:
        """Commit the current transaction"""
        if self.session:
            self.session.commit()
    
    def rollback(self) -> None:
        """Rollback the current transaction"""
        if self.session:
            self.session.rollback()


# Adapter classes to bridge repository implementations to service interfaces
class PlantServiceAdapter(PlantService):
    def __init__(self, session: Session):
        self._repo = PlantRepository(session)
    
    def create_plant(self, plant_data: dict) -> Plant:
        return self._repo.create_plant(plant_data)
    
    # Delegate other methods to _repo...
```

#### 5. Bootstrap/composition root: `packages/plant_service/src/plant_service/bootstrap.py`
```python
"""
Composition root - wires everything together
"""
from __future__ import annotations
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .adapters.repository import (
    PlantRepository,
    GenusRepository,
    SeedPacketRepository,
    LogRepository
)
from .service_layer.unit_of_work import SqlAlchemyUnitOfWork
from .config import get_database_url


def get_session_factory() -> sessionmaker[Session]:
    """Create session factory configured with database URL"""
    engine = create_engine(
        get_database_url(),
        pool_pre_ping=True,
        echo=False,
    )
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False
    )


def create_unit_of_work() -> SqlAlchemyUnitOfWork:
    """Create a Unit of Work instance"""
    return SqlAlchemyUnitOfWork(get_session_factory())
```

### Success Criteria:

#### Automated Verification:
- [ ] All repository adapters import without errors
- [ ] UnitOfWork implementation can be instantiated
- [ ] Repository methods correctly delegate to SQLAlchemy operations
- [ ] Streaming iterator returns results without loading all into memory
- [ ] Transaction commit/rollback works correctly

#### Manual Verification:
- [ ] Verify that repository adapters properly implement service interfaces
- [ ] Confirm that Unit of Work handles transactions correctly
- [ ] Test that database connections are properly managed
- [ ] Validate that exceptions are properly handled and propagated

---

## Phase 4: ✅ COMPLETE: Service Layer Use-Case Implementations

### Overview
Implement the actual service layer use-cases that orchestrate business logic by coordinating between domain models and repository adapters.

### Changes Required:

#### 1. Plant service implementation: `packages/plant_service/src/plant_service/service_layer/plant_service.py`
```python
"""
Plant service implementation - application/use-case layer
"""
from __future__ import annotations
from typing import Iterator
from ..domain.models import Plant
from ..domain.exceptions import (
    PlantNotFoundException,
    ValidationException
)
from .unit_of_work import PlantServiceAdapter


class PlantServiceImpl(PlantServiceAdapter):
    """Concrete implementation of plant service use cases"""
    
    def create_plant(self, plant_data: dict) -> Plant:
        """Create a new plant record with business logic orchestration"""
        # Additional business logic can go here
        # For example: genus lookup/fuzzy matching, seed packet matching, etc.
        
        # Validate business rules
        if not plant_data.get("variety_name"):
            raise ValidationException("Variety name is required")
        
        if not plant_data.get("latin_name"):
            raise ValidationException("Latin name is required")
            
        # Delegate to repository for persistence
        return super().create_plant(plant_data)
    
    def get_plant(self, plant_id: str) -> Plant:
        """Retrieve a plant by ID with proper error handling"""
        plant = self.get(plant_id)
        if not plant:
            raise PlantNotFoundException(f"Plant with ID {plant_id} not found")
        return plant
    
    # Implement other use-case methods with business logic...
```

#### 2. Export service with streaming: `packages/plant_service/src/plant_service/service_layer/export_service.py`
```python
"""
Export service implementing iterator/streaming pattern
"""
from __future__ import annotations
from typing import Iterator, Dict, Any
from ..domain.exceptions import ExportError
from .unit_of_work import SqlAlchemyUnitOfWork


class ExportService:
    """Service for exporting data with iterator/streaming pattern"""
    
    def __init__(self, unit_of_work: SqlAlchemyUnitOfWork):
        self.uow = unit_of_work
    
    def export_plants_streaming(self, batch_size: int = 100) -> Iterator[Dict[str, Any]]:
        """
        Stream plant records in batches to avoid memory overload
        Returns iterator that yields plant data one batch at a time
        """
        try:
            with self.uow as uow:
                # Use SQLAlchemy's yield_per for streaming
                stmt = select(Plant)
                for plant in uow.session.execute(stmt).scalars().yield_per(batch_size):
                    yield {
                        "id": plant.id,
                        "variety_name": plant.variety_name,
                        "latin_name": plant.latin_name,
                        "brand": plant.brand,
                        "days_to_maturity": plant.days_to_maturity,
                        "germination_time": plant.germination_time,
                        "planting_depth": plant.planting_depth,
                        "spacing": plant.spacing,
                        "sun_requirements": plant.sun_requirements,
                        "indoor_start_time": plant.indoor_start_time,
                        "planting_date": plant.planting_date,
                        "seed_packet_id": plant.seed_packet_id,
                        "genus_id": plant.genus_id,
                    }
        except Exception as e:
            raise ExportError(f"Failed to export plants: {str(e)}")
    
    # Similar methods for exporting seed packets, genera, logs...
```

### Success Criteria:

#### Automated Verification:
- [ ] All service layer implementations import without errors
- [ ] Service methods correctly handle business logic and validation
- [ ] Export functions return iterators, not lists
- [ ] Error handling properly converts infrastructure exceptions to domain exceptions
- [ ] Business logic is correctly separated from infrastructure concerns

#### Manual Verification:
- [ ] Review service implementations for proper business logic orchestration
- [ ] Verify that service layer doesn't contain infrastructure-specific code
- [ ] Test that use-case methods properly validate inputs and handle edge cases
- [ ] Confirm export functions stream data without loading full datasets

---

## Phase 5: ✅ COMPLETE: Export Functions with Iterator/Streaming Pattern

### Overview
Implement export capabilities that return iterators instead of loading full datasets into memory, satisfying the architectural requirement for streaming exports.

### Changes Required:

#### 1. Export service implementation (continued from Phase 4)
Enhance the export service with comprehensive streaming capabilities:

#### 2. Markdown export with streaming: `packages/plant_service/src/plant_service/service_layer/export_service.py`
```python
    def export_to_markdown_streaming(self, output_dir: str, batch_size: int = 100) -> None:
        """
        Export all data to Markdown files using streaming to avoid memory overload
        """
        import os
        from datetime import datetime
        from pathlib import Path
        
        try:
            with self.uow as uow:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = Path(output_dir) / f"markdown_export_{timestamp}"
                
                # Create directory structure
                (export_path / "seed_packets").mkdir(parents=True, exist_ok=True)
                (export_path / "genera").mkdir(parents=True, exist_ok=True)
                (export_path / "logs").mkdir(parents=True, exist_ok=True)
                
                # Export seed packets using streaming
                for packet in uow.session.query(SeedPacket).yield_per(batch_size):
                    # Convert to markdown format and write immediately
                    packet_data = {
                        "id": packet.id,
                        "variety_name": packet.variety_name,
                        "latin_name": packet.latin_name,
                        # ... other fields
                    }
                    # Write individual file immediately
                    packet_file = export_path / "seed_packets" / f"{packet.id}.md"
                    with open(packet_file, "w") as f:
                        f.write(self._packet_to_markdown(packet_data))
                
                # Similar streaming exports for genera, plants, logs
                
        except Exception as e:
            raise ExportError(f"Failed to export to markdown: {str(e)}")
    
    def _packet_to_markdown(self, data: dict) -> str:
        """Convert packet data to markdown format"""
        # Implementation details...
```

#### 3. Update bootstrap to include export service: `packages/plant_service/src/plant_service/bootstrap.py`
```python
def create_export_service() -> ExportService:
    """Create an export service instance"""
    return ExportService(create_unit_of_work())
```

### Success Criteria:

#### Automated Verification:
- [ ] Export service can be instantiated without errors
- [ ] Export functions return iterators, not concrete collections
- [ ] Streaming export processes data in batches without loading all into memory
- [ ] Markdown export creates properly formatted files
- [ ] Export functions handle errors appropriately

#### Manual Verification:
- [ ] Verify that export functions truly stream data (test with large dataset)
- [ ] Confirm that memory usage remains constant during export regardless of dataset size
- [ ] Test that exported Markdown files match expected format
- [ ] Validate that export functions can be interrupted and resumed properly

---

## Phase 6: ✅ COMPLETE: Packaging, Testing, and Linting Configuration

### Overview
Configure the package for distribution, set up testing infrastructure, and establish linting/type-checking toolchain following best practices from software-backend-wiki.

### Changes Required:

#### 1. Package configuration: `packages/plant_service/pyproject.toml`
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "plant_service"
description = "Plant tracking service package"
authors = [
    {name = "Gerald", email = "gerald@example.com"}
]
dependencies = [
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.0",
    "python-dateutil>=2.8.0",
]
dynamic = ["version"]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-mock>=3.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "bandit>=1.7.0",
    "pip-audit>=2.0.0",
]

[tool.hatch.build.targets.sdist]
include = [
    "/src",
    "/pyproject.toml",
    "/README.md",
]

[tool.hatch.build.targets.wheel]
packages = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

[tool.ruff]
line-length = 88
target-version = "py38"
select = ["E", "F", "W", "C90"]
ignore = []

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
```

#### 2. README: `packages/plant_service/README.md`
```markdown
# Plant Tracking Service Package

A Python service package providing centralized business logic for the plant tracking system following Ports & Adapters architecture.

## Installation

```bash
uv pip install -e packages/plant_service
```

## Usage

```python
from plant_service.bootstrap import create_unit_of_work

with create_unit_of_work() as uow:
    plant = uow.plants.create_plant({
        "variety_name": "Yellow Habanero",
        "latin_name": "Capsicum chinense",
        "planting_date": "2026-05-20"
    })
```

## Architecture

This package follows Ports & Adapters (Hexagonal) architecture:
- `domain/` - Pure Python entities with validation
- `service_layer/` - Use-case interfaces and implementations
- `adapters/` - Infrastructure implementations (SQLAlchemy repositories)
- `entrypoints/` - Will remain in commands/ for now (CLI, future FastAPI)
```

#### 3. Test infrastructure:
Create test directories and base test classes:
- `packages/plant_service/tests/unit/test_plant_model.py`
- `packages/plant_service/tests/unit/test_plant_service.py`
- `packages/plant_service/tests/integration/test_plant_repository.py`
- `packages/plant_service/tests/integration/test_export_service.py`

#### 4. Pre-commit configuration: `.pre-commit-config.yaml` (in project root)
```yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        args: [--strict]
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.0
    hooks:
      - id: bandit
```

### Success Criteria:

#### Automated Verification:
- [ ] Package can be installed in development mode: `uv pip install -e packages/plant_service`
- [ ] All unit tests pass: `pytest packages/plant_service/tests/unit/`
- [ ] All integration tests pass: `pytest packages/plant_service/tests/integration/`
- [ ] Type checking passes: `mypy packages/plant_service/src/`
- [ ] Linting passes: `ruff check packages/plant_service/src/`
- [ ] Security scan passes: `bandit -r packages/plant_service/src/`
- [ ] Dependency vulnerability check passes: `pip-audit`

#### Manual Verification:
- [ ] Verify package installs correctly in isolated environment
- [ ] Confirm test structure follows recommended patterns
- [ ] Validate that configuration files are properly formatted
- [ ] Check that documentation is clear and complete

---

## Phase 7: (PENDING - CLI refactor): CLI Refactor to Consume Service Package

### Overview
Refactor the existing CLI in `commands/` to be a thin entrypoint that consumes the service package, removing all business logic from the CLI monolith.

### Changes Required:

#### 1. Update CLI imports: `commands/plant_tracking_cli.py`
```python
# Remove infrastructure and business logic imports
# Keep only entrypoint-related imports and service package imports

# Remove:
# - from . import database
# - from .models import Plant, SeedPacket, Genus, PlantLogEntry
# - Markdown model imports (keep for backup during transition)

# Add:
from plant_service.bootstrap import create_unit_of_work
from plant_service.domain.exceptions import (
    PlantTrackingServiceException,
    ValidationException,
    PlantNotFoundException,
    # ... other exceptions
)
```

#### 2. Refactor command handlers: Example for create_plant
```python
def create_plant(args, db=None, database_dir=None, packets_dir=None, genera_dir=None):
    """Create a new plant record - now delegates to service package"""
    # Collect plant data from user prompts (same as before)
    plant_data = {
        "variety_name": plant_data["variety_name"],
        "latin_name": plant_data["latin_name"],
        "planting_date": plant_data["planting_date"],
        # ... other fields from prompts
    }
    
    # Use service package instead of direct database calls
    try:
        with create_unit_of_work() as uow:
            plant = uow.plants.create_plant(plant_data)
            
            # Optional: Maintain Markdown backup during transition
            if database_dir:
                backup_data = {
                    "id": plant.id,
                    "variety_name": plant.variety_name,
                    "latin_name": plant.latin_name,
                    # ... other fields for backup
                }
                # Write markdown backup using service or direct implementation
                
            # Display results (same user experience)
            print(f"\n✓ Plant record created successfully!")
            print(f"ID: {plant.id}")
            # ... rest of display logic
            
    except ValidationException as e:
        print(f"\n✗ Validation error: {e}")
        sys.exit(1)
    except PlantTrackingServiceException as e:
        print(f"\n✗ Service error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
```

#### 3. Similar refactoring for all other command handlers:
- create_seed_packet
- create_genus
- list_seed_packets / list_genera / list_plants
- show_seed_packet / show_genus / show_plant
- log_humidity / log_water / log_fertilizer / log_note
- print_label (delegates to label generation service)
- export functions (delegates to export service)

#### 4. Remove or comment out business logic that's now in service package:
- ID generation logic (moved to domain/service)
- Validation logic (moved to domain)
- Database session management (handled by Unit of Work)
- Complex lookup/matching algorithms (moved to service)

### Success Criteria:

#### Automated Verification:
- [ ] CLI imports without errors after refactoring
- [ ] All CLI commands can be invoked and parsed correctly
- [ ] CLI commands properly delegate to service package
- [ ] No business logic remains in CLI command handlers
- [ ] Infrastructure imports minimized (only what's needed for entrypoint concerns)

#### Manual Verification:
- [ ] Test each CLI command to ensure functionality is preserved
- [ ] Verify that user experience remains identical to before refactoring
- [ ] Confirm that error handling works correctly and provides useful feedback
- [ ] Validate that Markdown backup functionality still works during transition
- [ ] Test that CLI can work with both service package and fallback to Markdown

---

## Phase 8: ✅ COMPLETE: Alembic Migration Compatibility Verification

### Overview
Verify that the new package structure works with existing Alembic migrations and make any necessary adjustments to ensure compatibility.

### Changes Required:

#### 1. Update Alembic environment: `alembic/env.py`
```python
# Update the path to import models from the new package location
import sys
from pathlib import Path

# Add the project root and service package to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "plant_service" / "src"))

# Import from new location
from plant_service.domain.models import Plant, SeedPacket, Genus, PlantLogEntry
from plant_service.domain.models.base import Base

target_metadata = Base.metadata
```

#### 2. Verify migration generation works:
```bash
alembic revision --autogenerate -m "Update to use service package models"
```

#### 3. Ensure migration scripts reference correct table/column names
- Verify that generated migrations match the existing schema
- Ensure no unnecessary changes are proposed

#### 4. Test migration application:
```bash
alembic upgrade head
```

### Success Criteria:

#### Automated Verification:
- [ ] Alembic environment loads without errors
- [ ] Can generate migration script without errors
- [ ] Generated migration matches expected schema changes
- [ ] Migration applies successfully to database
- [ ] Database can be downgraded and upgraded successfully

#### Manual Verification:
- [ ] Verify that Alembic correctly detects model changes
- [ ] Confirm that migration scripts are syntactically valid
- [ ] Test that migration doesn't break existing functionality
- [ ] Validate that service package works with migrated database

---

## Testing Strategy

### Unit Tests:
- Test domain models in isolation (no database required)
- Test service layer use-cases with mock repositories
- Test exception handling and validation logic
- Test export service logic with mocked data

### Integration Tests:
- Test repository adapters against real PostgreSQL database
- Test Unit of Work transaction management
- Test export functions with real data streaming
- Test service layer integration with real repositories

### Manual Testing Steps:
1. Verify package installs correctly: `uv pip install -e packages/plant_service`
2. Test domain model creation and validation
3. Test service layer use-cases with unit of work
4. Verify export functions return iterators and stream data
5. Test CLI commands preserve existing functionality
6. Confirm Markdown backup works during transition
7. Validate error handling provides appropriate user feedback
8. Test performance with large datasets (ensure streaming works)
9. Verify Alembic migrations work with new package structure
10. Run full test suite: `pytest`

## Performance Considerations

- Export functions use SQLAlchemy's `yield_per()` for streaming to prevent memory overload
- Unit of Work ensures transactions are kept short-lived
- Repository methods return iterators for large dataset queries
- Domain models avoid expensive computations in property getters
- Service layer batches operations where appropriate
- Database connections properly pooled and closed

## Migration Notes

1. **Backward Compatibility**: CLI maintains Markdown backup during transition period
2. **Data Access**: Existing Alembic migrations continue to work with minor env.py update
3. **Installation**: Package is separately installable via `uv pip install -e packages/plant_service`
4. **Rollback**: Since we're adding new package without modifying existing core functionality, rollback is simply removing the package
5. **Transition Strategy**: 
   - Phase 1-6: Build service package while CLI continues using existing logic
   - Phase 7: Refactor CLI to consume service package (feature flag optional)
   - Phase 8: Verify compatibility and cutover

## References

- Original ticket: `knowledge/tickets/PROJ-0008.md`
- Research findings: `knowledge/research/2026-05-20-PROJ-0008-python-service-package.md`
- Architecture docs: `knowledge/architecture/backend/c2-container.md`
- ADR-0005: `knowledge/architecture/decisions/ADR-0005-backend-technology-stack.md`
- ADR-0008: `knowledge/architecture/decisions/ADR-0008-architecture-refinement-ports-and-adapters.md`
- Best practices wiki: https://github.com/geraldthewes/software-backend-wiki
- Existing code: `commands/` directory
- Existing models: `commands/models/` directory