---
title: C2 Container Diagram for Plant Tracking System
---

## H2 Scope

This C2 container diagram depicts the deployable components of the Plant Tracking System's backend services relevant to the Database + Knowledge Base sprint.
It shows the User (actor) interacting with the API Gateway.
The API Gateway communicates with the PostgreSQL database for structured data storage.
It also interacts with the Pinecone vector store for semantic search capabilities.
External systems such as Telegram (for Hermes agent interactions) are outside the sprint scope but noted in the interface contracts.

## H2 Architecture Overview

The system follows a containerized microservices architecture.
The API Gateway acts as the single entry point handling HTTP requests, authentication, and request routing.
The API Gateway communicates with PostgreSQL via the libpq protocol for ACID-compliant transactions and complex queries on structured plant data.
For natural language querying and similarity search, the API Gateway interacts with Pinecone via REST/HTTPS for vector storage and retrieval operations.
All backend services are containerized using Docker for consistency and independent scaling.
The User represents the gardener who interacts with the system via mobile or web interfaces (not shown in this container diagram) to perform plant tracking activities.

## H3 Component Details

### User (Actor)
- **Role**: Home gardener who uses the system to track plants, scan QR codes, and request insights via Hermes agent.
- **Responsibilities**:Initiates interactions by scanning QR codes to retrieve plant data, submitting care activities, and querying the Hermes agent for analysis.
- **Boundary**: External actor outside the system boundary.

### API Gateway
- **Technology**: Python/FastAPI running in Docker containers.
- **Responsibilities**:
  - Handles all incoming HTTP requests from clients (mobile/web interfaces).
  - Provides authentication (JWT-based) and rate limiting.
  - Routes requests to appropriate services: PostgreSQL for CRUD operations, Pinecone for vector operations.
  - Transforms data between external JSON formats and internal data models.
  - Implements request/response logging and error handling.
- **Interfaces**:
  - Receives HTTPS requests from clients.
  - Sends SQL queries to PostgreSQL via libpq/TCP.
  - Sends vector operations (upsert/query) to Pinecone via REST/HTTPS.

### Database (PostgreSQL)
- **Technology**: PostgreSQL 15 running in Docker containers.
- **Responsibilities**:
  - Stores structured plant data including plant records, care activities (watering, fertilizing), observations, and metadata.
  - Ensures data integrity through ACID transactions.
  - Supports complex reporting queries for filtering, aggregation, and time-series analysis.
  - Provides full-text search capabilities for plant attributes.
- **Interfaces**:
  - Receives SQL queries from API Gateway via libpq/TCP.
  - Returns query results and status to API Gateway via libpq/TCP.

### Knowledge Base Vector Store (Pinecone)
- **Technology**: Pinecone managed vector database service (external).
- **Responsibilities**:
  - Stores vector embeddings of plant care notes, observations, and growth patterns for semantic similarity search.
  - Enables natural language querying via the Hermes agent by finding similar plant care scenarios.
  - Supports metadata filtering alongside vector search for contextualized results.
  - Handles horizontal scaling and managed backups automatically.
- **Interfaces**:
  - Receives upsert and query requests from API Gateway via REST/HTTPS.
  - Returns vector search results with metadata to API Gateway via REST/HTTPS.

## H2 Traceability

