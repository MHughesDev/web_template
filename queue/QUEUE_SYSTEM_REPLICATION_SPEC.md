# queue/QUEUE_SYSTEM_REPLICATION_SPEC.md

**Document purpose:** This is a full, implementation-ready replication spec for the queue system currently present in this repository as of **2026-04-23**. It is intended to let another agent recreate the **same queue system behavior, contracts, and tooling** in another repo.

---

## 1) System identity and intent

- The queue is a **CSV-based agent work orchestration lane**, not a PM backlog.
- It is designed for **single-lane processing**: the top open queue row is the active item.
- It supports:
  - strict lifecycle semantics (open → in-progress/blocked → archive)
  - dependency gating
  - branch/PR traceability
  - validation and intelligence tooling
  - operator/executor role separation

Core statement (must preserve):
- **Queue processors implement work; operators maintain queue ledgers.**

---

## 2) Required file layout

Recreate the following files and paths:

- `queue/queue.csv`
- `queue/queuearchive.csv`
- `queue/QUEUE_INSTRUCTIONS.md`
- `queue/QUEUE_AGENT_PROMPT.md`
- `queue/queue.lock` (recommended)
- `docs/queue/queue-system-overview.md`
- `docs/queue/queue-categories.md`
- `docs/queue/queue-intelligence.md`
- `docs/procedures/start-queue-item.md`
- `docs/procedures/archive-queue-item.md`
- `docs/procedures/add-queue-category.md`
- `.cursor/rules/queue.md`
- `prompts/queue_worker_executor.md`
- `prompts/queue_processor.md`
- `skills/agent-ops/queue-triage.md`
- `skills/agent-ops/queue-triage.py`
- `skills/agent-ops/queue-intelligence.md`
- `skills/agent-ops/queue-intelligence.py`
- `scripts/queue-top-item.sh`
- `scripts/queue_top_item.py`
- `scripts/queue-peek.sh`
- `scripts/queue-validate.sh`
- `scripts/queue_validate.py`
- `scripts/queue-archive.sh`
- `scripts/queue_archive.py`
- `scripts/queue-graph.sh`
- `scripts/queue-analyze.sh`
- `scripts/queue-pr-merge.sh`

Dependency module used by scripts:
- `packages/queue_ops/__init__.py`

Also wire Makefile targets (section 7 below).

---

## 3) Data model and CSV schemas

### 3.1 Open queue schema (`queue/queue.csv`)

Current expected header in validator and `make queue:top-item` path:

```csv
id,batch,phase,category,summary,agent_instructions,constraints,dependencies,related_files,notes,created_date
```

Column semantics:

- `id` (required): globally unique queue ID (e.g., `Q-001`), never reused.
- `batch` (optional): grouping label for release train.
- `phase` (optional): ordering within batch.
- `category` (required): must be from queue categories registry.
- `summary` (required): long-form contract. Policy says include goal + acceptance criteria + done definition + out-of-scope + dependencies. Validator enforces minimum length behavior (see section 8).
- `agent_instructions` (optional): executor-focused ordered/unordered steps.
- `constraints` (optional): non-negotiable implementation characteristics (UI behavior, color codes, API contract, naming rules, etc.).
- `dependencies` (optional): comma-separated IDs that must be archived as done.
- `related_files` (optional): comma-separated repo-relative paths to read before implementation.
- `notes` (optional): operator notes/blockers/PR links/completion context.
- `created_date` (required): ISO date (`YYYY-MM-DD`).

### 3.2 Archive schema (`queue/queuearchive.csv`)

Expected archive header:

```csv
id,batch,phase,category,summary,agent_instructions,constraints,dependencies,related_files,notes,created_date,status,completed_date
```

Archive-only columns:

- `status` (required): `done` / `cancelled` / `superseded`
- `completed_date` (required): ISO date of archive action

### 3.3 CSV title comment convention

Both queue files are expected to support an optional first-line title comment, e.g.:

```text
# queue/queue.csv
```

Script loaders skip this line if it starts with `#`.

---

## 4) Lifecycle and operating rules

### 4.1 Single-lane policy

- Top data row in `queue/queue.csv` is the active item.
- Process one item at a time in default policy.
- Do not reorder rows without explicit human decision.

### 4.2 Dependency readiness

Before starting work:
- Parse `dependencies` IDs.
- Verify each dependency exists in archive with status `done`.
- If any missing, item is blocked.

### 4.3 Blocked handling

- Blocked rows stay in open queue.
- Notes should include: `blocked_by`, owner, next step.
- Do not archive blocked work.

### 4.4 Done/cancelled/superseded handling

- Move row from open queue to archive.
- Include `status` and `completed_date`.
- Keep archive append-only.

