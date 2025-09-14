param(
  [string]$RepoDir = (Resolve-Path "$PSScriptRoot\..").Path
)
Write-Host "🔧 Running Ruff lint/fix in $RepoDir..." -ForegroundColor Cyan
# If Python tools aren’t in the container, this is just a placeholder. Safe to re-run.
docker compose exec -T backend sh -lc "python -V 2>/dev/null || true"
# Run ruff inside the container if present; otherwise just print a note
docker compose exec -T backend sh -lc "ruff --version 2>/dev/null && ruff check --fix . || echo 'ruff not installed in image; skipping auto-fix.'"