| PRD ID | Requirement Description                                                                 | Mapped Component(s) | Status       | Rationale                                                                 |
|--------|---------------------------------------------------------------------------------------|---------------------|--------------|---------------------------------------------------------------------------|
| FR6    | Users can create plant records with core attributes from seed packet information      | Database            | Architected  | Plant records stored in PostgreSQL with structured schema.                |
| FR7    | Users can store plant data in markdown files with structured format                   | Database            | Deferred     | Markdown storage deferred to Postgres migration (FR50); see Deferred section. |
| FR8    | Users can add notes and observations to plant records with timestamps                 | Database            | Architected  | Notes and observations stored as structured records in PostgreSQL.        |
| FR9    | Users can attach photos to plant records for visual documentation                     | Database            | Deferred     | Photo storage requires BLOB handling or object storage; deferred for MVP. |
| FR10   | Users can update plant records with new information over time                         | Database            | Architected  | PostgreSQL supports UPDATE operations for record modifications.           |
| FR11   | Users can store multiple plants in a searchable database format                       | Database            | Architected  | PostgreSQL designed for multi-record storage with indexing.               |
| FR12   | Users can retrieve complete plant records by scanning QR codes                        | API Gateway, Database | Architected | API Gateway retrieves full plant record from PostgreSQL by plant ID.      |
| FR13   | Users can query plant data using natural language via Hermes agent                    | Knowledge Base      | Architected  | Pinecone enables semantic search for natural language queries via Hermes. |
| FR14   | Users can compare data between different plants                                       | Knowledge Base      | Architected  | Pinecone similarity search facilitates cross-plant comparisons.           |
| FR15   | Users can filter plant records by various criteria (date, variety, location, etc.)    | Database            | Architected  | PostgreSQL WHERE clauses support filtering by any indexed attribute.      |
| FR16   | Users can export plant data for backup or analysis                                    | Database            | Architected  | PostgreSQL provides pg_dump and CSV export utilities.                     |
| FR17   | Users can receive data-driven insights about plant health and care patterns           | Knowledge Base      | Architected  | Pinecone vector search enables pattern detection in care activities.      |
| FR18   | Users can identify root causes of plant issues through data analysis                  | Knowledge Base      | Architected  | Similarity search identifies analogous past issues and outcomes.          |
| FR19   | Users can track plant progress over time (growth, flowering, fruiting)                | Database, Knowledge Base | Architected | Time-series data in PostgreSQL; vector embeddings enable trend analysis.  |
| FR20   | Users can receive personalized care recommendations based on plant history            | Knowledge Base      | Architected  | Pinecone retrieves similar plant histories to inform recommendations.     |
| FR21   | Users can detect patterns and correlations in plant care data                         | Knowledge Base      | Architected  | Vector space allows clustering and correlation detection.                 |
| FR22   | Users can record watering schedules and amounts                                       | Database            | Architected  | Structured fields in PostgreSQL for irrigation tracking.                  |
| FR23   | Users can record fertilizer applications (type, amount, frequency)                    | Database            | Architected  | Structured fields for fertilizer tracking in PostgreSQL.                  |
| FR24   | Users can track indoor/outdoor status changes                                         | Database            | Architected  | Status field in PostgreSQL updated on location change.                    |
| FR25   | Users can monitor temperature and humidity conditions                                 | Database            | Architected  | Environmental metrics stored as numeric fields in PostgreSQL.             |
| FR26   | Users can record rainfall and precipitation data                                      | Database            | Architected  | Precipitation stored as numeric field in PostgreSQL.                      |
| FR27   | Users can track sunlight exposure and shade conditions                                | Database            | Architected  | Sunlight levels stored as categorical or numeric field in PostgreSQL.     |
| FR28   | Users can record soil amendments and treatments                                       | Database            | Architected  | Soil treatment records stored as structured data in PostgreSQL.           |
| FR29   | Users can document pruning, staking, and support activities                           | Database            | Architected  | Garden maintenance activities stored as timestamped records.              |
| FR30   | Users can note pest observations and treatments                                       | Database            | Architected  | Pest records stored with timestamps and treatment details in PostgreSQL.  |
| FR31   | Users can combine manual data entry with automated sensor data                        | Database            | Deferred     | Sensor integration requires external service adapters; deferred for MVP.  |
| FR32   | Users can import data from external sources (weather stations, etc.)                  | Database            | Deferred     | External data ingestion pipeline deferred; manual entry supported now.    |
| FR33   | Users can reconstruct missing data points from historical records                     | Database            | Architected  | PostgreSQL allows UPDATE/INSERT for historical data reconstruction.       |
| FR34   | Users can validate data quality and correct erroneous entries                         | Database            | Architected  | Application-level validation + PostgreSQL constraints ensure data quality.|
| FR35   | Users can gap-identify missing data periods in plant histories                        | Database            | Architected  | Time-series analysis in PostgreSQL identifies gaps in care records.       |
| FR36   | Users can interact with Hermes agent via Telegram for natural language queries        | Knowledge Base      | Architected  | Pinecone provides semantic search backend for Hermes agent on Telegram.   |
| FR37   | Users can request analysis of specific plant data and conditions                      | Knowledge Base      | Architected  | Pinecone similarity search enables condition-based analysis requests.     |
| FR38   | Users can ask for comparisons between different plants or time periods                | Knowledge Base      | Architected  | Vector comparisons support cross-plant and temporal analysis.             |
| FR39   | Users can receive predictive insights and recommendations from Hermes                 | Knowledge Base      | Deferred     | Multimodal Hermes requires image/vector integration; deferred for MVP.    |
| FR40   | Users can use Hermes for multimodal interactions (text, image, voice when available)  | Knowledge Base      | Deferred     | Multimodal Hermes requires image/vector integration; deferred for MVP.    |
| FR41   | Users can access the plant tracking system via mobile device interface                | API Gateway         | Deferred     | Mobile interface deferred; API Gateway serves web/Telegram clients now.   |
| FR42   | Users can capture photos directly through the mobile app                              | API Gateway         | Deferred     | Photo capture and storage deferred to FR9/FR47; API endpoint placeholder. |
| FR43   | Users can scan QR codes using mobile device camera                                    | API Gateway         | Architected  | API Gateway validates QR code (plant ID) and returns plant data.          |
| FR44   | Users can enter and edit plant data through mobile interface                          | API Gateway         | Deferred     | Mobile data entry deferred; web/Telegram interface supported now.         |
| FR45   | Users can view plant histories and analytics on mobile device                         | API Gateway         | Deferred     | Mobile analytics deferred; web/Telegram interface supported now.          |
| FR46   | Users can export plant data to CSV format for backup and analysis                     | Database            | Architected  | PostgreSQL COPY TO or \copy for CSV export.                               |
| FR47   | Users can import plant data from CSV or JSON formats                                  | Database            | Deferred     | Import pipeline deferred; manual entry and API ingestion supported now.   |
| FR48   | Users can backup and restore plant databases                                          | Database            | Architected  | PostgreSQL supports pg_dump/pg_restore and point-in-time recovery.        |
| FR49   | Users can share plant insights and data with others (optional)                        | API Gateway         | Deferred     | Sharing requires authz and UI; deferred for MVP.                          |
| FR50   | Users can migrate data from markdown to Postgres database format                      | Database            | Architected  | Migration scripts planned for markdown-to-Postgres transition.            |
| FR51   | Users can design label templates for reuse across multiple plants                     | API Gateway         | Deferred     | Label printing handled by Printer Service (out of sprint scope).          |
| FR52   | Users can adjust label sizes to fit different stakes and pots                         | API Gateway         | Deferred     | Label printing handled by Printer Service (out of sprint scope).          |
| FR53   | Users can generate labels with durable, weather-resistant materials                   | API Gateway         | Deferred     | Label printing handled by Printer Service (out of sprint scope).          |
| FR54   | Users can reprint labels when originals wear out or get damaged                       | API Gateway         | Deferred     | Label printing handled by Printer Service (out of sprint scope).          |
| FR55   | Users can customize label layouts (variety name, QR code, planting info)              | API Gateway         | Deferred     | Label printing handled by Printer Service (out of sprint scope).          |
| NFR1   | QR code scanning and plant data retrieval should complete within 3 seconds            | API Gateway, Database | Architected | Indexed queries and connection pooling target <1s DB latency.             |
| NFR2   | Hermes agent queries should return insights within 10 seconds                         | Knowledge Base      | Architected  | Pinecone query latency <100ms; end-to-end <2s via API Gateway.            |
| NFR3   | Data entry and saving operations should complete within 2 seconds                     | API Gateway, Database | Architected | Optimized writes and connection pooling target <500ms DB latency.         |
| NFR4   | The system should maintain data integrity with zero lost or corrupted plant records   | Database            | Architected  | ACID transactions, backups, and validation prevent data loss/corruption.  |
| NFR5   | QR code scanning should work successfully in 95%+ of attempts under typical garden lighting conditions | API Gateway | Deferred | Depends on mobile camera performance; web/Telegram MVP focuses on core data flows. |
| NFR6   | Label printing via Phomemo M120 should succeed in 90%+ of attempts when printer is properly connected and charged | API Gateway | Deferred | Printing handled by Printer Service (out of sprint scope).                |
| NFR7   | Data should be recoverable from backups in case of device failure or data corruption  | Database            | Architected  | Automated backups and WAL archiving enable point-in-time recovery.        |
| NFR8   | The interface should be usable in outdoor garden conditions with varying light levels | API Gateway         | Deferred     | Depends on mobile-specific UI; web/Telegram MVP focuses on core data flows. |
| NFR9   | Core functions (scan QR, add note, take photo) should be accessible within 2 taps from the main screen | API Gateway | Deferred | Depends on mobile-specific UI; web/Telegram MVP focuses on core data flows. |
| NFR10  | Text should be readable without zoom in typical outdoor lighting conditions           | API Gateway         | Deferred     | Depends on mobile-specific UI; web/Telegram MVP focuses on core data flows. |
| NFR11  | Touch targets should be appropriately sized for use with gardening gloves or in variable conditions | API Gateway | Deferred | Depends on mobile-specific UI; web/Telegram MVP focuses on core data flows. |
| NFR12  | Users should be able to export their complete plant database in standard formats (CSV, JSON) | Database | Architected | PostgreSQL supports CSV/JSON export via COTO and programming drivers.     |
| NFR13  | Import functionality should support standard data formats for migration or recovery   | Database            | Architected  | PostgreSQL supports CSV/JSON import via COPY and programming drivers.     |
| NFR14  | Data should be migratable from markdown storage to Postgres format without loss of information | Database | Architected | Migration scripts include data validation and transformation checks.      |
| NFR15  | The system should support easy label reprinting when originals wear out or get damaged | API Gateway | Deferred | Label printing handled by Printer Service (out of sprint scope).          |
| NFR16  | Data format should be human-readable and editable for manual correction when needed   | Database            | Architected  | PostgreSQL data accessible via SQL; admin tools allow manual correction.  |
| NFR17  | System should allow for graceful degradation when optional features (like Hermes agent) are unavailable | API Gateway | Architected | API returns cached data or stale-while-revalidate; queues requests if KB down. |

