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