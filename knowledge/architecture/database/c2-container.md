# C2 Container Diagram for Database + Knowledge Base

## Scope

This document describes the Container (C2) level architecture for the Plant Tracking System's backend services, specifically focusing on the database and knowledge base components as specified in Sprint 5: Database + Knowledge Base. The diagram includes exactly the four containers mandated by the sprint contract: User, API Gateway, Database (PostgreSQL), and Knowledge Base Vector Store (Pinecone). External systems such as Telegram are shown outside the system boundary for completeness but are not considered part of the four required containers.

## Architecture Overview

The Plant Tracking System backend follows a containerized microservices architecture. The API Gateway acts as the single entry point, handling authentication, rate limiting, and request/response transformation. It communicates with the PostgreSQL database for structured data storage and retrieval, and with the Pinecone vector store for semantic search and natural language querying capabilities. The User container represents the gardener interacting with the system via the API Gateway. All internal services are containerized using Docker for consistency and independent scaling.

### Component Details

#### User
- **Primary Responsibility**: Represents the gardener who interacts with the plant tracking system through the API Gateway to manage plant records and retrieve insights.
- **Input Data/Triggers**: User actions such as scanning QR codes, submitting plant data, or querying plant insights via natural language.
- **Output/Downstream Effects**: Sends HTTP requests to the API Gateway and receives responses containing plant data or analytical insights.
- **Failure/Graceful Degradation**: If the API Gateway is unavailable, the user receives connection errors and may retry after a timeout. Local caching of recently accessed data may be implemented to improve resilience.

