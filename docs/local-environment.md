# macOS tool inventory

Checked on 2026-11-24 in the workspace PowerShell session.

| Tool | Observed |
| --- | --- |
| macOS | 26.6.2, arm64 |
| VS Code | 1.147.0 via the application bundle. The PATH shim failed |
| Git / GitHub CLI | Apple Git 2.50.1 / gh 2.102.0 |
| Python / uv | 3.13.5 (Miniconda) / 0.9.21 |
| Node / npm | 22.20.0 / 10.9.3 |
| Docker / Compose / Buildx | 29.8.2 / 5.6.0 / 0.37.2 via the Docker Desktop CLI. Daemon 29.8.2 responded after an approved read-only query |
| Azure CLI | 2.87.0 |
| Kubernetes and IaC | kubectl, Helm, kind, minikube and Terraform were unavailable on PATH |
| CI and quality | Jenkins, Trivy and sonar-scanner were unavailable on PATH. The macOS Java launcher could not locate a runtime |
| App and observability dependencies | Deferred to locked app dependencies and phase-specific containers |

Docker can be invoked through `/Applications/Docker.app/Contents/Resources/bin/docker`. Resolve shell PATH setup and validate a container build in Phase 2. Kubernetes and CI tools are introduced when their phases begin.

## Installation commands by phase

Run `make setup` from the repository root to check your current shell. The audit reports missing or failing tools and exits normally so you can see the full list. If the daemon check fails with a permission error, try it from your own terminal.

| When needed | Missing or optional tool | macOS command |
| --- | --- | --- |
| Phase 4 | kubectl | `brew install kubernetes-cli` |
| Phase 4 | Minikube, if using it for local Kubernetes | `brew install minikube` |
| Phase 5 | Jenkins LTS, optional host installation | `brew install jenkins-lts` |
| Phases 5 and 7 | Trivy | `brew install trivy` |
| Phases 5 and 7 | SonarScanner, optional host installation | `brew install sonar-scanner` |
| Phase 6 | Terraform | `brew tap hashicorp/tap`, then `brew install hashicorp/tap/terraform` |
| Phase 9 | Helm | `brew install helm` |

Choose a kubectl version compatible with the selected cluster. Jenkins and SonarQube are planned as local containers. The Homebrew Jenkins LTS formula includes an OpenJDK dependency for anyone choosing a host install. The existing Docker Desktop CLI works by absolute path. Add it to a Bash or Zsh session with `export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"`. For PowerShell use `$env:PATH = "/Applications/Docker.app/Contents/Resources/bin:" + $env:PATH`. To repair the VS Code CLI shim, use **Shell Command: Install 'code' command in PATH** from the VS Code Command Palette.

Installation references are available from [Homebrew Formulae](https://formulae.brew.sh/), [HashiCorp](https://developer.hashicorp.com/terraform/install), and [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/).
