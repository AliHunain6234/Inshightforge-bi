# InsightForge BI

InsightForge is a capstone project (Aptura Tech Solutions internship, week 4) that demonstrates an end-to-end business-intelligence and predictive-analytics workflow: a secure login, an executive dashboard with KPIs, and a transparent **customer churn-risk** queue that explains why each customer is flagged.

## What it does

- **Secure sign-in:** salted PBKDF2-HMAC-SHA256 passwords (310,000 iterations), timing-safe comparison, signed short-lived session cookies and a login rate limit (8 attempts per window per address).
- **Role-based access:** the dashboard is for any signed-in user, the churn-risk queue for analysts and admins, and the audit log for admins only.
- **Executive dashboard:** governed KPIs and breakdowns computed from the database (`insightforge/analytics.py`).
- **Explainable churn risk:** a transparent scoring rule (not a black box) that ranks customers by risk and shows the reasons.
- **Audit log:** logins and other security events are recorded.
- **No dependencies:** the app runs on the Python 3.11+ standard library only (a threaded HTTP server, SQLite, plain HTML, CSS and JavaScript).
- **Synthetic demo data:** `python run.py --seed` creates 720 customers and 8,640 sales records so the dashboard has something to show.

## Quick start

```powershell
python run.py --seed
python run.py
```

Open `http://127.0.0.1:8080`. Demo credentials: `admin@example.com` / `change-me-password`.

## Test

```powershell
python -m unittest discover -s tests -v
```

## Security note

The demo password is for local evaluation only. Set `APP_SECRET`, change the seeded password, use TLS, and move secrets to a managed vault before deployment.

## API

All responses are JSON; errors look like `{"error": {"code": "STABLE_CODE", "message": "..."}}`.

| Method | Endpoint | Who | Purpose |
|---|---|---|---|
| GET | `/api/health` | Public | Liveness and version |
| POST | `/api/auth/login` | Public | Log in and receive a signed cookie |
| POST | `/api/auth/logout` | Any | End the session |
| GET | `/api/me` | Signed in | Current user |
| GET | `/api/dashboard` | Signed in | KPIs and breakdowns |
| GET | `/api/predictions` | Analyst, admin | Churn-risk queue with reasons |
| GET | `/api/audit` | Admin | Recent audit events |

## Architecture

Browser UI -> threaded HTTP/API layer -> security and role checks -> analytics service -> SQLite. Each module has one job: `security.py` (passwords and sessions), `db.py` (storage), `analytics.py` (KPIs and risk score), `server.py` (HTTP), `static/` (the interface). The diagrams in `diagrams/` show the current design, a redesign for a million users, and the analytics flow; the written version is in `docs/ARCHITECTURE.md`.

## Tests

7 automated tests pass (unit tests for passwords, sessions, KPIs and risk ordering; integration tests for health, unauthorised access, login, the session cookie and the dashboard). The notes are in `docs/TEST_REPORT.md`.

## Status and limitations

- SQLite and in-process rate limiting suit a demo or a single server, not a distributed production system.
- The churn score is a transparent reference rule, **not trained on real labelled customer history**. Calibration, fairness and drift checks are needed before any real decision depends on it.
- The data is synthetic, so it cannot show real business outcomes.
- The demo runs over plain HTTP; production needs TLS, an identity provider, MFA and secret rotation. More detail is in `docs/KNOWN_LIMITATIONS.md`, `docs/SECURITY.md` and `docs/DEPLOYMENT.md`.

## Structure

- `insightforge/`: modular application, data, security, analytics, and HTTP layers
- `static/`: responsive dashboard UI
- `tests/`: unit and integration tests
- `docs/`: architecture, API, deployment, security, limitations, and test evidence
