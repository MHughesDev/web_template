---
doc_id: "14.3"
title: "improvement loops"
section: "Repo Governance"
summary: "Post-task retrospectives and encoding learnings into durable artifacts — skills, rules, procedures, and queue items."
updated: "2026-04-17"
---

# 14.3 — improvement loops

<!-- Per spec §20 and §26.5 items 178-182 -->

**Purpose:** Post-task retrospectives and encoding learnings into durable artifacts — skills, rules, procedures, and queue items.

## 14.3.1 The improvement loop model

Every significant incident, failed deployment, prolonged debugging session, or architectural rethink is a source of learning. The improvement loop ensures that learning is **encoded into the repo** rather than lost in chat history.

```
Event (incident, CI failure, lengthy debug)
    ↓
Retrospective (what happened, why, what changes)
    ↓
Encoding (skill / rule / procedure / queue item)
    ↓
Verification (audit confirms the artifact is present and correct)
    ↓
Next event is handled better
```

## 14.3.2 When to run a retrospective

Run a retrospective (even a brief one) after:

- A production incident or severity-1 bug.
- A CI red build that took more than 30 minutes to diagnose.
- A PR that required more than 3 review rounds due to misunderstood conventions.
- A refactor that revealed a systemic design problem.
- An initialization run (after `skills/init/repo_initialize.md`) to capture what went wrong or was surprising.
- End of quarter (scheduled — see below).

## 14.3.3 Retrospective format

Document findings in `docs/repo-governance/retrospectives/YYYY-QN.md` (create the file if it doesn't exist):

```markdown
# 14.3 — improvement loops

**Date:** YYYY-MM-DD
**Participants:** (agent names / human handles)

## 14.3.4 What happened
One paragraph summary of the event or quarter.

## 14.3.5 What went well
- Bullet points of things to preserve.

## 14.3.6 What went wrong
- Bullet points of problems encountered.

## 14.3.7 Root causes
- Cause A → led to problem X
- Cause B → led to problem Y

## 14.3.8 Actions
| Action | Artifact type | Owner | Due |
|--------|--------------|-------|-----|
| Add skill for X pattern | `skills/` | Agent | Q+1 |
| Update procedure for Y | `docs/procedures/` | Agent | ASAP |
| Add queue item for Z | `queue/queue.csv` | Agent | This sprint |
```

## 14.3.9 Encoding learnings into artifacts

### Decision: which artifact type?

| What you learned | Artifact |
|-----------------|----------|
| A reusable multi-step process (deploy, rollback, flaky-fix) | `skills/<domain>/<skill-name>.md` |
| A rule agents should always follow | `.cursor/rules/<scope>.md` or AGENTS.md section |
| A step-by-step human/agent procedure | `docs/procedures/<procedure-name>.md` |
| A deferred improvement or known debt | `queue/queue.csv` row |
| A security boundary or accepted risk | `docs/security/accepted-risks.md` |

### Skill promotion criteria

Promote a pattern to a skill when:
1. You have performed the same multi-step process **more than twice**.
2. The process requires context (ordering, flags, conditions) that isn't obvious.
3. The process touches multiple files or systems.
4. The next agent to do this would likely make mistakes without guidance.

Skill format requirements (enforced by `make audit:self`):
- `## Purpose` — one-line description of what the skill does.
- `## When to invoke` — conditions that trigger use of this skill.
- `## Prerequisites` — what must be true before starting.

### Rule promotion criteria

Promote an observation to a rule when:
1. The same mistake was made twice in PRs or agent sessions.
2. The correct behaviour is non-obvious but always right.
3. The rule can be stated in 1-3 sentences.

Add rules to `.cursor/rules/global.md` for repo-wide enforcement, or to a module-specific AGENTS.md for scoped rules.

### Procedure promotion criteria

Promote a sequence to a procedure when:
1. It requires human approval steps (deploy, migration on prod).
2. It has rollback steps that differ from normal operation.
3. It should be audited (who ran it, when, with what outcome).

## 14.3.10 Queue items from retrospectives

Any learning that requires future work must become a queue item:

```csv
Q-XXX,open,improvement,<title>,<summary 100+ chars>,<due-date>,,
```

Label improvement-loop-sourced items with a comment in the summary referencing the retrospective file.

## 14.3.11 Quarterly improvement loop

At the end of each quarter:

1. **Review `queue/queue.csv`** for items marked `improvement` — were they completed?
2. **Review CI history** — what was the most common failure mode? Is it now a skill?
3. **Review flaky test metrics** from `docs/quality/flake-policy.md` — any systemic patterns?
4. **Review `docs/quality/testing-strategy.md`** — does coverage floor still make sense?
5. **Run `make audit:self`** and review any recurring failures.
6. **Write the retrospective** in `docs/repo-governance/retrospectives/YYYY-QN.md`.
7. **Add resulting queue items** to `queue/queue.csv`.

## 14.3.12 Measuring loop effectiveness

Track in each quarterly retrospective:
- **Mean time to encode** — time from event to artifact committed (goal: < 1 sprint).
- **Repeat incidents** — same root cause occurring twice in a quarter (goal: 0).
- **Skill adoption** — are skills being invoked in PRs/sessions where they apply?
- **Queue health** — items older than 2 sprints without update (indicates stale debt).
