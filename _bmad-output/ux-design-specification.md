---
stepsCompleted: [1, 2, 3]
inputDocuments: ['_bmad-output/briefs/plant-tracker-brief.md', '_bmad-output/prd.md']
---

# UX Design Specification plant-tracking

**Author:** Gerald
**Date:** 2026-05-18

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

## Visual Design: Color Palette & Mood

### Mood Statement

The interface evokes **a warm, sunlit garden shed** — a lived-in sanctuary where tools feel trusted and every object has its place. The mood is simultaneously **grounded, nurturing, and quietly joyful**.

This is not a cold productivity tool. It's a companion that feels like a friend who gardens alongside you — one who understands soil, pots, sunlight, and the small daily rituals of care. The interface should make users feel connected to their plants, calm and capable, and subtly motivated to log activities and celebrate growth.

### Design Principles Driving Color Choices

The palette follows established UI/UX principles:

- **Aesthetic-Usability Effect**: A coherent, beautiful interface creates positive first impressions and makes users more tolerant of minor friction. The warm, sunlit mood leverages this effect.
- **Color Psychology**: Brown tones communicate earthiness and groundedness. Terracotta conveys warmth and energy. Cream provides approachability and calm. All choices align with gardening's physical world.
- **Limited Palette (4-10 core hues)**: Five core colors plus six neutrals keeps the system manageable and consistent.
- **60-30-10 Rule**: ~60% Warm Cream (backgrounds), ~30% Saddle Brown (navigation, text, secondary elements), ~10% Terracotta/Burnt Sienna (accents, CTAs, active states).
- **WCAG 2.1 AA Compliance**: All text/background combinations meet minimum 4.5:1 contrast ratios. All semantic colors pass AA on the primary background.

### Core Color Palette

| Role | Color Name | Hex | Rationale |
|---|---|---|---|
| **Primary** | Terracotta | `#B04E2E` | Sun-baked clay — the emotional heart of the palette. References real terracotta pots, the most iconic object in home gardening. Darkened from original `#C65D3B` to pass WCAG AA with white text (5.28:1). Used for headers, active states, brand accents, primary navigation highlights. |
| **Secondary** | Saddle Brown | `#6B4226` | Rich earth — wooden planters, soil, leather gardening tools. Darkened from original `#8B5A2B` to achieve AAA for body text on Warm Cream (7.68:1). The anchor of the text hierarchy. Used for navigation, secondary buttons, body copy, labels. |
| **Background** | Warm Cream | `#F8F1E3` | Sun-bleached linen — soft, warm, non-fatiguing canvas. Keeps the interface feeling light, clean, and approachable rather than heavy. Excellent for long reading sessions (plant details, activity logs) and reduces eye strain. Unchanged from original. |
| **Accent** | Golden Earth | `#7A5C14` | Harvest sunlight — optimistic, abundant, celebration-worthy. Replaces the original Peru `#CD853F` which was too light for accessible text (L=0.30). 28° hue-separated from Terracotta for differentiation. Used for icons, milestone highlights, subtle decorative details. |
| **CTA** | Burnt Sienna | `#A04010` | Energetic warmth — the most saturated core color (82% saturation) for primary action buttons. Replaces original Save Button `#E07A3D` which shared identical luminance with Peru. Passes AA with white text (6.49:1). Higher saturation naturally draws the eye to important actions. |

### Semantic Colors

All semantic colors pass WCAG AA (4.5:1+) on Warm Cream background. Each maintains the warm, natural mood rather than introducing jarring primary colors.

| Role | Color Name | Hex | Contrast on Warm Cream | Rationale |
|---|---|---|---|---|
| **Success** | Growth Green | `#4A6B2E` | 5.44:1 | Muted olive — feels like new leaves, not artificial neon green. Celebrates completed care tasks and healthy plants. |
| **Warning** | Dry Amber | `#8A6400` | 4.79:1 | Deep amber — stays within the warm family but signals attention needed (dry soil, overdue tasks). |
| **Error** | Overdue Red | `#A0342E` | 6.18:1 | Desaturated terracotta-red — warm, not alarming. Signals overdue care or lost plants while maintaining brand coherence. |
| **Info** | Tip Teal | `#4A6B7A` | 5.08:1 | Muted slate-teal — the only cool tone in the palette. Provides a clear visual break for informational content and care tips without breaking the warm mood. |

