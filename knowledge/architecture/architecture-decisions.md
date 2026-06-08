## Sprint 1: C1 System Context

- System Architecture: C4 Model — visualizes system at appropriate abstraction levels for stakeholders
- Diagram Tool: Mermaid — enables version-controlled architecture diagrams in Markdown
- Data Storage Approach: Local markdown files — simple, human-readable, no external dependencies for MVP
- Label Printing: Phomemo M120 Bluetooth printer — provides durable, weather-resistant QR-coded labels via Bluetooth
- AI Integration: Hermes agent via Telegram — enables natural language querying and data analysis via Telegram Bot API
- External Data Source: Optional Weather Service — supplements environmental tracking when available via HTTPS/REST
- User Interaction: Mobile device camera for QR scanning — leverages existing hardware for accessibility

## Sprint 2: C2 Container Overview

- Container Architecture: Microservices with Docker — enables independent deployment and scaling of services
- Frontend Technology: Next.js with React — provides server-side rendering and optimal performance for mobile web
- Communication Protocol: REST over HTTPS — standardized, cacheable interactions between services
- Bluetooth Connectivity: Python libraries — reliable connectivity to Phomemo M120 printer
- Telegram Integration: Bot API — familiar messaging interface for natural language interaction with Hermes agent
- Data Storage: Markdown files with planned Postgres migration path — human-readable MVP with scalability option
- External Services: Telegram Service (external), Phomemo Printer Interface (external device) — clearly bounded system interactions

## Sprint 3: Frontend Container

- Mobile App Frontend: React Native [Post-MVP] — cross-platform native performance with access to device cameras and sensors
- Web Interface: Next.js with React — server-side rendered web app accessible via mobile/desktop browsers
- QR Scanner Service: Dockerized camera API wrapper — handles QR code decoding with native camera integration
- Photo Capture Service: Dockerized camera API wrapper — manages image capture and format conversion for plant documentation
- Hermes Agent Container: AI analysis via Telegram Bot API — provides natural language querying and insights generation
- Communication Protocol: HTTPS/REST with JSON and Bearer token — standardized authentication for frontend-Hermes communication
- Device Camera Access: Native module interface (mobile) / Browser Media API (web) — consistent cross-platform camera utilization
- Telegram Integration: HTTPS/Telegram Bot API with Bot token — enables natural language interaction via familiar messaging interface

## Sprint 4: Backend / Orchestration Container (Superseded)

> **Note:** This sprint's microservices approach has been superseded by Sprint 10's Ports & Adapters architecture (ADR-0008).

- **API Gateway**: Node.js/Express — originally selected for microservices orchestration (deprecated)
- **Plant Data Service**: Python/FastAPI — data validation and CRUD operations (retained as FastAPI entrypoint)
- **QR and Print Service**: Python — QR code generation and Bluetooth communication (deferred)
- **Hermes Agent**: Python — python-telegram-bot library for Telegram API (deferred)
- **Communication Protocol**: REST over HTTPS — standardized, cacheable interactions
- **Printer Interface**: Bluetooth Serial Port Profile (SPP) — Phomemo M120 connectivity (deferred)
- **Data Storage**: Local markdown files — original MVP approach (migrated to PostgreSQL)
- **Containerization**: Docker — consistent deployment across environments
- **Authentication**: Environment variables and Docker secrets — secure secret injection
- **Error Handling**: Circuit breaker pattern — graceful degradation for external service failures
- **Rate Limiting**: Token bucket algorithm — protects external services from abuse

## Sprint 5: Database + Knowledge Base

- **FastAPI Entrypoint**: Python/FastAPI (Docker) — HTTP routing, request validation, response formatting
- **Database**: PostgreSQL 15 (Docker) — primary data store for structured plant data with ACID transactions
- **Knowledge Base**: Pinecone managed service — vector database for semantic search and natural language queries (deferred)
- **Communication**:
  - FastAPI Entrypoint ↔ Database: PostgreSQL wire protocol (libpq/TCP via SQLAlchemy)
  - Service ↔ Knowledge Base: REST over HTTPS (deferred)
  - Client ↔ FastAPI: HTTPS/REST with JWT authentication (deferred)
- **Data Integrity**: Connection pooling, backup strategies, and migration safeguards
- **Containerization**: Docker — ensures consistency and enables independent scaling
- **Authentication**:
  - Service to Database: Username/password via libpq
  - Service to Knowledge Base: Pinecone API key via Bearer token (deferred)
  - Client to FastAPI: JWT validation (HS256, 1-hour expiry) (deferred)

## Sprint 5: Database + Knowledge Base
- **FastAPI Entrypoint**: Python/FastAPI (Docker) — HTTP routing, request validation, response formatting
- **Database**: PostgreSQL 15 (Docker) — primary data store for structured plant data with ACID transactions
- **Knowledge Base**: Pinecone managed service — vector database for semantic search and natural language queries (deferred)
- **Communication**: 
  - FastAPI Entrypoint ↔ Database: PostgreSQL wire protocol (libpq/TCP via SQLAlchemy)
  - Service ↔ Knowledge Base: REST over HTTPS (deferred)
  - Client ↔ FastAPI: HTTPS/REST with JWT authentication (deferred)
