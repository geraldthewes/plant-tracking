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

## Plant Detail Screen Specification

### Screen Purpose
The Plant Detail screen is the primary data-entry surface. It appears immediately after a successful QR scan (or manual ID entry). The user is standing in the garden with one hand, needs to log care activities fast, see what this plant needs, and review recent history — all without navigating away.

### Entry Points
- QR scan success → loads this screen for scanned plant ID
- Manual ID entry → loads this screen for entered plant ID
- Plant Care list → tap any plant → loads this screen
- Activity Log → tap any entry → loads this screen with that plant

### Screen Layout (Portrait/Mobile — Top to Bottom)

#### 1. **Sticky Header** (Always visible during scroll)
- **Back Button**: "←" — returns to previous screen (home, plant care list, or activity log)
- **Plant ID**: e.g., "HABY-2026-001" — monospace, bold, primary identifier
- **Variety Name**: e.g., "Yellow Habanero" — secondary text below ID
- **Status Badge**: Color-coded pill showing current lifecycle stage
  - 🌱 Seed / Germinating (green)
  - 🪴 Seedling (light green)
  - 🌿 Vegetative (dark green)
  - 🌸 Flowering (pink)
  - 🌶️ Fruiting (orange)
  - ✅ Harvested (blue)
  - ❌ Lost (red)
- **More Menu**: "⋮" icon — opens dropdown with: Edit Plant Info, View Full History, Print Label, Duplicate Plant, Delete

#### 2. **Quick Action Bar** (Immediately below header — primary data entry)
A single horizontal row of 5 large, icon-labeled action buttons. These are the most common data-entry actions a gardener performs while standing at a plant.

| Button | Icon | Action | Data Captured |
|---|---|---|---|
| Water | 💧 | Log watering event | Date/time (auto), amount (oz/L), method (hand water, drip, etc.) |
| Feed | 🧪 | Log fertilizer application | Date/time (auto), product name, NPK ratio, dilution rate |
| Condition | 🌡️ | Record environmental conditions | Date/time (auto), temp (°F/°C), humidity (%), notes |
| Photo | 📷 | Capture and attach photo | Date/time (auto), photo file, optional caption |
| Note | 📝 | Add observation note | Date/time (auto), free-text observation |

**Interaction**: Tapping any button opens an inline form (not a full-screen modal) that slides down beneath the action bar. The form is pre-filled with auto-captured data (timestamp) and shows only the fields needed for that activity type. A prominent "Save" button confirms; a "✕" dismisses.

**Design rationale**: These 5 actions cover the core data-entry needs from FR22–FR30, FR9, FR12. They're large enough for gloved fingers and require zero scrolling to reach.

#### 3. **Care Needed Panel** (Contextual alerts for this plant)
A collapsible section showing what this specific plant needs attention for. This is the "what should I do right now?" section.

**Alert Types** (priority ordered):
- **🔴 Overdue Care**: Care tasks that are past their expected schedule
  - Example: "Last watered 3 days ago (typical: every 1–2 days)"
  - Example: "Fertilizer due — 14 days since last application"
- **⚠️ Condition Warning**: Environmental concerns based on recent data
  - Example: "Heat alert — 95°F today, consider shade cloth"
  - Example: "Soil moisture may be low — no rain in 5 days"
- **📋 Upcoming Milestone**: Lifecycle events approaching
  - Example: "Transplant window — 8 weeks indoors, last frost in 1 week"
  - Example: "Days to maturity: ~45 days remaining (expected harvest: Aug 15)"

**Interaction**:
- Tap an alert → opens the corresponding Quick Action form pre-filled (e.g., tap "water overdue" → opens Water form)
- "Mark as Done" dismisses an alert without logging data (for false positives)
- If no alerts, show a green check: "✅ All good — no pending care items"

**Data source**: Calculated from plant's care history frequency, seed packet specs (days to maturity, spacing, etc.), and recent environmental data. Simple rule-based logic, no ML needed initially.

#### 4. **Recent Activity Log** (Scrollable timeline)
A chronological timeline showing the most recent care activities for this plant. This is the "what's been happening?" section.

**Display**: Most recent first, grouped by date. Each entry shows:
- **Timestamp**: Relative time ("2 hours ago", "Yesterday", "Jun 10") + exact date on long press
- **Activity Icon**: Matches the Quick Action icon (💧, 🧪, 🌡️, 📷, 📝)
- **Activity Summary**: One-line summary of the entry
  - 💧 "Watered — 8 oz, hand water"
  - 🧪 "Fertilized — Liquid NPK 5-5-5, 1/2 strength"
  - 🌡️ "Conditions — 82°F, 65% humidity"
  - 📷 "Photo attached" (thumbnail visible)
  - 📝 "Lower leaves yellowing, possible overwatering"

**Interaction**:
- Tap any entry → expands to show full details + "Edit" option
- Swipe left on entry → "Delete" option (with confirmation)
- Bottom of list: "View Full History" button → loads complete historical view (all entries, filters, export)

**Design rationale**: Addresses FR12 (complete record retrieval), FR19 (track progress over time), FR35 (gap identification — visible gaps in timeline signal missed tracking). The recent view keeps the screen focused; full history is one tap away.

#### 5. **Photo Strip** (Horizontal scroll)
A horizontal scrollable row of the 6 most recent photos attached to this plant.

**Display**: Square thumbnails with date overlay (bottom-left corner). Most recent on the right (scroll left to see older).

**Interaction**:
- Tap thumbnail → opens full-screen photo viewer with swipe navigation, date, and caption
- "View All Photos" button on the right edge → loads full photo gallery view

**Design rationale**: Addresses FR9 (photo attachment), FR19 (visual progress tracking). Quick visual reference without leaving the screen.