**Deferred Requirements**
Requirements deferred to future sprints with risk assessment:

| PRD ID | Reason for Deferral                                                                 | Risk Level | Mitigation Strategy                                                                 | Target Sprint |
|--------|-----------------------------------------------------------------------------------|------------|-----------------------------------------------------------------------------------|---------------|
| FR7    | Markdown storage replaced by Postgres; direct markdown handling not needed in MVP   | Low        | FR50 provides migration path; interim manual entry via API.                       | Sprint 6      |
| FR9    | Photo storage requires BLOB/object storage infrastructure; increases complexity     | Medium     | MVP uses external image URLs; Sprint 6 adds local storage.                        | Sprint 6      |
| FR31   | Requires sensor integration adapters and real-time processing pipelines             | Medium     | MVP supports manual entry; Sprint 7 adds weather service adapters.                | Sprint 7      |
| FR32   | External data ingestion requires ETL pipelines and schema mapping                   | Medium     | MVP supports CSV/JSON import via API; Sprint 6 adds automation.                   | Sprint 6      |
| FR39   | Predictive insights require advanced ML models; increases scope                     | High       | MVP uses similarity-based insights; Sprint 8 adds predictive modeling.            | Sprint 8      |
| FR40   | Multimodal Hermes requires image embedding and voice processing; increases scope    | High       | MVP uses text-only Hermes; Sprint 8 adds image analysis via Pinecone metadata.    | Sprint 8      |
| FR41   | Mobile interface requires platform-specific development; increases scope            | Medium     | MVP uses web/Telegram interface; Sprint 6 adds React Native mobile app.           | Sprint 6      |
| FR42   | Photo capture and storage requires mobile camera integration and BLOB handling      | Medium     | MVP uses external photo URLs; Sprint 6 adds local photo storage.                  | Sprint 6      |
| FR43   | Mobile QR scanning depends on camera performance; increases scope                   | Low        | MVP uses web/Telegram QR validation; Sprint 6 adds mobile scanning.               | Sprint 6      |
| FR44   | Mobile data entry requires platform-specific development; increases scope           | Medium     | MVP uses web/Telegram interface; Sprint 6 adds mobile data entry.                 | Sprint 6      |
| FR45   | Mobile analytics requires platform-specific development; increases scope            | Medium     | MVP uses web/Telegram interface; Sprint 6 adds mobile analytics.                  | Sprint 6      |
| FR47   | Import pipeline requires validation, transformation, and error handling; increases scope | Medium     | MVP supports manual API entry; Sprint 6 adds bulk import with validation.       | Sprint 6      |
| FR49   | Sharing requires authentication zones, UI, and audit logging; increases scope       | Low        | MVP keeps data private; Sprint 8 adds opt-in sharing with access controls.        | Sprint 8      |
| FR50   | Data migration from markdown to Postgres requires validation scripts; increases scope | Low        | MVP uses direct Postgres storage; migration scripts provided for future use.      | Sprint 6      |
| FR51-FR55 | Label customization handled by Printer Service (out of sprint scope)             | Low        | Printer Service developed in Sprint 6; label customization deferred to Sprint 6.  | Sprint 6      |
| NFR5   | Depends on mobile camera performance; increases scope                               | Low        | MVP uses web/Telegram interface; Sprint 6 adds mobile QR scanning.                | Sprint 6      |
| NFR6   | Label printing handled by Printer Service (out of sprint scope)                     | Low        | Printer Service developed in Sprint 6; API Gateway prints via Bluetooth service.  | Sprint 6      |
| NFR8-NFR11 | Depends on mobile-specific UI; increases scope                                   | Medium     | MVP uses web/Telegram interface; Sprint 6 adds mobile UI with outdoor usability.  | Sprint 6      |
| NFR13  | Import functionality requires validation and error handling; increases scope        | Medium     | MVP supports manual API entry; Sprint 6 adds bulk import with validation.         | Sprint 6      |
| NFR15  | Label reprinting depends on Printer Service availability                          | Low        | Same as NFR6; reprint API added when Printer Service available.                   | Sprint 6      |

