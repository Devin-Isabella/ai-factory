# Tails backend logs to logs\backend.log (stop with Ctrl+C when run in foreground)
$ErrorActionPreference = "Stop"
New-Item -ItemType File -Force -Path .\logs\backend.log | Out-Null
docker compose logs -f backend | Tee-Object -FilePath .\logs\backend.log -Append
