# queue/QUEUE_INSTRUCTIONS.md

<!-- CROSS-REFERENCES -->
<!-- - Referenced by: AGENTS.md §9, CONTRIBUTING.md, queue/QUEUE_AGENT_PROMPT.md -->
<!-- - Related skills: skills/agent-ops/queue-triage.md, skills/agent-ops/queue-intelligence.md -->

**Purpose:** Human and agent SOP for all queue operations. Canonical reference for queue lifecycle, branch naming, PR linking, conflict resolution. Per spec §26.6 item 192.

## Overview

One paragraph. This file is the authoritative SOP for the CSV-based agent work queue. Any agent working on queue items must read this file completely before starting. The queue is NOT a product backlog — it is an agent work orchestration lane with strict lifecycle rules. Every row must declare S or M complexity with enforceable file-count limits. L complexity is forbidden.

## File Roles

Description of each queue file and its role:
- `queue/queue.csv` — Open items; top data row = active work item for single-lane processing (human-ops rows skipped)
- `queue/queuearchive.csv` — Historical record; append-only; completed/cancelled/superseded items
- `queue/QUEUE_AGENT_PROMPT.md` — Executable behavior contract for agents (must read before processing)
- `queue/QUEUE_SPLIT_TRIGGERS.md` — Quick reference card for split triggers (when a row must be decomposed)
- `queue/queue.lock` — Optional mutex file; present = someone is actively processing
- `queue/audit.log` — Append-only JSON lines for all claim/release/archive events

## Schema (Column Definitions)

The queue CSV uses the following columns. **Columns marked Required=yes must be
non-empty for `make queue:validate` to pass.** All paths in file columns are
repo-relative (e.g. `apps/api/app/routes/health.py`).

| Column | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique identifier. Format: `Q-NNN` for top-level, `Q-NNNa`, `Q-NNNb` for sub-tasks from a decomposed parent. Never reuse IDs. |
| `batch` | string | no | Batch label for coordinated release trains (e.g. `1-mvp`). |
| `phase` | string | no | Ordering within a batch (e.g. `1`, `2`, `3`). |
| `category` | string | yes | Must exactly match a value in `docs/queue/queue-categories.md`. |
| `complexity` | enum | yes | **`S` or `M` only. `L` is forbidden and fails validation.** S = 1–2 touch_files, single atomic deliverable. M = 3 touch_files max, one feature boundary crossed. |
| `goal` | string | yes | 1–2 sentences. What is being built and why. No acceptance criteria here. Max 300 chars. |
| `acceptance_criteria` | string | yes | Numbered list of verifiable conditions. Each item must be independently checkable by the agent or a reviewer. Minimum 1 item required. Use `\|` as line separator within the CSV cell (e.g. `1. Tests pass \| 2. No new warnings`). |
| `scope_boundary` | string | no | Explicit comma-separated list of files, modules, API surfaces, or behaviors that are OUT OF SCOPE for this item. Agent must not touch anything listed here. |
| `agent_instructions` | string | no | Numbered steps if execution order matters. Prose or bullets if order-free. Empty if the goal and acceptance criteria are sufficient. |
| `constraints` | string | no | Non-negotiable implementation characteristics: naming conventions, color tokens, API contracts, design system rules, performance budgets. |
| `context_files` | string | no | **Ordered** comma-separated repo-relative paths the agent reads for context. First listed = highest priority if context budget is tight. Agent reads but does NOT edit these files. |
| `touch_files` | string | yes | Comma-separated repo-relative paths the agent will write, create, or delete. **Hard limit: ≤2 for S, ≤3 for M.** Validation fails if this limit is exceeded for the declared complexity. |
| `verification_cmds` | string | no | Task-specific shell or make commands to run as proof of done, beyond the global checklist in AGENTS.md. Example: `make test -- -k test_invoice`. |
| `dependencies` | string | no | Comma-separated IDs that must be in `queuearchive.csv` with `status=done` before this item may be claimed. |
| `notes` | string | no | Operator channel only. Executors write only branch/PR info here. Do not put implementation detail in notes. |
| `created_date` | date | yes | ISO 8601 (YYYY-MM-DD). |

**Archive-only columns** (added when a row is moved to `queuearchive.csv`):

| Column | Type | Required | Description |
|---|---|---|---|
| `status` | string | yes | `done`, `cancelled`, or `superseded`. |
| `completed_date` | date | yes | ISO 8601 date when archived. |

## Granularity Rules — L Tasks Are Forbidden

Every row in `queue.csv` must be complexity `S` or `M`. Complexity `L` is
**forbidden** and will cause `make queue:validate` to fail. This is not
negotiable and is not overridable by operator notes.

### Complexity definitions

**S — Small:**
- `touch_files` contains ≤ 2 paths
- Single atomic deliverable: one widget, one function, one test file, one doc
  section, one config change
