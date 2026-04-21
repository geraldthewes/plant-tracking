## Sprint 1: C1 System Context

- System Architecture: C4 Model — visualizes system at appropriate abstraction levels for stakeholders
- Diagram Tool: Mermaid — enables version-controlled architecture diagrams in Markdown
- Data Storage Approach: Local markdown files — simple, human-readable, no external dependencies for MVP
- Label Printing: Phomemo M120 Bluetooth printer — provides durable, weather-resistant QR-coded labels via Bluetooth
- AI Integration: Hermes agent via Telegram — enables natural language querying and data analysis via Telegram Bot API
- External Data Source: Optional Weather Service — supplements environmental tracking when available via HTTPS/REST
- User Interaction: Mobile device camera for QR scanning — leverages existing hardware for accessibility

## Sprint 2: C2 Container Overview

- Frontend Framework: Next.js with React — provides SSR, SEO benefits, and React ecosystem for mobile web app
- Backend Services: Dockerized microservices — enables independent scaling and deployment of Hermes agent, QR service, and printer interface
- API Communication: REST over HTTPS — standardized, cacheable communication between frontend and backend services
- Bluetooth Communication: Direct Python Bluetooth library — reliable connectivity to Phomemo M120 printer for label printing
- External Integration: Telegram Bot API — enables natural language interaction with Hermes agent through familiar messaging interface