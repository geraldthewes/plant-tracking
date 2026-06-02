---
stepsCompleted: [1, 2, 3, 4]
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
  - Timestamp: Auto-captured as "now" on save (not visible in form)

- **Fertilizer Form**:
  - Product: Text input with autocomplete from known products
  - NPK Ratio: Optional text input (e.g., "5-5-5")
  - Dilution: Chips — Full · 1/2 · 1/4 · Custom
  - Notes: Optional text field
  - Timestamp: Auto-captured as "now" on save (not visible in form)

- **Condition Form**:
  - Temperature: Number input (°F / °C toggle)
  - Humidity: Number input (%)
  - Notes: Optional text field (e.g., "heat wave", "heavy rain")
  - Timestamp: Auto-captured as "now" on save (not visible in form)

- **Photo Form**:
  - Camera capture (primary) or Gallery pick
  - Auto-preview of captured photo
  - Optional caption field
  - Retake / Delete option before saving
  - Timestamp: Auto-captured as "now" on save (not visible in form)

- **Note Form**:
  - Text area (2–4 lines, auto-expand)
  - Category chips (optional): Observation · Pest · Disease · Treatment · Other
  - Timestamp: Auto-captured as "now" on save (not visible in form)

All forms share:
- "Save" button (bottom, full width, Burnt Sienna `#A04010`, white text)
- "✕" dismiss button (top-right, N-500)
- Tap outside form to dismiss (with unsaved changes warning if typed)

#### Hermes Chat Message Format
- **User messages**: Right-aligned, Terracotta `#B04E2E` background, white text, rounded corners
- **Hermes responses**: Left-aligned, Warm Cream `#F8F1E3` card with N-200 Sand `#D4C8B8` border, N-700 Soil `#4A3728` text
  - Response includes: insight text, data reference (collapsed by default), "Log this insight" action button (Burnt Sienna outline)
  - Loading state: Animated plant growth spinner in Saddle Brown (seed → sprout → leaf)

## Garden Browse Screen Specification

### Screen Purpose
The Garden Browse screen presents all tracked plants in a scannable, filterable grid/list. It's the primary discovery surface for finding any plant without scanning a QR code — used from the Home screen via More → Garden.

### Entry Points
- Home screen → Tap "More" button → Tap "Garden" section
- Plant Detail → "Scan Another" → QR scan fails or user backs out → lands here

### Screen Layout (Portrait/Mobile — Top to Bottom)

#### 1. **Header** (Sticky)
- **Back Button**: "←" — returns to Home screen
- **Screen Title**: "🌿 Garden" — N-900 text on Warm Cream
- **Search Icon**: "🔍" — opens search overlay
- **Add Button**: "+" icon — opens "Add New Plant" flow (rightmost, Burnt Sienna `#A04010` circular FAB, white "+")

#### 2. **Filter Bar** (Sticky below header)
A horizontal scrollable row of filter chips. Single-select for status, multi-select for variety/location.

| Filter Chip | Default | Options |
|---|---|---|
| Status | "All" | Seed · Seedling · Vegetative · Flowering · Fruiting · Harvested · Lost |
| Variety | "All" | Dynamically populated from existing plants (max 8 visible, scroll for more) |
| Location | "All" | Dynamically populated from plant locations |

**Interaction**:
- Tap a chip → toggle selection (selected: Terracotta `#B04E2E` background, white text; unselected: N-100 Parchment background, N-700 text, N-200 border)
- Changes apply instantly (client-side filter, no API call)
- Active filter count shown as a small badge on the filter bar if >0 filters active

#### 3. **Sort Toggle** (Right of filter bar)
Small text link: "Recent" / "Name A→Z" / "Name Z→A" — cycles on tap. Default: "Recent" (most recently updated first).

#### 4. **Plant Cards Grid** (Main content)
A 2-column grid of plant cards. Each card shows:

