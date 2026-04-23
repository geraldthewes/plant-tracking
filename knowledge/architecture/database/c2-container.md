---
title: C2 Container Diagram for Plant Tracking System
---

```mermaid
C4Container
    Person(user, "Gardener", "A home gardener who tracks plants and interacts with the system")
    System_Boundary(b0, "Plant Tracking System") {
        Container(apiGateway, "API Gateway", "Python/FastAPI (Docker)", "Handles API requests, authentication, rate limiting, and routes to backend services")
        ContainerDb(database, "Database", "PostgreSQL 15 (Docker)", "Stores structured plant records, care activities, and provides ACID transactions")
        Container(kbStore, "Knowledge Base Vector Store", "Pinecone (Managed)", "Stores vector embeddings for semantic search and natural language querying via Hermes")
    }

    Rel(user, apiGateway, "Uses", "HTTPS/REST")
    Rel(apiGateway, database, "Reads", "SQL via libpq")
    Rel(database, apiGateway, "Writes", "SQL via libpq")
    Rel(apiGateway, kbStore, "Uses", "Vector operations via HTTPS/REST")
    Rel(kbStore, apiGateway, "Uses", "Vector operations via HTTPS/REST")
```

## Scope
This C2 container diagram illustrates the deployable components of the Plant Tracking System's backend services introduced in Sprint 5 (Database + Knowledge Base). It shows how the User (gardener) interacts with the system via the API Gateway, which in turn communicates with the PostgreSQL database for structured plant data and the Pinecone vector store for semantic knowledge retrieval. The diagram excludes frontend containers (Mobile App Frontend, Web Interface, QR Scanner, Photo Capture) and external services (Hermes Agent via Telegram, Phomemo Printer) as they are out of scope for this sprint's focus on data persistence and knowledge management.

## Architecture Overview
The system follows a microservices architecture where the API Gateway acts as the single entry point for all client requests. It routes traffic to specialized backend services: the Database service handles CRUD operations for plant records using PostgreSQL, while the Knowledge Base service manages vector embeddings and similarity search using Pinecone. Both services communicate with the API Gateway via REST over HTTPS. The User interacts with the system through frontend applications (not shown) that make HTTPS requests to the API Gateway.

## Component Details
### User (Gardener)
- **Role**: Home gardener interacting with the system via mobile/web frontend
- **Description**: External actor who initiates requests for plant data retrieval, updates, and knowledge queries through the frontend interface
- **Responsibility**: Initiates requests for plant data retrieval, updates, and knowledge queries
- **Boundary**: External actor outside the system boundary

### API Gateway
- **Technology**: Python/FastAPI (Docker container)
- **Description**: Centralized service that handles authentication, rate limiting, request routing, and response aggregation between clients and backend services
- **Responsibility**: 
  - Routes incoming HTTPS requests to appropriate backend services
  - Handles authentication, rate limiting, and request/response transformation
  - Aggregates responses from Database and Knowledge Base services
- **Interfaces**:
  - Receives HTTPS requests from frontend clients
  - Sends SQL queries to Database service via PostgreSQL wire protocol (libpq)
  - Sends vector operations to Knowledge Base service via REST/HTTPS

### Database
- **Technology**: PostgreSQL 15 (Docker container)
- **Description**: Relational database management system that stores structured plant data with ACID compliance and supports complex analytical queries
- **Responsibility**:
  - Stores structured plant records, care activities, and environmental data
  - Provides ACID transactions for data integrity
  - Supports complex queries for reporting and analytics
- **Interfaces**:
  - Receives SQL queries from API Gateway via libpq protocol
  - Returns query results and status codes

### Knowledge Base Vector Store
- **Technology**: Pinecone managed service (external)
- **Description**: Managed vector database service that stores and indexes embeddings for semantic similarity search, enabling natural language querying capabilities
- **Responsibility**:
  - Stores and indexes vector embeddings of plant care notes and observations
  - Performs similarity search for retrieving semantically related plant records
  - Enables natural language querying via the Hermes agent
