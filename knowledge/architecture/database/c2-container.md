---
title: C2 Container Diagram for Plant Tracking System
---

# C2 Container Diagram for Plant Tracking System

## Scope
This C2 container diagram illustrates the deployable components of the Plant Tracking System's backend services, specifically focusing on the database and knowledge base layers introduced in Sprint 5. The diagram shows how the Gardener (user) interacts with the API Gateway, which in turn communicates with the PostgreSQL database for structured data storage and the Pinecone vector store for semantic search capabilities. This diagram does not include frontend containers, mobile app components, or label printing services, which are covered in other sprints.

## Architecture Overview
The system follows a containerized microservices architecture where the API Gateway acts as the single entry point for all client requests, handling authentication, rate limiting, and request/response transformation. The API Gateway communicates with two primary data stores: a PostgreSQL 15 database for ACID-compliant storage of structured plant records, care activities, and user data; and a Pinecone managed vector store for enabling semantic search and natural language queries via the Hermes agent. All inter-service communication occurs over secure HTTPS/REST protocols, with the database connection utilizing the PostgreSQL wire protocol over TCP. Docker containerization ensures consistency across environments and enables independent scaling of services.

## Component Details

### Gardener (Person)
- **Description**: A home gardener using the system to track plants and receive care insights.
- **Responsibilities**: Initiates requests via QR code scanning or natural language queries through the Hermes agent on Telegram.
- **Input Data**: QR code scans (plant IDs), natural language queries via Telegram.
- **Output/Downstream Effects**: Triggers API Gateway requests for plant data retrieval or Hermes agent analysis.

### API Gateway (Container)
- **Technology**: Python/FastAPI running in Docker
- **Description**: Handles authentication, routing, request validation, and response transformation for all backend services.
- **Responsibilities**: 
  - Authenticates users via JWT tokens
  - Routes requests to appropriate services (database or knowledge base)
  - Implements rate limiting and request/response logging
  - Transforms data between client formats and service-specific schemas
- **Input Data**: HTTPS requests from gardeners (via mobile/web or Telegram bot)
- **Output/Downstream Effects**: 
  - SQL queries/writes to PostgreSQL database
  - Vector upsert/query operations to Pinecone knowledge base
  - HTTP responses to clients with appropriate status codes and payloads

### Database (Container)
- **Technology**: PostgreSQL 15 running in Docker
- **Description**: Primary data store for structured plant information, care activities, and user data with ACID transaction guarantees.
- **Responsibilities**:
  - Stores plant records from seed packet information (variety, Latin name, brand, etc.)
  - Maintains care activity logs (watering, fertilizing, environmental conditions)
  - Preserves observation notes and timestamps
  - Supports complex queries for reporting and data analysis
  - Ensures data integrity through transactions and constraints
- **Input Data**: 
  - Structured plant data from API Gateway (inserts/updates)
  - Care activity logs from API Gateway
  - Query requests for plant histories and analytics
- **Output/Downstream Effects**: 
  - Query results returned to API Gateway
  - Confirmation of successful data operations
  - Error responses for constraint violations or system failures

### Knowledge Base Vector Store (Container)
- **Technology**: Pinecone managed vector service
- **Description**: Vector database enabling semantic similarity search for natural language querying and AI-powered insights via the Hermes agent.
- **Responsibilities**:
  - Stores vector embeddings of plant care notes, observations, and care activities
  - Performs similarity search to find related plant care patterns
  - Supports metadata filtering by plant ID, date ranges, and care types
  - Enables natural language queries through the Hermes agent
  - Provides scalable storage for growing plant knowledge base
- **Input Data**: 
  - Vector embeddings from API Gateway (for upsert operations)
  - Similarity search queries with metadata filters from API Gateway
- **Output/Downstream Effects**: 
  - Search results with similarity scores and associated metadata
  - Confirmation of successful vector operations
  - Error responses for service unavailability or index issues

