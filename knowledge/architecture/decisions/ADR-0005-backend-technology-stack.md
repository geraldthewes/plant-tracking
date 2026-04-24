---
title: ADR-0005 - Backend Technology Stack
---

# Backend Technology Stack for Plant Tracking System

## Status
Accepted

## Context
We need to select the backend technology stack for the Plant Tracking System that supports:
- RESTful API for frontend communication
- QR code generation
- Bluetooth communication with Phomemo M120 printer
- Data storage and retrieval (initially markdown, later PostgreSQL)
- Integration with Hermes agent via Telegram Bot API
- Docker containerization for consistent deployment

The backend must be maintainable by a single developer and leverage familiar technologies.

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

## Consequences
### Positive
- Leverages developer familiarity with Python ecosystem
- FastAPI provides high performance and automatic API documentation
- Docker ensures consistent environments and easy deployment
- Asynchronous capabilities support concurrent operations
- Rich Python libraries for QR, Bluetooth, and Telegram integration
- Clear migration path from markdown to PostgreSQL

### Negative
- Python may have higher memory usage than some alternatives (e.g., Go)
- Asynchronous programming requires learning curve for some developers
- Docker adds complexity for simple deployment
- Bluetooth library compatibility may vary across Linux distributions

## Related NFRs
- NFR-PERF-02: Hermes agent queries return insights within 10 seconds
- NFR-RELI-01: Data integrity with zero lost records
- NFR-DATA-02: Export/import functionality in standard formats
- NFR-MAINT-01: Graceful degradation when optional features unavailable

## Relationships
None