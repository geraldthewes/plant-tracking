# Backend Technology Stack for Plant Tracking System

## Status
Accepted - We need to select the backend technology stack for the Plant Tracking System that supports RESTful API for frontend communication, QR code generation, Bluetooth communication with Phomemo M120 printer, data storage and retrieval (initially markdown, later PostgreSQL), integration with Hermes agent via Telegram Bot API, and Docker containerization for consistent deployment. The backend must be maintainable by a single developer and leverage familiar technologies. This decision impacts the system's performance, scalability, and maintainability while establishing the foundation for all backend services.

### Relationships
None

## Context
We need to select the backend technology stack for the Plant Tracking System that supports RESTful API for frontend communication, QR code generation, Bluetooth communication with Phomemo M120 printer, data storage and retrieval (initially markdown, later PostgreSQL), integration with Hermes agent via Telegram Bot API, and Docker containerization for consistent deployment. The backend must be maintainable by a single developer and leverage familiar technologies. This selection impacts the system's performance, scalability, and maintainability while establishing the foundation for all backend services.

## Decision
We chose to use:
- **Language**: Python 3.9+
- **Framework**: FastAPI for high-performance, async-capable REST APIs
- **Containerization**: Docker for all backend services
- **Communication**: REST/HTTPS with JSON payloads for all inter-service communication
- **QR Generation**: Python library (qrcode) for generating QR codes
- **Bluetooth**: Python library (pybluez) for communicating with Phomemo M120 printer
- **Telegram Integration**: Python library (python-telegram-bot) for interacting with Telegram Bot API
- **Data Storage (MVP)**: Local markdown files with structured format
- **Data Storage (Future)**: Migration path to PostgreSQL with SQLAlchemy ORM
- **API Documentation**: OpenAPI/Swagger via FastAPI automatic docs

### Alternatives Considered
- **Node.js/Express**: JavaScript backend with Express framework - Rejected because it would split the developer's expertise and limit access to Python-specific libraries for Bluetooth and QR generation
- **Go/Gin**: Go language with Gin framework - Rejected due to learning curve and fewer mature libraries for Telegram integration compared to Python
- **Django**: Python Django framework - Rejected because it's heavier than needed for our microservices approach and includes ORM we don't need initially
- **Monolithic Python**: Single Python application instead of microservices - Rejected because it doesn't support independent scaling and deployment of services

### Trade-offs
- **Selected Approach (Python/FastAPI/Microservices)**:
  - *Pros*: Leverages existing Python expertise, high performance with async capabilities, automatic API documentation, rich ecosystem for required integrations
  - *Cons*: Requires managing multiple containers, potential overhead from containerization
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
### positive
- Leverages developer familiarity with Python ecosystem
- FastAPI provides high performance and automatic API documentation
- Docker ensures consistent environments and easy deployment
- Asynchronous capabilities support concurrent operations
- Rich Python libraries for QR, Bluetooth, and Telegram integration
- Clear migration path from markdown to PostgreSQL

### negative
- Python may have higher memory usage than some alternatives (e.g., Go)
- Asynchronous programming requires learning curve for some developers
- Docker adds complexity for simple deployment
- Bluetooth library compatibility may vary across Linux distributions

### Related NFRs
- NFR-PERF-02: Hermes agent queries return insights within 10 seconds
- NFR-RELI-01: Data integrity with zero lost records
- NFR-DATA-02: Export/import functionality in standard formats
- NFR-MAINT-01: Graceful degradation when optional features unavailable