### Neutral Scale

A six-step warm-neutral scale eliminates cool grays, which would clash with the terracotta warmth. All neutrals share a brown bias (hue ~25-40°).

| Token | Name | Hex | Luminance | Usage |
|---|---|---|---|---|
| **N-900** | Deep Earth | `#2C1810` | 0.012 | Page headings, display text |
| **N-700** | Soil | `#4A3728` | 0.043 | Body text, labels, primary content |
| **N-500** | Loam | `#7A6552` | 0.141 | Secondary text, captions, helper text (4.90:1 on Warm Cream) |
| **N-300** | Dust | `#A89888` | 0.326 | Tertiary text, placeholders, disabled states |
| **N-200** | Sand | `#D4C8B8` | 0.588 | Borders, dividers, card outlines |
| **N-100** | Parchment | `#EDE5D8` | 0.790 | Subtle backgrounds, hover states, card surfaces |

### WCAG AA Contrast Verification

All text/background combinations verified against WCAG 2.1 AA (4.5:1 minimum for normal text, 3:1 for large text/UI components):

| Foreground | Background | Ratio | Status |
|---|---|---|---|
| N-900 Heading | Warm Cream | 15.00:1 | AA + AAA ✅ |
| N-700 Body | Warm Cream | 10.00:1 | AA + AAA ✅ |
| Saddle Brown | Warm Cream | 7.68:1 | AA + AAA ✅ |
| N-500 Secondary | Warm Cream | 4.90:1 | AA ✅ |
| White | Terracotta | 5.28:1 | AA ✅ |
| White | Saddle Brown | 8.63:1 | AA + AAA ✅ |
| White | Golden Earth | 6.23:1 | AA ✅ |
| White | Burnt Sienna (CTA) | 6.49:1 | AA ✅ |
| Growth Green | Warm Cream | 5.44:1 | AA ✅ |
| Dry Amber | Warm Cream | 4.79:1 | AA ✅ |
| Overdue Red | Warm Cream | 6.18:1 | AA ✅ |
| Tip Teal | Warm Cream | 5.08:1 | AA ✅ |

### Color Application to UI Elements

**Headers**: Terracotta `#B04E2E` background, white text. Or N-900 text on Warm Cream.

**Primary Buttons (Save, Confirm)**: Burnt Sienna `#A04010` background, white text. Hover: darken 10%. Disabled: reduce opacity to 50% with N-300 text overlay.

**Secondary Buttons**: Saddle Brown `#6B4226` background, white text. Or outlined: N-500 border, N-700 text on Warm Cream background.

**Navigation**: Saddle Brown `#6B4226` for inactive items. Terracotta `#B04E2E` for active item.

**Cards**: N-100 Parchment `#EDE5D8` background, N-200 Sand `#D4C8B8` border, N-700 Soil `#4A3728` text.

**Status Badges** (lifecycle stages):
| Stage | Background | Text | Icon |
|---|---|---|---|
| Seed / Germinating | Growth Green `#4A6B2E` | White `#FFFFFF` | 🌱 |
| Seedling | `#6B8F4E` (lighter growth) | White `#FFFFFF` | 🪴 |
| Vegetative | `#3D5A24` (darker growth) | White `#FFFFFF` | 🌿 |
| Flowering | Terracotta `#B04E2E` | White `#FFFFFF` | 🌸 |
| Fruiting | Burnt Sienna `#A04010` | White `#FFFFFF` | 🌶️ |
| Harvested | Golden Earth `#7A5C14` | White `#FFFFFF` | ✅ |
| Lost | Overdue Red `#A0342E` | White `#FFFFFF` | ❌ |

