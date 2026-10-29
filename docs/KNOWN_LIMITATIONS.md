# Known limitations

- SQLite and in-process throttling are suitable for evaluation and single-node deployments, not distributed production.
- The reference score is transparent and directionally validated but is not trained against a real organization's labeled history; calibration, fairness, drift, and outcome monitoring are required before consequential use.
- Seed data is synthetic and cannot demonstrate real causal business outcomes.
- The local demo uses HTTP and a documented evaluator account. Production requires TLS, an identity provider, MFA, and secret rotation.
- The UI uses compact native charts to avoid runtime dependencies; enterprise deployment should add accessible chart descriptions, localization, and broader browser/device testing.
- Audit retention is local and finite; production should stream append-only events to a governed SIEM/object store.
