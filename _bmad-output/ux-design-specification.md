---
stepsCompleted: [1, 2]
inputDocuments: ['_bmad-output/briefs/plant-tracker-brief.md', '_bmad-output/prd.md']
---

# UX Design Specification plant-tracking

**Author:** Gerald
**Date:** 2026-05-15

## Discovery Summary

### System Understanding
- Plant tracking system with QR labels for individual plants
- Uses VARIETY-YYYY-SEQ format for unique plant IDs (e.g., HABY-2026-001)
- Dual-platform: mobile app for garden use, desktop/web app for setup and management
- Core features: QR scanning, photo capture, care logging, Hermes agent integration via Telegram
- Data model: seed packet info + growing conditions + care activities + observations + photos
- Storage: markdown files with migration path to Postgres

### Target Users
- Home gardeners tracking individual plants from seed to harvest
- Users frustrated with losing track of planting dates, care requirements, variety performance
- Gardeners valuing data-driven insights to improve plant health and yields
- Comfortable with technology but preferring simple, low-traction solutions when possible

### Key Features & Goals
- QR code labeling system for instant plant record access (FR5)
- Comprehensive data capture from seed packets and ongoing care (FR6-FR30)
- Natural language interface via Hermes agent for querying and insights (FR36-FR41)
- Photo attachment for visual progress tracking (FR9)
- Environmental and care tracking (watering, fertilizing, conditions) (FR22-FR30)
- Data analysis for identifying patterns and personalized recommendations (FR17-FR21)
- Offline-capable core functionality with markdown storage (FR7, FR51)
- Future migration path to Postgres (FR51)
- Label design: variety name top, QR middle, planted info bottom (FR52-FR56)

### Home Screen Requirements (inferred)
Based on user journeys and PRD, the home screen should support:
- Quick garden actions: QR scanning, quick logging, photo capture
- Recent activity feed showing care events
- Proactive alerts for plants needing attention
- Navigation to detailed views (Garden, Analysis, Library)
- Optimized for one-handed use in outdoor conditions

## Core User Experience

### Defining Experience
The core user action on the home screen is **initiating QR code scanning to access a plant's record for data entry**. This is the gateway to all other functionality and happens every time a user interacts with a plant in the garden. It should be completely effortless - one tap to activate scanner, immediate access to the plant record ready for logging care activities.

### Platform Strategy
Mobile-first responsive web app (accessible via mobile browser) optimized for:
- One-handed use in garden conditions
- Quick access to camera for QR scanning
- Outdoor usability (bright sun to shade)
- Touch targets sized for gardening gloves
- GPS optional for garden mapping/microclimate

### Effortless Interactions
- **QR Scanning**: One tap to activate camera, <3 second recognition once active (NFR-PERF-01)
- **Quick Log**: From plant record, one tap to log watering/fertilizing/humidity/note
- **Photo Capture**: One tap from plant record to take and attach photo
- **Hermes Query**: One tap from plant record to initiate natural language query via Telegram

### Critical Success Moments
- User taps scan button and immediately sees camera activate (<1 sec)
- User points camera at QR code and sees instant recognition and plant record access (<3 sec total)
- User logs care activity and gets confirming feedback (timestamped entry added)
- User takes photo and sees it immediately attached to plant record
- User gets meaningful insight from Hermes agent that changes their care approach

### Experience Principles
1. **Scan-On-Demand**: Camera activates only when user taps scan button (privacy/battery conscious)
2. **Garden-Optimized**: Every interaction works in outdoor conditions with one hand
3. **Immediate Feedback**: Actions provide instant visual confirmation
4. **Progressive Disclosure**: Advanced features accessible but not overwhelming
5. **Physical-Digital Seamless**: QR label is the true entry point to digital care
6. **Forgiving Interface**: Late data entry allowed without penalty (missed tracking recovery)

## Emotional Response

### Primary Emotions
1. **Empowerment** - Users feel in control of their plant care journey, able to make data-driven decisions rather than relying on guesswork or memory
2. **Simplicity & Clarity** - The interface feels uncluttered and intuitive, reducing cognitive load in the garden environment where users may be distracted or wearing gloves
3. **Connection** - Users feel more connected to their plants through the ability to see their care history, growth patterns, and insights
4. **Trust** - Confidence that the data is accurate and reliable, enabling better care decisions
5. **Insightful** - Feeling that they're gaining valuable understanding about their plants that improves their gardening skills

### Secondary Emotions
6. **Satisfaction** - From seeing tangible progress and care records accumulate over time
7. **Curiosity** - Encouraged to explore patterns and ask questions via the Hermes agent
8. **Peace of mind** - Knowing they're not losing track of important care information or planting details

### Differentiation from Competitors
Unlike commercial apps that feel transactional or monetization-focused, our system should feel like a **gardener's trusted companion** - humble, helpful, and focused entirely on the user's success with their plants rather than extracting value from them.

The home screen should make users feel: *"I can easily care for my plants better today because I have the right information at my fingertips."*

