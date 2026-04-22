---
name: review-wiki
description: Maintain the knowledge/review-wiki/ Karpathy-style knowledge base — upsert pattern entries, update index and log, enforce structure. Use when adding pitfall/strength/backlog/non-issue/rejected-alternative entries or initializing the wiki directory tree.
---

# Review Wiki Maintenance

This skill manages all file operations for `knowledge/review-wiki/`. Use it whenever you need to:
- Add a new pattern entry (pitfall, strength, backlog item, non-issue, rejected alternative)
- Update an existing entry with a new occurrence from a subsequent critique session
- Initialize the wiki tree if it doesn't exist yet
- Update `index.md` with a new topic line
- Append a session summary line to `log.md`

## Directory Bootstrap

If `knowledge/review-wiki/` does not exist, create it:

```bash
mkdir -p knowledge/review-wiki/pitfalls \
         knowledge/review-wiki/strengths \
         knowledge/review-wiki/backlog \
         knowledge/review-wiki/non-issues \
         knowledge/review-wiki/rejected-alternatives
```

Then create minimal seed files:
- `knowledge/review-wiki/README.md` — purpose, structure, external references
- `knowledge/review-wiki/index.md` — header + empty section placeholders
- `knowledge/review-wiki/log.md` — header line only

## Slug Rules

Convert an item title to a file slug:
1. Lowercase the entire title
2. Replace spaces and non-alphanumeric characters with hyphens (`-`)
3. Collapse consecutive hyphens to one
4. Strip leading/trailing hyphens
5. Truncate to 60 characters (at a word boundary if possible)

Examples:
- "Missing Error Handling for Model Communication Failures" → `missing-error-handling-for-model-communication-failures`
- "No Explicit Security Considerations for LLM API Keys" → `no-explicit-security-considerations-for-llm-api-keys`

## Topic File: Create (Upsert — New Entry)

Path: `knowledge/review-wiki/<section>/<slug>.md`

Where `<section>` is one of: `pitfalls`, `strengths`, `backlog`, `non-issues`, `rejected-alternatives`.

Template:

```markdown
---
topic: <full title from the critique report>
category: <pitfall|strength|backlog|non-issue|rejected-alternative>
first_seen: <YYYY-MM-DD>
last_updated: <YYYY-MM-DD>
occurrences:
  - report: <relative path to the critique report>
    severity: <critical|high|medium|low|n/a>
    reason: "<one-sentence reason from the user>"
    ticket: <PROJ-XXXX>   # omit if no ticket was created
---

# <Title>

## Pattern

Copy the original **Problem**, **Why it matters**, and **Evidence** blocks verbatim from the
critique report. Preserve the original wording — do not paraphrase or summarise.

```
**Severity**: <emoji + label from report>

**Problem**:
<copied verbatim>

**Why it matters**:
<copied verbatim>

**Evidence**:
<copied verbatim>
```

## Recommendation

Copy the original **Recommendation** block verbatim from the critique report.

```
<copied verbatim>
```

## Estimated Impact

Copy the original **Estimated impact** block verbatim from the critique report (if present).

```
<copied verbatim>
```

## References
<!-- Add relevant external links, e.g.:
- [software-backend-wiki: Error Handling](https://github.com/geraldthewes/software-backend-wiki)
- OWASP A10: https://owasp.org/www-project-top-ten/
- Related ticket: PROJ-XXXX
-->

## Occurrences
- **<YYYY-MM-DD>** — `<report path>` (<severity>)
  Reason: <one-sentence reason>
```

## Topic File: Update (Upsert — Existing Entry)

When `<section>/<slug>.md` already exists, **do not overwrite it**. Instead:

1. Read the existing file.
2. Append to the `occurrences:` list in the YAML frontmatter:
   ```yaml
     - report: <new report path>
       severity: <severity>
       reason: "<reason>"
       ticket: <PROJ-XXXX>   # omit if none
   ```
3. Update `last_updated:` in frontmatter to today's date.
4. Append to the `## Occurrences` body section:
   ```markdown
   - **<YYYY-MM-DD>** — `<report path>` (<severity>)
     Reason: <one-sentence reason>
   ```

Use the Edit tool for these targeted appends, not the Write tool (to avoid overwriting existing content).

## Index Update

After each upsert, add or refresh the entry in `knowledge/review-wiki/index.md`.

Format (one line per topic, under the matching section header):
```
- [<title>](<relative-path>) — <one-line summary>
```

Example:
```
- [No error handling for model failures](pitfalls/missing-error-handling-for-model-communication-failures.md) — circuit breaker pattern missing for LLM API outages
```

If the topic already has a line in `index.md`, update it in place. Use the Edit tool.

## Log Update

After a complete `/triage_critique` session, append one line to `knowledge/review-wiki/log.md`:

```markdown
## [<YYYY-MM-DD>] <report-path> | <N> tickets, <M> pitfalls, <T> nits, <P> backlog, <Q> non-issues, <R> rejected-alts, <S> strengths
```

## Severity → Ticket Priority Mapping

| Critique severity | Ticket priority |
|---|---|
| 🔴 Critical | critical |
| 🟠 Major | high |
| 🟡 Medium | medium |
| 🟢 Minor | low |
| 💡 Alternative | medium (user can override) |

## Ticket Frontmatter Extensions

Tickets created via `/triage_critique` add two fields beyond the standard IDLC schema:

```yaml
source_report: knowledge/research/YYYY-MM-DD-project-critique.md
source_severity: critical
```
