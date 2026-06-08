---
doc_id: "5.36"
title: "pre-deploy checklist"
section: "Procedures"
status: "current"
summary: "Pre-flight validation checklist for cloud deployments. Run before any deployment to staging or production."
updated: "2026-05-17"
---

# Pre-Deployment Checklist

## Purpose

Validate that all prerequisites are met before deploying to cloud infrastructure. This checklist prevents common deployment failures by catching issues early.

## When to Run

- Before first deployment to new environment
- Before every production deployment
- After infrastructure changes
- When onboarding new team members to deployment process

## How to Run

```bash
# Automated check
make pre-deploy-check ENV=staging

# Or manual review
# Go through each section and verify items
```

---

## Security Checklist

### Secrets Management

- [ ] **No secrets in Git**
  ```bash
  # Run secret scanner
  make secrets:scan
  # Should report: "No secrets found"
  ```

- [ ] **SECRET_KEY is unique per environment**
  - Not "changethis" or default value
  - Different values for staging vs. production
  - 64+ character random string
  ```bash
  # Verify in GitHub/GitLab environment
  # Should be: openssl rand -hex 32
  ```

- [ ] **Database password is complex**
  - 20+ characters
  - Mix of alphanumeric and symbols
  - Not "postgres" or "password"

- [ ] **First superuser password is complex**
  - Different from database password
  - Not stored in code or default configs

- [ ] **Sentry DSN uses correct environment**
  - Staging DSN for staging
  - Production DSN for production
  - Not the template example DSN

- [ ] **Email credentials secured**
  - SMTP password in secrets, not config
  - Test email disabled or configured correctly

### Infrastructure Security

- [ ] **Container runs as non-root**
  - Already in template: `runAsUser: 1000`
  - Verify: `kubectl exec -n prod deployment/api -- id`
  - Should show: `uid=1000` not `uid=0`

- [ ] **Read-only root filesystem (production)**
  - Optional hardening: `readOnlyRootFilesystem: true`
  - Temp directory mounted for writes if needed

- [ ] **Resource limits enforced**
  - CPU and memory limits set in deployment
  - Prevents resource exhaustion attacks

- [ ] **Network policies considered**
  - Database traffic restricted to app namespace
  - Ingress only on required ports (80, 443, 8000)

- [ ] **TLS 1.2+ only**
  - Let's Encrypt or custom certificates
  - HTTP redirects to HTTPS
  - No port 80 except for redirect

---

## Configuration Checklist

### Environment Variables

- [ ] **DOMAIN is set to real domain**
  ```bash
  # Not localhost
  grep DOMAIN .env.staging  # Should show: staging.yourdomain.com
  grep DOMAIN .env.production  # Should show: yourdomain.com
  ```

- [ ] **FRONTEND_HOST uses HTTPS in production**
  ```bash
  # Production should use https://
  grep FRONTEND_HOST .env.production  # Should show: https://yourdomain.com
  
  # Staging can use http:// or https://
  grep FRONTEND_HOST .env.staging  # Should show: https://staging.yourdomain.com
  ```

- [ ] **CORS_ORIGINS includes production domain**
  ```bash
  # Must include your production frontend URL
  grep BACKEND_CORS_ORIGINS .env.production
  # Should contain: https://yourdomain.com
  ```

- [ ] **ENVIRONMENT is set correctly**
  ```bash
  # Not "local" or "development"
  grep ENVIRONMENT .env.production  # Should show: production
  grep ENVIRONMENT .env.staging  # Should show: staging
  ```

- [ ] **Debug mode disabled in production**
  ```bash
  # No DEBUG=true in production
  # Logs should not show debug stack traces to clients
  ```

### Kubernetes Configuration

- [ ] **Image references updated**
  ```bash
  # Not template-api:latest
  grep "newName:" deploy/k8s/overlays/staging/kustomization.yaml
  # Should show: ghcr.io/your-org/your-repo/api
  ```

- [ ] **Namespace set correctly**
  ```bash
  # Staging overlay: namespace: staging
  # Production overlay: namespace: prod
  grep "namespace:" deploy/k8s/overlays/staging/kustomization.yaml
  grep "namespace:" deploy/k8s/overlays/prod/kustomization.yaml
  ```

- [ ] **Domain in ingress rules**
  ```bash
  # Traefik or ingress configured with real domain
  grep "Host(" deploy/k8s/base/ingress.yaml  # or compose.traefik.yml
  # Should show: api.yourdomain.com
  ```

---

## Database Checklist

### Connection

- [ ] **Database server is provisioned**
  - Managed PostgreSQL instance exists
  - Instance is "Available" in cloud console

- [ ] **Database is accessible from cluster**
  ```bash
  # Test from pod
  kubectl run -it --rm db-test --image=postgres:16 --restart=Never \
    -- psql "postgresql://user:pass@host:port/db?sslmode=require"
  # Should connect successfully
  ```

- [ ] **Migrations tested on staging database**
  ```bash
  # Run on staging DB
  cd apps/api
  alembic upgrade head --sql  # Review SQL first
  alembic upgrade head  # Apply if looks good
  ```

