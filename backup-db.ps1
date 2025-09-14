param([string]\ = "C:\\Users\\devin\\ai-factory\\backups")
if(-not (Test-Path \)){ New-Item -ItemType Directory -Path \ | Out-Null }
\20250908154253 = Get-Date -Format 'yyyyMMdd-HHmmss'
\ = Join-Path \ ("ai_factory_\20250908154253.sql")
docker exec ai_factory_db bash -lc "pg_dump -U ai_factory -d ai_factory" | Out-File -FilePath \ -Encoding utf8
Write-Host ("Backup written: {0}" -f \)