#### API Gateway
- **Primary Responsibility**: Acts as the main entry point for all client requests, providing authentication, rate limiting, input validation, and request routing to appropriate backend services.
- **Input Data/Triggers**: HTTP requests from the User container (representing the gardener's interactions) and internal service communications.
- **Output/Downstream Effects**: Routes requests to the Database or Knowledge Base Vector Store, aggregates responses, and returns formatted data to the caller.
- **Failure/Graceful Degradation**: Implements circuit breaker patterns for downstream service failures. Returns appropriate HTTP error codes (503) when services are unavailable. Uses request queuing and retry mechanisms with exponential backoff for transient failures.

#### Database (PostgreSQL)
- **Primary Responsibility**: Provides reliable, ACID-compliant storage for structured plant data including plant records, care activities, observations, and metadata. Supports complex queries for reporting and data analysis.
- **Input Data/Triggers**: SQL queries and commands from the API Gateway for CRUD operations on plant data.
- **Output/Downstream Effects**: Returns query results to the API Gateway. Ensures data persistence, integrity, and consistency through transactions.
- **Failure/Graceful Degradation**: Utilizes connection pooling with timeout and retry mechanisms. Implements fallback to cached data for read operations during database unavailability. Provides clear error messages for write failures requiring user intervention.

#### Knowledge Base Vector Store (Pinecone)
- **Primary Responsibility**: Enables semantic search and similarity matching for natural language querying and analytical insights. Stores vector embeddings of plant care notes, observations, and metadata for similarity-based retrieval.
- **Input Data/Triggers**: Vector upsert and query requests from the API Gateway containing text data to be embedded or searched.
- **Output/Downstream Effects**: Returns similarity search results and vector storage confirmations to the API Gateway.
- **Failure/Graceful Degradation**: Implements retry mechanisms with exponential backoff for transient failures. Falls back to PostgreSQL-based text search (using ILIKE) for semantic search when the vector store is unavailable. Provides degraded but functional search capabilities.

## Traceability

| PRD ID | Requirement Summary | Document Section |
|--------|---------------------|------------------|
| DB-001 | FR11: Users can store multiple plants in a searchable database format | Component Details → Database |
| DB-001 | FR12: Users can retrieve complete plant records by scanning QR codes | Component Details → API Gateway, Database |
| DB-001 | FR15: Users can filter plant records by various criteria (date, variety, location, etc.) | Component Details → Database |
| DB-001 | FR16: Users can export plant data for backup or analysis | Component Details → Database |
| DB-001 | FR19: Users can track plant progress over time (growth, flowering, fruiting) | Component Details → Database |
| DB-001 | FR32: Users can import data from external sources (weather stations, etc.) | Component Details → Database |
| DB-001 | FR33: Users can reconstruct missing data points from historical records | Component Details → Database |
| DB-001 | FR34: Users can validate data quality and correct erroneous entries | Component Details → Database |
| DB-001 | FR35: Users can gap-identify missing data periods in plant histories | Component Details → Database |
| DB-001 | FR46: Users can export plant data to CSV format for backup and analysis | Component Details → Database |
| DB-001 | FR47: Users can import plant data from CSV or JSON formats | Component Details → Database |
| DB-001 | FR48: Users can backup and restore plant databases | Component Details → Database |
| DB-001 | FR50: Users can migrate data from markdown to Postgres database format | Component Details → Database |
| KB-002 | FR13: Users can query plant data using natural language via Hermes agent | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR14: Users can compare data between different plants | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR17: Users can receive data-driven insights about plant health and care patterns | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR18: Users can identify root causes of plant issues through data analysis | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR20: Users can receive personalized care recommendations based on plant history | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR21: Users can detect patterns and correlations in plant care data | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR36: Users can interact with Hermes agent via Telegram for natural language queries | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR37: Users can request analysis of specific plant data and conditions | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR38: Users can ask for comparisons between different plants or time periods | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR39: Users can receive predictive insights and recommendations from Hermes | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR40: Users can use Hermes for multimodal interactions (text, image, voice when available) | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR49: Users can share plant insights and data with others (optional) | Component Details → API Gateway, Knowledge Base Vector Store |

### Deferred Requirements
The following Functional Requirements are deferred to future sprints as they fall outside the scope of Sprint 5 (Database + Knowledge Base):

- **FR6, FR7, FR8, FR9, FR10**: Core plant record creation and management (handled in earlier sprints)
  - *Impact*: Medium - These requirements are foundational but not blocking for database/KB functionality
  - *Likelihood*: Low - Well understood with clear implementation paths in sprints 1-4
  - *Mitigation*: Clear data models and interfaces ensure seamless integration

- **FR22-FR30**: Environmental and care tracking data points (stored in Database but specific capture mechanisms handled elsewhere)
  - *Impact*: Medium - Data storage ready, capture mechanisms deferred
  - *Likelihood*: Low - Straightforward to implement when needed
  - *Mitigation*: Database schema designed to accommodate these data types

- **FR41-FR45**: Mobile interface specifics (handled in frontend sprints)
  - *Impact*: Low - Backend services independent of frontend implementation
  - *Likelihood*: Low - Clearly scoped to frontend work
  - *Mitigation*: API contracts remain stable regardless of frontend implementation

## Interface Contract Documentation

### Database Connection String Format
- **Template**: `postgresql://username:password@host:port/database`
- **Example**: `postgresql://plantuser:securepass@db-host:5432/plantdb`
- **Environment Variable**: `DATABASE_URL`
- **Pool Configuration**: 
  - Minimum connections: 2
  - Maximum connections: 20
  - Connection timeout: 10 seconds
  - Idle timeout: 30 seconds
  - Max lifetime: 60 minutes

### Knowledge Base API Endpoint Schemas

#### Vector Upsert Endpoint
- **URL**: `/api/v1/vectors/upsert`
- **Method**: `POST`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <pinecone-api-key>`
- **Request Body**:
  ```json
  {
    "vectors": [
      {
        "id": "plant-record-123",
        "values": [0.1, 0.2, 0.3, ...],  // 1500-dimensional embedding vector
        "metadata": {
          "plantId": "HABY-2026-001",
          "text": "Applied 1/2 strength liquid fertilizer on 2026-04-29",
          "timestamp": "2026-04-29T10:30:00Z"
        }
      }
    ],
    "namespace": "plant-tracking"
  }
  ```
- **Success Response**:
  ```json
  {
    "upsertedCount": 1,
    "namespace": "plant-tracking"
  }
  ```
- **Error Responses**:
  - `400`: Invalid request payload (malformed JSON, missing required fields)
  - `401`: Unauthorized (invalid or missing API key)
  - `429`: Rate limit exceeded (too many requests)
  - `500`: Internal server error (vector store failure)
  - `503`: Service unavailable (temporary vector store outage)

#### Vector Query Endpoint
- **URL**: `/api/v1/vectors/query`
- **Method**: `POST`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <pinecone-api-key>`
- **Request Body**:
  ```json
  {
    "vector": [0.1, 0.2, 0.3, ...],  // 1500-dimensional query vector
    "topK": 10,
    "includeMetadata": true,
    "namespace": "plant-tracking"
  }
  ```
- **Success Response**:
  ```json
  {
    "matches": [
      {
        "id": "plant-record-123",
        "score": 0.92,
        "metadata": {
          "plantId": "HABY-2026-001",
          "text": "Applied 1/2 strength liquid fertilizer on 2026-04-29",
          "timestamp": "2026-04-29T10:30:00Z"
        }
      }
    ],
    "namespace": "plant-tracking",
    "usage": {
      "readUnits": 10
    }
  }
  ```
- **Error Responses**:
  - `400`: Invalid request payload (malformed JSON, missing required fields)
  - `401`: Unauthorized (invalid or missing API key)
  - `429`: Rate limit exceeded (too many requests)
  - `500`: Internal server error (vector store failure)
  - `503`: Service unavailable (temporary vector store outage)

### Authentication Mechanisms
- **PostgreSQL**: 
  - Uses libpq with MD5 or SCRAM-SHA-256 authentication
  - Credentials managed via Docker secrets or environment variables
  - Connection encrypted via TLS when required
- **Pinecone Vector Store**:
  - Uses Bearer token authentication with API key
  - API key stored as environment variable (`PINECONE_API_KEY`)
  - All API calls must include `Authorization: Bearer <token>` header
- **API Gateway**:
  - Uses JWT (JSON Web Token) for stateless authentication
  - Tokens issued upon successful login with sufficient expiration (24 hours)
  - Secret key managed via Docker secrets or environment variables
  - Tokens validated on each protected route

## Adversarial Edge Case Coverage

### 1. DB Connection Pool Exhaustion
- **Mitigation Strategy**: 
  - Connection pool sizing (min=2, max=20) based on load testing
  - 30-second timeout for connection acquisition
  - Exponential backoff retry (max 3 attempts) with jitter
- **Fallback Path**: 
  - HTTP 503 (Service Unavailable) response with Retry-After header
  - Redis L2 cache fallback for read-only operations
- **Monitoring Metrics/Alerts**:
  - Active connection count (Critical >90%, Warning >70%)
  - Average connection wait time (Alert >100ms)
  - Failed connection attempts per minute (Alert >10)
  - Alert notification via Slack webhook and email

### 2. KB Vector Index Corruption/Drift
- **Mitigation Strategy**:
  - Hourly health checks via Pinecone describe_index_stats
  - 6-hour snapshot backups to Amazon S3
  - Automatic index recreation from backups if corruption detected
- **Fallback Path**: 
  - PostgreSQL ILIKE-based text search for semantic queries
  - Stale cached results from previous successful queries
- **Monitoring Metrics/Alerts**:
  - Vector count drift (Alert >5% deviation from expected)
  - Query latency p95 (Alert >2x baseline)
  - Backup success/failure status
  - Alert notification via Slack webhook

### 3. Schema Migration Rollback
- **Mitigation Strategy**:
  - Flyway versioned migrations with checksum validation
  - Blue-green deployment for zero-downtime schema updates
  - Pre-migration backup of entire database
- **Fallback Path**: 
  - Automatic rollback to previous schema version on failure
  - Read-only mode during migration window
- **Monitoring Metrics/Alerts**:
  - Migration duration (Alert >30 minutes, 5x normal baseline of 6 minutes)
  - Migration success/failure status
  - Database connection errors during migration
  - Alert notification via Slack webhook and email

### 4. High Latency Fallback (Cache Miss)
- **Mitigation Strategy**:
  - L1/L2 cache layers (Caffeine in-memory + Redis)
  - Stale-while-revalidate cache strategy
  - Cache warming for frequently accessed plant data
- **Fallback Path**:
  - Return stale cached data with X-Stale header set to true
  - Fallback to direct database/vector store request with timeout
- **Monitoring Metrics/Alerts**:
  - Cache hit ratio (Critical <50%, Warning <70%)
  - 95th percentile latency (Alert >2x baseline)
  - Cache eviction rate (Alert >1000 evictions/minute)
  - Alert notification via Slack webhook

# C2 Container Diagram for Database + Knowledge Base

## Scope

This document describes the Container (C2) level architecture for the Plant Tracking System's backend services, specifically focusing on the database and knowledge base components as specified in Sprint 5: Database + Knowledge Base. The diagram includes exactly the four containers mandated by the sprint contract: User, API Gateway, Database (PostgreSQL), and Knowledge Base Vector Store (Pinecone). External systems such as Telegram are shown outside the system boundary for completeness but are not considered part of the four required containers.

## Architecture Overview

The Plant Tracking System backend follows a containerized microservices architecture. The API Gateway acts as the single entry point, handling authentication, rate limiting, and request/response transformation. It communicates with the PostgreSQL database for structured data storage and retrieval, and with the Pinecone vector store for semantic search and natural language querying capabilities. The User container represents the gardener interacting with the system via the API Gateway. All internal services are containerized using Docker for consistency and independent scaling.

### Component Details

#### User
- **Primary Responsibility**: Represents the gardener who interacts with the plant tracking system through the API Gateway to manage plant records and retrieve insights.
- **Input Data/Triggers**: User actions such as scanning QR codes, submitting plant data, or querying plant insights via natural language.
- **Output/Downstream Effects**: Sends HTTP requests to the API Gateway and receives responses containing plant data or analytical insights.
- **Failure/Graceful Degradation**: If the API Gateway is unavailable, the user receives connection errors and may retry after a timeout. Local caching of recently accessed data may be implemented to improve resilience.

#### API Gateway
- **Primary Responsibility**: Acts as the main entry point for all client requests, providing authentication, rate limiting, input validation, and request routing to appropriate backend services.
- **Input Data/Triggers**: HTTP requests from the User container (representing the gardener's interactions) and internal service communications.
- **Output/Downstream Effects**: Routes requests to the Database or Knowledge Base Vector Store, aggregates responses, and returns formatted data to the caller.
- **Failure/Graceful Degradation**: Implements circuit breaker patterns for downstream service failures. Returns appropriate HTTP error codes (503) when services are unavailable. Uses request queuing and retry mechanisms with exponential backoff for transient failures.

#### Database (PostgreSQL)
- **Primary Responsibility**: Provides reliable, ACID-compliant storage for structured plant data including plant records, care activities, observations, and metadata. Supports complex queries for reporting and data analysis.
- **Input Data/Triggers**: SQL queries and commands from the API Gateway for CRUD operations on plant data.
- **Output/Downstream Effects**: Returns query results to the API Gateway. Ensures data persistence, integrity, and consistency through transactions.
- **Failure/Graceful Degradation**: Utilizes connection pooling with timeout and retry mechanisms. Implements fallback to cached data for read operations during database unavailability. Provides clear error messages for write failures requiring user intervention.

#### Knowledge Base Vector Store (Pinecone)
- **Primary Responsibility**: Enables semantic search and similarity matching for natural language querying and analytical insights. Stores vector embeddings of plant care notes, observations, and metadata for similarity-based retrieval.
- **Input Data/Triggers**: Vector upsert and query requests from the API Gateway containing text data to be embedded or searched.
- **Output/Downstream Effects**: Returns similarity search results and vector storage confirmations to the API Gateway.
- **Failure/Graceful Degradation**: Implements retry mechanisms with exponential backoff for transient failures. Falls back to PostgreSQL-based text search (using ILIKE) for semantic search when the vector store is unavailable. Provides degraded but functional search capabilities.

## Traceability

| PRD ID | Requirement Summary | Document Section |
|--------|---------------------|------------------|
| DB-001 | FR11: Users can store multiple plants in a searchable database format | Component Details → Database |
| DB-001 | FR12: Users can retrieve complete plant records by scanning QR codes | Component Details → API Gateway, Database |
| DB-001 | FR15: Users can filter plant records by various criteria (date, variety, location, etc.) | Component Details → Database |
| DB-001 | FR16: Users can export plant data for backup or analysis | Component Details → Database |
| DB-001 | FR19: Users can track plant progress over time (growth, flowering, fruiting) | Component Details → Database |
| DB-001 | FR32: Users can import data from external sources (weather stations, etc.) | Component Details → Database |
| DB-001 | FR33: Users can reconstruct missing data points from historical records | Component Details → Database |
| DB-001 | FR34: Users can validate data quality and correct erroneous entries | Component Details → Database |
| DB-001 | FR35: Users can gap-identify missing data periods in plant histories | Component Details → Database |
| DB-001 | FR46: Users can export plant data to CSV format for backup and analysis | Component Details → Database |
| DB-001 | FR47: Users can import plant data from CSV or JSON formats | Component Details → Database |
| DB-001 | FR48: Users can backup and restore plant databases | Component Details → Database |
| DB-001 | FR50: Users can migrate data from markdown to Postgres database format | Component Details → Database |
| KB-002 | FR13: Users can query plant data using natural language via Hermes agent | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR14: Users can compare data between different plants | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR17: Users can receive data-driven insights about plant health and care patterns | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR18: Users can identify root causes of plant issues through data analysis | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR20: Users can receive personalized care recommendations based on plant history | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR21: Users can detect patterns and correlations in plant care data | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR36: Users can interact with Hermes agent via Telegram for natural language queries | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR37: Users can request analysis of specific plant data and conditions | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR38: Users can ask for comparisons between different plants or time periods | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR39: Users can receive predictive insights and recommendations from Hermes | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR40: Users can use Hermes for multimodal interactions (text, image, voice when available) | Component Details → API Gateway, Knowledge Base Vector Store |
| KB-002 | FR49: Users can share plant insights and data with others (optional) | Component Details → API Gateway, Knowledge Base Vector Store |

### Deferred Requirements
The following Functional Requirements are deferred to future sprints as they fall outside the scope of Sprint 5 (Database + Knowledge Base):

- **FR6, FR7, FR8, FR9, FR10**: Core plant record creation and management (handled in earlier sprints)
  - *Impact*: Medium - These requirements are foundational but not blocking for database/KB functionality
  - *Likelihood*: Low - Well understood with clear implementation paths in sprints 1-4
  - *Mitigation*: Clear data models and interfaces ensure seamless integration

- **FR22-FR30**: Environmental and care tracking data points (stored in Database but specific capture mechanisms handled elsewhere)
  - *Impact*: Medium - Data storage ready, capture mechanisms deferred
  - *Likelihood*: Low - Straightforward to implement when needed
  - *Mitigation*: Database schema designed to accommodate these data types

- **FR41-FR45**: Mobile interface specifics (handled in frontend sprints)
  - *Impact*: Low - Backend services independent of frontend implementation
  - *Likelihood*: Low - Clearly scoped to frontend work
  - *Mitigation*: API contracts remain stable regardless of frontend implementation

## Interface Contract Documentation

### Database Connection String Format
- **Template**: `postgresql://username:password@host:port/database`
- **Example**: `postgresql://plantuser:securepass@db-host:5432/plantdb`
- **Environment Variable**: `DATABASE_URL`
- **Pool Configuration**: 
  - Minimum connections: 2
  - Maximum connections: 20
  - Connection timeout: 10 seconds
  - Idle timeout: 30 seconds
  - Max lifetime: 60 minutes

### Knowledge Base API Endpoint Schemas

#### Vector Upsert Endpoint
- **URL**: `/api/v1/vectors/upsert`
- **Method**: `POST`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <pinecone-api-key>`
- **Request Body**:
  ```json
  {
    "vectors": [
      {
        "id": "plant-record-123",
        "values": [0.1, 0.2, 0.3, ...],  // 1500-dimensional embedding vector
        "metadata": {
          "plantId": "HABY-2026-001",
          "text": "Applied 1/2 strength liquid fertilizer on 2026-04-29",
          "timestamp": "2026-04-29T10:30:00Z"
        }
      }
    ],
    "namespace": "plant-tracking"
  }
  ```
- **Success Response**:
  ```json
  {
    "upsertedCount": 1,
    "namespace": "plant-tracking"
  }
  ```
- **Error Responses**:
  - `400`: Invalid request payload (malformed JSON, missing required fields)
  - `401`: Unauthorized (invalid or missing API key)
  - `429`: Rate limit exceeded (too many requests)
  - `500`: Internal server error (vector store failure)
  - `503`: Service unavailable (temporary vector store outage)

#### Vector Query Endpoint
- **URL**: `/api/v1/vectors/query`
- **Method**: `POST`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <pinecone-api-key>`
- **Request Body**:
  ```json
  {
    "vector": [0.1, 0.2, 0.3, ...],  // 1500-dimensional query vector
    "topK": 10,
    "includeMetadata": true,
    "namespace": "plant-tracking"
  }
  ```
- **Success Response**:
  ```json
  {
    "matches": [
      {
        "id": "plant-record-123",
        "score": 0.92,
        "metadata": {
          "plantId": "HABY-2026-001",
          "text": "Applied 1/2 strength liquid fertilizer on 2026-04-29",
          "timestamp": "2026-04-29T10:30:00Z"
        }
      }
    ],
    "namespace": "plant-tracking",
    "usage": {
      "readUnits": 10
    }
  }
  ```
- **Error Responses**:
  - `400`: Invalid request payload (malformed JSON, missing required fields)
  - `401`: Unauthorized (invalid or missing API key)
  - `429`: Rate limit exceeded (too many requests)
  - `500`: Internal server error (vector store failure)
  - `503`: Service unavailable (temporary vector store outage)

### Authentication Mechanisms
- **PostgreSQL**: 
  - Uses libpq with MD5 or SCRAM-SHA-256 authentication
  - Credentials managed via Docker secrets or environment variables
  - Connection encrypted via TLS when required
- **Pinecone Vector Store**:
  - Uses Bearer token authentication with API key
  - API key stored as environment variable (`PINECONE_API_KEY`)
  - All API calls must include `Authorization: Bearer <token>` header
- **API Gateway**:
  - Uses JWT (JSON Web Token) for stateless authentication
  - Tokens issued upon successful login with sufficient expiration (24 hours)
  - Secret key managed via Docker secrets or environment variables
  - Tokens validated on each protected route

## Adversarial Edge Case Coverage

### 1. DB Connection Pool Exhaustion
- **Mitigation Strategy**: 
  - Connection pool sizing (min=2, max=20) based on load testing
  - 30-second timeout for connection acquisition
  - Exponential backoff retry (max 3 attempts) with jitter
- **Fallback Path**: 
  - HTTP 503 (Service Unavailable) response with Retry-After header
  - Redis L2 cache fallback for read-only operations
- **Monitoring Metrics/Alerts**:
  - Active connection count (Critical >90%, Warning >70%)
  - Average connection wait time (Alert >100ms)
  - Failed connection attempts per minute (Alert >10)
  - Alert notification via Slack webhook and email

### 2. KB Vector Index Corruption/Drift
- **Mitigation Strategy**:
  - Hourly health checks via Pinecone describe_index_stats
  - 6-hour snapshot backups to Amazon S3
  - Automatic index recreation from backups if corruption detected
- **Fallback Path**: 
  - PostgreSQL ILIKE-based text search for semantic queries
  - Stale cached results from previous successful queries
- **Monitoring Metrics/Alerts**:
  - Vector count drift (Alert >5% deviation from expected)
  - Query latency p95 (Alert >2x baseline)
  - Backup success/failure status
  - Alert notification via Slack webhook

### 3. Schema Migration Rollback
- **Mitigation Strategy**:
  - Flyway versioned migrations with checksum validation
  - Blue-green deployment for zero-downtime schema updates
  - Pre-migration backup of entire database
- **Fallback Path**: 
  - Automatic rollback to previous schema version on failure
  - Read-only mode during migration window
- **Monitoring Metrics/Alerts**:
  - Migration duration (Alert >30 minutes, 5x normal baseline of 6 minutes)
  - Migration success/failure status
  - Database connection errors during migration
  - Alert notification via Slack webhook and email

### 4. High Latency Fallback (Cache Miss)
- **Mitigation Strategy**:
  - L1/L2 cache layers (Caffeine in-memory + Redis)
  - Stale-while-revalidate cache strategy
  - Cache warming for frequently accessed plant data
- **Fallback Path**:
  - Return stale cached data with X-Stale header set to true
  - Fallback to direct database/vector store request with timeout
- **Monitoring Metrics/Alerts**:
  - Cache hit ratio (Critical <50%, Warning <70%)
  - 95th percentile latency (Alert >2x baseline)
  - Cache eviction rate (Alert >1000 evictions/minute)
  - Alert notification via Slack webhook

---
title: C2 Container Diagram for Database + Knowledge Base
---
```mermaid
flowchart LR
    %% External system (outside system boundary)
    telegram[["Telegram\n(External System)"]]

    %% System boundary - exactly 4 required containers inside
    subgraph sys["Plant Tracking System"]
        user["User\n(Gardener)"]
        apiGateway["API Gateway\n(Python/FastAPI)"]
        database["Database\n(PostgreSQL 15)"]
        kbStore["Knowledge Base\n(Pinecone)"]
    end

    %% Relationships using standard C4 types with protocol specifics
    user -->|"Uses via HTTPS"| apiGateway
    apiGateway -->|"Reads/Writes via libpq/TCP"| database
    apiGateway -->|"Reads/Writes via REST/HTTPS"| kbStore
    apiGateway -->|"Uses via REST/HTTPS"| telegram
```