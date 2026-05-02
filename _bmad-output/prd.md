---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
inputDocuments: ['_bmad-output/briefs/plant-tracker-brief.md']
workflowType: 'prd'
classification:
  projectType: mobile_app
  domain: general
  complexity: low
  projectContext: greenfield
---

**Product Requirements Document (PRD) – Plant Tracking System with QR Labels**  
**Version:** 0.1 (Rough Draft)  
**Date:** April 19, 2026  
**Author:** Grok (with input from team)  
**Status:** Draft for refinement  

## Executive Summary

A simple, easy-to-use plant tracking system designed for home gardeners that minimizes effort while maximizing insights. The system enables effortless data collection through QR-coded labels and provides actionable analysis to improve plant health over time. Unlike commercial plant tracking apps that feel monetization-focused, this solution prioritizes user value through a better implementation of core plant tracking concepts.

### What Makes This Special

The core insight is a better implementation of plant tracking concepts that improves upon previous approaches, delivering greater value with less work required.

## Project Classification

**Project Type:** mobile_app  
**Domain:** general  
**Complexity:** low  
**Project Context:** greenfield

## Success Criteria

### User Success
Users achieve success when they can accumulate data on each plant to identify learnings about what works and doesn't work, determine root causes of plant issues, and increase their gardening experience and knowledge. Success is measured by the ability to make data-driven decisions that improve plant outcomes.

### Business Success
Success is maximizing the number of healthy plants and, for fruit-bearing plants like peppers, maximizing yields while avoiding pests. The system provides value by enabling better plant care decisions that directly impact plant health and productivity.

### Technical Success
The system must reliably enable QR code scanning in outdoor garden conditions, maintain durable labels that withstand weather elements, ensure data integrity with no lost or corrupted plant records, provide timely access to plant information, and support effective data analysis for identifying patterns and insights.

### Measurable Outcomes
- Percentage increase in healthy plants compared to previous growing seasons
- Yield improvement percentage for fruit-bearing plants
- Reduction in plant loss or pest issues
- Time saved per plant management task (label creation, info retrieval)
- Number of actionable insights generated per growing season
- Gardener confidence and knowledge improvement metrics
- Data completeness rate (percentage of plants with full growth cycle data)

## Product Scope

### MVP - Minimum Viable Product
The essential components for proving the concept:
- QR label generation system using Phomemo M120 printer (supports 40x30mm and 50x70mm formats)
- Simple data storage (markdown files) for plant records
- Basic plant information capture from seed packets
- Label attachment and QR scanning functionality
- Core data model with essential plant attributes
- **Hermes agent integration** for natural language interface and data analysis

### Growth Features (Post-MVP)
Features that make the system competitive:
- Mobile app interface for easier data entry and retrieval
- Automated data analysis scripts for identifying plant care patterns
- Photo attachment capability for visual progress tracking
- Export/import functionality for data backup and sharing
- Enhanced labeling options (colors, custom templates)
- Advanced Hermes agent capabilities for predictive insights

### Vision (Future)
The dream version of the system:
- AI-powered plant disease/pest identification from photos (via Hermes vision capabilities)
- Predictive analytics for optimal planting times and care schedules (Hermes-powered forecasting)
- Integration with weather data for microclimate-specific recommendations
- Community sharing of plant care insights and best practices
- Full Postgres migration with web dashboard for advanced analytics
- Enhanced multimodal Hermes interactions (voice, image analysis)

## User Journeys

The core use case involves gardeners using a mobile web application during plant care activities. When questions arise about plant health or care requirements, gardeners can initiate chat sessions with expert agents (Hermes) for analysis and recommendations.

### Primary User - Success Path: Core Experience Journey
We meet Alex, a home gardener who's just opened a new packet of Yellow Habanero seeds. They're excited to start growing but frustrated from past seasons where they lost track of planting dates, forgot specific care requirements, and couldn't remember which varieties performed best.

Alex takes a clear photo of the seed packet front and back. On their laptop, they open the Plant Tracking web app and create a new plant record. Using their ID system (VARIETY-YYYY-SEQ), they assign HABY-2026-001 to this plant. Alex uploads the seed packet information, the system validates the data and adds it to the plants.md markdown file, and they enter all the data from the packet: variety name, Latin name, brand, days to maturity, germination time, planting depth, spacing, sun requirements, and indoor start time. They also add their planned planting date (2026-04-15) and note that they'll start indoors 8-10 weeks before last frost.