---

## 5) Executor vs operator split (critical)

### Executors (implementation agents)

Must do:
- read queue rows, contracts, related files
- implement code on branch
- open PR with evidence and queue ID
- provide handoff instructions for human operator

Must NOT do:
- edit `queue/queue.csv` or `queue/queuearchive.csv`
- run `make queue:archive*` in executor role
- perform queue ledger maintenance

Canonical executor contract files:
- `queue/QUEUE_AGENT_PROMPT.md`
- `prompts/queue_worker_executor.md`

### Operators (human or separate automation)

Do:
- update queue notes
- archive rows (`queue:archive-top` / `queue:archive`)
- run `queue:validate` after queue edits
- merge PR (`queue:pr-merge` or UI)

---

## 6) Branching and PR conventions

Queue branch pattern:
- `queue/<id>-short-slug`

PR convention:
- Title should include queue ID (example: `[Q-001] feat(...): ...`)
- PR body includes: commands run, files changed, acceptance criteria evidence, risk notes

---

## 7) Makefile command surface (must replicate)

Required aliases/targets:

- `make queue:peek` -> show queue header + first row
- `make queue:top-item` -> one-line JSON for top row (all columns)
- `make queue:validate` -> queue schema/invariant validation
- `make queue:archive QUEUE_ID=<id>` -> archive a specific row
- `make queue:archive-top` -> archive first open row by position
- `make queue:graph` -> dependency graph (Mermaid)
- `make queue:analyze` -> intelligence analysis JSON
- `make queue:pr-merge` -> `gh pr merge --merge --delete-branch`

Colon-form aliases are expected to map to hyphen-form targets.

---

## 8) Script-level behavior specification

### 8.1 `queue_top_item.py`

Behavior:
- read `queue/queue.csv`
- validate headers against `OPEN_FIELDS`
- if missing file: emit JSON error to stderr and non-zero exit
- if invalid CSV: emit JSON error to stderr and non-zero exit
- if no data rows: emit JSON `{"error":"no_open_items"...}` and zero exit
- else print JSON object for first row with trimmed fields in `OPEN_FIELDS`

### 8.2 `queue_validate.py` and `packages.queue_ops`

Current implementation validates:
- open header matches `OPEN_FIELDS`
- archive header matches `ARCHIVE_HEADER`
- summary length rule: if non-empty summary is shorter than min length (`100`), fail

Current implementation does **not** enforce all policy claims in docs (e.g., category set checking and duplicate ID checks are documented but not enforced in the Python module as-is).

### 8.3 `queue_archive.py`

Current behavior:
- supports `archive by ID` and `--top`
- `--top` resolves first open row ID then archives by ID
- appends archived row to archive file with today’s date
- writes queue file back without archived row
- default status is `done`

### 8.4 `queue-peek.sh`

Behavior:
- outputs first 3 lines of `queue/queue.csv` (title, header, first data row)

### 8.5 `queue-graph.sh` and `queue-analyze.sh`

- `queue-graph.sh` calls queue-intelligence graph mode.
- `queue-analyze.sh` validates queue first, then runs intelligence analysis.

### 8.6 `queue-pr-merge.sh`

Behavior:
- requires `gh` CLI installed
- runs `gh pr merge --merge --delete-branch`
- optional `PR_NUMBER` env var to merge a specific PR from non-head branch

---

## 9) Intelligence layer replication (`skills/agent-ops/queue-intelligence.py`)

Current capabilities:

1. **Dependency graph**
   - build graph from open items and dependency IDs
   - topological sorting via Kahn algorithm
   - cycle detection fallback
   - Mermaid rendering

2. **Readiness analysis**
   - ready item = all dependencies present in archived done IDs
   - blocked item output includes missing dependencies

3. **Complexity scoring**
   - heuristic score (1-10 + S/M/L/XL)
   - based on summary length + dependency count + category weighting

4. **Batch suggestion**
   - groups by `batch`, then by inferred module context (`apps/api/app/<module>/` pattern)

5. **Conflict detection**
   - path pattern extraction from summary + related_files
   - overlap between items => medium/high risk signals

CLI modes:
- `graph`
- `analyze`
- `ready`
- `blocked`

---

## 10) Category registry replication

Default category set from `docs/queue/queue-categories.md`:

- `core-api`
- `infrastructure`
- `testing`
- `documentation`
- `bugfix`
- `refactor`
- `security`
- `devops`

Procedure to add categories exists but is currently a template/stub in `docs/procedures/add-queue-category.md` and should be replicated in same form if exact parity is required.

---

## 11) Prompt/procedure/rule contracts to replicate

