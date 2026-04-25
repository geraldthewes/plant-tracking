# ADR-0006 - Data Persistence Strategy

## Status
Accepted - This data persistence strategy has been reviewed and approved as the foundation for managing plant tracking data in the Plant Tracking System. The decision establishes a clear path for data storage that balances simplicity for MVP with scalability for future growth. This ADR defines how plant records, care activities, observations, and other data will be stored, accessed, and migrated over time.

### Relationships
Relates to ADR-0001 (Technology Stack Selection) and ADR-0005 (Backend Technology Stack) - This data persistence strategy implements the storage layer decisions made in those ADRs, specifically the migration from markdown to PostgreSQL.

## Context
We need to define a data persistence strategy for the Plant Tracking System that supports storing plant records, care activities (watering, fertilizing, etc.), observations, photos, and seed packet information. The system must maintain data integrity, support efficient querying, and provide a migration path from simple storage to a more robust solution as the system grows. The strategy should leverage the PRD's mention of starting with markdown files and migrating to Postgres, while ensuring data is human-readable, backupable, and recoverable.

## Decision
We chose to implement a phased data persistence strategy:
- **MVP Phase**: Local markdown files with structured frontmatter for each plant record
- **Migration Path**: Structured markdown format designed for seamless migration to PostgreSQL
- **Future Phase**: PostgreSQL database with JSONB fields for flexible schema and vector extension for Hermes agent integration
- **Backup Strategy**: Regular exports to JSON/CSV with version-controlled markdown repository as primary backup

### Alternatives Considered
- **Pure Markdown Storage**: Keep all data in markdown files indefinitely - Rejected because it would limit querying capabilities and scalability as the system grows
- **Immediate PostgreSQL**: Start with PostgreSQL from day one - Rejected because it adds unnecessary complexity for MVP and delays initial deployment
- **SQLite Database**: Use SQLite for lightweight relational storage - Rejected because it doesn't support the vector extensions needed for Hermes agent integration and has weaker concurrent write handling
- **MongoDB**: Document-based NoSQL storage - Rejected because it doesn't align with the PRD's preference for structured querying and lacks the ACID guarantees needed for data integrity

### Trade-offs
- **Selected Approach (Phased Markdown to PostgreSQL)**:
  - *Pros*: Simple MVP with zero configuration, clear migration path, supports both human-readable editing and future querying capabilities
  - *Cons*: Requires migration effort later, need to maintain two storage systems during transition
- **Pure Markdown Alternative**:
  - *Pros*: Maximum simplicity, human-readable, no migration needed
  - *Cons*: Poor querying capabilities, scaling limitations, no structured data benefits
- **Immediate PostgreSQL Alternative**:
  - *Pros*: Robust querying from start, ACID transactions, familiar to developers
  - *Cons*: Complex setup for MVP, overkill for initial simplicity, delays deployment
- **SQLite Alternative**:
  - *Pros*: Lightweight, zero-configuration, good for single-user applications
  - *Cons*: Limited concurrent write handling, no native vector support for AI embeddings
- **MongoDB Alternative**:
  - *Pros*: Flexible schema, good for unstructured data, horizontal scaling
  - *Cons*: Eventual consistency model, lacks ACID guarantees, unfamiliar querying syntax

### MVP Implementation Details:
- Each plant record stored as individual markdown file: `plants/PLANT-ID.md`
- Structured frontmatter (YAML) for metadata: variety names, dates, IDs, etc.
- Markdown body for free-form observations, care notes, and analysis
- Attached photos stored in `plants/PLANT-ID/photos/` directory with timestamped filenames
- File-based locking mechanism to prevent concurrent write conflicts
- Regular automated backups to JSON format for migration readiness

### Migration Design:
- Frontmatter fields map directly to PostgreSQL columns
- Markdown body content stored in TEXT column for observations
- Photos referenced by file path in database, stored in object storage or filesystem
- Migration scripts designed to be idempotent and reversible
- Vector column for Hermes agent embeddings (Post-MVP)

## Consequences
### Positive
- Human-readable and editable format supports manual correction when needed
- Zero-configuration startup - system works immediately with file storage
- Easy backup and version control with standard tools (git, rsync, etc.)
- Clear migration path reduces future technical debt
- Supports graceful degradation - core functionality works even if DB unavailable
- Enables offline work with sync capability when connectivity returns

### Negative
- File-based storage may face scaling limitations with large numbers of plants
- Concurrent write handling requires careful implementation
- Backup strategy needs careful design to avoid inconsistent states
- Migration effort required when moving to PostgreSQL
- No built-in querying capabilities beyond grep-like text search in MVP

### Related NFRs
- NFR-DATA-02: Users should be able to export their complete plant database in standard formats (CSV, JSON) - The markdown structure is designed for easy conversion to CSV/JSON, and regular automated exports fulfill this requirement
- NFR-DATA-03: Data should be migratable from markdown storage to Postgres format without loss of information - The structured frontmatter and consistent formatting ensure lossless migration is possible
- NFR-MAINT-01: Data format should be human-readable and editable for manual correction when needed - Markdown with YAML frontmatter is inherently human-readable and editable with standard text editors
- NFR-RELI-01: The system should maintain data integrity with zero lost or corrupted plant records under normal usage conditions - File-based locking and automated backups protect against data loss and corruption