- Does not add new entries to `pubspec.yaml`, `pyproject.toml`, `package.json`,
  or equivalent dependency manifests

**M — Medium:**
- `touch_files` contains ≤ 3 paths
- Crosses at most one feature/module boundary
- If a new package dependency is required, that dependency addition is a
  separate S task that must complete first (and be listed in `dependencies`)

### Split triggers — a row MUST be decomposed when any of these fire

Before adding any row to `queue.csv`, apply this checklist. If **any** item is
true, the row is L complexity and must be split before entering the queue:

1. `touch_files` would exceed the limit for the declared complexity
2. The `goal` sentence contains "and" describing two **distinct** behaviors or
   deliverables
3. Tests are a major deliverable alongside implementation (tests become a
   separate S row with a dependency on the implementation row)
4. A new package/dependency is required (dependency addition = separate S row
   first, listed in `dependencies` of the implementation row)
5. The work crosses two or more feature module or layer boundaries
6. `acceptance_criteria` has more than 5 items (split at natural seams)
7. The human operator cannot describe the row's output in one commit message

### Sub-task ID convention

When a parent task is decomposed:
- The parent ID (e.g. `Q-042`) is **never** added to the queue directly
- Sub-tasks use lettered suffixes: `Q-042a`, `Q-042b`, `Q-042c`
- Each sub-task gets its own full row with its own `goal`, `acceptance_criteria`,
  `touch_files`, and `context_files`
- Sub-tasks chain via `dependencies`: `Q-042b` lists `Q-042a` in its
  `dependencies` field; `Q-042c` lists `Q-042b`
- Each sub-task sees only its own slice — never the full parent picture

### human-ops category

Items that are ops, secrets, Kubernetes config, CI pipeline config, or
infrastructure work that no coding agent should execute must use
`category=human-ops`. These rows are tracked in the queue for audit purposes
but are **skipped** by `make queue:top-item` (they are never returned as the
active work item). They must still pass all other validation rules.

See `docs/procedures/queue-decomposition.md` for the full SOP on decomposing L tasks.

## Lifecycle State Machine

State transitions per spec §17.3. Each state with location, transition rules, and notes requirements:
- **Open** → In Progress: agent creates branch named queue/<id>-slug
- **In Progress** → Done: work complete; agent archives with status=done, completed_date, PR URL, then runs **`make queue:pr-merge`** (or merges in UI) to update GitHub
- **In Progress** → Blocked: agent updates notes with blocker; stays in queue.csv
- **Blocked** → In Progress: blocker resolved; agent updates notes, resumes
- **Open/In Progress** → Cancelled: human decision; archive with status=cancelled
- **Open** → Superseded: newer item covers the same scope; archive with status=superseded + successor ID

## Single-Lane Processing Rules

Rules for single-lane processing:
1. Only ONE item may be "In Progress" at a time under the default policy
2. The top data row of queue.csv (skipping human-ops rows) is the next item to process
3. Before starting: verify all dependencies are in queuearchive.csv with status=done
4. Blocked top item: document blocker in notes; optionally process next ready item
5. Never reorder queue.csv rows without human approval

## Adding New Rows (Dependency-First Ordering)

0. **Apply the split triggers checklist** (see "Granularity Rules" section
   above). If any trigger fires, decompose into sub-tasks first and add those
   instead. Never add an `L`-complexity row directly.
1. Parse the new row's `dependencies` as queue IDs.
2. Place the new row **after** every open prerequisite row it depends on.
3. If all dependencies are already `status=done` in `queuearchive.csv`, place the row after existing currently-ready items in its batch/phase lane (or at the end of the open queue when no batch policy is active).
4. Never insert a row above an open row that it depends on.
5. If insertion cannot satisfy both dependency order and current FIFO/batch conventions, preserve dependency order first and add an explanatory note in `notes`.
6. Run `make queue:validate` after insertion.

## Claiming Work

How to claim a queue item:
1. Run **`make queue:top-item`** — stdout is **one line** of JSON with the full top non-human-ops row (all columns). Parse it; **`goal`** and **`acceptance_criteria`** together form the contract. Optional: `make queue:peek` for raw CSV (header + first data row).
2. Verify dependencies met (all IDs in queuearchive.csv with status=done)
3. Read every path in `context_files` (split on commas, trim whitespace) in
   priority order — first listed is highest priority if your context window is
   tight. Read `agent_instructions` if non-empty. Do NOT edit `context_files`
   paths — they are read-only context. The files you may write are in
   `touch_files` only.
4. Create branch: `git checkout -b queue/<id>-short-slug`
5. Update notes column (optional but recommended): "in_progress | branch: queue/<id>-slug"
6. Run mandatory skill search before starting implementation

## Branch Naming

