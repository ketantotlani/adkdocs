#!/usr/bin/env bash
set -e

export OLLAMA_API_BASE="${OLLAMA_API_BASE:-http://localhost:11434}"

mkdir -p .adk/artifacts

adk web \
  --session_service_uri "sqlite:///./.adk/sessions.db" \
  --artifact_service_uri "file://./.adk/artifacts" \
  --memory_service_uri "memory://" \
  .
