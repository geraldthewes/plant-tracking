# Generator Learnings - Sprint 1: C1 System Context

## Architecture Decisions Made
- Confirmed the core entities for the Plant Tracking System: User, Plant Tracking System, Hermes Agent (Telegram), Phomemo M120 Printer, Seed Packet Data Source, and Weather Service (optional)
- Established that the system enables home gardeners to track individual plants using QR-coded labels and derive insights via the Hermes agent
- Determined that label printing relies on the Phomemo M120 Bluetooth printer with no offline printing support in MVP
- Confirmed that seed packet data is manually entered by the user in MVP (no automated extraction from images)
- Verified that the Hermes agent is accessed via Telegram for natural language querying and analysis
- Established that data integrity is maintained through local markdown storage with manual backup capabilities

## Patterns That Scored Well
- Proper Mermaid syntax using double quotes and \n for line breaks (passed validation)
- Clear relationship labels specifying both action and protocol/directionality (e.g., "Scans QR code (User to System)")
- Correct use of C4 diagram shapes: stadium for actors, rectangles for internal system, subroutines for external systems
- Proper separation of concerns in markdown sections (Scope, Assumptions & Constraints, Component Definitions, Adversarial Edge Case Logging, Diagram)
- Comprehensive adversarial edge case logging covering network partitions, hardware failure, and data latency/consistency

## Issues Addressed from Critic Feedback
- Fixed markdown formatting issues: ensured proper blank lines around headings, kept line lengths under 80 characters, fixed double H1 headings, ensured proper list formatting, added trailing newline
- Corrected relationship labels to be more precise and avoid vague verbs
- Improved Component Definitions section readability by breaking long lines and using bullet points
- Enhanced Scope section to be more concise and actionable
- Verified all Mermaid syntax compliance with mmdc validation

## Domain Insights from PRD
- The system's core value proposition is combining durable QR-coded physical labels with comprehensive digital tracking
- Hermes agent enables free-form tracking and natural language querying for personalized insights
- Individual plant data science through Hermes agent provides personalized care recommendations
- Multi-source data fusion combines manual entry with potential automated sensor data
- The system prioritizes user value over monetization, focusing on ease of use in garden environments

## Mermaid/C4 Syntax Rules Confirmed
- Node labels must use double quotes and \n for line breaks (never HTML tags)
- All nodes inside a subgraph must be defined within the subgraph ... end block
- Relationship labels must include action AND technology/protocol
- External systems use subroutine shape [["Name\n(External)"]]
- Databases use cylinder shape [("Name\n(Tech)")] (not used in C1 but noted for future)
- Persons/actors use stadium shape (["Name\n(Role)"])
- Every element must have at least one relationship (no orphan nodes)
- Title must be set via YAML frontmatter (--- / title: ... / ---)