- **Status Badge**: Small color-coded pill in top-right corner (see Color Palette section)
- **Variety Name**: N-700 Soil, bold, max 2 lines, ellipsis overflow
- **Plant ID**: N-500 Loam, monospace, single line (e.g., "HABY-2026-001")
- **Lifecycle Stage Icon**: Large emoji center of card (🌱, 🪴, 🌿, 🌸, 🌶️, ✅, ❌)
- **Days Since Planted**: N-500 Loam, bottom of card (e.g., "42 days")
- **Care Alert Dot**: Small Overdue Red `#A0342E` dot overlay if plant has overdue care

**Interaction**:
- Tap card → opens Plant Detail screen for that plant
- Long-press card → context menu: Print Label · Duplicate · Delete

#### 5. **Empty State** (When no plants exist)
- Centered illustration: Large 🌱 emoji
- Text: "No plants yet" — N-700 Soil
- Subtext: "Tap + to add your first plant" — N-500 Loam
- CTA Button: "Add Your First Plant" — Burnt Sienna `#A04010`, white text

#### 6. **Search Overlay** (Modal)
- Full-width overlay from top, Warm Cream background
- Search input with N-200 Sand border, placeholder: "Search by ID, variety, or location"
- Real-time results below input as user types
- "✕" dismiss button (top-right)
- Tap outside overlay to dismiss

### Design Principles Applied
- **Quick Discovery**: 2-column grid maximizes visible plants per screen
- **Status-First**: Color badges visible at a glance — user can spot plants needing attention
- **Progressive Filtering**: Start broad, filter down. No empty filter states.
- **One-Tap to Action**: Add button always visible, card tap goes straight to detail
- **Garden-Optimized**: Large card touch targets, high contrast text

## Add New Plant Workflow Specification

### Workflow Overview
Adding a new plant is a multi-step wizard that captures all plant data from seed packet information through planting details. The wizard guides the user through: selecting or creating the genus → selecting or creating the variety → linking a seed packet → capturing planting details → generating the unique plant ID → previewing and confirming.

**Access**: Garden Browse → "+" button
**Platform**: Optimized for both mobile and desktop (more likely to be completed on desktop with seed packet in hand)

### Screen Layout — Wizard Format

The wizard uses a step indicator at the top showing progress. Each step can be navigated forward ("Continue") or backward ("← Back"). The final step shows a confirmation screen.

**Step Indicator**: Horizontal dots with labels — "Genus" · "Variety" · "Packet" · "Details" · "Confirm" — current step in Terracotta `#B04E2E`, completed steps in Growth Green `#4A6B2E`, future steps in N-300 Dust.

### Step 1: Select or Create Genus

**Purpose**: Identify the biological genus of the plant (e.g., *Capsicum*, *Solanum*, *Brassica*).

**Layout**:
- **Header**: "Which genus?" — N-900 text
- **Help Text**: "The biological genus (e.g., Capsicum for peppers, Solanum for tomatoes)" — N-500
- **Existing Genus List**: Scrollable list of known genera, each as a tappable card:
  - Genus name (italicized, N-700, e.g., "*Capsicum*")
  - Species count (N-500, e.g., "3 varieties")
- **Search Bar**: "Search genera..." — appears when 5+ genera exist
- **"Create New Genus" Button**: Burnt Sienna outline button, full width, at bottom: "+ Create New Genus"

**Interaction — Select Existing**:
- Tap genus card → highlighted with Terracotta border → "Continue" button enabled → advances to Step 2

**Interaction — Create New**:
- Tap "+ Create New Genus" → inline form slides down:
  - **Genus Name**: Text input, placeholder: "Capsicum", required, italicized preview
  - **Common Name**: Text input, placeholder: "Peppers", optional
  - **Family**: Text input, placeholder: "Solanaceae", optional
  - "Save Genus" button (Burnt Sienna `#A04010`) → saves genus, auto-selects it → advances to Step 2
  - "Cancel" → collapses form
