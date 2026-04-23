---
title: Database + Knowledge Base - C2 Container Diagram
---

# Database + Knowledge Base - C2 Container Diagram

## Scope
This C2 container diagram illustrates the deployable components of the Plant Tracking System's backend services introduced in Sprint 5 (Database + Knowledge Base). It shows how the User (gardener) interacts with the system via the API Gateway, which in turn communicates with the PostgreSQL database for structured plant data and the Pinecone vector store for semantic knowledge retrieval. The diagram excludes frontend containers (Mobile App Frontend, Web Interface, QR Scanner, Photo Capture) and external services (Hermes Agent via Telegram, Phomemo Printer) as they are out of scope for this sprint's focus on data persistence and knowledge management.

## Architecture Overview
The system follows a microservices architecture where the API Gateway acts as the single entry point for all client requests. It routes traffic to specialized backend services: the Database service handles CRUD operations for plant records using PostgreSQL, while the Knowledge Base service manages vector embeddings and similarity search using Pinecone. Both services communicate with the API Gateway via REST over HTTPS. The User interacts with the system through frontend applications (not shown) that make HTTPS requests to the API Gateway.

## Component Details
### User
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
| PRD ID | Requirement Description | Document Section |
|--------|-------------------------|------------------|
| FR7 | Users can store plant data in markdown files with structured format | Component Details (Database) |
| FR11 | Users can store multiple plants in a searchable database format | Component Details (Database) |
| FR13 | Users can query plant data using natural language via Hermes agent | Component Details (Knowledge Base) |
| FR15 | Users can filter plant records by various criteria (date, variety, location, etc.) | Component Details (Database) |
| FR17 | Users can receive data-driven insights about plant health and care patterns | Component Details (Knowledge Base) |
| FR37 | Users can request analysis of specific plant data and conditions | Component Details (Knowledge Base) |
| FR38 | Users can ask for comparisons between different plants or time periods | Component Details (Knowledge Base) |
| FR39 | Users can receive predictive insights and recommendations from Hermes | Component Details (Knowledge Base) |
| FR40 | Users can use Hermes for multimodal interactions (text, image, voice when available) | Component Details (Knowledge Base) |
| FR46 | Users can export plant data to CSV format for backup and analysis | Interface Contract Documentation |
| FR48 | Users can backup and restore plant databases | Interface Contract Documentation |
| FR50 | Users can migrate data from markdown to Postgres database format | Interface Contract Documentation |

### Deferred Requirements
The following functional requirements are deferred to future sprints with risk assessment justification:

