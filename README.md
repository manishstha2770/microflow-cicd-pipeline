# MicroFlow – Automated CI/CD Pipeline for Microservices

MicroFlow is a portfolio project for a small e-commerce system and its delivery pipeline. The planned demo runs from catalog browsing through checkout and simulated payment, with build, quality, security, deployment, and observability evidence.

**Current milestone** — Phase 1 repository and architecture baseline. See [project status](PROJECT_STATUS.md) for verification and [the roadmap](docs/roadmap.md) for implementation gates.

## Repository guide

| Path | Purpose |
| --- | --- |
| [services/](services/README.md) | Reserved roots for the four domain services and FastAPI gateway |
| [frontend/](frontend/README.md) | React dashboard and its independent image |
| [tests/integration/](tests/integration/README.md) | Cross-service and checkout tests |
| [kubernetes/](kubernetes/README.md) | Native Kubernetes manifests |
| [security/](security/README.md) | Threat model and security documentation |
| [scripts/](scripts/README.md) | Project automation |
| [helm/](helm/README.md) | Workload releases, Kubernetes resources, and environment values |
| [terraform/](terraform/README.md) | Azure infrastructure and state configuration |
| [jenkins/](jenkins/README.md) | Jenkins support scripts and quality gates |
| [monitoring/](monitoring/README.md) | Metrics, dashboards, and logging configuration |
| [setup.sh](setup.sh) | Checks installed tools, including the Docker Desktop CLI fallback |
| [Makefile](Makefile) | Runs the setup audit and baseline tests |
| [.env.example](.env.example) | Documents local settings with blank secret values |
| [.gitignore](.gitignore) | Excludes local credentials, state, dependencies, and build outputs |

[Architecture and diagrams](docs/architecture.md) · [macOS tool inventory](docs/local-environment.md) · [Implementation roadmap](docs/roadmap.md)

The planned GitHub repository name is `microflow-cicd`. Phase 3 adds the root `docker-compose.yml`. Phase 5 adds the root `Jenkinsfile`. Phase 6 adds `main.tf`, `variables.tf`, and `outputs.tf` under `terraform/`. Phase 7 adds the root `SECURITY.md`.

## Verify the Phase 1 baseline

Run from the repository root.

```sh
make setup
make test
git status --short
```

## Run the microservice baseline

```sh
docker compose build
docker compose up
```

Open `http://localhost:8080` for the storefront and `http://localhost:8000/docs` only with local port forwarding if the gateway is exposed.
