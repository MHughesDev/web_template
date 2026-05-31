---
doc_id: "5.31"
title: "add adr"
section: "Procedures"
summary: "Create a new Architecture Decision Record (ADR) following the template and registration process."
status: "accepted"
updated: "2026-05-17"
---

# 5.31 — Add ADR

**Purpose:** Create a new Architecture Decision Record to document significant technical decisions.

**When to use:**
- Technology selection (database, framework, library)
- Architecture pattern adoption (microservices, CQRS, etc.)
- Integration approach decisions
- Security model changes
- Performance trade-off decisions

**When NOT to use:**
- Routine coding decisions (use code comments)
- Already-documented decisions (reference existing)
- Personal preference without technical impact

---

## Prerequisites

- [ ] Decision has been discussed/reviewed
- [ ] No existing ADR covers this
- [ ] Significant technical impact
- [ ] Reversibility considered

---

## ADR Structure

See template: `docs/adr/template.md`

```markdown
---
doc_id: "7.N"
title: "ADR-XXXX decision-title"
section: "ADR"
status: "proposed | accepted | deprecated | superseded"
updated: "YYYY-MM-DD"
---

# ADR-XXXX: Title

**Status:** {status}

**Date:** YYYY-MM-DD

## Context

What prompted this decision?

## Decision

What was decided? Be specific.

## Consequences

Easier, harder, risks, follow-up work.

## Alternatives Considered

Table of rejected options with reasons.

## References
```

---

## Steps

### 1. Check existing ADRs

```bash
ls docs/adr/
grep -r "your-topic" docs/adr/
```

### 2. Pick number

Format: `ADR-NNNN-kebab-case.md`

```bash
# Find next number
ls docs/adr/*.md | sort -V | tail -1
# Next is +1
```

### 3. Copy template

```bash
ADR_NUM=0005
cp docs/adr/template.md docs/adr/$ADR_NUM-your-decision.md
```

### 4. Fill in sections

**Context:**
- Problem/opportunity
- Constraints
- Why decide now

**Decision:**
- Specific choice
- Exact approach
- Implementation notes

**Consequences:**
- Easier (benefits)
- Harder (costs)
- Risks accepted
- Follow-up work

**Alternatives:**
| Option | Rejected because |
|--------|-----------------|
| A | Reason |
| B | Reason |

### 5. Assign doc_id

Edit frontmatter:
```yaml
doc_id: "7.N"  # Next available in Section 7
```



Add to Section 7 table:
```markdown
| 7.N | ADR-XXXX title | `docs/adr/000X-title.md` | One-line summary. |
```

### 7. Update ADR index

Edit `docs/adr/README.md`:
```markdown
- [ADR-000X: Title](000X-title.md) - Status: {status}
```

### 8. Submit PR

```markdown
## New ADR: {Title}

**ADR-XXXX**
**Status:** Proposed

**Decision:** {one sentence}

**Impact:** {affected systems}

**Alternatives considered:** {count}
```

### 9. Review process

- Technical review (peers)
- Stakeholder review (if needed)
- Accept or revise

### 10. Mark accepted

After merge:
```bash
git checkout main
# Edit ADR
# Change status to "accepted"
git add docs/adr/000X-title.md
git commit -m "ADR-000X: Mark as accepted"
git push
```

---

## Status Lifecycle

```
Proposed → Accepted → Deprecated
              ↓
         Superseded by ADR-YYYY
```

- **Proposed:** Under review
- **Accepted:** Current truth
- **Deprecated:** No longer relevant (tech removed)
- **Superseded:** Replaced by newer ADR

---

## Validation

- [ ] Template sections complete
- [ ] At least 2 alternatives listed
- [ ] Consequences honest (not just benefits)
- [ ] doc_id assigned
- [ ] ADR index updated

---

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Too vague | Insufficient context | Add specific constraints |
| No alternatives | Biased decision | Force 2+ options |
| Only benefits | Incomplete | List real costs/risks |

---

## See Also

- ADR template: `docs/adr/template.md`
- Index: `docs/adr/README.md`
