---
doc_id: "5.30"
title: "add procedure"
section: "Procedures"
summary: "Meta-procedure for adding new procedures to the repository. Ensures consistent structure, sizing, cross-referencing, and registration."
status: "accepted"
updated: "2026-05-17"
---

# 5.30 — Add Procedure

**Purpose:** Add a new procedure to the repository following the canonical format and sizing guidelines.


---

## When to Use

Use this procedure when:
- A workflow is repeated twice (encode it)
- A new operational pattern emerges
- A gap in the procedure library is identified
- A queue row requires a procedure that doesn't exist

**Do NOT create a procedure for:**
- One-off tasks (use queue instead)
- Already-documented workflows (reference existing)
- Generic development practices (link to external docs)

---

## Procedure Sizing Guidelines

A procedure should be **one complete workflow**:

| Attribute | Target | Anti-pattern |
|-----------|--------|--------------|
| Outcome | Single discrete result | Multiple unrelated outcomes |
| Steps | 3-15 steps | < 3 (too small) or > 20 (too large) |
| Scope | Bounded, clear boundaries | "Everything about X" |
| Duration | 5 min to 2 hours | Days-long processes |
| Actors | 1-2 roles | Entire org chart |

**Examples of good procedure size:**
- "Add a make target" (discrete, bounded)
- "Database migration" (clear start/end)
- "Open a pull request" (specific situation)

**Examples to avoid:**
- "Build the application" (too broad — decompose)
- "Add a comment" (too small — belongs in style guide)
- "Manage the company" (absurd scope)

---

## Steps

### 1. Check for existing procedure

Before creating, verify no procedure already covers this:

```bash
# Search by keyword
grep -r "procedure-keyword" docs/procedures/

# Search by concept
make skills:list | grep -i "concept"

# Check similar procedures
cat docs/procedures/README.md
```

**If similar exists:**
- Extend existing procedure instead
- Or break into separate concerns

### 2. Determine procedure scope

Define clearly:
- **Trigger:** When is this procedure invoked?
- **Outcome:** What specific result is achieved?
- **Audience:** Human, agent, or both?
- **Prerequisites:** What must be true before starting?

Write this in 1-2 sentences. If you can't, the scope is unclear.

### 3. Choose section and doc_id

| Section | ID Range | Use For |
|---------|----------|---------|
| 5.0-5.9 | Core procedures | Make, optional editor MCP, prompts, queue, db |
| 5.10-5.19 | Workflow procedures | Archive, handoff, plan, PR, implement |
| 5.20-5.29 | Dev procedures | Init, scaffold, skills, rules, validation |
| 5.30+ | Meta/extended | This and future meta-procedures |

**doc_id format:** `5.NN` (always 2 digits after section)


### 4. Create procedure file

Create `docs/procedures/{kebab-case-title}.md`:

```yaml
---
doc_id: "5.NN"
title: "kebab-case-title"
section: "Procedures"
status: "draft"
updated: "YYYY-MM-DD"
---

# 5.NN — Title Case Title

**Purpose:** What this procedure achieves.

**When to use:** Specific trigger conditions.

**Prerequisites:** What must be ready before starting.

---

## Steps

### 1. Step one
Action details...

### 2. Step two
Action details...

### 3. Step three
Action details...

---

## Validation

How to verify this procedure was executed correctly.

---

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Problem X | Why it happens | How to fix |

---

## See Also

- Related procedure: `docs/procedures/related.md`
- Skill: `skills/category/skill.md`
- Rule: `.cursor/rules/rule.mdc`
```

### 5. Write procedure content

Follow the template structure:

1. **Purpose** — One sentence outcome
2. **When to use** — Trigger conditions
3. **Prerequisites** — Required state before starting
4. **Steps** — Numbered, actionable, verifiable
5. **Validation** — How to confirm success
6. **Common Issues** — Troubleshooting table (optional)
7. **See Also** — Cross-references

**Writing rules:**
- Each step starts with a verb
- Steps are sequential (no branching in primary flow)
- If/then logic goes in "Common Issues" or sub-sections
- Code examples show exact commands
- Use `make` targets, not raw shell


Add entry to Section 5 table:

```markdown
| 5.NN | kebab-case-title | `docs/procedures/{filename}.md` | One-line summary. |
```

Run validation:
```bash
```

### 7. Update procedures index

Add to `docs/procedures/README.md` index table.

### 8. Create cross-references

Reference the new procedure from:
- Related skills (in `skills/`)
- Related prompts (in `prompts/`)
- Parent procedures (that invoke this)
- AGENTS.md files (if scope-specific)

### 9. Submit for review

Include in PR:
- New procedure file
- Procedures index update
- Cross-reference additions

**PR description template:**
```markdown
## New Procedure: {Title}

**doc_id:** 5.NN
**Purpose:** {one sentence}
**Sizing:** {step count} steps, {estimated duration}

### Changes
- Created `docs/procedures/{file}.md`
- Updated `docs/procedures/README.md`
- Added cross-references to: {files}

### Verification
- [ ] Procedure follows sizing guidelines (5-15 steps)
- [ ] doc_id unique and sequential
- [ ] Cross-references added
```

---

## Validation Checklist

Before marking complete:
- [ ] File at `docs/procedures/{kebab-case}.md`
- [ ] Valid frontmatter with doc_id, title, section, summary, status
- [ ] 3-15 steps (if outside range, justify in PR)
- [ ] Each step starts with verb
- [ ] Prerequisites clearly stated
- [ ] Procedures index updated
- [ ] Cross-references added

---

## Example: Good Procedure

See `docs/procedures/add-make-target.md` (5.1):
- 8 steps
- Clear outcome: make target exists and works
- Prerequisites: Makefile exists
- Validation: Run `make <target>`
- Cross-referenced from skills

## Example: Procedure to Split

If a procedure grows beyond 15 steps:
1. Identify natural breakpoint (usually validation phase)
2. Extract sub-procedure
3. Reference from parent with "See procedure X"
4. Both procedures now sized correctly

---

## See Also

- Add skill: `docs/procedures/update-or-create-skill.md`
- Add rule: `docs/procedures/update-or-create-rule.md`