From the laptop web app, they generate a label with the variety name at the top, QR code encoding HABY-2026-001 in the middle, and "Planted 2026" + Latin name at the bottom. They send the print job to their Phomemo M120 printer and attach the label to the pot where they've planted the seeds indoors.

Two weeks later, Alex notices germination and begins tracking: they record the germination date (2026-04-01), note they used a seed starting mix, and record indoor growing conditions (70°F temp, 60% humidity). As the seedlings grow, they track fertilizer applications: "2026-04-15: Applied 1/4 strength liquid fertilizer (NPK 5-5-5)" and "2026-04-29: Applied 1/2 strength liquid fertilizer."

When it's time to transplant outdoors (2026-05-15), Alex updates the plant's location from "indoor seed tray" to "garden bed 3, row 2". They begin tracking outdoor conditions: daily temperature high/low, rainfall amounts, and note any extreme weather events. On 2026-06-10 during a heat wave (95°F high), they notice slight wilting and increase watering frequency, recording: "2026-06-10: Heat wave response - increased watering to twice daily, added shade cloth."

Six weeks after transplanting, Alex notices some leaves on their Habanero plant are yellowing and curling. Concerned, they open the Plant Tracking mobile app in the garden and scan the QR code on the label. The mobile app instantly displays the complete history for HABY-2026-001: indoor start date, germination, fertilizer applications, transplant date, outdoor conditions, and watering schedule. They message their Hermes agent via Telegram: "@hermes_agent analyze HABY-2026-001 for leaf yellowing causes." Hermes queries the Plant Tracking System for the plant's full data, analyzes it, and responds with insights: "Based on your data: 1) Fertilizer applied regularly but watering increased during heat wave, 2) Jimmy Nardello peppers (same planting date) show healthy growth with less frequent watering, 3) Likely overwatering during heat wave rather than fertilizer deficiency." Back in the mobile app, Alex adds an observation note: "2026-07-01: Lower leaves yellowing and curling, confirmed overwatering during heat wave per Hermes analysis."

Alex adjusts their watering schedule to every other day (checking soil moisture first) and continues fertilizing every two weeks. Over the next two weeks, the yellowing stops and new growth appears green and healthy. At season's end, they harvest 45 peppers from this plant. They add final notes: "2026-08-15: First harvest, 2026-09-02: Final harvest, Total yield: 45 peppers. Key insights from Hermes analysis: 1) Habaneros in my garden prefer less frequent watering than I initially provided, especially during heat waves. 2) Regular light fertilizing every two weeks worked well when combined with proper watering. 3) Starting indoors 8 weeks before transplant gave me a 6-week head start on the growing season." These insights get stored with the plant record for reference next season.

### Journey Requirements Summary
This journey reveals requirements for:
- Comprehensive data capture (seed packet info, growing conditions, care activities)
- Environmental tracking (temperature, humidity, rainfall, indoor/outdoor status)
- Input tracking (watering, fertilizing, soil amendments)
- Observation logging with timestamps
- Data visualization and comparison capabilities
- QR code labeling system for instant record access
- Photographic documentation capability
- Data analysis tools for identifying patterns and insights (powered by Hermes agent)
- Flexible data model that accommodates various data types
- Natural language interface for querying plant data and receiving insights

### Primary User - Edge Case: Missed Tracking and Recovery
We meet Sam, an enthusiastic but sometimes forgetful gardener who planted five different pepper varieties but got busy with work and missed tracking several data points.

Sam planted Jalapeño (JALP-2026-002), Serrano (SERR-2026-001), Banana Pepper (BANP-2026-001), and two Habanero plants (HABY-2026-002 and HABY-2026-003) but only recorded the initial planting data for all five. During a particularly busy work week, Sam missed recording watering schedules, fertilizer applications, and temperature data for all plants.

Two weeks later, Sam notices the Jalapeño plants look stunted while the Serrano plants are thriving. Concerned, Sam scans the QR codes on both plant labels. The JALP-2026-002 record shows only planting data with no subsequent care records, while SERR-2026-001 shows the same limited data. Sam realizes they need to reconstruct what happened.

Sam checks their garden calendar and recalls: they fertilized all plants two weeks after transplanting (approximately 2026-05-29), there was a rainfall event of 0.5 inches on 2026-06-05, and they watered deeply twice during that week. They update both plant records with this reconstructed data.

