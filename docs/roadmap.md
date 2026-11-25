# Implementation roadmap

| Phase | Deliverables | Verification before completion |
| --- | --- | --- |
| 1 · Environment setup | Tool audit, setup script, templates and repository | Run setup audit and foundation tests |
| 2 · Microservices | Five FastAPI apps, React, PostgreSQL, Redis, JWT, seed data and pytest | Run unit and integration tests and verify Swagger and simulated checkout |
| 3 · Docker containerization | Multi-stage Dockerfiles, Compose, non-root workloads and local runbook | Build and start Compose and verify health, persistence and browser API calls |
| 4 · Local Kubernetes deployment | Native manifests, ingress, PVCs, probes, HPA and disruption budgets | Verify local discovery, access, and replacement of a test pod with approval |
| 5 · Jenkins CI/CD | Declarative Jenkinsfile, local Jenkins, GitHub webhook guide, SHA tags and all requested delivery stages | Exercise quality and scan gates, staging, approval, health verification and rollback |
| 6 · Terraform and Azure | Reusable Azure modules, example variables and cost and cleanup guide | Run format and validation locally and prepare an approval-gated deployment |
| 7 · DevSecOps | Security scans, SBOMs, RBAC, policies, restricted pods, Key Vault CSI and threat model | Test pipeline gates, workload restrictions and secret access in available environments |
| 8 · Monitoring and observability | Prometheus, Grafana, alerts, Loki and k6 | Check metrics, logs and alerts and demonstrate scale-out under controlled load |
| 9 · Helm and deployment automation | Reusable charts, three environment values files and Jenkins Helm deployment | Lint and render each environment and verify upgrades, history and rollback |
| 10 · Final testing and GitHub portfolio | Full review, publishing-ready README, resume summary and 20 implementation-based interview answers | Run regression and secret checks and record remaining limitations before publication approval |

Phase 2 starts after explicit approval. System-level installs, destructive actions, Azure provisioning and GitHub publication require explicit approval. Verify locally before any Azure deployment.

## Implementation conventions

- Start with Python 3.13 and Node 22 as local candidates. Resolve supported patch versions and commit lockfiles during Phase 2. Pin container bases and validate native ARM64 and AMD64 builds before publishing either platform.
- Each deployable owns its dependency lock, Dockerfile, health endpoints where applicable, and unit tests. Shared contracts define versioned API behavior. Repository-level integration tests exercise services over HTTP with real data stores.
- Jenkins tests pull requests and reports status to GitHub. Trusted branches build and scan each platform, publish immutable image manifests, deploy by digest, and archive test, scan and rollout evidence. Scope registry and deployment credentials to their stages.