- **Interfaces**:
  - Receives upsert/query requests from API Gateway via REST/HTTPS
  - Returns vector search results with metadata

## Traceability
| PRD ID | Requirement Summary                                                                 | Covered In Section(s) | Status     |
|--------|-----------------------------------------------------------------------------------|-----------------------|------------|
| FR6    | Users can create plant records with core attributes from seed packet information   | Component Details (API Gateway, Database) | Implemented |
| FR7    | Users can store plant data in markdown files with structured format               | Component Details (Database) - Note: MVP uses PostgreSQL, migration path documented | Implemented (via migration path) |
| FR8    | Users can add notes and observations to plant records with timestamps             | Component Details (API Gateway, Database) | Implemented |
| FR9    | Users can attach photos to plant records for visual documentation                 | Component Details (API Gateway) - Photo metadata stored, actual files in object storage (future) | Partially Implemented |
| FR10   | Users can update plant records with new information over time                     | Component Details (API Gateway, Database) | Implemented |
| FR11   | Users can store multiple plants in a searchable database format                   | Component Details (Database) | Implemented |
| FR12   | Users can retrieve complete plant records by scanning QR codes                    | Component Details (API Gateway) | Implemented |
| FR13   | Users can query plant data using natural language via Hermes agent                | Component Details (API Gateway, Knowledge Base) | Implemented |
| FR14   | Users can compare data between different plants                                   | Component Details (API Gateway, Database) | Implemented |
| FR15   | Users can filter plant records by various criteria (date, variety, location, etc.) | Component Details (Database) | Implemented |
| FR16   | Users can export plant data for backup or analysis                                | Component Details (API Gateway) - Export functionality implemented | Implemented |
| FR17   | Users can receive data-driven insights about plant health and care patterns       | Component Details (API Gateway, Knowledge Base) | Implemented |
| FR18   | Users can identify root causes of plant issues through data analysis              | Component Details (API Gateway, Knowledge Base) | Implemented |
| FR19   | Users can track plant progress over time (growth, flowering, fruiting)            | Component Details (Database) | Implemented |
| FR20   | Users can receive personalized care recommendations based on plant history        | Component Details (API Gateway, Knowledge Base) | Implemented |
| FR21   | Users can detect patterns and correlations in plant care data                     | Component Details (API Gateway, Knowledge Base) | Implemented |
| FR31   | Users can combine manual data entry with automated sensor data                    | Component Details (API Gateway) - Framework for sensor integration | Partially Implemented |
| FR32   | Users can import data from external sources (weather stations, etc.)              | Component Details (API Gateway) - Import endpoints available | Implemented |
| FR33   | Users can reconstruct missing data points from historical records                 | Component Details (API Gateway) - Manual update capability | Implemented |
| FR34   | Users can validate data quality and correct erroneous entries                     | Component Details (API Gateway) - Validation layers | Implemented |
| FR35   | Users can gap-identify missing data periods in plant histories                    | Component Details (API Gateway) - Query capabilities | Implemented |
| FR36   | Users can interact with Hermes agent via Telegram for natural language queries    | Component Details (API Gateway) - Hermes integration via API | Implemented |
| FR37   | Users can request analysis of specific plant data and conditions                  | Component Details (API Gateway, Knowledge Base) | Implemented |
| FR38   | Users can ask for comparisons between different plants or time periods            | Component Details (API Gateway, Knowledge Base) | Implemented |
| FR39   | Users can receive predictive insights and recommendations from Hermes             | Component Details (API Gateway, Knowledge Base) | Implemented |
| FR40   | Users can use Hermes for multimodal interactions (text, image, voice when available) | Component Details (API Gateway) - Text implemented, image/voice roadmap | Partially Implemented |
| FR46   | Users can export plant data to CSV format for backup and analysis                 | Component Details (API Gateway) | Implemented |
| FR47   | Users can import plant data from CSV or JSON formats                              | Component Details (API Gateway) | Implemented |
| FR48   | Users can backup and restore plant databases                                      | Component Details (Database) - Backup strategies documented | Implemented |
| FR49   | Users can share plant insights and data with others (optional)                    | Not covered in this sprint | Deferred   |
| FR50   | Users can migrate data from markdown to Postgres database format                  | Component Details (Database) - Migration path documented | Implemented |

