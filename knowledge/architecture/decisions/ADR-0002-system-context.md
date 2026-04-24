# ADR-0002 - System Context Diagram

## status
Accepted - We need to define the system boundary and key external interactions for the Plant Tracking System. This C1 diagram shows the system in relation to its users and external dependencies. The system boundary clearly delineates what is internal to the Plant Tracking System versus what represents external entities that the system interacts with. Understanding these boundaries is crucial for determining system responsibilities, data flows, and integration points. This foundational diagram establishes the context for all subsequent architectural decisions and provides stakeholders with a clear view of the system's ecosystem.

### relationships
None

## context
We need to define the system boundary and key external interactions for the Plant Tracking System. This C1 diagram shows the system in relation to its users and external dependencies. Understanding these boundaries helps determine what functionality belongs inside the system versus what should be handled by external services. This is essential for architecture planning, integration design, and defining system responsibilities. Clear boundaries prevent scope creep and help teams understand where the system ends and external dependencies begin.

## decision
We chose to model the Plant Tracking System as a single system with the following external entities:
- **Gardener (Actor)**: The home gardener who uses the system
- **Hermes Agent (External)**: AI agent accessed via Telegram for natural language querying and analysis
- **Phomemo M120 Printer (External)**: Bluetooth label printer for generating QR-coded labels
- **Seed Packet Data Source (External)**: Physical seed packets providing variety information
- **Weather Service (External)**: Optional service for environmental data (out of MVP scope)

### alternatives considered
- **Expanded System Boundary**: Including Hermes Agent and Phomemo Printer as internal components - Rejected because these are external services we don't own or control
- **Separate Systems for Each Function**: Modeling data storage, QR generation, and printing as separate systems - Rejected because they are tightly integrated components of our solution
- **Weather Service as Core Dependency**: Making weather data a required system input - Rejected because the PRD indicates this is optional and out of MVP scope

### trade-offs
- **Single System Boundary Selected**:
  - *Pros*: Clear separation of concerns, simple to understand, accurate representation of ownership
  - *Cons*: Hides internal complexity, requires additional diagrams to show internal structure
- **Expanded Boundary Alternative**:
  - *Pros*: Shows more detail about integrated components
  - *Cons*: Misrepresents ownership, creates confusion about what we actually build vs integrate
- **Multiple Systems Alternative**:
  - *Pros*: Shows modularity and separation of concerns
  - *Cons*: Over-complicates the context view, misrepresents the cohesive nature of our solution
- **Required Weather Service Alternative**:
  - *Pros*: Ensures weather data availability for all use cases
  - *Cons*: Creates unnecessary dependency, increases scope beyond MVP, contradicts PRD

## consequences
### positive
- Clear boundary definition shows what's internal vs external
- Identifies all key user interactions and external dependencies
- Supports understanding of data flows and system responsibilities
- Provides foundation for more detailed C2 and C3 diagrams

### negative
- Simplifies internal complexity into a single system node
- Doesn't show internal architectural decisions
- External systems are treated as black boxes

## related nfrs
- NFR-USAB-01: Interface usable in outdoor garden conditions
- NFR-RELI-01: QR code scanning works 95%+ of attempts
- NFR-MAINT-01: Graceful degradation when optional features unavailable

## diagram
```mermaid
---
title: C1 System Context for Plant Tracking System
---
flowchart LR
    gardener(["Gardener\n(Actor)"])

    sys["Plant Tracking System\n(Internal System)"]

    hermes[["Hermes Agent\n(External)"]]
    phomemo[["Phomemo M120 Printer\n(External)"]]
    seed[["Seed Packet Data Source\n(External)"]]
    weather[["Weather Service\n(External)" ]]

    gardener -->|"Enters seed packet data via manual input"| sys
    gardener -->|"Scans QR code via camera"| sys
    gardener -->|"Queries Hermes agent via Telegram"| hermes
    sys -->|"Prints QR-coded label via Bluetooth"| phomemo
    sys -->|"Retrieves variety information from"| seed
    sys -.->|"Optional: Retrieves weather data via HTTPS"| weather
```