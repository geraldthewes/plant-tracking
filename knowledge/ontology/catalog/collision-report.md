# Collision Report

> Terms found in multiple domains or with naming conflicts between the legacy glossary and the codebase. Generated: 2026-05-27.

---

## 1. `watering` vs `water` — Event Type Name

- **Legacy glossary:** Event type listed as `watering`
- **Domain model:** `VALID_EVENT_TYPES = {"humidity", "water", "fertilizer", "note"}` (plant_log.py:15)
- **Resolution:** `water` is the canonical value in the domain model. The glossary used `watering` as the label but `water` is the actual stored enum value.
- **Action:** Updated care-logging.md to use `water` with a note about the legacy naming.

---

## 2. `Variety` vs `Genus` — Semantic Overlap

- **Legacy glossary:** Defines both `Variety` and `Genus` as separate entities
- **Domain model:** `taxonomy.variety` is semantically subsumed by `taxonomy.genus` — the system uses genus (variety_name + latin_name pair) as the identity anchor
- **Relation:** `taxonomy.variety` is a `narrowMatch` of `taxonomy.genus`
- **Resolution:** Both documented with explicit "Not this" exclusion. Variety is the common name portion; Genus is the complete identity.

---

## 3. `Genus` — Botanical Misnomer

- **Domain usage:** `Genus` represents a variety + latin_name pair (e.g., "Yellow Habanero" + "Capsicum chinense")
- **Botanical reality:** A genus in taxonomy is a higher-level classification (e.g., "Capsicum")
- **Resolution:** Retained `Genus` as the domain term since it's the established entity name. Documented precise definition to avoid confusion with botanical genus.

---

## 4. `Observation` — Split Across Two Domains

- **Legacy glossary:** `Observation` defined as free-form markdown in Plant file body
- **Domain model:** `care-logging.note-event` serves a similar purpose but is structured
- **Resolution:** Both concepts documented. `plant.observation` (free-form, in Plant file) vs `care-logging.note-event` (structured log entry). Not merged — they serve different purposes.

---

## 5. `Plant` backward-compatible fields

- **Legacy glossary:** Plants may carry `variety_name`, `latin_name`, `brand`, etc. directly
- **Domain model:** Plant entity still carries these fields but they're deprecated in favor of `genus_id` and `seed_packet_id` references
- **Resolution:** Documented in `plant.plant` with deprecation note. No collision — this is a migration path.
