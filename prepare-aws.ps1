# Script para preparar el despliegue en AWS EC2
# Ejecutar en tu PC local ANTES de subir a EC2

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Preparar despliegue AWS EC2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Exportar imagenes Docker
Write-Host "[1/4] Exportando imagenes Docker..." -ForegroundColor Yellow
docker save bookstore-auth-service:latest -o auth-service.tar
docker save bookstore-catalog-service:latest -o catalog-service.tar
docker save bookstore-orders-service:latest -o orders-service.tar

Write-Host "OK - Imagenes exportadas" -ForegroundColor Green
Write-Host ""

# 2. Comprimir
Write-Host "[2/4] Comprimiendo archivos..." -ForegroundColor Yellow
if (Get-Command tar -ErrorAction SilentlyContinue) {
    tar -czf bookstore-images.tar.gz auth-service.tar catalog-service.tar orders-service.tar
    Write-Host "OK - Archivos comprimidos en bookstore-images.tar.gz" -ForegroundColor Green
} else {
    Write-Host "AVISO: tar no disponible. Sube los archivos .tar individuales" -ForegroundColor Yellow
}
Write-Host ""

# 3. Mostrar tamanos
Write-Host "[3/4] Tamanos de archivos:" -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.tar*" | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  $($_.Name): $sizeMB MB"
}
Write-Host ""

# 4. Instrucciones
Write-Host "[4/4] Proximos pasos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Crea una instancia EC2 t2.medium en AWS Academy" -ForegroundColor White
Write-Host "2. Configura Security Group con puertos: 22, 30001, 30002, 30003" -ForegroundColor White
Write-Host "3. Sube el archivo con SCP:" -ForegroundColor White
Write-Host ""
Write-Host '   scp -i "ruta\a\tu-key.pem" bookstore-images.tar.gz ec2-user@TU-IP-EC2:~' -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Conectate a EC2 y ejecuta:" -ForegroundColor White
Write-Host ""
Write-Host "   # Instalar Docker" -ForegroundColor Cyan
Write-Host "   sudo yum update -y && sudo yum install -y docker" -ForegroundColor Cyan
Write-Host "   sudo systemctl start docker" -ForegroundColor Cyan
Write-Host "   sudo usermod -a -G docker ec2-user" -ForegroundColor Cyan
Write-Host "   exit" -ForegroundColor Cyan
Write-Host ""
Write-Host "   # (Volver a conectar)" -ForegroundColor Cyan
Write-Host "   tar -xzf bookstore-images.tar.gz" -ForegroundColor Cyan
Write-Host "   docker load -i auth-service.tar" -ForegroundColor Cyan
Write-Host "   docker load -i catalog-service.tar" -ForegroundColor Cyan
Write-Host "   docker load -i orders-service.tar" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Sube docker-compose.yml y init-databases.sql" -ForegroundColor White
Write-Host ""
Write-Host '   scp -i "ruta\a\tu-key.pem" docker-compose.yml ec2-user@TU-IP-EC2:~' -ForegroundColor Cyan
Write-Host '   scp -i "ruta\a\tu-key.pem" init-databases.sql ec2-user@TU-IP-EC2:~' -ForegroundColor Cyan
Write-Host ""
Write-Host "6. En EC2, instala docker-compose y despliega:" -ForegroundColor White
Write-Host ""
Write-Host '   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose' -ForegroundColor Cyan
Write-Host "   sudo chmod +x /usr/local/bin/docker-compose" -ForegroundColor Cyan
Write-Host "   docker-compose up -d" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OK - Preparacion completa" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ver guia completa en: GUIA_AWS.md" -ForegroundColor Yellow
