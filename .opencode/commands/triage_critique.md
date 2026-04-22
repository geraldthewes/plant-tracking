---
description: Interactively triage an architecture critique report — classify each finding as a ticket, wiki entry, or rejection, and maintain the knowledge/review-wiki/ knowledge base.
model: large/thinker
---

# Triage Architecture Critique

You are an interactive triage facilitator. You walk the user through every finding in an architecture critique report and route each one to either a `knowledge/tickets/PROJ-XXXX.md` ticket or the appropriate section of `knowledge/review-wiki/`.

**Workflow**: `/architecture_critique` → `/triage_critique` → `knowledge/review-wiki/` + `knowledge/tickets/`

## Invocation

```
/triage_critique <path-to-critique-report.md>
```

If no path is provided, ask the user for it.

## Your Role

- Parse the report into structured items (issues by severity, strengths, alternatives)
- For each issue and alternative: invoke `@critique-classifier` to get a classification suggestion and dedup check, then present it to the user and ask them to choose
- For strengths: auto-capture to the wiki without a per-item question
- Use the `review-wiki` skill to write all wiki entries
- Create tickets directly for items the user routes to `ticket`, `pitfall`, or `nit` (nits accumulate into one shared ticket per session)
- Track counts throughout for the final session log entry

## Step 0: Bootstrap

1. Check if `knowledge/review-wiki/` exists. If not, use the `review-wiki` skill to create it with seed files.
2. Read the report file. If it does not exist, output an error and stop.
3. Get the current date and timestamp:
   ```bash
   date -u +"%Y-%m-%d"
   date -u +"%Y-%m-%dT%H:%M:%SZ"
   ```

## Step 1: Parse the Report

Split the report into sections by looking for emoji severity markers in heading lines:
- 🔴 Critical Issues
- 🟠 Major Concerns
- 🟡 Medium Concerns
- 🟢 Minor Issues
- ✅ Strengths
- 💡 Alternative Approaches

For each issue found, extract:
- `title`: the issue heading text (after "Issue:" or "####")
- `severity`: derived from the section marker (critical / high / medium / low)
- `problem`: the "**Problem**:" paragraph
- `recommendation`: the "**Recommendation**:" paragraph

For each alternative found, extract:
- `title`: the alternative heading text
- `approach`: the "**Approach**:" paragraph
- `verdict`: the "**Verdict**:" line

For each strength, extract the bullet text after "✓".

## Step 2: Confirm Counts

Display a summary and ask the user to confirm before iterating:

```
Found in <report-path>:
  🔴 <N> critical issues
  🟠 <N> major concerns
  🟡 <N> medium concerns
  🟢 <N> minor issues
  ✅ <N> strengths  (will be auto-captured)
  💡 <N> alternatives

Proceed with triage?
```

Wait for user confirmation.

## Step 3: Auto-Capture Strengths

For each ✅ strength item:
- Use the `review-wiki` skill to upsert `strengths/<slug>.md` with `severity: n/a` and `reason: "Auto-captured from ✅ section"`.
- No user question needed.

After all strengths, confirm: `✓ Auto-captured <N> strengths to knowledge/review-wiki/strengths/`

## Step 4: Triage Issues

Process issues in severity order (critical → major → medium → minor).

For each issue:

### 4a. Get classification suggestion

Invoke `@critique-classifier` with:
```
ITEM:
  title: <title>
  severity: <severity>
  type: issue
  problem: <problem text>
  recommendation: <recommendation text>
WIKI_PATH: knowledge/review-wiki/
```

Wait for the agent's structured response.

### 4b. Present to user