## Traceability
| PRD ID | Requirement Description                                 | Covered in Section(s) | Status       |
|--------|---------------------------------------------------------|-----------------------|--------------|
| FR6    | Users can create plant records with core attributes     | Component Details (Database) | Architected |
| FR7    | Users can store plant data in markdown files            | Deferred (see below)  | Deferred     |
| FR8    | Users can add notes and observations to plant records   | Component Details (Database) | Architected |
| FR9    | Users can attach photos to plant records                | Deferred (see below)  | Deferred     |
| FR10   | Users can update plant records with new information     | Component Details (Database) | Architected |
| FR11   | Users can store multiple plants in a searchable database| Component Details (Database, KB) | Architected |
| FR12   | Users can retrieve complete plant records by scanning QR codes | Component Details (API Gateway) | Architected |
| FR13   | Users can query plant data using natural language via Hermes agent | Component Details (KB, API Gateway) | Architected |
| FR14   | Users can compare data between different plants         | Component Details (Database) | Architected |
| FR15   | Users can filter plant records by various criteria      | Component Details (Database) | Architected |
| FR16   | Users can export plant data for backup or analysis      | Deferred (see below)  | Deferred     |
| FR17   | Users can receive data-driven insights about plant health| Component Details (KB) | Architected |
| FR18   | Users can identify root causes of plant issues          | Component Details (KB) | Architected |
| FR19   | Users can track plant progress over time                | Component Details (Database) | Architected |
| FR20   | Users can receive personalized care recommendations     | Component Details (KB) | Architected |
| FR21   | Users can detect patterns and correlations in plant care data | Component Details (Database, KB) | Architected |
| FR22   | Users can record watering schedules and amounts         | Component Details (Database) | Architected |
| FR23   | Users can record fertilizer applications                | Component Details (Database) | Architected |
| FR24   | Users can track indoor/outdoor status changes           | Component Details (Database) | Architected |
| FR25   | Users can monitor temperature and humidity conditions   | Component Details (Database) | Architected |
| FR26   | Users can record rainfall and precipitation data        | Component Details (Database) | Architected |
| FR27   | Users can track sunlight exposure and shade conditions  | Component Details (Database) | Architected |
| FR28   | Users can record soil amendments and treatments         | Component Details (Database) | Architected |
| FR29   | Users can document pruning, staking, and support activities | Component Details (Database) | Architected |
| FR30   | Users can note pest observations and treatments         | Component Details (Database) | Architected |
| FR31   | Users can combine manual data entry with automated sensor data | Deferred (see below) | Deferred     |
| FR32   | Users can import data from external sources             | Deferred (see below)  | Deferred     |
| FR33   | Users can reconstruct missing data points from historical records | Component Details (Database) | Architected |
| FR34   | Users can validate data quality and correct erroneous entries | Component Details (Database) | Architected |
| FR35   | Users can gap-identify missing data periods in plant histories | Component Details (Database) | Architected |
| FR36   | Users can interact with Hermes agent via Telegram       | Component Details (API Gateway) | Architected |
| FR37   | Users can request analysis of specific plant data       | Component Details (KB) | Architected |
| FR38   | Users can ask for comparisons between different plants  | Component Details (Database, KB) | Architected |
| FR39   | Users can receive predictive insights and recommendations | Component Details (KB) | Architected |
| FR40   | Users can use Hermes for multimodal interactions        | Deferred (see below)  | Deferred     |
| FR41   | Users can access the plant tracking system via mobile device interface | Deferred (see below) | Deferred     |
| FR42   | Users can capture photos directly through the mobile app | Deferred (see below) | Deferred     |
| FR43   | Users can scan QR codes using mobile device camera      | Deferred (see below) | Deferred     |
| FR44   | Users can enter and edit plant data through mobile interface | Deferred (see below) | Deferred     |
| FR45   | Users can view plant histories and analytics on mobile device | Deferred (see below) | Deferred     |
| FR46   | Users can export plant data to CSV format               | Deferred (see below)  | Deferred     |
| FR47   | Users can import plant data from CSV or JSON formats    | Deferred (see below)  | Deferred     |
| FR48   | Users can backup and restore plant databases            | Deferred (see below)  | Deferred     |
| FR49   | Users can share plant insights and data with others     | Deferred (see below)  | Deferred     |
| FR50   | Users can migrate data from markdown to Postgres format | Deferred (see below)  | Deferred     |
| FR51   | Users can customize label layouts                       | Deferred (see below)  | Deferred     |
| FR52   | Users can adjust label sizes                            | Deferred (see below)  | Deferred     |
| FR53   | Users can generate labels with durable materials        | Deferred (see below)  | Deferred     |
| FR54   | Users can reprint labels when originals wear out        | Deferred (see below)  | Deferred     |
| FR55   | Users can design label templates for reuse              | Deferred (see below)  | Deferred     |