| PRD ID | Requirement Description | Deferred To | Risk Assessment |
|--------|-------------------------|-------------|-----------------|
| FR6 | Users can create plant records with core attributes from seed packet information | Sprint 6 (Mobile App) | Low risk - depends on mobile frontend development which is scheduled for Sprint 6 |
| FR8 | Users can add notes and observations to plant records with timestamps | Sprint 6 (Mobile App) | Low risk - basic note functionality can be added in mobile app sprint |
| FR9 | Users can attach photos to plant records for visual documentation | Sprint 7 (Advanced Features) | Medium risk - requires image storage and processing infrastructure |
| FR10 | Users can update plant records with new information over time | Sprint 6 (Mobile App) | Low risk - update functionality is straightforward addition to data model |
| FR12 | Users can retrieve complete plant records by scanning QR codes | Sprint 6 (Mobile App) | Low risk - QR scanning depends on mobile camera access |
| FR14 | Users can compare data between different plants | Sprint 6 (Mobile App) | Low risk - comparison UI can be built in mobile app sprint |
| FR16 | Users can export plant data for backup or analysis | Sprint 6 (Mobile App) | Low risk - covered by FR46 but mobile-specific implementation deferred |
| FR18 | Users can identify root causes of plant issues through data analysis | Sprint 7 (Advanced Features) | Medium risk - requires advanced analytics beyond basic insights |
| FR19 | Users can track plant progress over time (growth, flowering, fruiting) | Sprint 6 (Mobile App) | Low risk - progress tracking UI can be added in mobile app sprint |
| FR20 | Users can receive personalized care recommendations based on plant history | Sprint 7 (Advanced Features) | Medium risk - requires recommendation engine development |
| FR21 | Users can detect patterns and correlations in plant care data | Sprint 7 (Advanced Features) | Medium risk - requires correlation analysis capabilities |
| FR22 | Users can record watering schedules and amounts | Sprint 6 (Mobile App) | Low risk - basic input tracking can be added in mobile app sprint |
| FR23 | Users can record fertilizer applications (type, amount, frequency) | Sprint 6 (Mobile App) | Low risk - basic input tracking can be added in mobile app sprint |
| FR24 | Users can track indoor/outdoor status changes | Sprint 6 (Mobile App) | Low risk - simple status flag can be added in mobile app sprint |
| FR25 | Users can monitor temperature and humidity conditions | Sprint 7 (Advanced Features) | Medium risk - requires sensor integration or weather service API |
| FR26 | Users can record rainfall and precipitation data | Sprint 7 (Advanced Features) | Medium risk - requires sensor integration or weather service API |
| FR27 | Users can track sunlight exposure and shade conditions | Sprint 7 (Advanced Features) | Medium risk - requires sensor integration or manual input UI |
| FR28 | Users can record soil amendments and treatments | Sprint 6 (Mobile App) | Low risk - basic input tracking can be added in mobile app sprint |
| FR29 | Users can document pruning, staking, and support activities | Sprint 6 (Mobile App) | Low risk - basic input tracking can be added in mobile app sprint |
| FR30 | Users can note pest observations and treatments | Sprint 6 (Mobile App) | Low risk - basic input tracking can be added in mobile app sprint |
| FR31 | Users can combine manual data entry with automated sensor data | Sprint 7 (Advanced Features) | Medium risk - requires sensor integration framework |
| FR32 | Users can import data from external sources (weather stations, etc.) | Sprint 7 (Advanced Features) | Medium risk - requires external API integration |
| FR33 | Users can reconstruct missing data points from historical records | Sprint 7 (Advanced Features) | Medium risk - requires data imputation algorithms |
| FR34 | Users can validate data quality and correct erroneous entries | Sprint 6 (Mobile App) | Low risk - basic validation can be added in mobile app sprint |
| FR35 | Users can gap-identify missing data periods in plant histories | Sprint 7 (Advanced Features) | Medium risk - requires gap analysis algorithms |

## Interface Contract Documentation
### Database Connection String Format
```
postgresql://username:password@host:port/database?sslmode=require
```
Example: `postgresql://plantuser:securepass@db-service:5432/plantdb?sslmode=require`
Environment variable pattern: `${DATABASE_CONNECTION_STRING}`

### Knowledge Base API Endpoint Schemas
**Upsert Vector Embedding**
```
POST /vectors/upsert
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "vectors": [
    {
      "id": "plant_HABY-2026-001_note_2026-07-01",
      "values": [0.1, 0.2, ..., 0.768],  // 768-dimensional embedding
      "metadata": {
        "plantId": "HABY-2026-001",
        "type": "care_note",
        "timestamp": "2026-07-01T10:30:00Z",
        "content": "Lower leaves yellowing and curling, confirmed overwatering during heat wave per Hermes analysis."
      }
    }
  ]
}
```

**Query Similar Vectors**
```
POST /vectors/query
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "vector": [0.1, 0.2, ..., 0.768],  // Query embedding
  "topK": 10,
  "includeMetadata": true,
  "filter": {
    "plantId": "HABY-2026-001"
  }
}
```

### Authentication Mechanisms
- **API Gateway to Database**: PostgreSQL username/password authentication via libpq
- **API Gateway to Knowledge Base**: Pinecone API key transmitted via HTTP Authorization header (Bearer token)
- **Client to API Gateway**: JWT token validation using HMAC-SHA256 secret stored in environment variables

