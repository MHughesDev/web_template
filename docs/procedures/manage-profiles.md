---
doc_id: "5.3"
title: "manage profiles"
section: "Procedures"
summary: "Add, enable, disable, and remove optional application profiles (web, mobile, workers, billing, AI/RAG)."
status: "accepted"
updated: "2026-05-17"
---

# 5.3 — Manage Profiles

**Purpose:** Add, enable, disable, or remove optional application profiles from the repository.

**When to use:**
- Adding web frontend to a backend-only project
- Adding mobile (iOS/Android) support
- Enabling background workers/queues
- Adding billing/subscription features
- Enabling AI/RAG capabilities
- Disabling an unused profile to reduce maintenance burden

**Prerequisites:**
- [ ] `IDEA.md` §11 and §12 define the profile requirements
- [ ] For mobile: Apple Developer Program membership (iOS) or Google Play account (Android)
- [ ] For workers: Message queue infrastructure decision (Redis/RabbitMQ/SQS)
- [ ] For billing: Payment provider account (Stripe/Paddle)

---

## Terminology

| Term | Meaning |
|------|---------|
| **Profile** | Optional feature set with its own codebase, dependencies, and operational burden |
| **Enable** | Activate an existing profile scaffold (set env vars, configure) |
| **Add** | Create scaffold for a profile that doesn't exist in the repo |
| **Disable** | Deactivate without deleting code (toggle off) |
| **Remove** | Delete profile code and all references |

---

## Profile Types

| Profile | Location | Key Files |
|---------|----------|-----------|
| Web | `apps/web/` | React frontend, Vite, Tailwind |
| Mobile | `apps/mobile/` | Flutter iOS/Android |
| Workers | `packages/tasks/` | Background job processors |
| Billing | Integrated | Stripe webhooks, subscription logic |
| AI/RAG | `packages/ai/` | ChromaDB, embeddings, retrieval |

---

## Steps: Add a New Profile

### 1. Validate in IDEA.md

Check `IDEA.md` §11 (Frontend) and §12 (Backend/API):
- Confirm profile is explicitly requested
- Review acceptance criteria
- Note any specific requirements

### 2. Check existing structure

```bash
ls -la apps/
ls -la packages/
```

Verify profile doesn't already exist.

### 3. Scaffold the profile

Use the canonical scaffold command:

```bash
make scaffold-module MODULE=<profile-name>
```

Or for full app profiles:

```bash
# Web
make profile-enable PROFILE=web

# Mobile
make profile-enable PROFILE=mobile
```

### 4. Install dependencies

```bash
# Web
cd apps/web && bun install

# Mobile
cd apps/mobile && flutter pub get

# Workers/AI (Python)
pip install -e packages/tasks
pip install -e packages/ai
```

### 5. Configure environment

Edit `.env` and `config/{dev,staging,prod}.json`:

```bash
# Copy example config
cp .env.example .env

# Edit with profile-specific vars
# - Web: API_BASE_URL
# - Mobile: API_BASE_URL, bundle IDs
# - Workers: REDIS_URL, QUEUE_NAME
# - Billing: STRIPE_SECRET_KEY, webhook secret
```

### 6. Update documentation

Edit `docs/optional-clients/{profile}.md`:
- When to enable/disable
- Prerequisites
- Environment variables
- Operational burden

### 7. Update compose.yml (if needed)

Add services to `compose.yml`:
```yaml
# Example: Add worker service
worker:
  build:
    context: .
    dockerfile: packages/tasks/Dockerfile
  depends_on:
    - db
    - redis
```

### 8. Verify health check

```bash
# Build and run
docker compose up -d

# Check health
make health-check

# Profile-specific verification
curl http://localhost:3000/health  # Web
curl http://localhost:8000/api/v1/health  # API
```

---

## Steps: Enable an Existing Profile

### 1. Check if scaffolded

```bash
ls apps/<profile>/ 2>/dev/null || echo "Profile not scaffolded - run Add first"
```

### 2. Set environment variables

```bash
# Edit .env
export WEB_ENABLED=true
export MOBILE_ENABLED=true
export WORKERS_ENABLED=true
```

### 3. Start profile services

```bash
# Web only
docker compose up web -d

# With mobile build
make mobile:build-android

# With workers
docker compose up worker -d
```

### 4. Verify

```bash
# Check running containers
docker compose ps

# Test endpoints
curl http://localhost:3000  # Web
```

---

## Steps: Disable a Profile

### 1. Stop services

```bash
docker compose stop web
docker compose rm web
```

### 2. Toggle environment

```bash
# Edit .env
export WEB_ENABLED=false
```

### 3. Remove from compose (optional)

Comment out or remove profile services from `compose.yml`.

### 4. Document

Add note to `docs/optional-clients/{profile}.md`:
```markdown
## Status
Currently disabled as of YYYY-MM-DD.
Reason: {brief justification}
To re-enable: follow Enable procedure
```

---

## Steps: Remove a Profile Permanently

**WARNING:** Destructive. Code will be deleted.

### 1. Archive data

If profile has data (DB tables, uploaded files):
```bash
# Backup
make db:dump > backup-pre-profile-removal.sql

# Archive files
tar czf profile-files-archive.tar.gz apps/<profile>/
```

### 2. Remove code

```bash
# Delete directory
rm -rf apps/<profile>/
rm -rf packages/<profile>/

# Remove from compose.yml
# Remove from Makefile
# Remove from .cursor/mcp.json (if applicable)
```

### 3. Clean up dependencies

```bash
# Remove from pyproject.toml or package.json
# Run install to update lock files
```

### 4. Update docs

- Remove from `docs/optional-clients/`
- Update any cross-references

### 5. Verify clean removal

```bash
# Search for dangling references
grep -r "apps/<profile>" . --include="*.md" --include="*.json" --include="*.yml"
grep -r "<profile>_ENABLED" . --include="*.env*"

# Ensure build still works
make docker:build
```

---

## Validation

After Add/Enable:
- [ ] Profile directory exists with expected structure
- [ ] Dependencies install without errors
- [ ] Environment variables documented
- [ ] Health check passes
- [ ] Cross-profile integration documented (if applicable)

After Disable:
- [ ] Services stopped
- [ ] `.env` toggle set
- [ ] No errors in remaining services

After Remove:
- [ ] Directory deleted
- [ ] No references in codebase
- [ ] Build succeeds
- [ ] Tests pass

---

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| `make profile-enable` fails | Profile already exists | Check `apps/` directory; use Enable instead |
| Mobile build fails | Xcode/Android SDK not installed | Install prerequisites from `docs/optional-clients/mobile.md` |
| Workers not processing | Queue not connected | Check `REDIS_URL` and queue service health |
| Billing webhooks fail | URL not registered | Configure webhook endpoint in Stripe dashboard |
| Profile conflicts | Multiple profiles share port/resource | Check `compose.yml` port mappings |

---

## See Also

- Optional clients: `docs/optional-clients/`
- Web profile: `docs/optional-clients/web.md`
- Mobile profile: `docs/optional-clients/mobile.md`
- Add make target: `docs/procedures/add-make-target.md`
