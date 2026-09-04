#!/usr/bin/env bash
set -e

export OLLAMA_API_BASE="${OLLAMA_API_BASE:-http://localhost:11434}"

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

mkdir -p .adk/artifacts
ARTIFACT_URI="$(python -c 'from pathlib import Path; print(Path(".adk/artifacts").resolve().as_uri())')"

adk web \
  --session_service_uri "sqlite:///./.adk/sessions.db" \
  --artifact_service_uri "$ARTIFACT_URI" \
  src