- Genus is saved to the library immediately and available for future plants

### Step 2: Select or Create Variety

**Purpose**: Select the specific variety/cultivar within the chosen genus.

**Layout**:
- **Header**: "Which variety?" — N-900 text
- **Context Badge**: Shows selected genus (e.g., "*Capsicum*" — Terracotta pill, N-100 background)
- **Existing Variety List**: Scrollable list of varieties within selected genus:
  - Variety name (N-700 bold, e.g., "Yellow Habanero")
  - Common abbreviation (N-500, e.g., "HABY")
  - Packet count (N-500, e.g., "2 packets on file")
- **Search Bar**: "Search varieties..." — appears when 5+ varieties exist
- **"Add New Variety" Button**: Burnt Sienna outline button: "+ Add New Variety"

**Interaction — Select Existing**:
- Tap variety card → highlighted → "Continue" enabled → advances to Step 3

**Interaction — Add New Variety**:
- Tap "+ Add New Variety" → inline form slides down:
  - **Variety Name**: Text input, placeholder: "Yellow Habanero", required
  - **Abbreviation**: Text input, placeholder: "HABY", required, max 6 chars, auto-uppercased
    - Validation: Check for duplicates within genus. If conflict: "HABY is already used for 'Habanero'. Suggest: HABY2"
  - **Synonyms**: Text input, placeholder: "Habanero Amarillo, Yellow Heat", optional, comma-separated
  - "Save Variety" button → saves to library → auto-selects → advances to Step 3
  - "Cancel" → collapses form

### Step 3: Link Seed Packet

**Purpose**: Associate the plant with a physical seed packet. This pre-fills planting specifications from the packet's stored data.

**Layout**:
- **Header**: "Which seed packet?" — N-900 text
- **Context Summary**: Shows selected genus + variety (e.g., "*Capsicum* — Yellow Habanero")
- **Existing Packet List**: Cards showing seed packets matching the selected variety:
  - Brand name (N-700 bold, e.g., "Baker Creek")
  - Packet date (N-500, e.g., "Packed for 2024")
  - Small thumbnail of packet photo (if available)
  - Specs summary (N-500, e.g., "80–100 days · 1/4\" deep · Full Sun")
- **No Matching Packets State**: If no packets exist for this variety:
  - Message: "No packets on file for Yellow Habanero" — N-500
  - CTA: "+ Add Seed Packet" (Burnt Sienna outline) → opens Add Seed Packet flow (see below)
- **"Skip for Now" Link**: N-500 text link at bottom: "Skip — I'll add details manually"

**Interaction — Select Existing**:
- Tap packet card → highlighted → packet data pre-fills into Step 4 → "Continue" advances to Step 4

**Interaction — Add Seed Packet**:
- Tap "+ Add Seed Packet" → navigates to Add Seed Packet flow (see full spec below)
- Upon completion of Add Seed Packet → returns here with new packet pre-selected → advances to Step 4

**Interaction — Skip**:
- Tap "Skip for Now" → advances to Step 4 with empty fields for manual entry

### Step 4: Planting Details

**Purpose**: Capture all planting-specific data. If a seed packet was linked in Step 3, the packet's specifications pre-fill the form. User can override any field.

**Layout**:
- **Header**: "Planting details" — N-900 text
- **Form Fields** (all scrollable, grouped logically):

**Group: Identity**
| Field | Type | Pre-filled? | Required? | Notes |
|---|---|---|---|---|
| Plant ID Preview | Display only | Auto-generated | Yes | Shows next ID in VARIETY-YYYY-SEQ format (e.g., "HABY-2026-002"). Read-only. |
| Year Planted | Year picker | Current year | Yes | Default: current year |

