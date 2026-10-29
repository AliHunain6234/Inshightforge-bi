# API contract

All API responses use JSON. Errors follow `{"error":{"code":"STABLE_CODE","message":"Safe message"}}`.

| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| GET | `/api/health` | Public | Liveness and version |
| POST | `/api/auth/login` | Public | Authenticate and issue signed cookie |
| POST | `/api/auth/logout` | Any | Expire session |
| GET | `/api/me` | Authenticated | Current identity |
| GET | `/api/dashboard` | Authenticated | Governed KPIs and dimensions |
| GET | `/api/predictions` | Analyst/Admin | Explainable churn-risk queue |
| GET | `/api/audit` | Admin | Recent audit evidence |