## H2 Interface Contract Documentation

### Database Connection String Format
```
Format: postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require
Example: postgresql://plantuser:securepass@db-service:5432/plantdb?sslmode=require
Environment Variable: DATABASE_URL
Connection Pool:
  - Minimum connections: 5
  - Maximum connections: 20
  - Connection timeout: 5s
  - Idle timeout: 30s
  - Max lifetime: 1h
```

### Knowledge Base API Endpoint Schemas

**Vector Upsert**
```
POST /vectors/upsert
Headers:
  - Authorization: Bearer <pinecone-api-key>
  - Content-Type: application/json
Request Body:
{
  "vectors": [
    {
      "id": "plant_HABY-2026-001_obs_2026-06-15",
      "values": [0.1, 0.2, ..., 0.768],  // 768-dimension embedding
      "metadata": {
        "plantId": "HABY-2026-001",
        "type": "observation",
        "content": "Leaf yellowing observed during heat wave",
        "timestamp": "2026-06-15T08:30:00Z",
        "careActivity": "watering"
      }
    }
  ],
  "namespace": "plant-tracking"
}
Success Response:
  - Status: 200 OK
  - Body: { "upsertedCount": 1 }
Error Responses:
  - 400: Invalid request payload
  - 401: Unauthorized (invalid/missing API key)
  - 429: Rate limit exceeded
  - 500: Internal server error
```

