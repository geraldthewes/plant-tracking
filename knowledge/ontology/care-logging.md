# Care Logging Domain — Ontology

> Activity logging, care events, and observation tracking.

---

## care-logging.log-entry

- id: care-logging.log-entry
- status: active
- owner: core-team

A timestamped record of a care action or observation performed on a specific Plant. Composite identity: (plant_id, timestamp, event_type). Not the same as `plant.observation` — log entries are structured events; observations are free-form narrative text.

**Used by:** LogService, LogRepository, PlantLogEntry domain model, export service.

---

## care-logging.event-type

- id: care-logging.event-type
- status: active
- owner: core-team

The category of care action recorded in a log entry. Valid values: `water`, `humidity`, `fertilizer`, `note`. Not the same as `plant.plant-lifecycle-state` — event types are discrete care actions; lifecycle states are growth milestones.

**Note:** Code uses `water` (domain/plant_log.py:VALID_EVENT_TYPES). Glossary previously used `watering` — `water` is the canonical value in the domain model.

**Used by:** PlantLogEntry.create_from_dict() validation, LogService, CLI log commands.

---

## care-logging.water-event

- id: care-logging.water-event
- status: active
- owner: core-team

A log entry recording a watering event with volume in milliliters. Requires `amount_ml` field. Not the same as `care-logging.humidity-event` — water events record irrigation volume; humidity events record ambient moisture level.

**Used by:** PlantLogEntry (event_type="water"), normalize_water_amount() utility.

---

## care-logging.humidity-event

- id: care-logging.humidity-event
- status: active
- owner: core-team

A log entry recording humidity observation or misting on a 1-10 scale. Requires `level` field. Not the same as `care-logging.water-event` — humidity measures ambient moisture; water records irrigation volume.

**Used by:** PlantLogEntry (event_type="humidity"), LogService.

---

## care-logging.fertilizer-event

- id: care-logging.fertilizer-event
- status: active
- owner: core-team

A log entry recording fertilizer application with type and strength. Requires `fertilizer_type` and `fertilizer_strength` fields. Not the same as `care-logging.water-event` — fertilizer events record nutrient applications; water events record irrigation.

**Used by:** PlantLogEntry (event_type="fertilizer"), LogService.

---

## care-logging.note-event

- id: care-logging.note-event
- status: active
- owner: core-team

A log entry recording free-form observational text. Requires `text` field. Not the same as `plant.observation` — note events are structured log entries; observations are free-form markdown in the Plant file body.

**Used by:** PlantLogEntry (event_type="note"), LogService, Hermes Agent note-adding.

---

## care-logging.water-normalization

- id: care-logging.water-normalization
- status: active
- owner: core-team

Conversion of water amount strings (qt, L, ml, cups, tsp, tbsp, oz, fl oz) to milliliters. Not the same as `care-logging.water-event` — normalization is the conversion utility; water event is the log entry.

**Used by:** normalize_water_amount() in domain/utils.py, CLI log water command.

---

## care-logging.npk

- id: care-logging.npk
- status: active
- owner: core-team

Nitrogen-Phosphorus-Potassium ratio in fertilizer (e.g., "NPK 5-5-5"). Not the same as `care-logging.fertilizer-event` — NPK is the nutrient ratio format; fertilizer event is the log entry recording the application.

**Used by:** PlantLogEntry fertilizer_strength field, Hermes Agent fertilizer recommendations.