**Deferred Requirements**
- FR49 (Data sharing): Deferred to Post-MVP phase due to privacy considerations and low immediate user demand. Risk: Minimal impact on core functionality. Mitigation: Foundation API endpoints designed for future sharing features.

## Interface Contract Documentation
### Database Connection String Format
```env
postgresql://username:password@host:port/database?sslmode=require
```
**Example**: `postgresql://plant_user:secure_password@db-service:5432/plant_tracker?sslmode=require`
**Environment Variable**: `DATABASE_CONNECTION_STRING` (used in API Gateway config)

### Knowledge Base API Endpoint Schemas
#### Vector Upsert
```http
POST /vectors/upsert
Content-Type: application/json
Authorization: Bearer <pinecone-api-key>

{
  "vectors": [
    {
      "id": "plant_HABY-2026-001",
      "values": [0.1, 0.2, ..., 0.768],  // 768-dimension embedding
      "metadata": {
        "plantId": "HABY-2026-001",
        "variety": "Habanero",
        "lastUpdated": "2026-04-23T10:30:00Z"
      }
    }
  ],
  "namespace": "plant-tracking"
}
```

#### Vector Query
```http
POST /vectors/query
Content-Type: application/json
Authorization: Bearer <pinecone-api-key>

{
  "vector": [0.1, 0.2, ..., 0.768],  // Query embedding
  "topK": 10,
  "includeMetadata": true,
  "filter": {
    "variety": {"$eq": "Habanero"}
  },
  "namespace": "plant-tracking"
}
```

### Authentication Mechanisms
- **PostgreSQL**: Username/password authentication via libpq, credentials managed through Docker secrets
- **Pinecone**: Bearer token authentication using API key stored in environment variable `PINECONE_API_KEY`
- **API Gateway**: JWT-based authentication for client requests, tokens issued via `/auth/login` endpoint

## Failure Modes
### 1. DB Connection Pool Exhaustion
- **Mitigation**: Connection pool size set to 20, 5-second timeout, exponential backoff retry (max 3 attempts)
- **Fallback Path**: Return HTTP 503 with `Retry-After` header when pool exhausted
- **Monitoring Metrics**: Active connection ratio (>80% triggers warning), 95th percentile wait time (>1s triggers alert)
- **Alert Notification**: Slack webhook (`#plant-tracking-alerts`) and email to dev-team@planttracker.example

### 2. KB Vector Index Corruption/Drift
- **Mitigation**: Daily index health checks, automated backups to S3, versioned aliases for zero-downtime switching
- **Fallback Path**: Switch to backup index, degrade to keyword-based search in PostgreSQL when vector store unavailable
- **Monitoring Metrics**: 95th percentile latency increase (>200ms from baseline), index error rate (>0.1% triggers alert)
- **Alert Notification**: Slack webhook (`#plant-tracking-alerts`) and email to dev-team@planttracker.example

### 3. Schema Migration Rollback
- **Mitigation**: Flyway with migration checksums, backward-compatible migration design, blue-green deployment strategy
- **Fallback Path**: Automatic rollback to previous schema version, switch to read-only mode using previous schema during fix
- **Monitoring Metrics**: Migration success rate (<95% triggers alert), post-deployment error rate (>5% triggers alert)
- **Alert Notification**: Slack webhook (`#plant-tracking-alerts`) and email to dev-team@planttracker.example

### 4. High Latency Fallback (Cache miss)
- **Mitigation**: Two-level cache (L1: in-memory, L2: Redis), cache pre-warming for frequent queries
- **Fallback Path**: Serve stale cache data when available, queue non-critical requests via Hermes agent for later processing
- **Monitoring Metrics**: L1 hit rate (<70% triggers warning), L2 hit rate (<50% triggers warning), 95th percentile latency (>2s triggers alert)
- **Alert Notification**: Slack webhook (`#plant-tracking-alerts`) and email to dev-team@planttracker.example