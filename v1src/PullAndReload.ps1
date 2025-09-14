param(
  [int]$HealthWaitSec = 90,
  [string]$Api = "http://localhost:8000"
)

function Wait-Health([string]$u,[int]$sec){
  $deadline=(Get-Date).AddSeconds($sec)
  while((Get-Date) -lt $deadline){
    try{
      $h = Invoke-RestMethod "$u/health" -TimeoutSec 6
      if($h.status -eq "ok"){ return $true }
    }catch{}
    Start-Sleep 3
  }
  return $false
}

Write-Host "🔁 Git pull (fetch latest)..." -ForegroundColor Cyan
git fetch --all 2>$null | Out-Null
git status --porcelain=2 | Out-Null  # warm up
git pull --rebase --autostash

if($LASTEXITCODE -ne 0){
  Write-Host "⚠️  git pull reported issues. Attempting a clean rebase…" -ForegroundColor Yellow
  git rebase --abort 2>$null | Out-Null
  git stash push -u -m "autostash-before-pull" 2>$null | Out-Null
  git pull --rebase
}

Write-Host "🧹 Bringing stack down (ignore warnings about stopping containers)..." -ForegroundColor DarkCyan
docker compose down --remove-orphans 2>$null | Out-Null

Write-Host "🔨 Building images (incremental)..." -ForegroundColor Cyan
docker compose build

Write-Host "🚀 Starting services..." -ForegroundColor Cyan
docker compose up -d

Write-Host "⏳ Waiting for $Api/health ..." -ForegroundColor Cyan
if(-not (Wait-Health $Api $HealthWaitSec)){
  Write-Host "⚠️  Health not ready, restarting backend once and retrying..." -ForegroundColor Yellow
  docker compose restart backend | Out-Null
  if(-not (Wait-Health $Api $HealthWaitSec)){
    Write-Host "❌ Backend still not healthy. Showing last 200 log lines:" -ForegroundColor Red
    docker compose logs --no-log-prefix --tail 200 backend
    throw "Backend did not become healthy"
  }
}

Write-Host "✅ Pull & reload complete. Backend healthy." -ForegroundColor Green
