# Deployment and implementation plan

1. Provision isolated dev/staging/production environments using infrastructure as code.
2. Replace SQLite with managed PostgreSQL and configure migrations, backups, TLS, and least-privilege service identities.
3. Store application secrets in a managed vault; never use the demo secret or credentials.
4. Build an immutable container, generate an SBOM, scan dependencies and image, sign it, then promote the same artifact.
5. Run unit, integration, security, accessibility, and load gates in CI. Require review and protected branches.
6. Deploy canary or blue/green behind a WAF/load balancer. Validate health, error rate, latency, and business KPIs before promotion.
7. Configure dashboards, traces, audit retention, alert ownership, incident runbooks, and rollback.

Local smoke test: seed the database, start the server, verify `/api/health`, authenticate, load the dashboard, predictions, and audit pages, then run the complete test suite.