### Deferred Requirements
Requirements not covered in this sprint's scope (Database + Knowledge Base) are deferred to future sprints with the following risk assessment:

- **FR7, FR9, FR16, FR46-FFR50**: Data storage format migration - Low risk. Markdown storage is sufficient for MVP; migration to Postgres planned for Sprint 6.
- **FR8, FR22-FR30**: Care activity tracking - Covered in this sprint via database storage.
- **FR31-FR35**: Multi-source data integration - Medium risk. Manual data entry is prioritized; sensor integration deferred to Sprint 7.
- **FR36-FR40**: Hermes agent interactions - Covered in this sprint via API Gateway and KB.
- **FR41-FR45**: Mobile interface - High risk. Deferred to Sprint 6; web interface sufficient for initial validation.
- **FR51-FR55**: Label customization - Low risk. Basic label generation sufficient for MVP; enhancements deferred to Sprint 6.

## Interface Contract

### Database Connection String Format
```
postgresql://username:password@host:port/database?sslmode=require
```
Example: `postgresql://plantuser:securepass@postgres-service:5432/plantdb?sslmode=require`
Environment variable: `DATABASE_CONNECTION_STRING`

### Knowledge Base API Endpoint Schemas

#### Vector Upsert Operation
```
POST /vectors/upsert
Headers:
  Authorization: Bearer <PINECONE_API_KEY>
  Content-Type: application/json
Body:
{
  "vectors": [
    {
      "id": "plant_HABY-2026-001_observation_2026-06-15",
      "values": [0.1, 0.2, ..., 0.768],  // 768-dimensional embedding
      "metadata": {
        "plantId": "HABY-2026-001",
        "type": "observation",
        "date": "2026-06-15",
        "text": "Lower leaves yellowing and curling during heat wave"
      }
    }
  ],
  "namespace": "plant-tracker"
}
```
Success Response: HTTP 200 OK
```json
{
  "upsertedCount": 1
}
```
Error Responses:
- HTTP 400: Invalid request payload
- HTTP 401: Unauthorized (invalid API key)
- HTTP 429: Rate limit exceeded
- HTTP 500: Internal server error
- HTTP 503: Service unavailable

#### Vector Query Operation
```
POST /vectors/query
Headers:
  Authorization: Bearer <PINECONE_API_KEY>
  Content-Type: application/json
Body:
{
  "vector": [0.1, 0.2, ..., 0.768],  // Query embedding
  "topK": 10,
  "includeMetadata": true,
  "filter": {
    "plantId": {"$eq": "HABY-2026-001"},
    "date": {"$gte": "2026-06-01"}
  },
  "namespace": "plant-tracker"
}
```
Success Response: HTTP 200 OK
```json
{
  "matches": [
    {
      "id": "plant_HABY-2026-001_observation_2026-06-10",
      "score": 0.87,
      "metadata": {
        "plantId": "HABY-2026-001",
        "type": "observation",
        "date": "2026-06-10",
        "text": "Noticed slight wilting during heat wave"
      }
    }
  ]
}
```
Error Responses: Same as upsert endpoint

### Authentication Mechanisms
- **PostgreSQL**: Credentials managed via Docker secrets; connection uses `sslmode=require` for TLS encryption
- **Pinecone**: Authentication via Bearer token using environment variable `PINECONE_API_KEY`
- **API Gateway**: 
  - Clients authenticate via JWT tokens issued at `/auth/login` endpoint
  - JWT format: HS256 signed token with 1-hour expiration
  - Secret key managed via Docker secrets
  - Protected routes validate token signature and expiration

