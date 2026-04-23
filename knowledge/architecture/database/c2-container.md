---
title: C2 Container Diagram for Plant Tracking System
---

# Plant Tracking System - C2 Container Diagram

## Scope
This diagram shows the container-level architecture for the Plant Tracking System's backend services, focusing on the Database + Knowledge Base sprint. It includes the User (actor), API Gateway, Database (PostgreSQL), and Knowledge Base Vector Store (Pinecone) containers, along with the external Telegram service used by the Hermes agent. The diagram illustrates how these components interact to support plant data storage, retrieval, and AI-powered insights.

## Architecture Overview
The system follows a containerized microservices architecture where the API Gateway acts as the single entry point for all client requests. The API Gateway handles authentication, rate limiting, and request/response transformation. It communicates with the PostgreSQL database for structured plant data storage and retrieval using the libpq protocol, and with the Pinecone vector store for semantic search and natural language querying via REST/HTTPS. The Hermes agent (accessed via Telegram) interacts with the API Gateway to provide natural language querying and analysis capabilities. All internal services are containerized using Docker for consistency and independent scaling.

## Component Details
### User
- **Technology**: Human actor
- **Description**: The gardener who interacts with the system via mobile/web interfaces and Telegram for natural language queries
- **Primary Responsibility**: Initiates requests to the system (QR scanning, data entry, Telegram queries) and receives responses
- **Input Data/Triggers**: User actions (scanning QR codes, entering plant data, sending Telegram messages)
- **Output/Downstream Effects**: Receives plant records, insights, and system responses
- **Failure/Graceful Degradation**: If the system is unavailable, the user cannot access plant data or receive insights; manual tracking may be used as fallback

### API Gateway
- **Technology**: Python/FastAPI running in Docker
- **Description**: Central orchestration service handling all external requests
- **Primary Responsibility**: Routes requests to appropriate services, manages authentication, and transforms data
- **Input Data/Triggers**: HTTP requests from users/webhooks, Telegram bot messages
- **Output/Downstream Effects**: Database queries, vector store operations, responses to clients
- **Failure/Graceful Degradation**: Implements circuit breaker pattern; if downstream services fail, returns appropriate error responses with retry-after headers

### Database
- **Technology**: PostgreSQL 15
- **Description**: Primary relational database for structured plant data
- **Primary Responsibility**: Stores plant records, care activities, observations, and metadata with ACID compliance (Atomicity, Consistency, Isolation, Durability)
- **Input Data/Triggers**: SQL queries from API Gateway (INSERT, SELECT, UPDATE, DELETE)
- **Output/Downstream Effects**: Query results, transaction confirmations
- **Failure/Graceful Degradation**: Uses connection pooling with timeout and retry mechanisms; fallback to read-only mode if write operations fail

### Knowledge Base Vector Store
- **Technology**: Pinecone managed vector database
- **Description**: External service for semantic search and similarity matching
- **Primary Responsibility**: Stores vector embeddings of plant care notes and observations for natural language querying
- **Input Data/Triggers**: Vector upsert and query requests via REST/HTTPS
- **Output/Downstream Effects**: Similarity search results, vector status
- **Failure/Graceful Degradation**: Implements health checks; falls back to PostgreSQL ILIKE (case-insensitive SQL LIKE)-based text search if unavailable

