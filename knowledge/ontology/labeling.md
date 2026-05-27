# Labeling Domain — Ontology

> QR-coded label generation, printing, and physical plant identification.

---

## labeling.label

- id: labeling.label
- status: active
- owner: core-team

A physical QR-coded label printed on the Phomemo M120 printer and attached to a plant, pot, or stake. Encodes the Plant's ID for instant retrieval. Not the same as `plant.plant-id` — the label is the physical artifact; the plant ID is the data it encodes.

**Used by:** LabelGenerator, printer.py, CLI label commands.

---

## labeling.label-format

- id: labeling.label-format
- status: active
- owner: core-team

The physical dimensions of the printed label. Supported formats: `40x30mm` or `50x70mm` (Phomemo M120 supported sizes). Not the same as `labeling.label` — format is the dimension specification; label is the printed artifact.

**Used by:** LabelFormat domain model, Phomemo printer configuration.

---

## labeling.phomemo-printer

- id: labeling.phomemo-printer
- status: active
- owner: core-team

The Phomemo M120 Bluetooth/USB label printer used to generate QR-coded plant labels. External system connected via Bluetooth. Not the same as `labeling.label` — the printer is the hardware device; the label is the output artifact.

**Used by:** printer.py, C1 system context, CLI print commands.

---

## labeling.qr-code

- id: labeling.qr-code
- status: active
- owner: core-team

The QR code embedded in the label. Encodes only the plant ID (not the full record). Scanned by mobile app for instant plant retrieval. Not the same as `labeling.label` — the QR code is the encoded data pattern; the label is the complete printed artifact with variety name and other text.

**Used by:** LabelGenerator, mobile app QR scanning.