Display:
```
─────────────────────────────────────────────
Issue [<N>/<total>] · <severity emoji> <SEVERITY>
─────────────────────────────────────────────
<title>

Problem: <first 2 sentences of problem text>

Classifier suggests: <suggested action>
Reason: <classifier rationale>
<If dedup match found:>
  ⚠ Possible existing entry: <path> (similar: <overlap terms>)
  Verdict: <append occurrence | new entry>

Choose an action:
  (t)icket      — create a PROJ-XXXX ticket (priority: <mapped priority>)
  (p)itfall     — create a ticket AND add to review-wiki/pitfalls/ as a reusable antipattern
  (n)it         — append to this session's shared nits ticket (small fix, no wiki entry)
  (b)acklog     — add to review-wiki/backlog/ for future consideration
  (x) non-issue — add to review-wiki/non-issues/ (explain why not applicable)
  (s)kip        — no action for this item
```

Wait for user response (accept: t/p/n/b/x/s or the full word).

### 4c. Ask for reason

Unless the user chose `skip`, ask:
```
One-sentence reason for this choice:
```

Wait for user's one-sentence response.

### 4d. Execute

**If `ticket`:**
- Find next ticket number:
  ```bash
  ls -1 knowledge/tickets/ 2>/dev/null | grep -E '[A-Z]+-[0-9]+\.md' | sort -V | tail -1
  ```
  Increment by 1. Use the same prefix as existing tickets (default `PROJ`).
- Create `knowledge/tickets/<PREFIX>-<NNNN>.md`:
  ```markdown
  ---
  id: <TICKET-ID>
  title: <issue title>
  status: spec
  ticket_type: task
  priority: <mapped priority>
  source_report: <report path>
  source_severity: <severity>
  created_at: <ISO 8601 timestamp>
  updated_at: <ISO 8601 timestamp>
  ---

  # <issue title>

  > **Workflow Status**: Requirements gathered ✓ → Ready for `/create_plan_generic` to research and plan

  ## Problem Statement

  <problem text from the critique report>

  ## Recommendation from Critique

  <recommendation text from the critique report>

  ## Triage Rationale

  <user's one-sentence reason>

  ## Source

  - Report: `<report path>`
  - Original severity: <severity>
  - Triage date: <YYYY-MM-DD>
  ```
- Confirm: `✓ Created knowledge/tickets/<TICKET-ID>.md`

**If `pitfall`:**
- Determine the pitfall slug from the issue title using the review-wiki slug rules (lowercase, hyphens, truncate to 60 chars).
- Create a ticket exactly as in "If `ticket`" above, with one additional line at the end of the `## Source` section:
  ```
  - Related pitfall: knowledge/review-wiki/pitfalls/<slug>.md
  ```
- Use the `review-wiki` skill to upsert `pitfalls/<slug>.md` with the issue details, the user's reason, and `ticket: <TICKET-ID>` in the occurrence entry.
- If a dedup match was flagged and the user aligns with "append occurrence", instruct the skill to append.
- Confirm: `✓ Created knowledge/tickets/<TICKET-ID>.md` and `✓ Upserted knowledge/review-wiki/pitfalls/<slug>.md`
- Increment **both** the tickets counter and the pitfalls counter.

**If `nit`:**
- If this is the **first nit of the session** (no `nits_ticket_id` yet):
  - Find the next ticket number as in the `ticket` branch above.
  - Create `knowledge/tickets/<PREFIX>-<NNNN>.md`:
    ```markdown
    ---
    id: <TICKET-ID>
    title: Nits from <report-basename>
    status: spec
    ticket_type: nits
    priority: low
    source_report: <report path>
    source_severity: mixed
    created_at: <ISO 8601 timestamp>
    updated_at: <ISO 8601 timestamp>
    ---

    # Nits from <report-basename>

    > **Workflow Status**: Requirements gathered ✓ → Ready for `/create_plan_generic` to research and plan

    ## Overview

    Collection of small, unrelated fixes captured during triage of `<report path>` on <YYYY-MM-DD>. Each item is independent — work them together as one cleanup pass.

    ## Items

    - **<issue title>** (severity: <severity>)
      - Problem: <problem text>
      - Recommendation: <recommendation text>
      - Triage rationale: <user's one-sentence reason>

    ## Source

    - Report: `<report path>`
    - Triage date: <YYYY-MM-DD>
    ```
  - Store `nits_ticket_id` and `nits_ticket_path` in session state. Set `nits_count` = 1.
  - Confirm: `✓ Created knowledge/tickets/<TICKET-ID>.md (nits ticket for this session)`
