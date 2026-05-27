# Taxonomy Domain — Ontology

> Plant classification, naming, and variety identity.

---

## taxonomy.genus

- id: taxonomy.genus
- status: active
- owner: core-team

A unique pairing of variety name and Latin (scientific) name. Genus records eliminate redundant data entry by capturing plant type identity once, regardless of seed packet brand. Not the same as `seed-inventory.seed-packet` — a Seed Packet is brand-specific; a Genus is brand-agnostic.

**Used by:** GenusService, GenusRepository, Plant genus_id reference, Label generation (latin_name resolution).

---

## taxonomy.variety

- id: taxonomy.variety
- status: active
- owner: core-team

A cultivar or named variety of a plant species (e.g., "Yellow Habanero", "Jimmy Nardello"). In this system, variety identity is captured by the `taxonomy.genus` entity (variety_name + latin_name pair). Not the same as `taxonomy.genus` — variety is the common name portion only; genus is the full variety + latin name pairing.

**Used by:** Genus.variety_name field, SeedPacket.variety_name field, Plant variety display.

---

## taxonomy.variety-name

- id: taxonomy.variety-name
- status: active
- owner: core-team

The common name of a plant variety (e.g., "Yellow Habanero"). Stored on both Genus and Seed Packet entities. Not the same as `taxonomy.latin-name` — variety name is the common/marketing name; latin name is the scientific classification.

**Used by:** Genus, SeedPacket, Plant (backward-compatible), Label display.

---

## taxonomy.latin-name

- id: taxonomy.latin-name
- status: active
- owner: core-team

The scientific/Latin name of a plant (e.g., "Capsicum chinense"). Unique key is (variety_name, latin_name) on both Genus and Seed Packet. Not the same as `taxonomy.variety-name` — latin name provides scientific precision; variety name is the common name.

**Used by:** Genus, SeedPacket, Label display, Genus uniqueness constraint.
