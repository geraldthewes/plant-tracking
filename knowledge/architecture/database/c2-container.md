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
- **Responsibility**: Initiates requests for plant data retrieval, updates, and knowledge queries
- **Boundary**: External actor outside the system boundary

### API Gateway
- **Technology**: Python/FastAPI (Docker container)
- **Responsibility**: 
  - Routes incoming HTTPS requests to appropriate backend services
  - Handles authentication, rate limiting, and request/response transformation
  - Aggregates responses from Database and Knowledge Base services
- **Interfaces**:
  - Receives HTTPS requests from frontend clients
  - Sends SQL queries to Database service via PostgreSQL wire protocol
  - Sends vector operations to Knowledge Base service via REST/HTTPS

### Database
- **Technology**: PostgreSQL 15 (Docker container)
- **Responsibility**:
  - Stores structured plant records, care activities, and environmental data
  - Provides ACID transactions for data integrity
  - Supports complex queries for reporting and analytics
- **Interfaces**:
  - Receives SQL queries from API Gateway via libpq protocol
  - Returns query results and status codes

### Knowledge Base Vector Store
- **Technology**: Pinecone managed service (external)
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
| DB-001 | Users can store plant data in markdown files with structured format | Component Details (Database) |
| DB-002 | Users can store multiple plants in a searchable database format | Component Details (Database) |
| DB-003 | Users can export plant data to CSV format for backup and analysis | Interface Contract Documentation |
| KB-001 | Users can request analysis of specific plant data and conditions | Component Details (Knowledge Base) |
| KB-002 | Users can ask for comparisons between different plants or time periods | Component Details (Knowledge Base) |
| KB-003 | Users can receive data-driven insights about plant health and care patterns | Component Details (Knowledge Base) |
| NFR-01 | The system should maintain data integrity with zero lost or corrupted plant records | Component Details (Database) |
| NFR-02 | Data should be recoverable from backups in case of device failure or data corruption | Interface Contract Documentation |

## Interface Contract Documentation
### Database Connection String Format
```
postgresql://username:password@host:port/database?sslmode=require
```
Example: `postgresql://plantuser:securepass@db-service:5432/plantdb?sslmode=require`

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

```mermaid
flowchart LR
    user(["Gardener\n(Actor)"])
    
    subgraph sys["Plant Tracking System"]
        api["API Gateway\n(Python/FastAPI, Docker)"]
        db[("PostgreSQL\n(Primary DB)")]
        kb[["Pinecone\n(Vector Store)"]]
    end
    
    user -->|"Uses via HTTPS"| api
    api -->|"Executes SQL queries via libpq"| db
    api -->|"Vector operations via REST/HTTPS"| kb
```