**Group: Seed Packet Info** (greyed out / read-only if packet linked; editable if skipped)
| Field | Type | Pre-filled from packet? | Required? |
|---|---|---|---|
| Variety Name | Text | Yes | Yes |
| Latin Name | Text | Yes | Yes | Italicized display |
| Brand | Text | Yes | Yes |
| Days to Maturity | Text range | Yes | Yes | e.g., "80–100" |
| Days to Germination | Text range | Yes | Yes | e.g., "7–21" |
| Planting Depth | Text | Yes | Yes | e.g., "1/4\"" |
| Plant Spacing | Text range | Yes | Yes | e.g., "12\"–18\"" |
| Sun Requirement | Dropdown | Yes | Yes | Full Sun · Partial Sun · Full Shade · Partial Shade |
| Start Indoors | Text | Yes | Yes | e.g., "8–10 weeks before last frost" |
| Heirloom / Non-GMO / Organic | Multi-chips | Yes | No | Toggles: Heirloom · Non-GMO · Organic · Open-Pollinated |
| Scoville Units | Text | Yes | No | e.g., "100,000–350,000" |

**Group: Planting Actions**
| Field | Type | Default | Required? |
|---|---|---|---|
| Planted Date | Date picker | Today | Yes | |
| Planting Location | Text | Empty | No | e.g., "indoor seed tray", "garden bed 3, row 2" |
| Seed Packet Photo | Photo upload | Empty | Recommended | Tap to take photo or pick from gallery |
| Notes | Text area (2–4 lines) | Empty | No | Any additional observations |

**Interaction**:
- All fields are editable even if pre-filled (user can override packet data)
- Required fields validated on "Continue" — inline error messages in Overdue Red `#A0342E`
- "Continue" button (bottom, Burnt Sienna `#A04010`) → advances to Step 5
- "Save as Draft" link (N-500) → saves partial data, returns to Garden Browse

### Step 5: Confirm & Generate

**Purpose**: Review all data, confirm, and generate the plant record + QR label.

**Layout**:
- **Header**: "Review & confirm" — N-900 text
- **Data Summary**: Read-only card showing all entered data, organized in collapsible sections:
  - **Identity**: Plant ID, Variety, Genus
  - **Packet Info**: All seed packet fields
  - **Planting**: Date, location, notes
  - **Photos**: Packet photo thumbnail (if attached)
- **Edit Links**: Each section has a "← Edit" link that jumps back to the relevant step
- **Label Preview**: QR label mockup showing:
  - Top: Variety name
  - Middle: QR code (visual placeholder)
  - Bottom: Year planted + Latin name
- **Action Buttons** (bottom, sticky):
  - "Confirm & Create Plant" — Burnt Sienna `#A04010`, white text, full width
  - "Add to Print Queue" — Burnt Sienna outline checkbox: "☐ Add label to print queue"

**Interaction**:
- Tap "Confirm & Create Plant" → saves plant record → shows success screen
- Success screen: Large ✅ Growth Green icon, "Plant HABY-2026-002 created!" text
- Post-success actions (button row):
  - "View Plant Record" → navigates to Plant Detail screen
  - "Print Label" → sends label to print queue (Phomemo M120)
  - "Add Another Plant" → resets wizard to Step 1, keeps genus/variety selected
  - "Done" → returns to Garden Browse screen

### User Flow — Add New Plant (Complete Path)

#### Flow 1: New plant from existing packet
1. Garden Browse → tap "+" button → wizard opens at Step 1
2. Select existing genus: "Capsicum" → Continue
3. Select existing variety: "Yellow Habanero" → Continue
4. Select existing seed packet: "Baker Creek, Packed 2024" → packet data pre-fills → Continue
5. Review pre-filled details, adjust planted date to today, add location: "indoor seed tray" → Continue
6. Review summary, confirm → Plant HABY-2026-002 created
7. Tap "View Plant Record" → Plant Detail screen loads

