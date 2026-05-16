# Plant Tracking System — Glossary & Ontology

> Living document describing the domain entities, their attributes, and relationships.
> Sources: PRD, architecture decisions, database spec, UI design diagrams.

---

## 1. Core Entities

### Plant

**Definition:** An individual growing instance — a specific physical plant that the gardener is tracking. Plants are the central entity around which all other data revolves.

**Identity:** `id` — auto-generated in `VARIETY-YYYY-SEQ` format (e.g., `HABY-2026-001`). The variety code is derived from the variety name, followed by the year, followed by a sequential number.

**Attributes:**
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (`^[A-Z]{2,4}-\d{4}-\d{3}$`) |
| `planting_date` | date (YYYY-MM-DD) | Yes | Date the plant was planted (seeds sown or seedling placed in pot) |
| `location` | string | No | Current growing location (e.g., "garden bed 3, row 2", "indoor seed tray") |
| `status` | enum | No | Current lifecycle stage (see Plant Lifecycle) |
| `genus_id` | string | No | Reference to Genus entity (`^GENUS-\d{3}$` or `"unknown"`) |
| `seed_packet_id` | string | No | Reference to Seed Packet entity (`^SPKT-\d{3}$` or `"unknown"`) |
| `created_at` | datetime (ISO 8601) | Yes | Record creation timestamp |
| `updated_at` | datetime (ISO 8601) | Yes | Last modification timestamp |

**Lifecycle States:** `Seed_Packet_Entered` → `Indoor_Seedling` → `Indoor_Growing` → `Transplanted_Outdoor` → `Flowering` → `Fruiting` → `Harvesting` → `Season_Complete` → `Dormant`

**Storage:** `database/{plant_id}.md` (YAML frontmatter + markdown body for observations)

**Notes:**
- A Plant is a unique physical instance — the same variety planted twice creates two Plant records.
- Backward-compatible plants may carry `variety_name`, `latin_name`, and other fields directly on the Plant record. These are deprecated in favor of referencing Genus and Seed Packet.

---

### Genus

**Definition:** A unique pairing of variety name and Latin (scientific) name. Genus records eliminate redundant data entry by capturing the identity of a plant type once, regardless of which seed packet brand it came from.

**Identity:** `id` — auto-generated in `GENUS-NNN` format (e.g., `GENUS-001`).

**Attributes:**
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (`^GENUS-\d{3}$`) |
| `variety_name` | string | Yes | Common name of the plant variety (e.g., "Yellow Habanero") |
| `latin_name` | string | Yes | Scientific/Latin name (e.g., "Capsicum chinense") |
| `created_at` | datetime | Yes | Record creation timestamp |
| `updated_at` | datetime | Yes | Last modification timestamp |

**Unique key:** `(variety_name, latin_name)`

**Storage:** `database/genera/{id}.md`

**Notes:**
- A Genus is brand-agnostic. "Yellow Habanero" from Brand A and "Yellow Habanero" from Brand B share the same Genus.
- Label generation resolves `latin_name` from the Genus database when `genus_id` is present.

---

### Seed Packet

**Definition:** Reusable variety information captured from a physical seed packet. Contains brand-specific growing instructions and timing data. Multiple Plants can reference the same Seed Packet.

**Identity:** `id` — auto-generated in `SPKT-NNN` format (e.g., `SPKT-001`).

**Attributes:**
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (`^SPKT-\d{3}$`) |
| `variety_name` | string | Yes | Common name on the packet |
| `latin_name` | string | Yes | Scientific name on the packet |
| `brand` | string | No | Seed company name |
| `days_to_maturity` | string | No | Days from planting to harvest (range or single value) |
| `germination_time` | string | No | Expected germination period |
| `planting_depth` | string | No | Recommended planting depth |
| `spacing` | string | No | Recommended spacing between plants |
| `sun_requirements` | string | No | Sunlight requirements (e.g., "Full Sun") |
| `indoor_start_time` | string | No | When to start indoors relative to last frost |
| `created_at` | datetime | Yes | Record creation timestamp |
| `updated_at` | datetime | Yes | Last modification timestamp |