**Vector Query**
```
POST /vectors/query
Headers:
  - Authorization: Bearer <pinecone-api-key>
  - Content-Type: application/json
Request Body:
{
  "vector": [0.1, 0.2, ..., 0.768],  // Query embedding
  "topK": 10,
  "includeMetadata": true,
  "filter": {
    "plantId": { "$eq": "HABY-2026-001" },
    "type": { "$eq": "observation" }
  },
  "namespace": "plant-tracking"
}
Success Response:
  - Status: 200 OK
  - Body: {
      "matches": [
        {
          "id": "plant_HABY-2026-001_obs_2026-06-10",
          "score": 0.92,
          "metadata": { ... }
        }
      ]
    }
Error Responses:
  - 400: Invalid request payload
  - 401: Unauthorized (invalid/missing API key)
  - 429: Rate limit exceeded
  - 500: Internal server error
```

### Authentication Mechanisms
- **PostgreSQL**:
  - Credentials managed via Docker secrets (username/password)
  - SSL enforced (sslmode=require)
  - Authentication: MD5 or SCRAM-SHA-256
- **Pinecone**:
  - Bearer token authentication via API key
  - API key stored as Docker secret (PINECONE_API_KEY)
  - Token passed in Authorization header: `Bearer <key>`
- **API Gateway (Client-Facing)**:
  - JWT authentication for HTTPS endpoints
  - Access token issued upon login via `/auth/login`
  - Token passed in Authorization header: `Bearer <jwt>`
  - Refresh token endpoint: `/auth/refresh`
  - Token expiration: 15 minutes (access), 7 days (refresh)
  - Secret key stored as Docker secret (JWT_SECRET)

## H2 Adversarial Edge Case Coverage