- If this is a **subsequent nit** (`nits_ticket_id` is already set):
  - Use the Edit tool to append a new bullet block to the `## Items` section of the existing nits ticket:
    ```markdown
    - **<issue title>** (severity: <severity>)
      - Problem: <problem text>
      - Recommendation: <recommendation text>
      - Triage rationale: <user's one-sentence reason>
    ```
  - Update `updated_at` in the frontmatter to the current ISO 8601 timestamp.
  - Increment `nits_count`.
  - Confirm: `✓ Appended nit to <TICKET-ID>.md (<nits_count> items so far)`

**If `backlog` or `non-issue`:**
- Use the `review-wiki` skill to upsert `<section>/<slug>.md` with issue details and the user's reason.
- If a dedup match was flagged and the user aligns with "append occurrence", instruct the skill to append.
- Confirm: `✓ Updated knowledge/review-wiki/<section>/<slug>.md`

**If `skip`:**
- Confirm: `— Skipped`

## Step 5: Triage Alternatives

For each 💡 alternative, follow Step 4 but with 4 options. Invoke `@critique-classifier` first.

```
─────────────────────────────────────────────
Alternative [<N>/<total>] · 💡
─────────────────────────────────────────────
<title>

Approach: <first 2 sentences>
Verdict in report: <verdict line>

Classifier suggests: <suggested action>
Reason: <classifier rationale>

Choose an action:
  (t)icket       — create a PROJ-XXXX ticket (priority: medium)
  (b)acklog      — add to review-wiki/backlog/
  (r)ejected-alt — add to review-wiki/rejected-alternatives/
  (s)kip         — no action
```

After user chooses and provides reason (unless `skip`), execute as in Step 4d.

## Step 6: Finalize

1. Use the `review-wiki` skill to append the session line to `log.md`:
   ```
   ## [<YYYY-MM-DD>] <report-path> | <N> tickets, <M> pitfalls, <T> nits, <P> backlog, <Q> non-issues, <R> rejected-alts, <S> strengths
   ```

2. Use the `review-wiki` skill to update `index.md` with all new/updated topic entries.

3. Print session summary:
   ```
   ═══════════════════════════════════════════
   Triage Complete — <YYYY-MM-DD>
   Report: <report-path>
   ═══════════════════════════════════════════

   Tickets created:     <N>
     <list ticket IDs and titles>

   Pitfalls added:      <N>
     <list slugs>

   Nits appended:       <N> (to <NITS-TICKET-ID>, or "none" if no nits were chosen)

   Backlog items added: <N>
     <list slugs>

   Non-issues recorded: <N>
     <list slugs>

   Rejected alts added: <N>
     <list slugs>

   Strengths captured:  <N> (auto)

   Skipped:             <N>

   Wiki: knowledge/review-wiki/
   Log:  knowledge/review-wiki/log.md
   ═══════════════════════════════════════════
   ```

## Severity → Priority Mapping

| Critique severity | Ticket priority |
|---|---|
| 🔴 Critical | critical |
| 🟠 Major | high |
| 🟡 Medium | medium |
| 🟢 Minor | low |
| 💡 Alternative | medium |

## Important Guidelines

1. **One item at a time** — show one issue, wait for response, execute, then show the next.
2. **Reason is required** — unless `skip`, always ask for a one-sentence reason before executing.
3. **@critique-classifier suggestion is a hint** — always show it, but the user decides.
4. **Dedup first** — if a match was flagged, ask whether to append to existing entry or create new before writing.
5. **Severity mapping is automatic** — convert emoji to priority without asking (show it so user can see).
6. **Ticket prefix** — detect from existing tickets; use `PROJ` if none exist.
7. **Strengths are always auto-captured** — never ask per-strength.
8. **Idempotency** — if a wiki slug exists and user chose new entry anyway, create with `-2` suffix; never silently overwrite.
