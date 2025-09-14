# update-main.ps1 — opens the file in Notepad, or writes content if -Write is used
param([switch]$Write)

$path = "backend\app\main.py"
if ($Write) {
  @"
PUT YOUR FINAL main.py CONTENT HERE
"@ | Set-Content -Path $path -Encoding UTF8
  "✅ Wrote $path"
} else {
  notepad $path
}