#### 6. **Hermes Inline Chat Widget** (Collapsible, at bottom)
An inline chat interface for querying the Hermes agent about this specific plant. This is the "get AI insights right here" section.

**Default State**: Collapsed — shows a small bar: "💬 Ask Hermes about this plant" with an expand arrow.

**Expanded State**:
- **Chat History**: Shows previous Hermes queries and responses for this plant (scrollable)
- **Input Field**: Text input with placeholder: "Ask about yellowing leaves, compare with other plants..."
- **Send Button**: Submit query to Hermes
- **Quick Prompts**: Tappable suggestion chips above input:
  - "What might be causing [current issue]?"
  - "Compare with other [variety] plants"
  - "Is the care schedule on track?"
  - "Predict harvest date"

**Response Display**: Hermes responses render as formatted cards with:
- Analysis summary (1–2 sentences)
- Supporting data references (e.g., "Based on 12 watering events and 3 fertilizer applications...")
- Actionable recommendation
- "Log this insight" button → saves the response as a Note entry in the activity log

**Interaction**:
- Tap collapsed bar → expand chat
- Type query + send → Hermes processes and returns insight
- Response appears in chat thread
- Tap "Log this insight" → saves to activity log as a note with Hermes attribution
- Swipe down on expanded chat → collapse

**Data flow**: Hermes queries the Plant Tracking API for this plant's data, analyzes it, and returns insights. The inline widget is the in-app alternative to messaging Hermes via Telegram (FR36–FR41).

#### 7. **Bottom Navigation Bar** (Sticky footer)
A minimal 2-button footer for navigation away from this plant.

| Button | Icon | Action |
|---|---|---|
| Scan Another | 📱 | Opens QR scanner to move to next plant |
| Plant Info | ℹ️ | Opens read-only view of full plant metadata (seed packet data, planting dates, location, etc.) |

**Design rationale**: "Scan Another" enables rapid plant-to-plant workflow (water this plant → scan next → water that). "Plant Info" provides access to static metadata without cluttering the main screen.

### User Flows on Plant Detail Screen

#### Flow 1: Quick Water Log (Primary Use Case)
1. User scans QR code on plant → Plant Detail loads
2. User sees "💧 Last watered 3 days ago" alert in Care Needed panel
3. User taps 💧 Water button in Quick Action Bar
4. Inline form slides down: amount field, method dropdown, auto-filled timestamp
5. User enters "8 oz", selects "Hand Water", taps "Save"
6. Form collapses, new entry appears at top of Activity Log
7. Alert disappears (care is now current)
8. User taps "Scan Another" to move to next plant

#### Flow 2: Investigate Issue with Hermes
1. User scans QR code on plant → Plant Detail loads
2. User notices yellowing leaves, taps 📝 Note button
3. Enters observation: "Lower leaves yellowing and curling"
4. User expands Hermes chat widget
5. Taps "What might be causing [current issue]?" quick prompt
6. Hermes responds: "Based on your data: watering increased during heat wave, likely overwatering"
7. User taps "Log this insight" → Hermes response saved as note
8. User adjusts watering schedule going forward

#### Flow 3: Review History Before Decision
1. User scans QR code on plant → Plant Detail loads
2. User scrolls through Recent Activity Log
3. Taps a few entries to expand and review details
4. Scrolls to Photo Strip, reviews recent photos for visual comparison
5. Uses information to decide on care action
6. Taps appropriate Quick Action button to log the action

### Design Principles Applied
- **Data Entry First**: Quick Action Bar is the first interactive element — no scrolling needed
- **Context-Aware Alerts**: Care Needed panel tells user what to do, not just what happened
- **Progressive Disclosure**: Recent log is visible; full history is one tap away. Hermes is collapsed by default.
- **Garden-Optimized**: Large touch targets, high contrast, minimal text, one-handed operation
- **Rapid Multi-Plant Workflow**: "Scan Another" button enables quick movement between plants
- **Forgiving**: All entries are editable after save; late data entry supported with custom date picker
- **Physical-Digital Bridge**: Plant ID always visible, connecting back to the physical QR label

### Component Specifications

#### Quick Action Form (Inline)
When a Quick Action button is tapped, an inline form slides down beneath the Quick Action Bar:

- **Water Form**:
  - Amount: Number input with units selector (oz / mL / L / cup)
  - Method: Chips — Hand Water · Drip · Soaker · Shower · Other
  - Notes: Optional text field
  - Date: Auto-filled, editable (tap to pick different date for back-logging)

- **Fertilizer Form**:
  - Product: Text input with autocomplete from known products
  - NPK Ratio: Optional text input (e.g., "5-5-5")
  - Dilution: Chips — Full · 1/2 · 1/4 · Custom
  - Notes: Optional text field
  - Date: Auto-filled, editable

- **Condition Form**:
  - Temperature: Number input (°F / °C toggle)
  - Humidity: Number input (%)
  - Notes: Optional text field (e.g., "heat wave", "heavy rain")
  - Date: Auto-filled, editable

- **Photo Form**:
  - Camera capture (primary) or Gallery pick
  - Auto-preview of captured photo
  - Optional caption field
  - Retake / Delete option before saving

- **Note Form**:
  - Text area (2–4 lines, auto-expand)
  - Category chips (optional): Observation · Pest · Disease · Treatment · Other
  - Date: Auto-filled, editable

All forms share:
- "Save" button (bottom, full width, green)
- "✕" dismiss button (top-right)
- Tap outside form to dismiss (with unsaved changes warning if typed)

#### Hermes Chat Message Format
- **User messages**: Right-aligned, green bubble
- **Hermes responses**: Left-aligned, white card with subtle border
  - Response includes: insight text, data reference (collapsed by default), "Log this insight" action
  - Loading state: Animated plant growth spinner (seed → sprout → leaf)