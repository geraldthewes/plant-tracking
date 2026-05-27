# Plant Domain — Ontology

> Core plant lifecycle, tracking, and identity management.

---

## plant.plant

- id: plant.plant
- status: active
- owner: core-team

An individual growing instance — a specific physical plant that the gardener is tracking. Not the same as `taxonomy.genus` — a Genus is a plant type; a Plant is a single physical instance of that type.

**Used by:** PlantService, PlantRepository, all CLI commands, FastAPI routes.

---

## plant.plant-id

- id: plant.plant-id
- status: active
- owner: core-team

Unique identifier for a plant in `VARIETY-YYYY-SEQ` format (e.g., `HABY-2026-001`). Not the same as `plant.variety-code` — the variety code is only the prefix portion of the full plant ID.

**Used by:** Plant.generate_id(), QR label encoding, CLI --plant-id flag.

---

## plant.variety-code

- id: plant.variety-code
- status: active
- owner: core-team

The 2-4 letter abbreviation derived from the variety name, used as the prefix in plant IDs (e.g., `HABY` for Yellow Habanero). First 2 letters of each word, max 4 chars total. Not the same as `plant.plant-id` — the variety code is just the prefix, not the full identifier.

**Used by:** Plant.make_abbrev(), Plant.generate_id().

---

## plant.plant-lifecycle-state

- id: plant.plant-lifecycle-state
- status: active
- owner: core-team

The current growth stage of a plant. States: `Seed_Packet_Entered` → `Indoor_Seedling` → `Indoor_Growing` → `Transplanted_Outdoor` → `Flowering` → `Fruiting` → `Harvesting` → `Season_Complete` → `Dormant`. Not the same as `care-logging.event-type` — lifecycle states are milestones, log events are care actions.

**Used by:** Plant.status field, CLI list commands, Hermes Agent queries.

---

## plant.germination

- id: plant.germination
- status: active
- owner: core-team

The process of a seed sprouting. Recorded as a date on the Plant. Not the same as `seed-inventory.germination-time` — germination-time is the expected duration from the seed packet; germination is the actual observed event.

**Used by:** Plant record, observations, Hermes Agent analysis.

---

## plant.transplant

- id: plant.transplant
- status: active
- owner: core-team

Moving a plant from one container or location to another (e.g., indoor to outdoor). Not the same as `plant.plant-lifecycle-state` — transplant is an action; Transplanted_Outdoor is the resulting state.

**Used by:** Plant.location field updates, observations.

---

## plant.hardening-off

- id: plant.hardening-off
- status: active
- owner: core-team

Gradual acclimation of indoor plants to outdoor conditions before transplanting. Not the same as `plant.transplant` — hardening off is a preparatory process, transplant is the physical relocation.

**Used by:** Observations, Hermes Agent care recommendations.

---

## plant.growing-season

- id: plant.growing-season
- status: active
- owner: core-team

The period from first planting to end of harvest for a given year. Not the same as `seed-inventory.days-to-maturity` — growing season is the calendar window for a location; days to maturity is a variety-specific duration.

**Used by:** CLI reporting, Hermes Agent seasonal analysis.

---

## plant.last-frost

- id: plant.last-frost
- status: active
- owner: core-team

The last expected frost date for a given location — used to determine indoor start timing. Not the same as `plant.planting-date` — last frost is a planning reference; planting date is when the plant was actually planted.

**Used by:** Seed Packet indoor_start_time calculations, Hermes Agent planning.

---

## plant.planting-date

- id: plant.planting-date
- status: active
- owner: core-team

Date the plant was planted (seeds sown or seedling placed in pot). Required field on Plant records. Not the same as `plant.created-at` — planting date is when the plant was planted in the garden; created_at is when the database record was created.

**Used by:** Plant entity, Plant.generate_id() (for year extraction), CLI create command.

---

## plant.yield

- id: plant.yield
- status: active
- owner: core-team

The total harvest quantity from a plant (e.g., "45 peppers"). Not the same as `care-logging.event-type` — yield is a cumulative measurement; log events are individual care actions.

**Used by:** Observations, Hermes Agent pattern analysis.