Looking at the data, Sam notices something interesting: despite the same reconstructed care, the Serrano plants are much healthier. Sam consults their Hermes agent: "@hermes_agent compare JALP-2026-002 vs SERR-2026-001 growth patterns" and receives insights: "Despite identical care reconstruction, Serrano shows 40% better growth metrics. Seed packet data indicates Serrano has higher drought tolerance." This helps Sam adjust their care approach for future Jalapeño plants: more consistent watering schedule and better soil moisture retention through mulching.

Sam adds a note to both plant records: "2026-07-15: Learned that Serrano peppers tolerate inconsistent watering better than Jalapeños in my garden soil per Hermes analysis. For future Jalapeño plants, I'll implement a more consistent watering schedule and better soil moisture retention through mulching."

This journey reveals requirements for:
- Data reconstruction capabilities (ability to add/update historical data)
- Gap identification (visualizing missing data periods)
- Comparative analysis tools (easy side-by-side comparison of similar plants)
- Learning capture mechanism (documenting insights gained from missing data situations)
- Forgiving interface that allows late data entry without penalty
- Pattern recognition that works even with incomplete datasets
- Export/import functionality for backing up reconstructed data
- Natural language querying capabilities via Hermes agent for data comparison and analysis

## Innovation & Novel Patterns

### Detected Innovation Areas
1. **QR-Physical-Digital Integration**: Combining durable QR-coded physical labels with comprehensive digital tracking creates a tangible connection between the physical plant and its digital record, reducing the friction of data collection in garden environments.

2. **Hermes-Enhanced Free-Form Tracking**: Using the Hermes agent (via Telegram interface) to handle unstructured care activity tracking, natural language querying, and sophisticated data analysis allows gardeners to record observations in conversational language while still extracting structured insights, making the system adaptable to individual gardening styles and practices.

3. **Individual Plant Data Science**: Applying data science techniques through the Hermes agent to individual plant histories rather than general gardening advice enables personalized care recommendations based on what actually works for each specific plant in each specific environment.

4. **Multi-Source Data Fusion**: Combining manual data entry (scan/chat interface) with automated sensor data collection creates a comprehensive view of plant health and growing conditions without overburdening the user with manual data collection, all analyzed through the Hermes agent.

### Market Context & Competitive Landscape
Existing plant tracking solutions tend to be either:
- Simple journals/apps with basic data entry but limited analysis capabilities
- Sensor-focused systems that excel at environmental monitoring but lack care activity tracking and personalized insights
- Commercial apps that prioritize monetization through subscriptions or premium features rather than user value

Your approach innovates by combining the accessibility of physical labeling with the analytical power of the Hermes agent, creating a system that's both easy to use in the garden and capable of delivering meaningful, personalized insights through natural language interaction.

### Validation Approach
1. **Pilot Testing**: Track a subset of plants using data-driven insights from Hermes agent vs. traditional care methods
2. **Outcome Measurement**: Compare plant health, yield, and resistance to pests/diseases between the two groups
3. **User Feedback**: Collect qualitative feedback on gained insights, confidence in care decisions via Hermes interactions, and time savings
4. **Iterative Improvement**: Refine data collection and Hermes prompting based on real-world results and user experiences

### Risk Mitigation
1. **Data Quality**: Implement validation checks and allow easy correction of erroneous entries
2. **Analysis Accuracy**: Start with simple descriptive statistics via Hermes before progressing to complex predictive models
3. **User Adoption**: Maintain backward compatibility with basic tracking while gradually introducing advanced Hermes features
4. **Technology Dependence**: Ensure core functionality works without Hermes agent for users who prefer simplicity, but enhance with Hermes when available

## Mobile App Specific Requirements

### Platform Requirements
**Dual-platform interaction model:** The system provides two client interfaces serving different use contexts, with all core operations available on both:

- **Mobile App** — Used in the garden during care activities: QR code scanning, photo capture, recording watering/fertilizing, adding observations, quick data lookup. Optimized for one-handed use in outdoor conditions.
- **Desktop/Laptop Web App** — Used at home for initial setup, system configuration, monitoring dashboards, reporting, label generation/printing, data management, and bulk operations.

Both clients communicate with the same backend API and share the same data store. Starting with a responsive web app accessible on both mobile browsers and desktop browsers, with potential for a dedicated mobile app later.

