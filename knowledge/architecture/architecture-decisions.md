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

## Sprint 4: Backend / Orchestration Container

- **API Gateway**: Node.js/Express — lightweight, fast routing for microservices orchestration
- **Plant Data Service**: Python/FastAPI — excellent for data validation and CRUD operations with automatic OpenAPI docs
- **QR and Print Service**: Python — mature libraries for QR code generation and Bluetooth communication
- **Hermes Agent**: Python — seamless integration with python-telegram-bot library for Telegram API
- **Communication Protocol**: REST over HTTPS — standardized, cacheable, and easy to debug for internal service communications
- **Printer Interface**: Bluetooth Serial Port Profile (SPP) — reliable connectivity to Phomemo M120 via Python libraries
- **Data Storage**: Local markdown files — human-readable, atomic operations with file locking for data integrity
- **Containerization**: Docker — consistent deployment across environments, independent scaling of services
- **Authentication**: Environment variables and Docker secrets — secure injection of API keys/secrets, encrypted at rest
- **Error Handling**: Circuit breaker pattern — graceful degradation for Hermes agent unavailability with fallback to cached results
- **Rate Limiting**: Token bucket algorithm — protects external services (Telegram) from abuse while allowing bursts

## Sprint 5: Database + Knowledge Base

- **API Gateway**: Python/FastAPI (Docker) — handles authentication, routing, and request/response transformation
- **Database**: PostgreSQL 15 (Docker) — primary data store for structured plant data with ACID transactions
- **Knowledge Base**: Pinecone managed service — vector database for semantic search and natural language queries
- **Communication**:
  - API Gateway ↔ Database: PostgreSQL wire protocol (libpq/TCP)
  - API Gateway ↔ Knowledge Base: REST over HTTPS
  - Client ↔ API Gateway: HTTPS/REST with JWT authentication
- **Data Integrity**: Connection pooling, backup strategies, and migration safeguards
- **Containerization**: Docker — ensures consistency and enables independent scaling
- **Authentication**:
  - API Gateway to Database: Username/password via libpq
  - API Gateway to Knowledge Base: Pinecone API key via Bearer token
  - Client to API Gateway: JWT validation (HS256, 1-hour expiry)

## Sprint 5: Database + Knowledge Base
- **API Gateway**: Python/FastAPI (Docker) — handles authentication, routing, and request/response transformation
- **Database**: PostgreSQL 15 (Docker) — primary data store for structured plant data with ACID transactions
- **Knowledge Base**: Pinecone managed service — vector database for semantic search and natural language queries
- **Communication**: 
  - API Gateway ↔ Database: PostgreSQL wire protocol (libpq/TCP)
  - API Gateway ↔ Knowledge Base: REST over HTTPS
  - Client ↔ API Gateway: HTTPS/REST with JWT authentication
- **Data Integrity**: Connection pooling, backup strategies, and migration safeguards
- **Containerization**: Docker — ensures consistency and enables independent scaling
- **Authentication**: 
  - API Gateway to Database: Username/password via libpq
  - API Gateway to Knowledge Base: Pinecone API key via Bearer token
  - Client to API Gateway: JWT validation (HS256, 1-hour expiry)

## Sprint 7: ADRs + Cross-Cutting Concerns
- Technology Stack: Hybrid (Next.js/React frontend, Python/FastAPI backend) — Leverages existing expertise and enables rapid web prototyping
- Frontend MVP: Next.js with React and TypeScript — Provides excellent developer experience and performance for web interface
- Frontend Post-MVP: React Native with TypeScript — Enables cross-platform mobile access with native device capabilities
- Backend: Python 3.9+ with FastAPI running in Docker containers — High performance with async capabilities and rich ecosystem for integrations
- Data Storage (MVP): Local markdown files — Human-readable and easy to backup with clear migration path to PostgreSQL
- AI Integration: Hermes agent accessed via Telegram Bot API — Provides sophisticated AI capabilities without custom UI
- Device Integration: Python libraries for Bluetooth communication with Phomemo M120 — Reliable connectivity for label printing in garden environments
- QR Handling: Client-side QR code generation and scanning libraries — Eliminates need for separate QR service container

## Sprint 7: ADRs + Cross-Cutting Concerns
- Technology Stack: Hybrid (Next.js/React frontend, Python/FastAPI backend) — Leverages existing expertise and enables rapid web prototyping
- Frontend MVP: Next.js with React and TypeScript — Provides excellent developer experience and performance for web interface
- Frontend Post-MVP: React Native with TypeScript — Enables cross-platform mobile access with native device capabilities
- Backend: Python 3.9+ with FastAPI running in Docker containers — High performance with async capabilities and rich ecosystem for integrations
- Data Storage (MVP): Local markdown files — Human-readable and easy to backup with clear migration path to PostgreSQL
- AI Integration: Hermes agent accessed via Telegram Bot API — Provides sophisticated AI capabilities without custom UI
- Device Integration: Python libraries for Bluetooth communication with Phomemo M120 — Reliable connectivity for label printing in garden environments
- QR Handling: Client-side QR code generation and scanning libraries — Eliminates need for separate QR service container

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