- [ ] **Backup strategy documented**
  - Automated daily backups enabled
  - Retention period defined (e.g., 7 days)
  - Restore procedure tested

- [ ] **Connection pooling configured**
  - Pool size appropriate for connection limits
  - Timeout values set (30s connect, 60s read)

### Schema

- [ ] **Migration files committed**
  ```bash
  # Check for uncommitted migrations
  git status apps/api/app/alembic/versions/
  # Should be clean
  ```

- [ ] **No destructive migrations without plan**
  - Drop column/table migrations reviewed
  - Data migration strategy documented
  - Rollback tested for all migrations

---

## Infrastructure Checklist

### Kubernetes

- [ ] **Cluster is running**
  ```bash
  kubectl get nodes
  # All nodes should be Ready
  ```

- [ ] **kubectl can connect from local machine**
  ```bash
  kubectl get namespaces
  # Should show: default, kube-system, staging, prod
  ```

- [ ] **Container registry is accessible**
  ```bash
  # From local machine
  docker pull ghcr.io/your-org/your-repo/api:latest
  # Should succeed
  ```

- [ ] **Namespaces created**
  ```bash
  kubectl get namespaces
  # staging and prod should exist
  ```

### Domain & DNS

- [ ] **Domain purchased**
  - Active registration
  - Not expiring within 30 days

- [ ] **DNS A records created**
  ```bash
  dig api.yourdomain.com
  # Should return your load balancer IP
  ```

- [ ] **DNS propagation complete**
  ```bash
  # Check from multiple locations
  nslookup api.yourdomain.com 8.8.8.8  # Google DNS
  nslookup api.yourdomain.com 1.1.1.1  # Cloudflare DNS
  ```

### Load Balancer & TLS

- [ ] **Load balancer IP is known**
  ```bash
  kubectl get svc -n ingress-nginx  # or traefik namespace
  # EXTERNAL-IP should show IP or hostname
  ```

- [ ] **Port 443 is open**
  ```bash
  # From external machine
  nmap -p 443 api.yourdomain.com
  # Should show: 443/tcp open https
  ```

- [ ] **TLS certificate strategy confirmed**
  - Let's Encrypt (auto) via Traefik/cert-manager
  - Or custom certificate uploaded to load balancer

---

## CI/CD Checklist

### GitHub/GitLab Configuration

- [ ] **GitHub Environments configured**
  ```
  Repository Settings → Environments
  - staging (with protection rules)
  - production (with protection rules + required reviewers)
  ```

- [ ] **Environment Secrets set**
  ```
  staging environment:
  - SECRET_KEY
  - POSTGRES_PASSWORD
  - FIRST_SUPERUSER_PASSWORD
  - SMTP_PASSWORD
  - SENTRY_DSN
  
  production environment:
  - Same keys, different values
  ```

- [ ] **KUBECONFIG in repository secrets**
  ```bash
  # Base64-encoded kubeconfig
  cat ~/.kube/config | base64 | head -c 100
  # Verify exists in: Settings → Secrets and variables → Actions
  ```

### Pipeline

- [ ] **CI passes on main branch**
  ```bash
  # Check latest run
  # GitHub: Actions tab → All workflows
  # All checks should be green
  ```

- [ ] **Image builds successfully**
  ```bash
  make image-build
  # Or verify in CI logs
  ```

- [ ] **Image pushes to registry**
  ```bash
  # Verify in GHCR/ECR/GCR
  # Tag should match commit SHA or latest
  ```

- [ ] **Staging deployment works from CI**
  ```bash
  # Push to main, watch Actions
  # Should deploy to staging automatically
  ```

---

## Observability Checklist

### Error Tracking

- [ ] **Sentry project created**
  - Project exists at sentry.io
  - DSN configured in environment secrets
  - Release tracking enabled

- [ ] **Alerts configured**
  - Error rate spike notification
  - New issue notification
  - Assigned to on-call engineer

### Logging

- [ ] **Structured logging enabled**
  - JSON format in production
  - Correlation IDs on requests
  - Sensitive data redaction

- [ ] **Logs aggregating**
  - CloudWatch, Datadog, or self-hosted
  - Query interface accessible to team
  - Retention period defined (e.g., 30 days)

### Health Checks

- [ ] **External services are reachable from this environment**
  ```bash
  make smoke-external
  ```
  Read-only, secret-safe connectivity check for whatever this deployment's
  `.env` configures (database, SMTP, Sentry). Fails fast with `OK` / `FAILED`
  / `not configured (skipped)` per service and a non-zero exit code if any
  *configured* service is unreachable — run it before cutting over traffic
  to catch a misconfigured `.env` early.

- [ ] **Health endpoint responds**
  ```bash
  curl http://localhost:8000/api/v1/utils/health-check/
  # Should return: {"status":"ok"}
  ```

- [ ] **Readiness probe configured**
  - Checks database connectivity
  - Returns 200 when ready for traffic
  - Kubernetes uses for rolling updates