Branch naming convention: `queue/<id>-short-slug`
- id: the exact value from the id column (e.g., Q-001)
- short-slug: 3-5 words, kebab-case, describing the work (e.g., add-invoice-endpoint)
- Full example: `queue/Q-001-add-invoice-endpoint`
- Alternative (cursor-initiated): `cursor/<descriptive-slug>-<suffix>`

## PR Linking

Every queue-driven PR must:
- Include the queue ID in the PR title: `[Q-001] type(scope): description`
- Paste the PR URL in the queue item's notes column
- After CI/review and the work is complete: **archive the item** (see Archiving), **`make queue:validate`**, then update GitHub with **`make queue:pr-merge`** (`gh pr merge --merge --delete-branch`) or merge in the UI

## Blocked Items

Protocol for blocked items (do NOT archive):
- Update notes: `blocked_by: <reason> | owner: <who> | next_step: <what triggers unblocking>`
- Create escalation (GitHub issue or comment on relevant PR)
- Item stays at its position in queue.csv
- After unblocking: update notes, resume processing

## Archiving

How to archive a completed item (then update GitHub):
1. **Token-friendly (recommended for single-lane):** run **`make queue:archive-top`** — moves the **first data row** in `queue.csv` to `queuearchive.csv` with `status=done` and today's `completed_date`. No queue id in the command; use when the top row is the item you are closing.
2. Or run `make queue:archive QUEUE_ID=<id>` (scripted) or manually:
   - Copy row to queuearchive.csv
   - Add: status=done, completed_date=YYYY-MM-DD, PR URL in notes
   - Remove from queue.csv
3. Run **`make queue:validate`** — must pass
4. **Update GitHub last:** from the PR branch run **`make queue:pr-merge`** — `gh pr merge --merge --delete-branch` — or merge in the GitHub UI. Optional: `PR_NUMBER=<n> make queue:pr-merge` if not on the PR branch. Then update local `main` if needed (`git checkout main && git pull`).

**Warning:** `queue:archive-top` archives by **position**, not by id. Only use when the top open row is the item you intend to close (default single-lane policy).

## Batch/Phase Policy

Batch semantics: items with the same batch value are released as a coordinated unit. Phase within batch determines ordering. Processors MAY process items in strict FIFO within a batch. If batch policy is active: document in queue notes.

## Conflict Resolution

If two processors collide on queue.csv:
1. Stop immediately
2. Re-run `make queue:validate` on both copies
3. Use `main` branch as the truth
4. Merge manually: never silently drop rows
5. Verify no duplicate IDs after merge

## Validation

Run `make queue:validate` after any modification. Validation checks:
- Header row matches expected columns (new 16-column schema)
- No duplicate IDs across queue.csv and queuearchive.csv
- All categories in docs/queue/queue-categories.md
- No circular dependencies

**New checks (granularity enforcement):**
- `complexity` must be `S` or `M` — `L` or any other value fails
- For `S` rows: `touch_files` must contain ≤ 2 comma-separated paths
- For `M` rows: `touch_files` must contain ≤ 3 comma-separated paths
- `goal` must be present and ≤ 300 characters
- `acceptance_criteria` must be present and contain at least one numbered item
  (must match pattern `1.` or `1)`)
- `touch_files` must be present and non-empty
- `category=human-ops` rows: skip active-item selection but still validate
  all other required fields
- Column count must match the new header exactly (new columns: `complexity`,
  `goal`, `acceptance_criteria`, `scope_boundary`, `context_files`,
  `touch_files`, `verification_cmds`; removed: `summary`, `related_files`)

## Initialization-derived MVP work

When repository initialization runs ([`skills/init/repo_initialize.md`](../skills/init/repo_initialize.md)), it adds an **initial batch** of queue rows that walk the product from the baseline app to the MVP defined in `IDEA.md §4`. These rows follow the same schema as every other row but with three conventions that make the MVP path auditable:

### How initialized MVP work enters the queue

1. The skill decomposes each `IDEA.md §4` MVP bullet into one or more queue-sized rows (S or M complexity).
2. Each row's `context_files` references the docs the skill itself produced in phase 2 (e.g. `docs/architecture/data-model.md`, `docs/api/endpoints.md`). Executors do not have to re-read `IDEA.md`.
3. Rows are tagged on the MVP critical path with `batch=mvp-1`, `mvp-2`, … in dependency order. The first executable MVP row is the topmost row in `queue/queue.csv` that has all dependencies satisfied.

### How agents select the next initialization row

Standard `make queue:top-item` semantics apply — the first non-human-ops data row whose dependencies are satisfied is the active row. Initialization does **not** introduce a parallel selection mechanism; the queue stays single-lane.

### Blocked open-question rows

For every entry in `IDEA.md §19` that the initializer judged blocking (architecture or implementation), it creates a `category=human-ops` row with:

- `goal` = `Resolve open question: <verbatim question>`
- `notes` = `blocked_by: open_question`
- `dependencies` = `(empty)` (so the question can be answered at any time)

These rows are skipped by `make queue:top-item` but visible to operators and audits. When a question is answered, the operator archives the human-ops row with `status=done` and adds the answer to `docs/open-questions.md`.

### Linking docs updates to queue execution

When an executor lands a queue row whose work materially changes a doc that initialization produced (e.g. adding a real endpoint changes `docs/api/endpoints.md`), the same PR must update that doc. The `touch_files` field for such rows therefore commonly includes both a code path and a docs path. Reviewers reject PRs that change behavior without updating the corresponding initialized doc.

### Definition of "done" for initialization-derived rows

A row is done when:

- All `acceptance_criteria` items are demonstrated true in the PR (CI green, manual checks linked, or files committed).
- Any doc this row owns updating has been updated in the same PR.
- The row is moved to `queue/queuearchive.csv` with `status=done` and `completed_date`.
- The PR is merged via `make queue:pr-merge` (or the UI), and the feature branch is deleted.

## Generic row examples (illustrative — do NOT copy into `queue.csv`)

These examples show the shape of well-formed rows for the four common archetypes. They are illustrative only; do not add them to `queue/queue.csv`. Real rows come from initialization or from `docs/procedures/add-make-target.md`-style sources.

> **Schema header** (always row 1 of `queue/queue.csv`):
> `id,batch,phase,category,complexity,goal,acceptance_criteria,scope_boundary,agent_instructions,constraints,context_files,touch_files,verification_cmds,dependencies,notes,created_date`

### Example 1 — normal MVP work row (feature implementation)

A typical S-complexity row on the MVP critical path. Adds one route on top of an existing module.

```
Q-EX1,mvp-1,2,core-api,S,
"Add GET /api/v1/widgets/{id} that returns a single widget by id with 404 when missing.",
"1. Endpoint returns 200 + Widget schema when the row exists | 2. Endpoint returns 404 + WIDGET_NOT_FOUND when missing | 3. pytest in tests/api/routes/test_widgets.py covers both paths",
"Do not modify Widget model or migrations",
,
"Path must match `/api/v1/widgets/{id}`; error code WIDGET_NOT_FOUND defined in docs/api/error-codes.md",
"docs/api/endpoints.md,docs/architecture/bounded-contexts.md,apps/api/app/api/routes/items.py",
"apps/api/app/api/routes/widgets.py,apps/api/tests/api/routes/test_widgets.py",
"make test -- -k widgets",
,
,
2026-05-18
```

### Example 2 — blocked open-question row (`category=human-ops`)

Created by `repo_initialize` when `IDEA.md §19` lists a question whose answer changes product behavior. Skipped by `make queue:top-item`; resolved by a human writing the answer into `docs/open-questions.md` and archiving this row.

```
Q-EX2,,,human-ops,S,
"Resolve open question: Should invoices support multiple currencies?",
"1. Decision recorded in docs/open-questions.md with rationale | 2. Any new product ADR added if the decision is architecturally significant | 3. Follow-up MVP rows added if implementation work is unblocked",
,
,
,
"IDEA.md,docs/open-questions.md",
"docs/open-questions.md",
,
,
"blocked_by: open_question | owner: product",
2026-05-18
```

### Example 3 — docs-update row (paired with a feature row)

Sometimes the implementation row also has to update a doc; sometimes the docs change is large enough to warrant its own row. Use this shape when the docs change has its own acceptance criteria.

```
Q-EX3,mvp-1,3,docs,S,
"Update docs/api/endpoints.md and docs/api/error-codes.md to describe the new GET /widgets/{id} endpoint and WIDGET_NOT_FOUND error.",
,
,
,
"docs/api/endpoints.md,docs/api/error-codes.md,apps/api/app/api/routes/widgets.py",
"docs/api/endpoints.md,docs/api/error-codes.md",
"Q-EX1",
,
2026-05-18
```

### Example 4 — validation / finalization row (end of an MVP batch)

The terminal row in a batch. Picks up after all feature and docs rows in the batch have archived; runs the full validation matrix and updates `docs/project-state.md` to reflect what the batch delivered.

```
Q-EX4,mvp-1,99,release,S,
"Run full validation matrix for mvp-1 and update docs/project-state.md.",
"Do not implement new features here",
"Use only existing make targets — do not invent commands",
,
"docs/project-state.md,queue/queue.csv,queue/queuearchive.csv",
"docs/project-state.md",
"Q-EX1,Q-EX3",
,
2026-05-18
```

The examples follow every queue invariant: `complexity` is `S`, `touch_files` ≤ 2 paths, `goal` ≤ 300 chars, `acceptance_criteria` is a `|`-separated numbered list, and `category` matches a value in `docs/queue/queue-categories.md`.