#### Flow 2: Completely new variety (no packet, no variety, no genus)
1. Garden Browse → tap "+" → Step 1
2. Tap "+ Create New Genus" → enter "Solanum", common: "Tomatoes" → Save → auto-selects → Continue
3. Step 2: Tap "+ Add New Variety" → enter "Brandywine", abbreviation: "BRNW" → Save → Continue
4. Step 3: No packets exist → tap "+ Add Seed Packet" → complete packet flow → return with packet selected → Continue
5. Step 4: Packet data pre-fills → add planting location → Continue
6. Step 5: Review → Confirm → Plant BRNW-2026-001 created
7. Tap "Add Another Plant" → wizard resets to Step 1, Solanum pre-selected

#### Flow 3: Quick add (skip packet)
1. Garden Browse → tap "+" → Step 1
2. Select "Capsicum" → Continue
3. Select "Jimmy Nardello" → Continue
4. Step 3: Tap "Skip for Now" → Continue
5. Step 4: Manually enter all variety details, planted date, location → Continue
6. Step 5: Review → Confirm → Plant JIMN-2026-004 created

## Add Seed Packet Workflow Specification

### Workflow Overview
The Add Seed Packet flow captures all data from a physical seed packet: a front/back photo, the brand, variety details, and all planting specifications printed on the packet. This data is stored once and reused for every plant created from that packet.

**Access**: During "Add New Plant" (Step 3) OR from Library → Seed Packets → "+"

### Screen Layout — Single-Page Form

Unlike the multi-step plant wizard, the seed packet form is a single scrollable page with clear sections. The primary input method is manual entry after photographing the packet.

#### 1. **Header**
- **Back Button**: "←" — returns to previous screen (Add Plant wizard or Packet List)
- **Screen Title**: "📦 New Seed Packet" — N-900 text

#### 2. **Photo Capture Section** (Top, prominent)
- **Dual Photo Areas**: Two side-by-side photo drop zones:
  - Left: "Front of Packet" — large tap target, N-200 border, camera icon centered
  - Right: "Back of Packet" — same styling
- **Interaction**:
  - Tap zone → opens camera (primary) or gallery picker (secondary option)
  - Photo fills zone with 100% width, aspect-ratio preserved
  - "Retake" and "✕ Remove" buttons appear on photo overlay (top-right)
  - Both photos are required for complete records but only Front is technically required

#### 3. **Brand & Origin Section**
| Field | Type | Required? | Notes |
|---|---|---|---|
| Brand | Text input with autocomplete | Yes | Autocomplete from known brands (Baker Creek, Botanical Interests, etc.) |
| Origin (Supplier) | Dropdown with "Add New" | No | Select from known suppliers or create new inline |
| Packed For / Lot Date | Text input | No | e.g., "Packed for 2024" |
| Seed Count / Weight | Text input | No | e.g., "18 seeds" or "300 mg" |

**Interaction — New Brand**: If brand not in autocomplete list, user types it → on blur, it's added to the brand library.

**Interaction — New Origin**: Tap "+ New" in dropdown → inline text input appears → type name → "Add" saves it.

#### 4. **Variety Information Section**
| Field | Type | Required? | Notes |
|---|---|---|---|
| Variety Name | Text input | Yes | e.g., "Yellow Habanero Pepper" |
| Latin Name | Text input | Yes | Italicized preview, e.g., "*Capsicum chinense*" |
| Genus | Dropdown with "Add New" | Yes | Auto-suggested from Latin name (first word). If Latin name is "*Capsicum chinense*", pre-selects "Capsicum". |
| Scoville Units | Text input | No | e.g., "100,000–350,000" (for peppers) |
| Certifications | Multi-chips | No | Heirloom · Non-GMO · Organic · Open-Pollinated · Hybrid |

**Interaction — Genus Auto-Suggest**: When Latin Name is entered, the system extracts the genus (first word) and checks if it exists in the library. If it exists, it's pre-selected. If not, "Add New Genus" option appears inline: "Capsicum not found. [Create it?]" — tapping creates the genus with the extracted name.

