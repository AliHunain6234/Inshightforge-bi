# Architecture

## Current reference architecture

Browser UI -> threaded HTTP/API layer -> security/RBAC middleware -> analytics service -> repository/SQLite. Cross-cutting controls include structured errors, audit logging, rate limiting, indexed queries, deterministic data generation, and automated tests.

The modules are intentionally separated: `security.py` owns credentials and sessions; `db.py` owns persistence; `analytics.py` owns KPI and risk calculations; `server.py` owns HTTP transport; `static/` owns presentation.

## Million-user / million-record redesign

Deploy the static UI behind a CDN and WAF. Route requests through a managed API gateway to stateless application containers across at least three availability zones. Store operational data in PostgreSQL with read replicas, connection pooling, partitioned fact tables, row-level access controls, encryption, point-in-time recovery, and automated failover. Cache hot aggregate queries and sessions in a highly available Redis cluster.

Use an event bus (Kafka/Kinesis/PubSub) for ingestion, an object-store lakehouse for immutable raw data, Spark/dbt for governed transformations, a columnar warehouse for BI, and a feature store/model registry for ML parity. Serve predictions asynchronously for bulk scoring and through autoscaled inference services for real-time scoring. Add OpenTelemetry, centralized logs, SLO-based alerts, secrets management, key rotation, network segmentation, backup restoration drills, and blue/green deployment.

Availability target: multi-AZ 99.9% initially, multi-region active/passive for recovery, RPO <= 5 minutes and RTO <= 30 minutes. Maintainability comes from bounded modules/services, schema contracts, migrations, CI quality gates, infrastructure as code, ownership metadata, and backward-compatible APIs.
