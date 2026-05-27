# Seed Inventory Domain — Ontology

> Seed packet management, brand-specific growing instructions, and seed provenance.

---

## seed-inventory.seed-packet

- id: seed-inventory.seed-packet
- status: active
- owner: core-team

Reusable variety information captured from a physical seed packet. Contains brand-specific growing instructions and timing data. Multiple Plants can reference the same Seed Packet. Not the same as `taxonomy.genus` — a Genus captures plant type once; a Seed Packet captures brand-specific instructions.

**Used by:** SeedPacketService, SeedPacketRepository, Plant seed_packet_id reference.

---

## seed-inventory.days-to-maturity

- id: seed-inventory.days-to-maturity
- status: active
- owner: core-team

Expected days from planting to first harvest, as stated on the seed packet. Not the same as `plant.growing-season` — days to maturity is variety-specific; growing season is the calendar window for a location.

**Used by:** SeedPacket entity, Hermes Agent timing predictions.

---

## seed-inventory.germination-time

- id: seed-inventory.germination-time
- status: active
- owner: core-team

Expected germination period stated on the seed packet. Not the same as `plant.germination` — germination-time is the expected duration; germination is the actual observed event.

**Used by:** SeedPacket entity, Hermes Agent germination tracking.

---

## seed-inventory.planting-depth

- id: seed-inventory.planting-depth
- status: active
- owner: core-team

Recommended planting depth from the seed packet. Not the same as `plant.transplant` — planting depth is a specification; transplant is a physical action.

**Used by:** SeedPacket entity, Hermes Agent planting recommendations.

---

## seed-inventory.spacing

- id: seed-inventory.spacing
- status: active
- owner: core-team

Recommended spacing between plants from the seed packet. Not the same as `plant.location` — spacing is a recommendation; location is the actual growing position.

**Used by:** SeedPacket entity, Hermes Agent garden layout advice.

---

## seed-inventory.sun-requirements

- id: seed-inventory.sun-requirements
- status: active
- owner: core-team

Sunlight requirements from the seed packet (e.g., "Full Sun"). Not the same as `plant.plant-lifecycle-state` — sun requirements are static specifications; lifecycle state tracks current growth stage.

**Used by:** SeedPacket entity, Hermes Agent care recommendations.

---

## seed-inventory.indoor-start-time

- id: seed-inventory.indoor-start-time
- status: active
- owner: core-team

When to start seeds indoors relative to last frost. Not the same as `plant.planting-date` — indoor start time is a relative recommendation; planting date is the actual date.

**Used by:** SeedPacket entity, Hermes Agent planning.

---

## seed-inventory.brand

- id: seed-inventory.brand
- status: active
- owner: core-team

Seed company name from the packet. Not the same as `taxonomy.genus` — brand identifies the seed supplier; genus identifies the plant type regardless of supplier.

**Used by:** SeedPacket entity, Plant brand field (backward-compatible).

---

## seed-inventory.origin

- id: seed-inventory.origin
- status: active
- owner: core-team

The source or provenance of a plant — where the seeds or cutting came from. Not the same as `seed-inventory.brand` — origin is the geographic or personal source; brand is the commercial seed company.

**Used by:** UI design diagrams (planned management screen), future Plant record field.