### Device Permissions & Features
- **Camera**: Essential for QR code scanning and plant photography
- **Storage**: For saving plant photos and exporting/importing data
- **Location (GPS)**: Optional but useful for garden mapping and microclimate tracking
- **Notifications**: Not required as the user plans to use Hermes/Telegram for reminders and notifications

### Technical Architecture Considerations
- **Offline Mode**: Not required as the user assumes connectivity will be available in 2026
- **Push Notifications**: Not needed since Hermes/Telegram will handle notifications and reminders
- **App Distribution**: Personal use only, no app store distribution planned
- **Integration Approach**: Direct integration with Hermes agent via Telegram for AI-powered analysis and natural language interface

### Implementation Considerations
- **Development Approach**: Start with a responsive web app (accessible on both mobile and desktop) focused on core QR scanning, data entry, and Hermes integration
- **Technology Stack**: Next.js (React) + Tailwind CSS + TypeScript for frontend (responsive for mobile + desktop), Python for backend API. Hermes agent integrates via Telegram bot and communicates with the Plant Tracking System backend API.
- **Data Storage**: Begin with local markdown/JSON storage as planned, with migration path to Postgres
- **AI Integration**: Hermes agent integrates via Telegram bot interface for natural language querying and analysis. Hermes communicates directly with the Plant Tracking System backend API to fetch plant data and make changes on the user's behalf.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy
**MVP Approach:** Problem-solving MVP focused on delivering core value: enabling gardeners to track individual plants and derive actionable insights through QR labeling and Hermes agent analysis.

**Resource Requirements:** Single developer capable of mobile web app development, familiar with Hermes agent integration via Telegram, and basic data storage/markdown handling.

### MVP Feature Set (Phase 1)
**Core User Journeys Supported:**
- Primary User - Success Path: Core experience journey (complete plant lifecycle tracking)
- Primary User - Edge Case: Missed tracking and recovery

**Must-Have Capabilities:**
- QR label generation and printing system
- Plant database (markdown files with structured data)
- Basic plant information capture from seed packets
- Label attachment and QR scanning functionality
- Note and picture capture capability
- Data retrieval for offline analysis
- **Hermes agent integration via Telegram** for natural language querying and insights

### Post-MVP Features
**Phase 2 (Post-MVP):**
- Mobile app interface for easier data entry and retrieval
- Automated data analysis scripts for identifying plant care patterns
- Photo attachment capability for visual progress tracking
- Export/import functionality for data backup and sharing
- Enhanced labeling options (colors, custom templates)
- Advanced Hermes agent capabilities for predictive insights and multimodal interactions

**Phase 3 (Expansion):**
- AI-powered plant disease/pest identification from photos (via Hermes vision capabilities)
- Predictive analytics for optimal planting times and care schedules (Hermes-powered forecasting)
- Integration with weather data for microclimate-specific recommendations
- Community sharing of plant care insights and best practices
- Full Postgres migration with web dashboard for advanced analytics
- Enhanced multimodal Hermes interactions (voice, image analysis)

### Risk Mitigation Strategy
**Technical Risks:** Start with basic Hermes text integration, validate data quality, ensure graceful degradation when Hermes unavailable
**Market Risks:** Validate core value proposition with early users, iterate based on feedback, focus on solving real gardening problems
**Resource Risks:** Begin with minimal viable scope, leverage existing tools (Phomemo, Telegram/Hermes), expand capabilities incrementally

## Functional Requirements

### Plant Identification & Labeling
- FR1: Users can generate a unique plant ID using the VARIETY-YYYY-SEQ format
- FR2: Users can create QR codes that encode only the plant ID
- FR3: Users can print QR-coded labels using the Phomemo M120 Bluetooth label printer
- FR4: Users can attach labels to plants, pots, or stakes in garden environments
- FR5: Users can scan QR codes to instantly retrieve plant records

### Data Capture & Storage
- FR6: Users can create plant records with core attributes from seed packet information
- FR7: Users can store plant data in markdown files with structured format
- FR8: Users can add notes and observations to plant records with timestamps
- FR9: Users can attach photos to plant records for visual documentation
- FR10: Users can update plant records with new information over time
- FR11: Users can store multiple plants in a searchable database format