## Traceability Matrix
| PRD ID | Requirement Type | Requirement Summary | Status | Traceability (Section/Line) |
|--------|------------------|---------------------|--------|-----------------------------|
| FR6    | Functional       | Create plant records with core attributes from seed packet information | Architected | Component Details (Database) |
| FR7    | Functional       | Store plant data in markdown files with structured format | Deferred | Deferred Requirements |
| FR8    | Functional       | Add notes and observations to plant records with timestamps | Architected | Component Details (Database) |
| FR9    | Functional       | Attach photos to plant records for visual documentation | Deferred | Deferred Requirements |
| FR10   | Functional       | Update plant records with new information over time | Architected | Component Details (Database) |
| FR11   | Functional       | Store multiple plants in a searchable database format | Architected | Component Details (Database) |
| FR12   | Functional       | Retrieve complete plant records by scanning QR codes | Architected | Component Details (API Gateway) |
| FR13   | Functional       | Query plant data using natural language via Hermes agent | Architected | Component Details (Knowledge Base Vector Store) |
| FR14   | Functional       | Compare data between different plants | Architected | Component Details (Knowledge Base Vector Store) |
| FR15   | Functional       | Filter plant records by various criteria (date, variety, location, etc.) | Architected | Component Details (Database) |
| FR16   | Functional       | Export plant data for backup or analysis | Deferred | Deferred Requirements |
| FR17   | Functional       | Receive data-driven insights about plant health and care patterns | Architected | Component Details (Knowledge Base Vector Store) |
| FR18   | Functional       | Identify root causes of plant issues through data analysis | Architected | Component Details (Knowledge Base Vector Store) |
| FR19   | Functional       | Track plant progress over time (growth, flowering, fruiting) | Architected | Component Details (Database) |
| FR20   | Functional       | Receive personalized care recommendations based on plant history | Architected | Component Details (Knowledge Base Vector Store) |
| FR21   | Functional       | Detect patterns and correlations in plant care data | Architected | Component Details (Knowledge Base Vector Store) |
| FR22   | Functional       | Record watering schedules and amounts | Architected | Component Details (Database) |
| FR23   | Functional       | Record fertilizer applications (type, amount, frequency) | Architected | Component Details (Database) |
| FR24   | Functional       | Track indoor/outdoor status changes | Architected | Component Details (Database) |
| FR25   | Functional       | Monitor temperature and humidity conditions | Architected | Component Details (Database) |
| FR26   | Functional       | Record rainfall and precipitation data | Architected | Component Details (Database) |
| FR27   | Functional       | Track sunlight exposure and shade conditions | Architected | Component Details (Database) |
| FR28   | Functional       | Record soil amendments and treatments | Architected | Component Details (Database) |
| FR29   | Functional       | Document pruning, staking, and support activities | Architected | Component Details (Database) |
| FR30   | Functional       | Note pest observations and treatments | Architected | Component Details (Database) |
| FR31   | Functional       | Combine manual data entry with automated sensor data | Deferred | Deferred Requirements |
| FR32   | Functional       | Import data from external sources (weather stations, etc.) | Deferred | Deferred Requirements |
| FR33   | Functional       | Reconstruct missing data points from historical records | Architected | Component Details (Database) |
| FR34   | Functional       | Validate data quality and correct erroneous entries | Architected | Component Details (Database) |
| FR35   | Functional       | Gap-identify missing data periods in plant histories | Architected | Component Details (Database) |
| FR36   | Functional       | Interact with Hermes agent via Telegram for natural language queries | Architected | Component Details (Telegram) |
| FR37   | Functional       | Request analysis of specific plant data and conditions | Architected | Component Details (Knowledge Base Vector Store) |
| FR38   | Functional       | Ask for comparisons between different plants or time periods | Architected | Component Details (Knowledge Base Vector Store) |
| FR39   | Functional       | Receive predictive insights and recommendations from Hermes | Deferred | Deferred Requirements |
| FR40   | Functional       | Use Hermes for multimodal interactions (text, image, voice when available) | Deferred | Deferred Requirements |
| FR41   | Functional       | Access the plant tracking system via mobile device interface | Deferred | Deferred Requirements |
| FR42   | Functional       | Capture photos directly through the mobile app | Deferred | Deferred Requirements |
| FR43   | Functional       | Scan QR codes using mobile device camera | Deferred | Deferred Requirements |
| FR44   | Functional       | Enter and edit plant data through mobile interface | Deferred | Deferred Requirements |
| FR45   | Functional       | View plant histories and analytics on mobile device | Deferred | Deferred Requirements |
| FR46   | Functional       | Export plant data to CSV format for backup and analysis | Deferred | Deferred Requirements |
| FR47   | Functional       | Import plant data from CSV or JSON formats | Deferred | Deferred Requirements |
| FR48   | Functional       | Backup and restore plant databases | Deferred | Deferred Requirements |
| FR49   | Functional       | Share plant insights and data with others (optional) | Deferred | Deferred Requirements |
| FR50   | Functional       | Migrate data from markdown to Postgres database format | Architected | Component Details (Database) |
| NFR1   | Non-Functional   | QR code scanning and plant data retrieval within 3 seconds | Architected | Architecture Overview |
| NFR2   | Non-Functional   | Hermes agent queries return insights within 10 seconds | Architected | Architecture Overview |
| NFR3   | Non-Functional   | Data entry and saving operations within 2 seconds | Architected | Architecture Overview |
| NFR4   | Non-Functional   | Zero lost or corrupted plant records under normal usage | Architected | Component Details (Database) |
| NFR5   | Non-Functional   | QR code scanning works in 95%+ of attempts under typical garden lighting | Deferred | Deferred Requirements |
| NFR6   | Non-Functional   | Label printing via Phomemo M120 succeeds in 90%+ of attempts | Deferred | Deferred Requirements |
| NFR7   | Non-Functional   | Data recoverable from backups in case of device failure or corruption | Architected | Component Details (Database) |
| NFR8   | Non-Functional   | Usable in outdoor garden conditions with varying light levels | Deferred | Deferred Requirements |
| NFR9   | Non-Functional   | Core functions accessible within 2 taps from main screen | Deferred | Deferred Requirements |
| NFR10  | Non-Functional   | Text readable without zoom in typical outdoor lighting | Deferred | Deferred Requirements |
| NFR11  | Non-Functional   | Touch targets appropriately sized for gardening gloves | Deferred | Deferred Requirements |
| NFR12  | Non-Functional   | Export complete plant database in standard formats (CSV, JSON) | Architected | Component Details (Database) |
| NFR13  | Non-Functional   | Import functionality supports standard data formats for migration/recovery | Deferred | Deferred Requirements |
| NFR14  | Non-Functional   | Data migratable from markdown to Postgres without loss of information | Architected | Component Details (Database) |
| NFR15  | Non-Functional   | Support easy label reprinting when originals wear out or get damaged | Deferred | Deferred Requirements |
| NFR16  | Non-Functional   | Data format human-readable and editable for manual correction | Architected | Component Details (Database) |
| NFR17  | Non-Functional   | Graceful degradation when optional features (like Hermes agent) are unavailable | Architected | Architecture Overview |