#### 5. **Planting Specifications Section**
| Field | Type | Required? | Notes |
|---|---|---|---|
| Days to Maturity | Text range input | Yes | e.g., "80–100" |
| Days to Germination | Text range input | Yes | e.g., "7–21" |
| Planting Depth | Text input | Yes | e.g., "1/4\"" |
| Plant Spacing | Text range input | Yes | e.g., "12\"–18\"" |
| Sun Requirement | Dropdown | Yes | Full Sun · Partial Sun · Full Shade · Partial Shade |
| Start Indoors | Text input | Yes | e.g., "8–10 weeks before last frost" |

#### 6. **Notes Section**
- Free-text area (2–4 lines, auto-expand)
- Placeholder: "Any special instructions printed on the packet..."
- Optional

#### 7. **Action Buttons** (Bottom, sticky)
- **"Save Packet"** — Burnt Sienna `#A04010`, white text, full width — saves packet to library
- **Post-save behavior**:
  - If accessed from Add Plant wizard → returns to Step 3 with new packet pre-selected
  - If accessed from Library → shows success toast: "Packet saved" → returns to Packet List

### User Flow — Add Seed Packet

#### Flow 1: From Add Plant wizard
1. Add Plant wizard, Step 3 → tap "+ Add Seed Packet"
2. Photo capture: tap "Front" → take photo of packet front → tap "Back" → take photo of packet back
3. Enter brand: "Baker Creek Heirloom Seeds" (autocomplete matches)
4. Enter variety: "Yellow Habanero Pepper", Latin: "Capsicum chinense"
5. Genus auto-suggested as "Capsicum" (exists in library) — pre-selected
6. Enter planting specs: 80–100 days maturity, 7–21 germination, 1/4" depth, 12"–18" spacing, Full Sun, 8–10 weeks before last frost
7. Add certifications: toggle Heirloom, Non-GMO chips
8. Tap "Save Packet" → packet saved → returns to Step 3 of Add Plant wizard with packet pre-selected

#### Flow 2: From Library (standalone)
1. More → Library → Seed Packets → tap "+"
2. Same form as Flow 1
3. Tap "Save Packet" → success toast → returns to Seed Packets list

## Add Genus Workflow Specification

### Workflow Overview
The Genus workflow exists in two forms: **inline creation** (during plant/packet creation when a new genus is needed) and **Library management** (full CRUD from the Library screen).

### Inline Genus Creation

**Trigger**: During Add Plant (Step 1) or Add Seed Packet (Variety section, Genus field)

**Form** (inline, slides down in context):
| Field | Type | Required? | Notes |
|---|---|---|---|
| Genus Name | Text input | Yes | Auto-italicized preview (e.g., "*Capsicum*") |
| Common Name | Text input | No | e.g., "Peppers" |
| Family | Text input | No | e.g., "Solanaceae" |

**Buttons**:
- "Save" (Burnt Sienna `#A04010`) → saves genus → auto-selects in parent form
- "Cancel" → collapses form

**Validation**: Duplicate check — if genus name already exists (case-insensitive), show: "Capsicum already exists. [Select it instead?]" — tapping the link cancels inline form and selects the existing genus.

### Library Genus Management Screen

**Access**: More → Library → "Genus" section

#### Screen Layout

1. **Header**: "🧬 Genus" — N-900, Back button, "+" FAB (Burnt Sienna)
2. **Genus List**: Scrollable cards, alphabetical:
   - Genus name (italicized, N-700 bold, e.g., "*Capsicum*")
   - Common name (N-500, e.g., "Peppers")
   - Variety count (N-500, e.g., "3 varieties")
   - Plant count (N-500, e.g., "12 plants tracked")
3. **Empty State**: "No genera yet" — N-500, with "+" CTA

#### Add Genus (from Library)
- Tap "+" FAB → full-page form:
  - Same fields as inline form (Genus Name, Common Name, Family)
  - Additional field: **Description** — text area, optional, for notes
  - "Save Genus" button (sticky bottom)