- [ ] **Liveness probe configured**
  - Returns 200 while app running
  - Triggers restart if failing

---

## Documentation Checklist

- [ ] **Incident response runbook exists**
  - File: `docs/operations/runbooks/incident-response.md` or similar
  - Contains: escalation paths, first-response steps

- [ ] **Rollback procedure documented**
  - File: `docs/operations/runbooks/rollback.md`
  - Contains: exact commands, decision criteria

- [ ] **Database recovery procedure documented**
  - File: `docs/operations/runbooks/database-recovery.md`
  - Contains: backup locations, restore commands

- [ ] **Team knows how to access logs**
  - Everyone has access to logging system
  - Knows how to filter by pod, time, severity

- [ ] **Deployment procedure reviewed by team**
  - Runbook walkthrough completed
  - Questions answered
  - Shadow deployment completed (if new team member)

---

## Final Verification (Staging)

Before first production deployment, verify on staging:

### Functionality

- [ ] **User registration works**
  ```bash
  curl -X POST https://staging.yourdomain.com/api/v1/users/signup \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"testpass123","full_name":"Test"}'
  # Should return 200 with user object
  ```

- [ ] **Login returns valid JWT**
  ```bash
  curl -X POST https://staging.yourdomain.com/api/v1/login/access-token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test@example.com&password=testpass123"
  # Should return: {"access_token":"eyJ...","token_type":"bearer"}
  ```

- [ ] **Authenticated requests succeed**
  ```bash
  curl https://staging.yourdomain.com/api/v1/users/me \
    -H "Authorization: Bearer <token>"
  # Should return current user object
  ```

- [ ] **Primary entity CRUD works**
  - Create resource
  - List resources  
  - Update resource
  - Delete resource

- [ ] **Password reset email sent** (if email enabled)
  - Request password reset
  - Verify email received in inbox
  - Reset link works

### Performance

- [ ] **Response time acceptable**
  ```bash
  # Most requests < 500ms p95
  curl -w "@curl-format.txt" https://staging.yourdomain.com/api/v1/utils/health-check/
  ```

- [ ] **Database queries optimized**
  - No N+1 queries
  - Indexes used for filtering
  - Slow query log reviewed

### Security

- [ ] **TLS certificate valid**
  ```bash
  openssl s_client -connect staging.yourdomain.com:443 -servername staging.yourdomain.com
  # Should show: Verification: OK
  ```

- [ ] **CORS headers correct**
  ```bash
  curl -I https://staging.yourdomain.com/api/v1/utils/health-check/ \
    -H "Origin: https://app.staging.yourdomain.com"
  # Should show: Access-Control-Allow-Origin: https://app.staging.yourdomain.com
  ```

---

## Quick Reference: One-Line Checks

```bash
# All checks in one command (after make target exists)
make pre-deploy-check ENV=staging

# Or individual checks:
make lint && make test                    # CI validation
docker pull ghcr.io/org/repo:latest       # Registry access
kubectl get nodes                         # Cluster health
dig api.yourdomain.com                    # DNS resolution
psql $DATABASE_URL -c "SELECT 1"        # Database connection
kubectl get secret api-secrets -n prod   # Secrets exist
curl -f https://api.yourdomain.com/api/v1/utils/health-check/  # App health
```

---

## Sign-Off

Before deploying to production, obtain sign-off from:

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Engineering Lead | | | |
| DevOps/SRE (if applicable) | | | |
| Product Owner (if major release) | | | |

**By signing, you confirm:**
- All checklist items verified
- Staging deployment tested
- Rollback plan understood
- Team ready to monitor post-deploy

---

## Post-Deployment Verification

After production deployment, run these checks:

- [ ] Health check returns 200
- [ ] Error rate at baseline (check Sentry)
- [ ] Can register new user
- [ ] Can login and access authenticated endpoints
- [ ] Logs flowing without errors
- [ ] Database connections stable
- [ ] Monitoring dashboards green

---

## Troubleshooting Checklist Failures

### "Secrets in Git" failure
```bash
# Check what was found
truffleHog filesystem . --json

# If false positive, add to . trufflehogignore
# If real secret, rotate immediately
```

### "Database connection refused"
- Check firewall/security groups
- Verify credentials in secrets
- Confirm SSL mode (try `sslmode=require`)
- Check if database instance is running

### "DNS not resolving"
- Check A record points to correct IP
- Wait for propagation (up to 48 hours)
- Verify with multiple DNS servers
- Check domain hasn't expired

### "Health check failing"
- Check pod logs: `kubectl logs -n prod deployment/api`
- Verify database connectivity
- Check environment variables set correctly
- Ensure migrations applied

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `docs/procedures/cloud-deployment-setup.md` | Full setup procedure |
| `docs/operations/deployment.md` | Deployment procedures |
| `docs/operations/runbooks/rollback.md` | Emergency rollback |
| `scripts/pre_deploy_check.py` | Automated validation |

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-05-17 | Initial pre-deploy checklist | Template |
