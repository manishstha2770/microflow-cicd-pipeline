#!/usr/bin/env bash
# Report tool availability without installing packages or changing the host.
set -u

docker_desktop=/Applications/Docker.app/Contents/Resources/bin/docker
docker_cli=$(command -v docker || true)
if [[ -z "$docker_cli" && -x "$docker_desktop" ]]; then
    docker_cli=$docker_desktop
fi

probe() {
    local label=$1 output
    shift
    if [[ -z "$1" ]] || ! command -v "$1" >/dev/null 2>&1; then
        printf '%-18s %s\n' "$label" 'Unavailable'
    elif output=$("$@" 2>&1); then
        printf '%-18s %s\n' "$label" "${output%%$'\n'*}"
    else
        while [[ $output == $'\n'* ]]; do
            output=${output#$'\n'}
        done
        printf '%-18s %s\n' "$label" "Check failed (${output%%$'\n'*})"
    fi
}

printf 'MicroFlow environment check (%s %s)\n\n' "$(uname -s)" "$(uname -m)"
probe Git git --version
probe Python python3 --version
probe Node.js node --version
probe npm npm --version
probe Docker "$docker_cli" --version
probe 'Docker Compose' "$docker_cli" compose version
probe 'Docker daemon' "$docker_cli" version --format '{{.Server.Version}}'
probe kubectl kubectl version --client
probe Minikube minikube version
probe Helm helm version --short
probe Terraform terraform version
probe 'Azure CLI' az version --query '"azure-cli"' --output tsv
if command -v jenkins >/dev/null 2>&1; then
    probe Jenkins jenkins --version
else
    probe Jenkins jenkins-lts --version
fi
probe Trivy trivy --version
probe 'SonarScanner' sonar-scanner --version
probe Java java -version
printf '\nSee docs/local-environment.md for installation commands and phase requirements.\n'
