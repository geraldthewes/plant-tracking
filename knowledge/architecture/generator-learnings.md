# Generator Learnings - Sprint 1: C1 System Context

## Architecture Decisions Made
- Confirmed the core entities for the Plant Tracking System: User, Plant Tracking System, Hermes Agent (Telegram), Phomemo M120 Printer, Seed Packet Data Source, and Weather Service (optional)
- Established that the system enables home gardeners to track individual plants using QR-coded labels and derive insights via the Hermes agent
- Determined that label printing relies on the Phomemo M120 Bluetooth printer with no offline printing support in MVP
- Confirmed that seed packet data is manually entered by the user in MVP (no automated extraction from images)
- Verified that the Hermes agent is accessed via Telegram for natural language querying and analysis
- Established that data integrity is maintained through local markdown storage with manual backup capabilities
- **Round 3 Update**: Removed self-referencing edge in C1 diagram (internal detail leaking into context view)
- **Round 3 Update**: Simplified edge labels to be concise and include specific protocol/technology (e.g., "via camera", "via Telegram")
- **Round 3 Update**: Added explicit C1 scope declarations for all adversarial edge cases (in-scope/out-of-scope)
- **Round 4 Update**: Fixed self-referencing edge and redundant diagram title pattern; simplified edge labels to be concise with specific protocol/technology annotations; added explicit C1 scope declarations for adversarial edge cases

## Patterns and Approaches that Scored Well with the Critic
- Proper Mermaid syntax using double quotes and \n for line breaks (passed validation)
- Clear relationship labels specifying both action and protocol/directionality (e.g., "Scans QR code via camera")
- Correct use of C4 diagram shapes: stadium for actors, rectangles for internal system, subroutines for external systems
- Proper separation of concerns in markdown sections (Scope, Assumptions & Constraints, Component Definitions, Adversarial Edge Case Logging, Diagram)
- Comprehensive adversarial edge case logging covering network partitions, hardware failure, and data latency/consistency
- Maintained all six required entities in C1 diagram with correct mappings to PRD requirements
- Fixed markdown formatting issues: proper blank lines around headings, consistent 2-space indentation, no trailing whitespace

## Issues the Critic Raised, How You Addressed Them, and What Worked
- **Medium - Mermaid Syntax & Render Compliance**: 
  - Issue: Self-referencing edge (sys→sys) and duplicate title pattern (YAML frontmatter title identical to H1 heading)
  - Addressed: Removed self-referencing edge (architecturally inappropriate for C1); differentiated YAML title ("C1 System Context for Plant Tracking System") from H1 heading ("Plant Tracking System - C1 System Context") to avoid duplication while maintaining both as required
  - What worked: mmdc validation now passes with clean Mermaid syntax
  
- **Medium - Relationship Specification**:
  - Issue: Verbose edge labels with redundant direction tags (e.g., "(User to System)") and missing protocol/technology annotations
  - Addressed: Simplified labels to essential action and protocol (e.g., "Scans QR code via camera" instead of "Scans QR code (User to System)"); added specific technologies (Telegram, Bluetooth, HTTPS/REST)
  - What worked: Labels now follow C4 conventions with action + technology/protocol
  
- **High - Adversarial Edge Case Logging**:
  - Issue: Missing explicit C1 scope declaration for each adversarial case (network partition, hardware failure, data latency)
  - Addressed: Added clear scope declarations for each case:
    * Network Partition: "This falls out of C1 scope (deferred to C2 or later)"
    - Hardware Failure — Phomemo Offline: "This falls out of C1 scope (deferred to C2 or later)"
    - Data Latency/Consistency: "This falls in C1 scope (accepted as manual process)"
  - What worked: Traceability established between architectural decisions and sprint scope

## Domain Insights about the System Gleaned from the PRD
- The system's core value proposition is combining durable QR-coded physical labels with comprehensive digital tracking
- Hermes agent enables free-form tracking and natural language querying for personalized insights
- Individual plant data science through Hermes agent provides personalized care recommendations based on actual garden performance
- Multi-source data fusion combines manual entry (seed packets, observations) with potential automated sensor data (weather service)
- The system prioritizes user value over monetization, focusing on ease of use in garden environments and actionable insights
- QR labelging creates tangible connection between physical plant and digital record, reducing friction in outdoor data collection

## Mermaid/C4 Syntax Rules Confirmed
- Node labels must use double quotes and \n for line breaks (never HTML tags or <br>)
- All nodes inside a subgraph must be defined within the subgraph ... end block (not applicable in C1 as no subgraph used)
- Relationship labels must include action AND technology/protocol (e.g., "via camera", "via Telegram")
- External systems use subroutine shape [["Name\n(External)"]]
- Databases use cylinder shape [("Name\n(Tech)")] (not used in C1 but confirmed for future sprints)
- Persons/actors use stadium shape (["Name\n(Role)"])
- Every element must have at least one relationship (no orphan nodes) - verified all six entities have edges
- Title must be set via YAML frontmatter (--- / title: ... / ---) - confirmed working with mmdc
- Avoid verbose direction tags in labels since arrow direction already indicates flow
- Declare C1 scope (in-scope/out-of-scope) for all adversarial edge cases to enable traceability