### Data Retrieval & Querying
- FR12: Users can retrieve complete plant records by scanning QR codes
- FR13: Users can query plant data using natural language via Hermes agent
- FR14: Users can compare data between different plants
- FR15: Users can filter plant records by various criteria (date, variety, location, etc.)
- FR16: Users can export plant data for backup or analysis

### Analysis & Insights
- FR17: Users can receive data-driven insights about plant health and care patterns
- FR18: Users can identify root causes of plant issues through data analysis
- FR19: Users can track plant progress over time (growth, flowering, fruiting)
- FR20: Users can receive personalized care recommendations based on plant history
- FR21: Users can detect patterns and correlations in plant care data

### Environmental & Care Tracking
- FR22: Users can record watering schedules and amounts
- FR23: Users can record fertilizer applications (type, amount, frequency)
- FR24: Users can track indoor/outdoor status changes
- FR25: Users can monitor temperature and humidity conditions
- FR26: Users can record rainfall and precipitation data
- FR27: Users can track sunlight exposure and shade conditions
- FR28: Users can record soil amendments and treatments
- FR29: Users can document pruning, staking, and support activities
- FR30: Users can note pest observations and treatments

### Multi-Source Data Integration
- FR31: Users can combine manual data entry with automated sensor data
- FR32: Users can import data from external sources (weather stations, etc.)
- FR33: Users can reconstruct missing data points from historical records
- FR34: Users can validate data quality and correct erroneous entries
- FR35: Users can gap-identify missing data periods in plant histories

### Hermes Agent Integration
- FR36: Users can interact with Hermes agent via Telegram for natural language queries
- FR37: Users can request analysis of specific plant data and conditions
- FR38: Users can ask for comparisons between different plants or time periods
- FR39: Users can receive predictive insights and recommendations from Hermes
- FR40: Users can use Hermes for multimodal interactions (text, image, voice when available)
- FR41: **Hermes agent communicates directly with the Plant Tracking System via API** to fetch plant data, query records, and make changes (e.g., adding care notes, updating observations) on the user's behalf when a Telegram request is received

### Mobile Interface
- FR42: Users can access the plant tracking system via mobile device interface
- FR43: Users can capture photos directly through the mobile app
- FR44: Users can scan QR codes using mobile device camera
- FR45: Users can enter and edit plant data through mobile interface
- FR46: Users can view plant histories and analytics on mobile device

### Export/Import & Backup
- FR47: Users can export plant data to CSV format for backup and analysis
- FR48: Users can import plant data from CSV or JSON formats
- FR49: Users can backup and restore plant databases
- FR50: Users can share plant insights and data with others (optional)
- FR51: Users can migrate data from markdown to Postgres database format

### Label Design & Printing
- FR52: Users can customize label layouts (variety name, QR code, planting info)
- FR53: Users can adjust label sizes to fit different stakes and pots
- FR54: Users can generate labels with durable, weather-resistant materials
- FR55: Users can reprint labels when originals wear out or get damaged
- FR56: Users can design label templates for reuse across multiple plants

## Non-Functional Requirements

### Performance
- QR code scanning and plant data retrieval should complete within 3 seconds for optimal user experience in garden settings
- Hermes agent queries should return insights within 10 seconds for natural conversation flow
- Data entry and saving operations should complete within 2 seconds to minimize friction during gardening activities

### Reliability
- The system should maintain data integrity with zero lost or corrupted plant records under normal usage conditions
- QR code scanning should work successfully in 95%+ of attempts under typical garden lighting conditions
- Label printing via Phomemo M120 should succeed in 90%+ of attempts when printer is properly connected and charged
- Data should be recoverable from backups in case of device failure or data corruption

### Usability
- The interface should be usable in outdoor garden conditions with varying light levels (bright sun to shade)
- Core functions (scan QR, add note, take photo) should be accessible within 2 taps from the main screen
- Text should be readable without zoom in typical outdoor lighting conditions
- Touch targets should be appropriately sized for use with gardening gloves or in variable conditions

### Data Portability
- Users should be able to export their complete plant database in standard formats (CSV, JSON)
- Import functionality should support standard data formats for migration or recovery
- Data should be migratable from markdown storage to Postgres format without loss of information

### Maintainability
- The system should support easy label reprinting when originals wear out or get damaged
- Data format should be human-readable and editable for manual correction when needed
- System should allow for graceful degradation when optional features (like Hermes agent) are unavailable
