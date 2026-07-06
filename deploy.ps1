# deploy.ps1 - NetMikuji
# Uso: powershell -ExecutionPolicy Bypass -File ".\deploy.ps1"

Write-Host "=== NetMikuji Deploy ===" -ForegroundColor Cyan

$dataDir = "docs\data"
if (-not (Test-Path $dataDir)) {
    Write-Host "AVISO: pasta $dataDir nao existe. Execute o scraper primeiro." -ForegroundColor Yellow
} else {
    $jsons = Get-ChildItem "$dataDir\*.json" -ErrorAction SilentlyContinue
    if ($jsons.Count -eq 0) {
        Write-Host "AVISO: nenhum JSON encontrado." -ForegroundColor Yellow
    } else {
        Write-Host "Dados: $($jsons.Count) arquivo(s) JSON" -ForegroundColor Green
    }
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git add docs/ scrape_mizuho.py update.py validate.py deploy.ps1 README.md CHANGELOG.md
git status --short

$commitMsg = "deploy: NetMikuji [$timestamp]"
git commit -m $commitMsg

if ($LASTEXITCODE -eq 0) {
    git push origin main
    Write-Host "Deploy concluido: $commitMsg" -ForegroundColor Green
} else {
    Write-Host "Nenhuma alteracao para commitar." -ForegroundColor Gray
}