## Failure Modes
### 1. DB Connection Pool Exhaustion
- **Mitigation Strategy**: 
  - Set maximum pool size to 20 connections
  - Implement connection timeout of 5 seconds
  - Use exponential backoff retry logic (max 3 attempts)
- **Fallback Path**: 
  - Return HTTP 503 (Service Unavailable) with retry-after header
  - Log alert for manual investigation
- **Monitoring Metric**: 
  - Active connections / pool capacity ratio (alert > 80%)
  - Connection wait time 95th percentile (alert > 1s)
- **Alert Notification Channel**: Slack webhook (#plant-tracking-alerts) and email alerts to dev-team@planttracker.example.com


### 2. KB Vector Index Corruption/Drift
- **Mitigation Strategy**:
  - Schedule daily index health checks via Pinecone API
  - Enable automated backups with point-in-time recovery
  - Implement versioned index aliases for zero-downtime rollback
- **Fallback Path**:
  - Switch to backup index if primary shows >15% error rate in test queries
  - Degrade to keyword-based search in PostgreSQL as secondary fallback
- **Monitoring Metric**:
  - Query latency 95th percentile (alert > 200ms increase from baseline)
  - Index error rate from Pinecone health endpoints
- **Alert Notification Channel**: Slack webhook (#plant-tracking-alerts) and email alerts to dev-team@planttracker.example.com


### 3. Schema Migration Rollback
- **Mitigation Strategy**:
  - Use database migration tool (e.g., Flyway) with checksum validation
  - Require all migrations to be backward-compatible
  - Perform blue-green deployment with traffic switching
- **Fallback Path**:
  - Automatically rollback migration on detected error post-deployment
  - Maintain read-only access to previous schema during rollback window
- **Monitoring Metric**:
  - Migration success/failure rate (alert on any failure)
  - Post-deployment error rate increase > 5%
- **Alert Notification Channel**: Slack webhook (#plant-tracking-alerts) and email alerts to dev-team@planttracker.example.com


### 4. High Latency Fallback (Cache miss)
- **Mitigation Strategy**:
  - Implement two-level caching: 
    - L1: In-memory LRU cache (1000 entries) in API Gateway
    - L2: Redis cache (5-minute TTL) for expensive queries
    - Pre-warm caches with frequent query patterns
- **Fallback Path**:
  - Serve stale cache data if available (with staleness warning)
  - Queue expensive requests and notify user of delay via Hermes
- **Monitoring Metric**:
  - Cache hit rate (alert < 70% for L1, < 50% for L2)
  - 95th percentile request latency (alert > 2s)
- **Alert Notification Channel**: Slack webhook (#plant-tracking-alerts) and email alerts to dev-team@planttracker.example.com

```mermaid
C4Container
    Person(user, "Gardener", "External actor who initiates requests for plant data retrieval, updates, and knowledge queries")
    Container(api, "API Gateway", "Python/FastAPI (Docker)", "Centralized service handling authentication, rate limiting, request routing, and response aggregation")
    Container(db, "Database", "PostgreSQL 15 (Docker)", "Relational database storing structured plant data with ACID compliance")
    Container(kb, "Knowledge Base Vector Store", "Pinecone (Managed)", "Vector database storing embeddings for semantic similarity search")
    
    Boundary(b0, "Plant Tracking System") {
        Container(api, "API Gateway", "Python/FastAPI (Docker)", "Centralized service handling authentication, rate limiting, request routing, and response aggregation")
        Container(db, "Database", "PostgreSQL 15 (Docker)", "Relational database storing structured plant data with ACID compliance")
        Container(kb, "Knowledge Base Vector Store", "Pinecone (Managed)", "Vector database storing embeddings for semantic similarity search")
    }
    
    Rel(user, api, "Uses via HTTPS")
    Rel(api, db, "Reads/Writes via SQL")
    Rel(api, kb, "Uses via REST/HTTPS")
```