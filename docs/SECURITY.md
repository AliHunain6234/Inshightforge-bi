# Security

Implemented controls: salted PBKDF2-HMAC-SHA256 passwords (310,000 iterations), timing-safe comparison, short-lived signed sessions, HttpOnly/SameSite cookies, endpoint RBAC, generic authentication failures, IP login throttling, parameterized SQL, request-size limits, path traversal defense, CSP and browser hardening headers, safe structured errors, and audit events.

Production additions: TLS/HSTS, CSRF tokens for state-changing authenticated operations, external identity provider with MFA, managed WAF/rate limiter, secret vault and rotation, database row-level security, encrypted backups, SIEM export, dependency/SAST/DAST scanning, privacy classification, retention/deletion policy, and independent penetration testing.
