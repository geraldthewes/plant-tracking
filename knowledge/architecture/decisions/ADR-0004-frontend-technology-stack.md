---
title: ADR-0004 - Frontend Technology Stack
---

# Frontend Technology Stack for Plant Tracking System

## Status
Accepted

## Context
We need to select the frontend technology stack for the Plant Tracking System that supports:
- QR code scanning and generation
- Photo capture for plant documentation
- Responsive design for mobile and web use
- Integration with backend services via REST/HTTPS
- Offline capabilities for garden environments (Post-MVP)
- Access to device capabilities (camera, storage)

The frontend must be maintainable by a single developer and leverage familiar technologies.

## Decision
We chose to use:
- **MVP (Web Interface)**: Next.js with React and TypeScript
  - Server-side rendering for better performance and SEO
  - TypeScript for type safety and developer productivity
  - Responsive design with Tailwind CSS
  - Deployed as a Docker container
- **Post-MVP (Mobile App)**: React Native with TypeScript
  - Cross-platform iOS and Android support
  - Access to native device capabilities (camera, Bluetooth)
  - Same business logic sharing potential with web interface
- **Shared Components**: 
  - QR code scanning library (react-qr-reader for web, react-native-camera for mobile)
  - State management with React Context or Zustand
  - Form handling with React Hook Form
  - Date handling with date-fns

## Consequences
### Positive
- Leverages developer familiarity with React ecosystem
- Enables code sharing between web and mobile (Post-MVP)
- Next.js provides excellent developer experience and performance
- TypeScript reduces runtime errors and improves maintainability
- Docker containerization ensures consistent deployment

### Negative
- Initial learning curve for Next.js if coming from plain React
- Docker adds complexity for simple web deployment
- Maintaining two codebases (web and mobile) increases effort
- React Native requires native toolchain setup (Xcode, Android Studio)

## Related NFRs
- NFR-USAB-01: Interface usable in outdoor garden conditions
- NFR-PERF-02: Hermes agent queries return insights within 10 seconds
- NFR-RELI-01: System maintains data integrity
- NFR-MAINT-01: Graceful degradation when optional features unavailable

## Relationships
None