### Deferred Requirements
- **FR7, FR9, FR16, FR31, FR32, FR39, FR40, FR41, FR42, FR43, FR44, FR45, FR46, FR47, FR48, FR49, FR50, FR51, FR52, FR53, FR54, FR55**: Data storage format migration, photo attachment, export functionality, multi-source data integration, predictive insights, multimodal Hermes interactions, mobile interface, and label customization - Deferred to future sprints as they require additional infrastructure, advanced ML models, or mobile-specific development beyond the MVP scope focused on backend services and Telegram/Hermes integration.
- **NFR5, NFR6, NFR8-NFR13**: Camera performance, label printing, outdoor usability, core function accessibility, text readability, touch target sizing, import format support - Deferred as they depend on mobile-specific hardware and UI; web/Telegram MVP focuses on core data flows.

## Interface Contract Documentation
### Database Connection String Format
- **Format**: `postgresql://username:password@host:port/database`
- **Example**: `postgresql://plantuser:securepassword@postgres-db:5432/plantdb`
- **Environment Variable**: `DATABASE_URL`
- **Notes**: Uses libpq protocol for communication; connection pooling configured with min=2, max=20 connections

### Knowledge Base API Endpoint Schemas
#### Upsert Vector Embedding
- **Endpoint**: `POST /api/v1/vectors/upsert`
- **Headers**: 
  - `Authorization: Bearer <pinecone_api_key>`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "vector": [0.1, 0.2, 0.3, ...],
    "id": "plant_HABY-2026-001_observation_2026-06-10",
    "metadata": {
      "plantId": "HABY-2026-001",
      "type": "observation",
      "timestamp": "2026-06-10T14:30:00Z",
      "content": "Leaf yellowing observed during heat wave"
    }
  }
  ```
- **Success Response**: 
  - Status: 200 OK
  - Body: `{"upserted": true, "vectorId": "plant_HABY-2026-001_observation_2026-06-10"}`
- **Error Responses**:
  - 400 Bad Request: Invalid vector dimensions or missing metadata
  - 401 Unauthorized: Invalid or missing API key
  - 429 Too Many Requests: Rate limit exceeded
  - 500 Internal Server Error: Vector store service failure
  - 503 Service Unavailable: Vector store temporarily unavailable

#### Query Similar Vectors
- **Endpoint**: `POST /api/v1/vectors/query`
- **Headers**: 
  - `Authorization: Bearer <pinecone_api_key>`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "vector": [0.1, 0.2, 0.3, ...],
    "topK": 5,
    "includeMetadata": true,
    "filter": {
      "plantId": {"$eq": "HABY-2026-001"}
    }
  }
  ```
- **Success Response**: 
  - Status: 200 OK
  - Body: 
    ```json
    {
      "matches": [
        {
          "id": "plant_HABY-2026-001_observation_2026-06-10",
          "score": 0.92,
          "metadata": {
            "plantId": "HABY-2026-001",
            "type": "observation",
            "timestamp": "2026-06-10T14:30:00Z",
            "content": "Leaf yellowing observed during heat wave"
          }
        }
      ]
    }
    ```
