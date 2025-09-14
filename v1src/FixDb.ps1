function Fix-DbDeps {
  Write-Host "📦 Installing SQLAlchemy + psycopg2 into backend..." -ForegroundColor Yellow
  docker compose exec -T backend pip install --no-cache-dir sqlalchemy psycopg2-binary
  Write-Host "✅ Dependencies installed" -ForegroundColor Green
}

Fix-DbDeps
Write-Host "`nDone." -ForegroundColor Cyan
