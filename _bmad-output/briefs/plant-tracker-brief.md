**Product Requirements Document (PRD) – Plant Tracking System with QR Labels**  
**Version:** 0.1 (Rough Draft)  
**Date:** April 19, 2026  
**Author:** Grok (with input from team)  
**Status:** Draft for refinement  

### 1. Overview & Goals
You want a **simple, low-tech system** to track **individual plants** (starting with peppers like Yellow Habanero and Jimmy Nardello) from seed packet to garden.  

Each plant gets:
- A **unique ID**
- A durable **thermal label** (printed on your **Phomemo M120** Bluetooth label printer) containing a **QR code** of the plant ID + readable text
- Data captured from the seed packet photo + user-added info (year planted, etc.)

**Core goals**
- Quick visual identification of any plant in the garden (scan QR → see all its data)
- Preserve all useful info from the seed packet automatically
- Start with **markdown file(s)** for storage (zero setup)
- Easy future migration to **Postgres**
- Labels are waterproof, sun-resistant, and fit on small stakes/pots

### 2. Unique Plant ID Recommendation
**Recommended format:** `VARIETY-YYYY-SEQ`  
**Example:** `HABY-2026-001` or `JIMN-2026-007`

**Why this format?**
- **Human-readable** on the label (you can glance and know variety + year)
- **Unique forever** (year + sequential number per variety)
- Short enough for QR codes and small labels
- Easy to generate manually or with a tiny script

**Alternatives considered (and why we rejected them)**
- Plain UUID → too long, not human-friendly
- Global `PLANT-2026-001` → loses variety context at a glance
- Just sequential number → collides across years/varieties

You can generate IDs in a simple Python script or even a Google Sheet that auto-increments per variety.

### 3. Data Model (What to Store)

#### Core Fields (extracted from seed packet photo + user input)
| Field                  | Source                  | Example (Habanero)                  | Example (Jimmy Nardello)          | Required? |
|------------------------|-------------------------|-------------------------------------|-----------------------------------|-----------|
| Plant ID               | System                  | HABY-2026-001                      | JIMN-2026-003                    | Yes      |
| Variety Name           | Packet                  | Habanero Yellow Pepper             | Pepper Sweet Jimmy Nardello      | Yes      |
| Latin Name             | Packet                  | *Capsicum chinense* (typical)      | *Capsicum annuum*                | Yes      |
| Brand                  | Packet                  | Gardeners Basics                   | Botanical Interests              | Yes      |
| Heirloom / Non-GMO / Organic | Packet            | Heirloom, Non-GMO                  | Heirloom, USDA Organic           | No       |
| Days to Maturity       | Packet                  | 80-100                             | 80-90 from transplant            | Yes      |
| Days to Germination    | Packet                  | 7-21                               | 10-25                            | Yes      |
| Planting Depth         | Packet                  | 1/4"                               | 1/4"                             | Yes      |
| Plant Spacing          | Packet                  | 12"-18"                            | 18"-24"                          | Yes      |
| Sun Requirement        | Packet                  | Full Sun                           | Full Sun                         | Yes      |
| Start Indoors          | Packet                  | 8-10 weeks before last frost       | 8-10 weeks before transplant     | Yes      |
| Scoville Units         | Packet                  | 100,000–350,000                    | N/A (sweet)                      | No       |
| Seed Weight / Qty      | Packet                  | 300 mg                             | 18 seeds                         | No       |
| Lot / Packed Date      | Packet                  | (if shown)                         | Packed for 2019                  | No       |
| Year Planted           | User                    | 2026                               | 2026                             | Yes      |
| Planted Date           | User                    | 2026-04-15                         | 2026-04-15                       | Yes      |
| Packet Photo Filename  | User                    | habanero-packet.jpg                | jimmy-nardello-packet.jpg        | Recommended |

**Additional useful tracking fields (add later as you go)**
- Germination date
- Transplant date
- First flower / First harvest date
- Total yield (fruits harvested)
- Location in garden (bed/row/pot)
- Notes / observations (pests, disease, flavor notes, etc.)
- Plant photo filenames (for visual progress)

### 4. Storage Plan
**Phase 1 (Now):** Markdown files  
- One file: `plants.md` with a simple markdown table (easy to read/edit)
- OR one file per plant: `HABY-2026-001.md` using YAML frontmatter + notes (cleaner for many plants)

**Phase 2 (Later):** Postgres  
Simple schema:
```sql
CREATE TABLE plants (
  id TEXT PRIMARY KEY,                    -- HABY-2026-001
  variety TEXT,
  latin_name TEXT,
  brand TEXT,
  packet_data JSONB,                      -- store everything else
  planted_at DATE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

Migration will be trivial (copy-paste or one script).

### 5. Label Design (M120 Printer)
**Layout (fits ~1–1.5 inch wide label):**
- Top: Variety name (large text)
- Middle: QR code encoding **only the Plant ID** (e.g. `HABY-2026-001`)
- Bottom: `Planted 2026` + Latin name (small text)

**Why QR only the ID?**  
Keeps the QR simple and reliable. Scan → copy ID → open your `plants.md` or future app and search. (Future enhancement: QR could encode a `plant://HABY-2026-001` deep link or short URL.)

Phomemo M120 app supports text + QR codes natively — you can design once and reuse the template.

### 6. User Workflow (Proposed)
1. Open new seed packet → take clear photo of front + back.
2. Start seeds or plant → decide how many plants from this packet.
3. Assign next Plant ID (from your list or tiny script).
4. Fill data in markdown (copy Latin/variety/instructions from packet photo).
5. Generate label in Phomemo app (or script that outputs image → print via Bluetooth).
6. Attach label to pot/stake.
7. Later: scan QR anytime to pull up the exact plant record and add notes.

### 7. Nice-to-Haves (Future Phases)
- Tiny Python/Obsidian script that generates the markdown entry + label image automatically.
- Mobile app (or even just a Notion/Google Sheet) that scans QR and shows/edits data.
- Auto-extract text from packet photo (simple OCR with phone camera).
- Export to CSV for backup.

This keeps the MVP **extremely simple** (markdown + Phomemo app) while being fully future-proof for Postgres.

Let me know what you want to tweak:
- ID format?
- Which extra fields are must-haves for you?
- Do you want a sample `plants.md` template right now?
- Sample label text layout?

We can iterate on this PRD quickly!