This aligns with the PRD's emphasis on "better implementation of core plant tracking concepts" that "prioritizes user value through a better implementation of core plant tracking concepts."

## Home Screen Specification

### Screen Layout (Portrait/Mobile)
The home screen centers on QR scanning as the primary interaction (activated on demand), with a row of three action buttons for quick access to key functions.

### Components & Actions

#### 1. **Header** (Always visible)
- **App Title**: "🌱 Plant Tracking" - Identifies the application
- **Settings Icon**: "⚙️" - Opens system configuration screen
- *Action*: Tap settings to access app preferences, label printing configuration, data export/import, etc.

#### 2. **Primary Interaction: QR Scanner Activator** (Dominant central area)
- **Scanner Button**: Large prominent button labeled "📱 Scan Plant QR Code"
- **Hint Text**: Small text below: "Tap to scan QR code and access plant record"
- **Manual Entry Option**: Small text/link "Or enter ID manually" for when scanning isn't possible
- *Actions*:
  - Tap "Scan Plant QR Code" button → Activates camera for QR scanning
  - Point camera at plant label QR code → Instantly retrieves and displays plant record
  - Tap "Or enter ID manually" → Opens manual plant ID entry screen
  - Successful scan/entry transitions to Plant Detail view for that specific plant

#### 3. **Row of Three Action Buttons** (Persistent access, typically bottom)
Each button is prominently sized for one-thumb use in garden conditions.

- **Button 1: Plant Care** 
  - **Label**: "🌿 Plant Care"
  - **Badge**: Shows count of plants needing attention today (e.g., "💧5" for 5 plants needing water/fertilizing/etc.)
  - *Action*: Opens filtered view of plants requiring care today (watering, fertilizing, etc.)
  - *Purpose*: Easy switch to see what plants need care today (addresses user's #2 need)

- **Button 2: Activity/History Log**
  - **Label**: "📓 Activity Log"
  - *No badge* (or could show total entries today if desired)
  - *Action*: Opens browseable list of all care activities across all plants, most recent first
  - *Purpose*: Quick access to see what's been happening in the garden (user expressed interest in activity/news)

- **Button 3: All Other Features**
  - **Label**: "☰ More"
  - *No badge*
  - *Action*: Opens a new screen/section containing all other functionality:
    - **Garden**: Browse/search all plants in grid/list view
    - **Analysis**: Data insights, trends, charts, Hermes agent natural language querying
    - **Library**: Manage varieties, seed packets, origins, label studio (print queue, templates)
    - **Settings**: App configuration, preferences, data export/import, backup/restore
    - **Help**: Tutorials, FAQ, support, about
  - *Purpose*: Provides access to all other functionality without cluttering the home screen (addresses user's #3 need)

### User Flow from Home Screen
1. **Default State**: Scanner button prominent and ready (camera OFF for privacy/battery)
2. **Activate Scanner & Scan/Enter Plant ID**: 
   - Tap "Scan Plant QR Code" button → Camera activates
   - Point camera at plant label QR code → Instant plant record access → From there, log care, take photos, add notes, request Hermes insights, view history
   - OR after tapping scan button: Tap manual entry → Enter plant ID → Access plant record
3. **Quick Access to Plant Care Today**: 
   - Tap "Plant Care" button → See list of plants needing attention today → Tap any plant to access its record for care
4. **Quick Access to Activity/History**:
   - Tap "Activity Log" button → Browse all care activities (most recent first) → Tap any entry to see full plant record
5. **Access All Other Features**:
   - Tap "More" button → Navigate to any other section of the app (Garden, Analysis, Library, Settings, Help)

### Design Principles Applied
- **Scan-On-Demand**: QR scanner activates only when user presses button (addresses privacy/battery concerns)
- **Three-Button Row**: Provides immediate access to the three key action categories requested:
  1. Plant Care (with attention badge) - addresses "what needs care today"
  2. Activity/History Log - addresses desire to see recent activity/news
  3. All Other Features - provides way to access everything else
- **Immediate Feedback**: All actions provide visual confirmation
- **One-Handed Optimized**: Large touch targets for buttons, scanner activation works with natural hand position
- **Progressive Disclosure**: Advanced features accessed via "More" button but not overwhelming home screen
- **Forgiving Interface**: Manual entry option for scanner use; late data entry allowed
- **Garden-Optimized**: Designed for use in outdoor conditions with potential distractions/gloves

This specification strictly implements your requested three-action model for quick access while keeping QR scanning as the primary interaction (activated on demand):
- ✅ **Action #1**: Capture QR code to start entering data on a plant (Scan button → activate camera → scan QR code)
- ✅ **Action #2**: Easy switch to view/do what plants need care today (Plant Care button with attention badge)
- ✅ **Action #3**: Way to get all other functionality (More button opening all other sections)
- Plus added Button 2: Activity/History log per your expressed interest in seeing activity/news on home screen
- The header remains minimal with just app title and settings
- Camera is NOT active by default - user must press scan button to activate it (addresses your concern)