# ==============================================================================
# Script de despliegue ALL-IN-ONE para BookStore Microservices
# ==============================================================================
# Requisitos: Docker Desktop con Kubernetes habilitado O Minikube instalado
# Ejecutar desde la raíz del proyecto: .\deploy.ps1
# ==============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BookStore Microservices - Deploy Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Detectar si estamos en Docker Desktop o Minikube
$K8S_CONTEXT = kubectl config current-context
Write-Host "🔍 Contexto k8s actual: $K8S_CONTEXT" -ForegroundColor Yellow

if ($K8S_CONTEXT -like "*docker-desktop*") {
    Write-Host "✅ Usando Docker Desktop Kubernetes" -ForegroundColor Green
    $USE_MINIKUBE = $false
} elseif ($K8S_CONTEXT -like "*minikube*") {
    Write-Host "✅ Usando Minikube" -ForegroundColor Green
    $USE_MINIKUBE = $true
    # Configurar Docker para usar el daemon de Minikube
    Write-Host "⚙️  Configurando Docker para usar Minikube daemon..." -ForegroundColor Yellow
    & minikube -p minikube docker-env --shell powershell | Invoke-Expression
} else {
    Write-Host "❌ No se detectó Docker Desktop ni Minikube. Abortando." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Paso 1/5: Construyendo imágenes Docker..." -ForegroundColor Cyan
Write-Host "---------------------------------------------" -ForegroundColor Cyan

docker build -t bookstore-auth-service:latest ./auth-service
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Error construyendo auth-service" -ForegroundColor Red; exit 1 }

docker build -t bookstore-catalog-service:latest ./catalog-service
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Error construyendo catalog-service" -ForegroundColor Red; exit 1 }

docker build -t bookstore-orders-service:latest ./orders-service
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Error construyendo orders-service" -ForegroundColor Red; exit 1 }

Write-Host "✅ Imágenes construidas exitosamente" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Paso 2/5: Desplegando MySQL..." -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
kubectl apply -f k8s/mysql.yaml
Write-Host "⏳ Esperando a que MySQL esté listo (esto puede tomar 30-60s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Esperar a que MySQL esté ready
$max_attempts = 30
$attempt = 0
while ($attempt -lt $max_attempts) {
    $ready = kubectl get pods -l app=mysql -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>$null
    if ($ready -eq "True") {
        Write-Host "✅ MySQL está listo" -ForegroundColor Green
        break
    }
    $attempt++
    Write-Host "⏳ Esperando MySQL... intento $attempt/$max_attempts" -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

if ($attempt -eq $max_attempts) {
    Write-Host "⚠️  MySQL tomó más tiempo de lo esperado, continuando de todos modos..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Paso 3/5: Desplegando microservicios..." -ForegroundColor Cyan
Write-Host "-------------------------------------------" -ForegroundColor Cyan
kubectl apply -f k8s/auth-service.yaml
kubectl apply -f k8s/catalog-service.yaml
kubectl apply -f k8s/orders-service.yaml
Write-Host "✅ Manifests aplicados" -ForegroundColor Green
Write-Host ""

Write-Host "⏳ Paso 4/5: Esperando a que los servicios estén listos..." -ForegroundColor Cyan
Write-Host "-----------------------------------------------------------" -ForegroundColor Cyan
Start-Sleep -Seconds 5

kubectl rollout status deployment/auth-service --timeout=120s
kubectl rollout status deployment/catalog-service --timeout=120s
kubectl rollout status deployment/orders-service --timeout=120s

Write-Host "✅ Todos los deployments están listos" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Paso 5/5: Estado del cluster" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan
kubectl get pods -o wide
Write-Host ""
kubectl get services
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ DESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($USE_MINIKUBE) {
    $MINIKUBE_IP = minikube ip
    Write-Host "🌐 URLs de acceso (Minikube):" -ForegroundColor Cyan
    Write-Host "   Auth Service:    http://${MINIKUBE_IP}:30001" -ForegroundColor White
    Write-Host "   Catalog Service: http://${MINIKUBE_IP}:30002" -ForegroundColor White
    Write-Host "   Orders Service:  http://${MINIKUBE_IP}:30003" -ForegroundColor White
} else {
    Write-Host "🌐 URLs de acceso (Docker Desktop):" -ForegroundColor Cyan
    Write-Host "   Auth Service:    http://localhost:30001" -ForegroundColor White
    Write-Host "   Catalog Service: http://localhost:30002" -ForegroundColor White
    Write-Host "   Orders Service:  http://localhost:30003" -ForegroundColor White
}

Write-Host ""
Write-Host "🧪 Para ejecutar pruebas E2E:" -ForegroundColor Cyan
Write-Host "   python test_e2e.py" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Ver logs de un servicio:" -ForegroundColor Cyan
Write-Host "   kubectl logs -l app=auth-service -f" -ForegroundColor White
Write-Host ""
Write-Host "🗑️  Para eliminar todo:" -ForegroundColor Cyan
Write-Host "   kubectl delete -f k8s/" -ForegroundColor White
Write-Host ""
