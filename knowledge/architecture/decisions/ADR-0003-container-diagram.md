---
title: ADR-0003 - Container Diagram
---

# Container Diagram for Plant Tracking System

## Status
Accepted

## Context
We need to define the deployable building blocks of the Plant Tracking System and how they communicate. This C2 diagram shows the containers within the system boundary.

## Decision
We chose to model the following containers:
- **Gardener (Actor)**: The home gardener using the system
- **Mobile App Frontend**: Next.js/React interface for data entry and retrieval
- **QR Code Service**: Generates QR codes for plant IDs
- **Print Service**: Handles Bluetooth communication with Phomemo M120 printer
- **Data Storage Service**: Manages plant records in markdown files
- **Hermes Agent Interface**: Communicates with Hermes agent via Telegram Bot API
- **External Systems**: Telegram Service, Phomemo M120 Printer, Seed Packet Data Source

## Consequences
### Positive
- Clear separation of concerns with specialized containers
- Each container can be developed, deployed, and scaled independently
- Technology choices are explicit in container labels
- Communication pathways are well-defined
- Supports microservices architecture with Docker containerization

### Negative
- Increased operational complexity compared to monolith
- Network overhead between containers
- Requires service discovery and load balancing considerations
- Data consistency challenges across services

## Related NFRs
- NFR-PERF-02: Hermes agent queries return insights within 10 seconds
- NFR-RELI-01: Data integrity with zero lost records
- NFR-DATA-02: Export/import functionality in standard formats
- NFR-MAINT-01: Graceful degradation when optional features unavailable

## Relationships
None

## Diagram
```mermaid
---
title: C2 Container Diagram for Plant Tracking System
---
flowchart LR
    gardener(["Gardener\n(Actor)"])

    subgraph sys["Plant Tracking System"]
        frontend["Mobile App Frontend\n(Next.js/React, Docker)"]
        qr["QR Code Service\n(Python, Docker)"]
        printer["Print Service\n(Python, Docker)"]
        storage["Data Storage Service\n(Python, Docker)"]
        hermes_interface["Hermes Agent Interface\n(Python, Docker)"]
        db[("Markdown Storage\n(Local Files)")]
    end

    telegram[["Telegram Service\n(External)"]]
    phomemo[["Phomemo M120 Printer\n(External)"]]
    seed[["Seed Packet Data Source\n(External)"]]

    gardener -->|"Uses interface via HTTPS"| frontend
    frontend -->|"Requests QR code via REST/HTTPS"| qr
    frontend -->|"Submits plant data via REST/HTTPS"| storage
    frontend -->|"Queries Hermes agent via REST/HTTPS"| hermes_interface
    qr -->|"Returns QR code via REST/HTTPS"| frontend
    printer -->|"Prints label via Bluetooth"| phomemo
    storage -->|"Reads/writes plant data via file I/O"| db
    hermes_interface -->|"Sends queries via Telegram Bot API"| telegram
    hermes_interface -->|"Receives insights via Telegram Bot API"| telegram
    storage -.->|"Retrieves variety information from"| seed
```