- On save → returns to Genus list, new genus visible

#### Edit Genus
- Tap genus card → Genus Detail screen:
  - All fields editable
  - "Varieties" section: scrollable list of varieties under this genus
  - "Plants" section: scrollable list of all tracked plants in this genus
  - "Delete Genus" button (Overdue Red, only appears if 0 varieties — with confirmation dialog)

### User Flow — Inline Genus Creation
1. Add Seed Packet → enter Latin Name: "Solanum lycopersicum"
2. Genus field shows: "Solanum not found. [Create it?]"
3. Tap "Create it?" → inline form slides down
4. Common Name auto-suggested: "Tomatoes" (based on known taxonomy), Family: "Solanaceae"
5. Tap "Save" → genus saved → pre-selected in parent form → continue with packet entry

## Library Screen Specification

### Screen Purpose
The Library is the management hub for reference data: Genus, Seed Packets, Varieties, and Label Templates. It's accessed via More → Library from the Home screen.

### Screen Layout

#### 1. **Header**
- **Back Button**: "←" — returns to More screen
- **Screen Title**: "📚 Library" — N-900 text

#### 2. **Section Cards** (Scrollable, each is a tappable card)
Each section shows a summary card with a count badge.

| Section | Icon | Description | Badge |
|---|---|---|---|
| Genus | 🧬 | Biological genera | Count of genera |
| Varieties | 🌱 | Plant varieties | Count of varieties |
| Seed Packets | 📦 | Seed packet records | Count of packets |
| Label Templates | 🏷️ | Label designs for printing | Count of templates |

**Card Layout**:
- Left: Section icon (large, Terracotta)
- Middle: Section name (N-700 bold) + description (N-500)
- Right: Count badge (N-100 Parchment circle, N-700 text) + chevron "›"

**Interaction**:
- Tap section card → navigates to the section's list screen (e.g., tap "Seed Packets" → Seed Packets list)

### Design Principles Applied
- **Reference Data Separation**: Library isolates management tasks from garden workflow
- **Count Badges**: Instant visibility into data volume
- **Minimal Navigation**: One tap from Library to any management screen
- **Inline Creation**: Reference data can be created on-the-fly during plant creation, reducing friction

## Quick Action Bar — Future Expansion

### Current State (5 Buttons)
The Quick Action Bar currently contains 5 buttons: 💧 Water, 🧪 Feed, 🌡️ Condition, 📷 Photo, 📝 Note.

### Planned Expansion
A "More" button (⋮ or "+") will be added to the Quick Action Bar to surface additional action types without exceeding the 5-button limit. This will include:

| Future Button | Icon | Action |
|---|---|---|
| Measurement | 📏 | Record plant height, leaf count, fruit count, stem diameter |
| Pest / Disease | 🐛 | Log pest observation or disease symptoms |
| Treatment | 💊 | Record pest treatment, pruning, staking, soil amendment |
| Harvest | 🫙 | Log harvest event with yield quantity |
| Transplant | 🪴 | Record transplant event with new location |
| Lifecycle Change | 🔄 | Advance plant lifecycle stage (e.g., Seedling → Vegetative) |

**Interaction**: Tapping "More" opens a horizontally-scrollable chip row below the Quick Action Bar with the additional action types. Each chip opens its own inline form (following the same pattern as existing Quick Action forms).

### Measurement Form (Specified for Future)
When the Measurement action is tapped:

- **Metric Type**: Chips — Height · Leaf Count · Fruit Count · Stem Diameter · Other
- **Value**: Number input
- **Unit**: Unit selector (depends on metric):
  - Height: inches / cm
  - Leaf Count: count (no unit)
  - Fruit Count: count (no unit)
  - Stem Diameter: inches / mm
  - Other: free-text unit input
- **Notes**: Optional text field
- **Date**: Auto-filled, editable
- Shared Save / Dismiss pattern