### 11.1 Must-have rule file
- `.cursor/rules/queue.md`
  - queue schema invariants
  - lifecycle and archive-before-delete policy
  - executor non-edit policy for queue CSVs
  - branch and PR expectations

### 11.2 Must-have prompts
- `queue/QUEUE_AGENT_PROMPT.md`
- `prompts/queue_worker_executor.md`
- `prompts/queue_processor.md`

These documents enforce:
- read order
- mandatory skills search
- dependency verification
- strict executor/operator separation

### 11.3 Must-have procedures
- `docs/procedures/start-queue-item.md`
- `docs/procedures/archive-queue-item.md`
- `docs/procedures/add-queue-category.md`

---

## 12) Lock and audit files

### 12.1 `queue/queue.lock`

Expected format is JSON object with:
- `owner`
- `claimed_at`
- `branch`
- `queue_id`

Current repository state uses `{}` as unlocked baseline and documents lock as advisory.

### 12.2 `queue/audit.log` (recommended)

Design intent:
- append-only JSON lines
- operation events like claim/release/archive/reorder

Note: this repo documents it heavily, but queue tooling shown here does not currently force write/update to audit log automatically.

---

## 13) Initialization and seeding path

Queue seeding script:
- `scripts/idea-to-queue.sh`

Behavior:
- seed queue rows by running `skills/init/repo_initialize.md` Phase 4 after IDEA.md is complete

This is required if you want full repo parity (not just runtime queue processing).

---

## 14) Known as-is drift / implementation quirks (replicate if exact parity required)

To reproduce this repo’s queue system *exactly as implemented right now*, preserve these quirks:

1. `scripts/queue_archive.py` has `OPEN_FIELDS` that omit `constraints`, while active queue schema includes `constraints`.
2. `queue/QUEUE_INSTRUCTIONS.md` lifecycle language still includes agent-archives wording in parts, while executor prompts enforce operator-only archive.
3. `docs/procedures/add-queue-category.md` is a skeleton template, not a fully fleshed operational SOP.
4. `packages.queue_ops.validate_*` enforces header and summary length but does not enforce all documented invariants (e.g., category membership, duplicate IDs, circular deps) directly in shown code.
5. Current `queue/queuearchive.csv` includes duplicated/irregular rows after canonical header (historical drift artifact).

If you want **functional parity** instead of **bug-for-bug parity**, fix these explicitly in your destination implementation.

---

## 15) End-to-end execution flow (replication-ready)

1. Executor reads queue contracts and runs `make queue:top-item`.
2. Executor verifies dependencies in archive done rows.
3. Executor creates `queue/<id>-slug` branch.
4. Executor implements task and opens PR with queue ID.
5. Executor handoff instructs operator to archive.
6. Operator runs `make queue:archive-top` (or by ID), then `make queue:validate`.
7. Operator runs `make queue:pr-merge` (or merge in UI).
8. Next queue top item becomes active.

---

## 16) Minimal acceptance tests for duplicate implementation

After cloning this system into another repo, run these checks:

- `make queue:top-item` prints one JSON line with all open fields.
- `make queue:peek` prints title/header/first row.
- `make queue:validate` fails on malformed headers and short summaries.
- `make queue:archive-top` moves first open row into archive with status/date.
- `make queue:archive QUEUE_ID=<id>` archives specific ID.
- `make queue:graph` emits Mermaid graph.
- `make queue:analyze` emits structured JSON analysis.
- `make queue:pr-merge` executes `gh pr merge --merge --delete-branch`.

---

## 17) Replication checklist

- [ ] Queue CSV/open + archive files created with proper header/comment format.
- [ ] Queue SOP and agent prompt files created.
- [ ] Executor prompt and processor prompt created.
- [ ] Queue rules file wired under `.cursor/rules/queue.md`.
- [ ] Queue scripts created and executable.
- [ ] `packages.queue_ops` module (or equivalent shared queue helpers) implemented.
- [ ] Make targets + colon aliases wired.
- [ ] Queue intelligence skill + script installed.
- [ ] Queue docs/procedures included and cross-linked.
- [ ] Role separation (executor no CSV writes) enforced in prompts and policy docs.

---

## 18) Source authority map (for implementer)

Use these source-of-truth layers in this order when reproducing:

1. Queue sections (system-level contract)
2. `AGENTS.md` queue interaction + mandatory skill search
3. `queue/QUEUE_INSTRUCTIONS.md` and `queue/QUEUE_AGENT_PROMPT.md`
4. `.cursor/rules/queue.md`
5. scripts + `packages.queue_ops` implementation behavior
6. queue docs/procedures/prompts/skills

This ordering is necessary because there are minor doc-vs-code drifts in current repo state.

---

**End of replication spec.**
