# Backend Technology Stack for Plant Tracking System


## Status

Accepted — Backend technology stack for Plant Tracking System. Architecture refined per ADR-0008 from microservices to Ports & Adapters single-service.

### Relationships

Relates to: ADR-0003 (Container Architecture — deprecated), ADR-0006 (Data Persistence Strategy), ADR-0008 (Architecture Refinement: Ports & Adapters)

## Context

We need to select the backend technology stack for the Plant Tracking System that supports RESTful API for frontend communication, QR code generation, Bluetooth communication with Phomemo M120 printer, data storage and retrieval (initially markdown, later PostgreSQL), integration with Hermes agent via Telegram Bot API, and Docker containerization for consistent deployment. The backend must be maintainable by a single developer and leverage familiar technologies. This selection impacts the system's performance, scalability, and maintainability while establishing the foundation for all backend services.

## Decision

We chose to use:
- **Language**: Python 3.9+
- **Architecture**: Ports & Adapters (Hexagonal) — single Python service with layered separation (ADR-0008)
- **Entrypoints**: CLI (argparse/click) + FastAPI for REST/HTTPS web API
- **Service Layer**: Use-case functions shared by CLI and FastAPI entrypoints
- **Domain Model**: Pure Python classes with no infrastructure imports
- **Adapters**: SQLAlchemy ORM for PostgreSQL, Alembic for migrations
- **Containerization**: Docker for consistent deployment
- **QR Generation**: Python library (qrcode) for generating QR codes
- **Bluetooth**: Python library (pybluez) for communicating with Phomemo M120 printer
- **Telegram Integration**: Python library (python-telegram-bot) for interacting with Telegram Bot API
- **Data Storage**: PostgreSQL with SQLAlchemy ORM (migrated from markdown per ADR-0006)
- **API Documentation**: OpenAPI/Swagger via FastAPI automatic docs
- **OpenAPI Export**: Automated export script (`backend/fastapi/scripts/export_openapi.py`) generates `openapi.json` without running the server
- **API Client Code Generation**: Orval — generates TypeScript API stubs from the exported OpenAPI spec, consumed by the frontend

### Alternatives Considered

- **Node.js/Express**: JavaScript backend with Express framework - Rejected because it would split the developer's expertise and limit access to Python-specific libraries for Bluetooth and QR generation
- **Go/Gin**: Go language with Gin framework - Rejected due to learning curve and fewer mature libraries for Telegram integration compared to Python
- **Django**: Python Django framework - Rejected because it's heavier than needed for our microservices approach and includes ORM we don't need initially
- **Monolithic Python**: Single Python application — Selected (refined per ADR-0008). Originally rejected for not supporting independent scaling, but re-evaluated as the correct choice for a single-developer project with one bounded context.

### Trade-offs

- **Selected Approach (Python/FastAPI/Ports & Adapters)**:
  - *Pros*: Leverages existing Python expertise, high performance with async capabilities, automatic API documentation, rich ecosystem for required integrations, shared service layer between CLI and web API
  - *Cons*: All entrypoints share same process; cannot scale individual use cases independently
- **Node.js/Express Alternative**:
  - *Pros*: Unified JavaScript/TypeScript stack, npm ecosystem
  - *Cons*: Split expertise needed (still need Python for Bluetooth/QR), fewer mature libraries for specific hardware integrations
- **Go/Gin Alternative**:
  - *Pros*: High performance, efficient memory usage, strong typing
  - *Cons*: Learning curve, less mature ecosystem for Telegram/Bluetooth integration
- **Django Alternative**:
  - *Pros*: Batteries-included, excellent ORM, mature framework
  - *Cons*: Heavier than needed, includes features we don't require, less suited for microservices
- **Monolithic Python Alternative**:
  - *Pros*: Simpler deployment, no inter-service communication overhead
  - *Cons*: Scaling bottlenecks, technology lock-in, harder to maintain as system grows

## Consequences

### Positive

- Leverages developer familiarity with Python ecosystem
- FastAPI provides high performance and automatic API documentation
- Single codebase reduces maintenance burden
- Docker ensures consistent environments and easy deployment
- Asynchronous capabilities support concurrent operations
- Rich Python libraries for QR, Bluetooth, and Telegram integration
- Shared service layer between CLI and FastAPI eliminates code duplication
- Domain model testable without database via repository pattern

### Negative

- Python may have higher memory usage than some alternatives (e.g., Go)
- Asynchronous programming requires learning curve for some developers
- Docker adds complexity for simple deployment
- Bluetooth library compatibility may vary across Linux distributions

### Related NFRs

- NFR-PERF-02: Hermes agent queries return insights within 10 seconds
- NFR-RELI-01: Data integrity with zero lost records
- NFR-DATA-02: Export/import functionality in standard formats
- NFR-MAINT-01: Graceful degradation when optional features unavailable
