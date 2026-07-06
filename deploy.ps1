# deploy.ps1
# Faz build e push para GitHub Pages (branch main, pasta docs/)
# Uso: powershell -ExecutionPolicy Bypass -File ".\deploy.ps1"

Write-Host "=== Loto PWA Deploy ===" -ForegroundColor Cyan

# Verifica se há arquivos de dados
$dataDir = "docs\data"
if (-not (Test-Path $dataDir)) {
    Write-Host "AVISO: pasta $dataDir não existe. Execute o scraper primeiro:" -ForegroundColor Yellow
    Write-Host "  cd scraper && pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host "  python scrape_mizuho.py" -ForegroundColor Yellow
}

# Git add, commit e push
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git add docs/ scraper/ deploy.ps1 README.md CHANGELOG.md 2>$null
git status --short

$commitMsg = "deploy: atualiza PWA e dados [$timestamp]"
git commit -m $commitMsg

if ($LASTEXITCODE -eq 0) {
    git push origin main
    Write-Host "`n✓ Deploy concluído: $commitMsg" -ForegroundColor Green
} else {
    Write-Host "`nNenhuma alteração para commitar." -ForegroundColor Gray
}
