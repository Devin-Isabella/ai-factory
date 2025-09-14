$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path
Set-Location $root

Write-Host "🚀 Bringing up backend (and db if defined)..." -ForegroundColor Cyan
docker compose up -d

# Wait for health
$api="http://localhost:8000"
$deadline=(Get-Date).AddSeconds(120); $ok=$false
while((Get-Date) -lt $deadline){
  try{ if((Invoke-RestMethod "$api/health" -TimeoutSec 6).status -eq "ok"){ $ok=$true; break } }catch{}
  Start-Sleep 3
}
if($ok){ Write-Host "✅ Backend /health OK" -ForegroundColor Green } else { Write-Host "⚠️  Backend not healthy yet" -ForegroundColor Yellow }

# Start background puller (idempotent)
$job = Get-Job -Name puller -ErrorAction SilentlyContinue
if($job){ Stop-Job $job -ErrorAction SilentlyContinue; Remove-Job $job -ErrorAction SilentlyContinue }

$script = Join-Path (Join-Path $root "ops") "puller.ps1"
Start-Job -Name puller -FilePath $script -ArgumentList 180 | Out-Null
Write-Host "🧭 Puller job started (job name: puller). View logs at .\logs\puller.log" -ForegroundColor Green
