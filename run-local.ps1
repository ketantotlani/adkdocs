$env:OLLAMA_API_BASE = "http://localhost:11434"

New-Item -ItemType Directory -Force -Path ".adk\artifacts" | Out-Null

adk web `
  --session_service_uri "sqlite:///./.adk/sessions.db" `
  --artifact_service_uri "file://./.adk/artifacts" `
  --memory_service_uri "memory://" `
  .