**Care Needed Alerts**:
| Level | Border/Background | Text | Rationale |
|---|---|---|---|
| Overdue | Overdue Red `#A0342E` border, `#F5E8E6` tinted bg | N-700 | Urgent but warm, not alarming |
| Warning | Dry Amber `#8A6400` border, `#F5F0E3` tinted bg | N-700 | Attention without panic |
| Milestone | Tip Teal `#4A6B7A` border, `#E8EDED` tinted bg | N-700 | Informational, cool break |
| All Clear | Growth Green `#4A6B2E` border, `#E6EDE3` tinted bg | Growth Green | Positive, natural |

**Hermes Chat**:
- User messages: Right-aligned, Terracotta `#B04E2E` background, white text
- Hermes responses: Left-aligned, Warm Cream `#F8F1E3` card with N-200 Sand `#D4C8B8` border, N-700 Soil `#4A3728` text

**Activity Log Entries**: N-700 text on Warm Cream. Activity icons in their respective semantic colors. Timestamps in N-500.

**Form Fields**: N-200 Sand `#D4C8B8` border on Warm Cream. Focus state: Terracotta `#B04E2E` border (3px). Error state: Overdue Red `#A0342E` border. Placeholder text in N-300 Dust `#A89888`.

### Why Not Green?

Many plant apps default to green. This palette intentionally avoids green as a primary color, using it only for the semantic "success" state. The reasons:

1. **Differentiation**: The warm terracotta palette visually distinguishes this app from every other plant/garden app on the market.
2. **Authenticity**: Real gardeners live in a world of terracotta pots, brown soil, wooden crates, and golden sunlight — not just green leaves.
3. **Timelessness**: Earth tones don't follow trends. The palette won't look dated in 2-3 years.
4. **Print Harmony**: These colors reproduce well on QR labels and printed care cards.

### Outdoor Readability Considerations

The palette was selected with garden conditions in mind:

- **High luminance contrast**: N-900 on Warm Cream achieves 15:1 — readable in direct sunlight where screen contrast is washed out.
- **Warm bias**: Warm backgrounds maintain perceived brightness better than cool whites under direct sun.
- **No pastel text**: All text colors have low luminance values (L < 0.15) ensuring they remain legible even on washed-out displays.
- **Semantic colors are saturated enough**: All pass 4.5:1 even when screen contrast is reduced by glare.

### Dark Mode (Future Consideration)

Not scoped for initial implementation. Garden usage is predominantly outdoors where dark mode offers minimal benefit and may reduce readability in bright conditions. When dark mode is eventually added, the neutral scale will invert and core colors will shift to reduced-saturation variants to prevent eye strain. The warm bias will be preserved — dark mode should feel like a dimly lit garden shed, not a clinical dark UI.

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
- **Status Badge**: Color-coded pill showing current lifecycle stage (see Color Palette section for exact hex values)
  - 🌱 Seed / Germinating — Growth Green
  - 🪴 Seedling — lighter Growth Green
  - 🌿 Vegetative — darker Growth Green
  - 🌸 Flowering — Terracotta
  - 🌶️ Fruiting — Burnt Sienna
  - ✅ Harvested — Golden Earth
  - ❌ Lost — Overdue Red
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
- If no alerts, show Growth Green check: "✅ All good — no pending care items" (Growth Green `#4A6B2E` border, tinted background `#E6EDE3`)

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
- "Save" button (bottom, full width, Burnt Sienna `#A04010`, white text)
- "✕" dismiss button (top-right, N-500)
- Tap outside form to dismiss (with unsaved changes warning if typed)

#### Hermes Chat Message Format
- **User messages**: Right-aligned, Terracotta `#B04E2E` background, white text, rounded corners
- **Hermes responses**: Left-aligned, Warm Cream `#F8F1E3` card with N-200 Sand `#D4C8B8` border, N-700 Soil `#4A3728` text
  - Response includes: insight text, data reference (collapsed by default), "Log this insight" action button (Burnt Sienna outline)
  - Loading state: Animated plant growth spinner in Saddle Brown (seed → sprout → leaf)