**Unique key:** `(variety_name, latin_name)`

**Storage:** `database/seed_packets/{id}.md`

**Notes:**
- Seed Packet is the source of truth for brand-specific growing instructions.
- A Seed Packet can be referenced by zero or many Plants (one-to-many).

---

### Activity Log (Log Entry)

**Definition:** A timestamped record of a care action or observation performed on a specific Plant. The log is the primary mechanism for building the data history that enables pattern analysis and insights.

**Identity:** Composite — identified by `(plant_id, timestamp, event_type)`. Stored in a single consolidated file.

**Event Types:**
| Type | Fields | Description |
|------|--------|-------------|
| `watering` | `amount` (quantity + unit, normalized) | Watering event with volume |
| `humidity` | `level` (1-10 scale) | Humidity observation or misting |
| `fertilizer` | `type` (name/brand), `strength` (concentration) | Fertilizer application |
| `note` | `text` (free-form) | General observation or care note |

**Attributes:**
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `plant_id` | string | Yes | Reference to the Plant |
| `event_type` | enum | Yes | One of: `watering`, `humidity`, `fertilizer`, `note` |
| `timestamp` | datetime | Yes | When the event occurred |
| `date` | date | Yes | Date portion (for `--date` flag; defaults to today) |
| Event-specific fields | varies | Yes | Fields depend on `event_type` (see table above) |

**Storage:** `database/logs/plant-activity-log.md` (single file, all plants)

**Notes:**
- All Plants can receive log entries at any lifecycle state.
- Water amounts are validated and normalized (supports qt, L, ml, cups, etc.).
- Designed for future database migration — structured YAML format.

---

## 2. Supporting Entities

### Label

**Definition:** A physical QR-coded label printed on the Phomemo M120 printer and attached to a plant, pot, or stake. Encodes the Plant's ID for instant retrieval.

**Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `plant_id` | string | The Plant ID encoded in the QR code |
| `format` | enum | `40x30mm` or `50x70mm` (Phomemo M120 supported sizes) |
| `variety_name` | string | Displayed at top of label |
| `latin_name` | string | Displayed on label (resolved from Genus or Plant) |
| `planting_date` | date | Displayed as "Planted YYYY" |

**Notes:**
- Labels are ephemeral — they can wear out and be reprinted.
- QR code encodes only the plant ID (not the full record).

---

### Photo

**Definition:** A photograph attached to a Plant record for visual progress tracking and documentation.

**Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `plant_id` | string | Reference to the Plant |
| `filepath` | string | Path to stored image file |
| `captured_at` | datetime | Timestamp of capture |
| `description` | string | Optional caption |

**Storage:** `photos/{plant_id}/` directory

---

### Observation

**Definition:** Free-form markdown text appended to a Plant record's body. Observations provide narrative context that structured log entries may not capture.

**Notes:**
- Stored in the markdown body of the Plant file, below the YAML frontmatter.
- Timestamped entries in list format (e.g., `- 2026-04-01: Germination observed`).

---

### Origin

**Definition:** The source or provenance of a plant — where the seeds or cutting came from.

**Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `source` | string | Source description (e.g., "local nursery", "seed exchange") |
| `location` | string | Geographic origin |

**Notes:** Referenced in UI design diagrams as a management screen; not yet fully specified in database spec.

---

### Variety

**Definition:** A cultivar or named variety of a plant species (e.g., "Yellow Habanero", "Jimmy Nardello"). In this system, variety identity is captured by the Genus entity (variety_name + latin_name pair).

**Notes:**
- "Variety" in common usage refers to the common name portion.
- The system distinguishes: Variety (common name) → Genus (variety + latin name) → Seed Packet (genus + brand + instructions).

