---
title: ADR-0003: Container Architecture and Microservices for Plant Tracking System
---

# ADR-0003: Container Architecture and Microservices for Plant Tracking System

## Status
### Relationships
None

## Context
As the Plant Tracking System grows in functionality, we need to decide on an architectural style that allows for independent development, deployment, and scaling of different system components. The system includes concerns like API gateway, data storage, QR generation/printing, AI agent integration, and potentially frontend services. We need to choose an architectural pattern that supports our goals of maintainability, scalability, and clear separation of concerns while keeping the MVP simple enough to implement.

## Decision
We decided to use a containerized microservices architecture with Docker for all backend services. Each major concern (API Gateway, Plant Data Service, QR and Print Service, Hermes Agent) runs in its own container, communicating via well-defined REST APIs over HTTPS.

### Alternatives Considered
- Alternative 1: Monolithic architecture with all components in a single container
- Alternative 2: Serverless functions (AWS Lambda) for each service
- Alternative 3: Hybrid approach with some components combined and others separated

### Trade-offs
#### Alternative 1 (Monolithic)
- Pros: Simpler deployment (single container), easier initial development, no network latency between components
- Cons: Scaling requires scaling the entire application, tighter coupling makes changes riskier, technology lock-in for the whole system

#### Alternative 2 (Serverless Functions)
- Pros: Automatic scaling, pay-per-use pricing, reduced operational overhead
- Cons: Cold start latency affecting response times, vendor lock-in, debugging complexity, limited execution duration, challenging for long-running processes like printer operations

#### Alternative 3 (Hybrid)
- Pros: Balance of simplicity and separation, can group related functions
- Cons: Still some coupling concerns, unclear boundaries between what should be combined vs separated

## Consequences
This decision enables independent deployment and scaling of services, allowing us to update the QR printing service without affecting the data storage service, for example. It provides technology flexibility - each service can use the language/framework best suited to its purpose. However, it introduces operational complexity in managing multiple containers, network communication challenges, and the need for service discovery and load balancing (handled simply via direct REST calls in our MVP). We accept this complexity because it aligns with our long-term scalability goals and keeps services loosely coupled.

## Diagram
```mermaid
flowchart LR
    subgraph sys["Plant Tracking System"]
        api_gw["API Gateway\n(Node.js/Express, Docker)"]
        plant_ds["Plant Data Service\n(Python/FastAPI, Docker)"]
        qr_print["QR and Print Service\n(Python, Docker)"]
        hermes["Hermes Agent\n(Python, Docker)"]
        md[("Markdown Files\n(Local Storage)")]
    end

    user(["User\n(Actor)"])
    telegram[["Telegram Service\n(External)"]]

    %% Edges
    user -->|Accesses via HTTPS/REST| api_gw
    api_gw -->|Routes REST/HTTPS requests via JSON| plant_ds
    api_gw -->|Routes REST/HTTPS requests via JSON| qr_print
    api_gw -->|Routes REST/HTTPS requests via JSON| hermes
    plant_ds -->|Executes SQL queries via libpq/TCP| md
    hermes -->|Sends/receives messages via HTTPS/Telegram Bot API| telegram
    qr_print -->|Sends print job via Bluetooth Serial| printer
    printer[["Phomemo M120 Printer\n(External)"]]
```

## Related NFRs
- NFR-RELI-01: The system should maintain data integrity with zero lost or corrupted plant records under normal usage conditions
- NFR-MAINT-01: System should allow for graceful degradation when optional features (like Hermes agent) are unavailable
- NFR-DATA-03: Data should be migratable from markdown storage to Postgres format without loss of information