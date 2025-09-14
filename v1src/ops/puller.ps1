param(
  [int]$IntervalSeconds = 180
)
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path
Set-Location $repo

$logDir = Join-Path $repo "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir "puller.log"
$statusFile = Join-Path $logDir "status.json"

function Write-Status($stage,$ok,$extra){
  $obj = [ordered]@{
    ts    = (Get-Date).ToString("s")
    stage = $stage
    ok    = [bool]$ok
  }
  if($extra){ $extra.GetEnumerator() | ForEach-Object { $obj[$_.Key]=$_.Value } }
  ($obj | ConvertTo-Json -Depth 6) | Set-Content $statusFile -Encoding UTF8
}

function Health-OK{
  param([string]$Api="http://localhost:8000",[int]$Timeout=60)
  $deadline=(Get-Date).AddSeconds($Timeout)
  while((Get-Date) -lt $deadline){
    try{
      $h = Invoke-RestMethod "$Api/health" -TimeoutSec 6
      if($h.status -eq 'ok'){ return $true }
    }catch{}
    Start-Sleep 2
  }
  return $false
}

"$((Get-Date).ToString('s')) puller: started (interval=$IntervalSeconds)" | Add-Content $logFile
Write-Status "start" $true @{}

while($true){
  try{
    Set-Location $repo
    git fetch origin 2>&1 | Tee-Object -FilePath $logFile -Append | Out-Null

    $local  = (git rev-parse HEAD).Trim()
    $remote = (git rev-parse origin/main).Trim()

    if($local -ne $remote){
      "$((Get-Date).ToString('s')) change detected: $local -> $remote" | Add-Content $logFile
      Write-Status "detected_change" $true @{ local=$local; remote=$remote }

      git pull --ff-only 2>&1 | Tee-Object -FilePath $logFile -Append | Out-Null
      Write-Status "pulled" $true @{ head=(git rev-parse HEAD).Trim() }

      docker compose build backend 2>&1 | Tee-Object -FilePath $logFile -Append | Out-Null
      docker compose up -d backend 2>&1 | Tee-Object -FilePath $logFile -Append | Out-Null

      if(Health-OK){
        Write-Status "health_ok" $true @{}
        "$((Get-Date).ToString('s')) backend healthy after pull" | Add-Content $logFile
      }else{
        Write-Status "health_fail" $false @{ note="backend /health not ok" }
        "$((Get-Date).ToString('s')) backend health failed" | Add-Content $logFile
      }
    }
  }catch{
    $msg=$_.Exception.Message
    Write-Status "error" $false @{ error=$msg }
    "$((Get-Date).ToString('s')) ERROR: $msg" | Add-Content $logFile
  }
  Start-Sleep -Seconds $IntervalSeconds
}
