$env:OLLAMA_API_BASE = "http://localhost:11434"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ProjectRoot

try {
  New-Item -ItemType Directory -Force -Path ".adk\artifacts" | Out-Null
  $ResolvedArtifactPath = (Resolve-Path ".adk\artifacts").Path
  $ArtifactUri = ([System.Uri]$ResolvedArtifactPath).AbsoluteUri

  adk web `
    --session_service_uri "sqlite:///./.adk/sessions.db" `
    --artifact_service_uri $ArtifactUri `
    src
}
finally {
  Pop-Location
}