## Failure Modes

### 1. DB Connection Pool Exhaustion
- **Mitigation**: 
  - Set connection pool size to 20 connections
  - Implement 5-second connection timeout
  - Exponential backoff retry (max 3 attempts)
- **Fallback Path**: 
  - Return HTTP 503 Service Unavailable with Retry-After header
  - Queue non-critical requests via Hermes agent for later processing
- **Monitoring Metrics**: 
  - Active connection count (alert > 80% utilization)
  - Connection acquisition time (alert > 2s average)
  - Failed connection attempts (alert > 5/minute)
- **Alert Notification**: Slack webhook `#db-alerts` and email `db-team@example.com`

### 2. KB Vector Index Corruption/Drift
- **Mitigation**: 
  - Daily health checks via Pinecone describe_index_stats
  - Weekly backup of index metadata to S3
  - Version-controlled index configuration
- **Fallback Path**: 
  - Degrade to keyword-based search in PostgreSQL using ILIKE queries
  - Serve stale cached results for non-time-sensitive queries
- **Monitoring Metrics**: 
  - Index vector count (alert > 10% unexpected change)
  - Query latency (alert > 500ms p95)
  - Failed vector operations (alert > 1/minute)
- **Alert Notification**: Slack webhook `#kb-alerts` and email `kb-team@example.com`

### 3. Schema Migration Rollback
- **Mitigation**: 
  - Use Flyway with checksum validation
  - Blue-green deployment strategy for zero-downtime migrations
  - Pre-migration backup of PostgreSQL data directory
- **Fallback Path**: 
  - Automatic rollback on migration failure
  - Traffic routed to previous version until fixed
  - Manual intervention for data corruption scenarios
- **Monitoring Metrics**: 
  - Migration success/failure counts
  - Database restart frequency (alert > 1/week)
  - Migration duration (alert > 5x normal)
- **Alert Notification**: Slack webhook `#migration-alerts` and email `dev-team@example.com`

### 4. High Latency Fallback (Cache Miss)
- **Mitigation**: 
  - L1 cache: API Gateway response caching (TTL 30s)
  - L2 cache: Database query result caching (TTL 5m)
  - Stale-while-revalidate pattern for non-critical data
- **Fallback Path**: 
  - Serve stale data from L2 cache with revalidation trigger
  - Queue non-critical requests via Hermes agent for background processing
  - Degrade to basic plant record retrieval without analytics
- **Monitoring Metrics**: 
  - Cache hit rates (L1 alert < 60%, L2 alert < 70%)
  - 95th percentile request latency (alert > 2s)
  - Hermes agent queue depth (alert > 100 items)
- **Alert Notification**: Slack webhook `#perf-alerts` and email `perf-team@example.com`

## Diagram
```mermaid
---
title: C2 Container Diagram for Plant Tracking System
---
flowchart LR
    %% External Actors
    Gardener["Gardener\n(Actor)"]
    
    %% System Boundary
    subgraph sys["Plant Tracking System"]
        %% Containers
        APIGateway["API Gateway\n(Python/FastAPI, Docker)"]
        Database["PostgreSQL Database\n(PostgreSQL 15, Docker)"]
        KBStore["Knowledge Base Vector Store\n(Pinecone Managed Service)"]
    end
    
    %% External Systems
    Telegram[["Telegram\n(External)"]]
    
    %% Relationships
    Gardener -->|Scans QR code via camera| APIGateway
    Gardener -->|Sends natural language query via| Telegram
    Telegram -->|Forwards query to API Gateway via HTTPS/REST| APIGateway
    APIGateway -->|Executes SQL queries via libpq/TCP| Database
    APIGateway -->|Performs vector operations via HTTPS/REST| KBStore
    Database -->|Returns query results via libpq/TCP| APIGateway
    KBStore -->|Returns search results via HTTPS/REST| APIGateway
```