### 1. DB Connection Pool Exhaustion
- **Mitigation Strategy**:
  - Set aggressive connection limits (max 20 connections)
  - Implement connection timeout (5s) and idle timeout (30s)
  - Use HikariCP monitoring for leak detection
- **Fallback Path**:
  - Reject new requests with HTTP 429 (Too Many Requests) after 3 retries
  - Queue requests in Redis (L1 cache) with 5s TTL for retry
- **Monitoring Metric**:
  - Active connections / max connections ratio (alert > 0.8)
  - Connection wait time 95th percentile (alert > 100ms)
- **Alert Notification Channel**:
  - Slack webhook (#plant-tracking-alerts) and email (dev-team@plant-tracking.local)

### 2. KB Vector Index Corruption/Drift
- **Mitigation Strategy**:
  - Daily consistency checks comparing vector count to PostgreSQL record count
  - Weekly snapshot backups of Pinecone index
  - Metadata validation on upsert (schema validation via JSON Schema)
- **Fallback Path**:
  - Switch to PostgreSQL ILIKE full-text search on observation content
  - Stale-while-reserve: serve last known good index for 5 minutes during recovery
- **Monitoring Metric**:
  - Vector count vs. PostgreSQL record count delta (alert > 5%)
  - Query latency 95th percentile (alert > 500ms)
  - Failed upsert rate (alert > 1%)
- **Alert Notification Channel**:
  - Slack webhook (#plant-tracking-alerts) and email (data-eng@plant-tracking.local)

### 3. Schema Migration Rollback
- **Mitigation Strategy**:
  - Use Flyway for version-controlled migrations
  - Pre-migration backup of PostgreSQL data directory
  - Blue-green deployment: migrate standby database, switch via DNS
  - Test migrations against production-snapshot data in staging
- **Fallback Path**:
  - Automatic rollback to previous version if migration fails
  - Traffic shifted back to original database via load balenger
  - Manual intervention required for data merge if rollback insufficient
- **Monitoring Metric**:
  - Migration duration (alert > 30 minutes, 5x baseline of 6 minutes)
  - Migration success/failure rate (alert on any failure)
  - Replica lag during blue-green switch (alert > 5s)
- **Alert Notification Channel**:
  - Slack webhook (#plant-tracking-alerts) and email (db-admin@plant-tracking.local)

### 4. High Latency Fallback (Cache Miss)
- **Mitigation Strategy':
  - L1 cache: API Gateway local cache (Caffeine) for frequent plant IDs
  - L2 cache: Redis for query results and vector search outcomes
  - Stale-while-revalidate: serve stale data (max 5min old) while fetching fresh
  - Thundering herd protection: single-flight pattern for cache misses
- **Fallback Path**:
  - Serve cached data if available (stale but acceptable)
  - Degrade to basic plant metadata only (without care history) if all caches miss
  - Log cache miss ratio for capacity planning
- **Monitoring Metric**:
  - Cache miss ratio L1/L2 (alert > 0.3 / > 0.6)
  - 95th percentile latency (alert > 2s for L1 miss, > 5s for L2 miss)
  - Cache hit ratio trend (alert if decreasing > 10%/hour)
- **Alert Notification Channel**:
  - Slack webhook (#plant-tracking-alerts) and email (perf-eng@plant-tracking.local)

## H2 Diagram

```mermaid
---
title: C2 Container Diagram for Plant Tracking System
---
flowchart LR
    %% Define actors and external systems
    user(["User\n(Actor)"])
    telegram[["Telegram\n(External)"]]
    kb[["Pinecone\n(Vector Store)"]]

    %% Define system boundary
    subgraph sys["Plant Tracking System"]
        api_gateway["API Gateway\n(Python/FastAPI, Docker)"]
        db[("PostgreSQL\n(Primary DB)")]
    end

    %% Relationships with labels
    user -->|"Uses via HTTPS"| api_gateway
    api_gateway -->|"Executes SQL queries via libpq/TCP"| db
    db -->|"Returns query results via libpq/TCP"| api_gateway
    api_gateway -->|"Vector operations via REST/HTTPS"| kb
    kb -->|"Returns vector data via REST/HTTPS"| api_gateway
    api_gateway -->|"Sends/receives messages via Telegram Bot API"| telegram
    telegram -->|"Sends user messages via Telegram Bot API"| api_gateway
```