- **Error Responses**:
  - 400 Bad Request: Invalid vector dimensions or missing parameters
  - 401 Unauthorized: Invalid or missing API key
  - 429 Too Many Requests: Rate limit exceeded
  - 500 Internal Server Error: Vector store service failure
  - 503 Service Unavailable: Vector store temporarily unavailable

### Authentication Mechanisms
- **PostgreSQL**: 
  - Credentials managed via Docker secrets; API Gateway reads username/password from environment variables
  - Connection uses libpq with MD5 authentication; SSL enabled for production deployments
- **Pinecone**: 
  - Bearer token authentication using API key stored as environment variable `PINECONE_API_KEY`
  - Token validated per request; rotated periodically via secret management
- **API Gateway (Client Authentication)**: 
  - JWT-based authentication for web/mobile clients; tokens issued upon successful login
  - Token validation: signature verification, expiration check, audience validation
  - Secret key stored as environment variable `JWT_SECRET`; rotated every 30 days

## Adversarial Edge Case Coverage
### 1. DB Connection Pool Exhaustion
- **Mitigation**: Connection pool sized (min=2, max=20) with 30-second timeout; exponential backoff retry (max 3 attempts)
- **Fallback Path**: API returns HTTP 503 with `Retry-After` header; cached read-only responses served from Redis L2 cache for frequent queries
- **Monitoring Metrics**: 
  - Active connection count (alert > 80% of max for 5 minutes)
  - Connection wait time (alert > 100ms p95)
  - Failed connection attempts (alert > 5/minute)
- **Alert Thresholds**: 
  - Critical: >90% pool utilization for 10 minutes → PagerDuty alert
  - Warning: >70% pool utilization for 5 minutes → Slack notification

### 2. KB Vector Index Corruption/Drift
- **Mitigation**: Hourly health checks via Pinecone describe_index_stats; automatic snapshot backup every 6 hours
- **Fallback Path**: Switch to PostgreSQL ILIKE-based text search for metadata filtering; degrade to exact-match queries
- **Monitoring Metrics**: 
  - Vector count drift (alert > 5% deviation from expected)
  - Query latency increase (alert > 50ms p95 degradation)
  - Health check failure rate (alert > 2 consecutive failures)
- **Alert Thresholds**: 
  - Critical: Index unusable (0 vectors) → PagerDuty + email
  - Warning: Performance degraded >20% baseline → Slack notification

### 3. Schema Migration Rollback
- **Mitigation**: Flyway with version-controlled migrations; blue-green deployment schema switching
- **Fallback Path**: Automatic rollback to previous schema version on failure; traffic shifted to stable version
- **Monitoring Metrics**: 
  - Migration duration (alert > 5x normal baseline)
  - Rollback frequency (alert > 1/week)
  - Post-migration error rate (alert > 0.1% increase)
- **Alert Thresholds**: 
  - Critical: Migration failure requiring manual intervention → PagerDuty + email + SMS
  - Warning: Rollback executed → Slack notification

### 4. High Latency Fallback (Cache Miss)
- **Mitigation**: L1 (in-memory) and L2 (Redis) cache layers; stale-while-revalidate strategy with 5-minute grace period
- **Fallback Path**: Serve stale data while fetching fresh; if backend slow, return cached data with `X-Stale: true` header
- **Monitoring Metrics**: 
  - Cache hit ratio (alert < 80% for 10 minutes)
  - 95th percentile latency (alert > 500ms)
  - Backend request rate (alert > 2x baseline indicating thundering herd)
- **Alert Thresholds**: 
  - Critical: Sustained high latency >1 second → PagerDuty alert
  - Warning: Cache hit ratio < 60% → Slack notification

```mermaid
flowchart LR
    %% Define containers and external systems
    user(["User\n(Actor)"])
    api_gateway["API Gateway\n(Python/FastAPI, Docker)"]
    db[("PostgreSQL\n(Primary DB)")]
    kb[["Pinecone\n(Vector Store)"]]
    telegram[["Telegram\n(External)"]]
    
    %% Relationships with labels
    user -->|"Uses via HTTPS"| api_gateway
    api_gateway -->|"Executes SQL queries via libpq/TCP"| db
    db -->|"Returns query results via libpq/TCP"| api_gateway
    api_gateway -->|"Vector operations via REST/HTTPS"| kb
    kb -->|"Returns vector data via REST/HTTPS"| api_gateway
    api_gateway -->|"Sends/receives messages via Telegram Bot API"| telegram
    telegram -->|"Sends user messages via Telegram Bot API"| api_gateway
    
    %% System boundary
    subgraph sys["Plant Tracking System"]
        api_gateway
        db
        kb
    end
```