- **Data Integrity**: Connection pooling, backup strategies, and migration safeguards
- **Containerization**: Docker — ensures consistency and enables independent scaling
- **Authentication**: 
  - Service to Database: Username/password via libpq
  - Service to Knowledge Base: Pinecone API key via Bearer token (deferred)
  - Client to FastAPI: JWT validation (HS256, 1-hour expiry) (deferred)

## Sprint 7: ADRs + Cross-Cutting Concerns
- Technology Stack: Hybrid (Next.js/React frontend, Python/FastAPI backend) — Leverages existing expertise and enables rapid web prototyping
- Frontend MVP: Next.js with React and TypeScript — Provides excellent developer experience and performance for web interface
- Frontend Post-MVP: React Native with TypeScript — Enables cross-platform mobile access with native device capabilities
- Backend: Python 3.9+ with FastAPI running in Docker containers — High performance with async capabilities and rich ecosystem for integrations
- Data Storage (MVP): Local markdown files — Human-readable and easy to backup with clear migration path to PostgreSQL
- AI Integration: Hermes agent accessed via Telegram Bot API — Provides sophisticated AI capabilities without custom UI
- Device Integration: Python libraries for Bluetooth communication with Phomemo M120 — Reliable connectivity for label printing in garden environments
- QR Handling: Client-side QR code generation and scanning libraries — Eliminates need for separate QR service container
- API Code Generation: Orval — Auto-generates TypeScript API client stubs from FastAPI OpenAPI spec, outputting to `frontend/src/api/`

## Sprint 7: ADRs + Cross-Cutting Concerns
- Technology Stack: Hybrid (Next.js/React frontend, Python/FastAPI backend) — Leverages existing expertise and enables rapid web prototyping
- Frontend MVP: Next.js with React and TypeScript — Provides excellent developer experience and performance for web interface
- Frontend Post-MVP: React Native with TypeScript — Enables cross-platform mobile access with native device capabilities
- Backend: Python 3.9+ with FastAPI running in Docker containers — High performance with async capabilities and rich ecosystem for integrations
- Data Storage (MVP): Local markdown files — Human-readable and easy to backup with clear migration path to PostgreSQL
- AI Integration: Hermes agent accessed via Telegram Bot API — Provides sophisticated AI capabilities without custom UI
- Device Integration: Python libraries for Bluetooth communication with Phomemo M120 — Reliable connectivity for label printing in garden environments
- QR Handling: Client-side QR code generation and scanning libraries — Eliminates need for separate QR service container
- API Code Generation: Orval — Auto-generates TypeScript API client stubs from FastAPI OpenAPI spec, outputting to `frontend/src/api/`

## Sprint 8: Final ADRs and Architecture Review
- Data Persistence Strategy: Phased approach from markdown to PostgreSQL — Human-readable MVP with clear migration path to robust storage
- ADR-0006: Data Persistence Strategy document — Defines structured markdown format designed for seamless migration to PostgreSQL
- Updated ADR-0005: Fixed heading case and ensured proper formatting compliance
- Fixed heading case in all ADR files (ADR-0001 through ADR-0006) to meet contract requirements (Title Case H1, sentence case H2/H3)
- Updated C4 diagrams in ADR-0002, ADR-0003, and ADR-0004 to use standard C4-Mermaid element types (Person, System, Container, Database)
- Validated all Mermaid diagrams with mmdc (exit code 0) ensuring syntax correctness
- Architecture Review: Validated all ADRs meet sprint contract requirements including naming conventions, section content, diagram validity, and NFR traceability
- NFR Traceability: All ADRs include proper ## Related NFRs subsections with valid identifiers from nfr_catalog.json

## Sprint 9: Hermes Agent Integration
- Hermes Agent Integration Strategy: Telegram Bot API with HTTPS/REST communication — Provides natural language querying and analysis capabilities via familiar messaging interface
- ADR-0007: Hermes Agent Integration Strategy document — Defines how the system interacts with the Hermes agent via Telegram Bot AI for data analysis and insights
- Integration Approach: HTTPS/REST with JSON payloads, Bot token authentication, and graceful degradation mechanisms
- Communication Protocol: Structured data exchange via JSON extracts from markdown records
- Fallback Mechanism: Manual analysis capability when Hermes agent is unavailable

## Sprint 10: Architecture Refinement — Ports & Adapters

- Architecture Style: Ports & Adapters (Hexagonal) single-service — Replaces microservices approach from Sprint 4
- ADR-0008: Architecture Refinement document — Documents decision to consolidate from microservices to layered single service
- ADR-0003: Deprecated — Superseded by ADR-0008
- ADR-0005: Updated — Reflects single-service architecture with shared service layer
- Entrypoints: CLI (argparse/click) + FastAPI HTTP routes — Both call same service functions
- Service Layer: Use-case functions shared between CLI and web — Zero business logic duplication
- Domain Model: Pure Python with no infrastructure imports — Fully unit-testable without database
- Repository Pattern: Protocol interfaces in domain, SQLAlchemy implementations in adapters — Swappable persistence
- Unit of Work: Transaction boundaries managed by SQLAlchemy Session — Atomic commit/rollback per use case
- Rationale: Single bounded context, single developer, no team boundary justifies distributed complexity
- FastAPI Entrypoint: Implemented in `backend/fastapi/` as separate package depending on `plant_service` — See PROJ-0010