---

### Hermes Agent

**Definition:** An external AI agent accessed via Telegram that provides natural language querying, data analysis, and care recommendations. It communicates with the Plant Tracking System API to fetch and update plant data.

**Capabilities:**
- Query plant data by plant ID
- Compare plants and identify patterns
- Analyze care history for root cause diagnosis
- Add notes on behalf of the user
- Predictive insights (future)

---

## 3. Entity Relationships

```
                    ┌─────────────┐
                    │   Genus     │
                    │ (variety +  │
                    │  latin name)│
                    └──────┬──────┘
                           │ 1
                           │
                    ┌──────┴──────┐
                    │ 0..N        │
                    ▼             ▼
              ┌──────────┐  ┌──────────────┐
              │  Plant   │  │ Seed Packet  │
              │          │  │ (brand +      │
              │          │  │  instructions)│
              └────┬─────┘  └──────────────┘
                   │ 1
                   │
                   │ 1..N (zero or many log entries per plant)
                   ▼
              ┌──────────────┐
              │ Activity Log │
              │   Entries    │
              └──────────────┘

              Plant 1 ──┐
                        ├──▶ 0..N Photos
              Plant 1 ──┼──▶ 0..N Observations (markdown body)
                        ├──▶ 0..N Labels (reprintable)
                        └──▶ 1 Origin (planned)
```

### Relationship Summary

| Source | Relationship | Target | Multiplicity | Description |
|--------|-------------|--------|-------------|-------------|
| Genus | referenced by | Plant | 1 → 0..N | A Genus can be referenced by many Plants |
| Seed Packet | referenced by | Plant | 1 → 0..N | A Seed Packet can be referenced by many Plants |
| Plant | has | Activity Log Entry | 1 → 0..N | A Plant can have many log entries |
| Plant | has | Photo | 1 → 0..N | A Plant can have many photos |
| Plant | has | Observation | 1 → 0..N | A Plant can have many observations |
| Plant | has | Label | 1 → 0..N | A Plant can have labels reprinted |
| Plant | references | Genus | N → 1 | Each Plant references one Genus |
| Plant | references | Seed Packet | N → 1 | Each Plant references one Seed Packet |

### Referential Integrity Rules

1. A Plant's `genus_id` must resolve to an existing Genus file (or be `"unknown"`)
2. A Plant's `seed_packet_id` must resolve to an existing Seed Packet file (or be `"unknown"`)
3. A Log Entry's `plant_id` must resolve to an existing Plant record
4. Genus uniqueness: no two Genus records may share the same `(variety_name, latin_name)` pair
5. Seed Packet uniqueness: no two Seed Packets may share the same `(variety_name, latin_name)` pair

---

## 4. Domain Terminology

| Term | Definition |
|------|-----------|
| **Plant ID** | Unique identifier in `VARIETY-YYYY-SEQ` format (e.g., `HABY-2026-001`). Encoded in QR labels. |
| **Variety Code** | The 2-4 letter abbreviation derived from the variety name, used as the prefix in Plant IDs (e.g., `HABY` for Yellow Habanero). |
| **Germination** | The process of a seed sprouting. Recorded as a date on the Plant. |
| **Transplant** | Moving a plant from one container/location to another (e.g., indoor to outdoor). |
| **Hardening Off** | Gradual acclimation of indoor plants to outdoor conditions before transplanting. |
| **NPK** | Nitrogen-Phosphorus-Potassium ratio in fertilizer (e.g., "NPK 5-5-5"). |
| **Days to Maturity** | Expected days from planting to first harvest, as stated on the seed packet. |
| **Growing Season** | The period from first planting to end of harvest for a given year. |
| **Last Frost** | The last expected frost date for a given location — used to determine indoor start timing. |
| **Yield** | The total harvest quantity from a plant (e.g., "45 peppers"). |
