# InsightForge BI

InsightForge is a production-style capstone demonstrating an end-to-end business intelligence and predictive analytics workflow. It includes secure authentication, role-based access, an executive dashboard, governed CSV ingestion, KPI APIs, a transparent churn-risk model, audit logging, tests, diagrams, deployment guidance, and a polished report.

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

## Structure

- `insightforge/`: modular application, data, security, analytics, and HTTP layers
- `static/`: responsive dashboard UI
- `tests/`: unit and integration tests
- `docs/`: architecture, API, deployment, security, limitations, and test evidence
