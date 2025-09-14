# watch.ps1 — lightweight watchdog for your backend container

param(
  [string]$HealthUrl = "http://localhost:8000/health",
  [string]$OpenApiUrl = "http://localhost:8000/openapi.json",
  [string]$ComposeSvc = "backend",
  [int]$PollSeconds = 10,
  [int]$RestartCooldownSeconds = 60,
  [string]$LogDir = ".\watch-logs"
)

$ErrorActionPreference = "SilentlyContinue"
$logFile = Join-Path $LogDir ("watch-{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))
"--- starting watcher at {0} ---" -f (Get-Date) | Out-File -FilePath $logFile -Append

function Log([string]$msg) {
  ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $msg) | Tee-Object -FilePath $logFile -Append
}

function Get-Ok([string]$url) {
  try { Invoke-RestMethod -Uri $url -TimeoutSec 5 -Method Get | Out-Null; return $true }
  catch { return $false }
}

function Is-Healthy([string]$url) {
  try {
    $r = Invoke-RestMethod -Uri $url -TimeoutSec 5 -Method Get
    if ($r -and $r.status -eq "ok") { return $true }
    return $false
  } catch { return $false }
}

$lastRestart = Get-Date "2000-01-01"
function Maybe-Restart([string]$svc) {
  $since = (New-TimeSpan -Start $lastRestart -End (Get-Date)).TotalSeconds
  if ($since -lt $RestartCooldownSeconds) {
    Log ("skip restart (cooldown: {0}s < {1}s)" -f ([int]$since), $RestartCooldownSeconds)
    return
  }
  Log "restarting docker compose service '$svc'..."
  try {
    docker compose restart $svc | Out-Null
    $global:lastRestart = Get-Date
    Start-Sleep -Seconds 5
  } catch {
    Log ("restart failed: {0}" -f $_.Exception.Message)
  }
}

while ($true) {
  $healthy = Is-Healthy $HealthUrl
  if (-not $healthy) {
    Log "unhealthy /health; attempting restart"
    Maybe-Restart $ComposeSvc
    Start-Sleep -Seconds $PollSeconds
    continue
  }

  $openapiOk = Get-Ok $OpenApiUrl
  if (-not $openapiOk) {
    Log "openapi check failed; attempting restart"
    Maybe-Restart $ComposeSvc
    Start-Sleep -Seconds $PollSeconds
    continue
  }

  Start-Sleep -Seconds $PollSeconds
}

