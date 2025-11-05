# Test del docker-compose localmente antes de subir a AWS
# Ejecutar en tu PC para verificar que todo funciona

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Docker Compose (Local)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/5] Deteniendo Kubernetes si está corriendo..." -ForegroundColor Yellow
try {
    kubectl delete deployments --all 2>$null
    kubectl delete services --all 2>$null
    Start-Sleep -Seconds 3
} catch {
    Write-Host "  (Kubernetes no estaba corriendo o no disponible)" -ForegroundColor Gray
}
Write-Host ""

Write-Host "[2/5] Verificando imágenes Docker..." -ForegroundColor Yellow
$images = @("bookstore-auth-service", "bookstore-catalog-service", "bookstore-orders-service")
$missingImages = @()

foreach ($img in $images) {
    $exists = docker images -q "${img}:latest"
    if ($exists) {
        Write-Host "  ✓ $img" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $img no encontrada" -ForegroundColor Red
        $missingImages += $img
    }
}

if ($missingImages.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠ Faltan imágenes. Construyendo..." -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($img in $missingImages) {
        $service = $img -replace "bookstore-", ""
        Write-Host "  Construyendo $service..." -ForegroundColor Cyan
        docker build -t "${img}:latest" "./${service}" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $img construida" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Error construyendo $img" -ForegroundColor Red
            exit 1
        }
    }
}
Write-Host ""

Write-Host "[3/5] Iniciando docker-compose..." -ForegroundColor Yellow
docker-compose down -v 2>$null
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Error iniciando docker-compose" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "[4/5] Esperando que los servicios estén listos..." -ForegroundColor Yellow
Write-Host "  (Esto puede tomar 30-60 segundos)" -ForegroundColor Gray
Write-Host ""

Start-Sleep -Seconds 10

$maxAttempts = 30
$attempt = 0
$allHealthy = $false

while ($attempt -lt $maxAttempts -and -not $allHealthy) {
    $attempt++
    Write-Host "  Intento $attempt/$maxAttempts..." -ForegroundColor Cyan
    
    try {
        $authHealth = Invoke-RestMethod -Uri "http://localhost:30001/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        $catalogHealth = Invoke-RestMethod -Uri "http://localhost:30002/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        $ordersHealth = Invoke-RestMethod -Uri "http://localhost:30003/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        
        if ($authHealth -and $catalogHealth -and $ordersHealth) {
            $allHealthy = $true
            Write-Host ""
            Write-Host "  ✓ Todos los servicios están saludables!" -ForegroundColor Green
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $allHealthy) {
    Write-Host ""
    Write-Host "✗ Servicios no respondieron a tiempo" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ver logs:" -ForegroundColor Yellow
    Write-Host "  docker-compose logs" -ForegroundColor Cyan
    exit 1
}
Write-Host ""

Write-Host "[5/5] Ejecutando pruebas E2E..." -ForegroundColor Yellow
python test_e2e.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  ✓ TODO FUNCIONA LOCALMENTE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Próximos pasos:" -ForegroundColor Yellow
    Write-Host "  1. Ejecuta: .\prepare-aws.ps1" -ForegroundColor White
    Write-Host "  2. Crea EC2 en AWS Academy" -ForegroundColor White
    Write-Host "  3. Sube archivos y despliega" -ForegroundColor White
    Write-Host "  4. Ver guía: DEPLOY_AWS_ACADEMY.md" -ForegroundColor White
    Write-Host ""
    Write-Host "Para detener los servicios locales:" -ForegroundColor Gray
    Write-Host "  docker-compose down" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "✗ Las pruebas E2E fallaron" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ver logs:" -ForegroundColor Yellow
    Write-Host "  docker-compose logs" -ForegroundColor Cyan
}
