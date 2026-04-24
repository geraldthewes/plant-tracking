# ADR-0001 - Technology Stack Selection

## Status

Accepted - This technology stack selection has been reviewed and approved as the
foundation for the Plant Tracking System. The decision represents a careful balance
between development efficiency, system capabilities, and long-term maintainability.
The selected technologies align with the project's greenfield nature and single
developer constraints while providing a clear migration path for future enhancements.

## Context

We need to select a technology stack for the Plant Tracking System that supports:
- Mobile-friendly interfaces for garden use
- QR code generation and scanning capabilities
- Integration with Phomemo M120 Bluetooth label printer
- Natural language querying via Hermes agent through Telegram
- Data storage and retrieval for plant records
- Offline capabilities for garden environments
- Cross-platform accessibility

The system must be maintainable by a single developer and leverage existing tools
mentioned in the PRD (Phomemo M120, Hermes agent, Telegram).

## Decision

We chose to use a hybrid technology stack consisting of:
- **Frontend**: Next.js with React and TypeScript for web interface (MVP),
  React Native for mobile app (Post-MVP)
- **Backend**: Python/FastAPI microservices running in Docker containers
- **Data Storage**: Local markdown files (MVP) with migration path to PostgreSQL
- **AI Integration**: Hermes agent accessed via Telegram Bot API
- **Device Integration**: Python libraries for Bluetooth communication with
  Phomemo M120
- **QR Handling**: Client-side QR code generation and scanning libraries

## Consequences

### Positive

- Leverages developer familiarity with Python and JavaScript/TypeScript ecosystems
- Enables rapid prototyping with Next.js for web interface
- Docker containerization ensures consistency across environments
- Telegram/Hermes integration provides sophisticated AI capabilities without
  custom UI
- Markdown storage is human-readable and easy to backup
- Migration path to PostgreSQL allows for scaling

### Negative

- Split stack (Python backend, JS frontend) increases context switching
- Docker adds complexity for simple deployment
- Dependence on external Hermes agent via Telegram creates external dependency
- Bluetooth printing reliability varies across devices

## Related NFRs

- NFR-PERF-02: Hermes agent queries should return insights within 10 seconds
- NFR-RELI-01: System should maintain data integrity with zero lost records
- NFR-DATA-02: Users should export/import data in standard formats
- NFR-MAINT-01: System should allow graceful degradation when optional features
  unavailable

## Relationships

None