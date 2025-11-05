# 🚀 Guía Completa de Despliegue en AWS - Proyecto 2

**Universidad EAFIT - ST0263 Tópicos Especiales en Telemática 2025-2**

Esta guía cubre los **2 patrones de escalamiento** requeridos:
- ✅ **Patrón 1**: Escalamiento en Máquinas Virtuales (EC2 + Docker Compose)
- ✅ **Patrón 2**: Escalamiento en Cluster Kubernetes (AWS EKS)
- ✅ **Bonus**: Dominio con certificado SSL (`https://proyecto2.dominio.tld`)

**Tiempo total estimado**: 2 horas  
**Requisitos cumplidos**: 100% ✅

---

## 📋 Requisitos Previos

- ✅ Cuenta AWS Academy (Learner Lab) activa
- ✅ Docker Desktop instalado
- ✅ Python 3.x instalado
- ✅ kubectl instalado
- ✅ AWS CLI (lo instalaremos)
- ✅ eksctl (lo instalaremos)

---

# 🎯 PARTE 1: ESCALAMIENTO EN MÁQUINAS VIRTUALES

**Tiempo: 30 minutos**

Este patrón despliega los microservicios en una instancia EC2 con Docker Compose, permitiendo escalamiento horizontal agregando más VMs.

---

## 1.1 PREPARACIÓN LOCAL (5 min)

### Construir imágenes Docker

```powershell
cd BookStore-Microservices
.\deploy.ps1
```

### Exportar imágenes

```powershell
.\prepare-aws.ps1
```

Esto genera:
- `bookstore-images.tar.gz` (~400 MB)
- Listo para subir a EC2

---

## 1.2 CONFIGURAR AWS (10 min)

### Iniciar Learner Lab

1. AWS Academy → Learner Lab → **Start Lab**
2. Espera círculo verde ●
3. Click **"AWS"** → Consola

### Obtener credenciales CLI

1. **AWS Details** → **Show** (AWS CLI)
2. Copiar todo el bloque
3. Crear `C:\Users\TuUsuario\.aws\credentials` (Windows)
4. Pegar contenido

### Instalar AWS CLI

**Windows:**
```powershell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

**Linux/Mac:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Configurar región

```powershell
aws configure set default.region us-east-1
```

### Crear EC2

**AWS Console → EC2 → Launch Instance:**

| Campo | Valor |
|-------|-------|
| Name | `bookstore-vm-01` |
| AMI | Amazon Linux 2023 |
| Instance type | `t2.medium` |
| Key pair | Crear nuevo: `bookstore-key.pem` |
| Auto-assign public IP | Enable |
| Security Group | Crear: `bookstore-sg-vms` |

**Security Group Rules:**
- SSH (22) - My IP
- TCP (30001) - 0.0.0.0/0 (Auth)
- TCP (30002) - 0.0.0.0/0 (Catalog)
- TCP (30003) - 0.0.0.0/0 (Orders)
- HTTP (80) - 0.0.0.0/0
- HTTPS (443) - 0.0.0.0/0

**Storage**: 20 GB gp3

Anota la **Public IPv4**: `3.85.123.45`

---

## 1.3 DESPLEGAR EN EC2 (15 min)

### Dar permisos al .pem (Windows)

```powershell
icacls "C:\AWS\bookstore-key.pem" /inheritance:r
icacls "C:\AWS\bookstore-key.pem" /grant:r "$env:USERNAME`:R"
```

### Conectar y configurar

```powershell
ssh -i "C:\AWS\bookstore-key.pem" ec2-user@3.85.123.45
```

```bash
# Instalar Docker
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user
exit
```

### Subir archivos

```powershell
scp -i "C:\AWS\bookstore-key.pem" bookstore-images.tar.gz ec2-user@3.85.123.45:~
scp -i "C:\AWS\bookstore-key.pem" docker-compose.yml ec2-user@3.85.123.45:~
scp -i "C:\AWS\bookstore-key.pem" init-databases.sql ec2-user@3.85.123.45:~
```

### Desplegar

```powershell
ssh -i "C:\AWS\bookstore-key.pem" ec2-user@3.85.123.45
```

```bash
# Cargar imágenes
tar -xzf bookstore-images.tar.gz
docker load -i auth-service.tar
docker load -i catalog-service.tar
docker load -i orders-service.tar

# Instalar docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Desplegar
docker-compose up -d
docker-compose ps
```

### Probar

```powershell
python test_e2e.py aws 3.85.123.45
```

✅ **PARTE 1 COMPLETADA**

---

# 🎯 PARTE 2: ESCALAMIENTO EN KUBERNETES (EKS)

**Tiempo: 45 minutos**

Este patrón despliega en un cluster Kubernetes gestionado (EKS) con auto-escalamiento.

---

## 2.1 INSTALAR HERRAMIENTAS (5 min)

### eksctl

**Windows:**
```powershell
$url = "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_Windows_amd64.zip"
Invoke-WebRequest -Uri $url -OutFile "eksctl.zip"
Expand-Archive -Path "eksctl.zip" -DestinationPath "C:\Program Files\eksctl"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\eksctl", "Machine")
```

**Linux/Mac:**
```bash
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
```

Reinicia PowerShell y verifica:
```powershell
eksctl version
kubectl version --client
```

---

## 2.2 CREAR REPOSITORIOS ECR (5 min)

```powershell
aws ecr create-repository --repository-name bookstore-auth-service --region us-east-1
aws ecr create-repository --repository-name bookstore-catalog-service --region us-east-1
aws ecr create-repository --repository-name bookstore-orders-service --region us-east-1

# Ver repositorios
aws ecr describe-repositories --region us-east-1 --query 'repositories[*].[repositoryName,repositoryUri]' --output table
```

Anota el **Account ID** (ej: `123456789012`)

---

## 2.3 SUBIR IMÁGENES A ECR (10 min)

```powershell
# Reemplaza con tu Account ID
$ACCOUNT_ID = "123456789012"
$REGION = "us-east-1"
$ECR_URL = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

# Login
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URL

# Tag y push
docker tag bookstore-auth-service:latest $ECR_URL/bookstore-auth-service:latest
docker push $ECR_URL/bookstore-auth-service:latest

docker tag bookstore-catalog-service:latest $ECR_URL/bookstore-catalog-service:latest
docker push $ECR_URL/bookstore-catalog-service:latest

docker tag bookstore-orders-service:latest $ECR_URL/bookstore-orders-service:latest
docker push $ECR_URL/bookstore-orders-service:latest
```

---

## 2.4 CREAR CLUSTER EKS (15 min)

```powershell
eksctl create cluster `
  --name bookstore-cluster `
  --region us-east-1 `
  --nodegroup-name bookstore-nodes `
  --node-type t3.medium `
  --nodes 2 `
  --nodes-min 2 `
  --nodes-max 4 `
  --managed
```

**Nota**: Tarda 10-15 minutos ☕

Verificar:
```powershell
kubectl get nodes
# Debe mostrar 2 nodos Ready
```

---

## 2.5 ACTUALIZAR MANIFESTS (5 min)

```powershell
$ACCOUNT_ID = "123456789012"  # TU ACCOUNT ID
$REGION = "us-east-1"
$ECR_URL = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

# Actualizar imágenes
(Get-Content k8s\auth-service.yaml) -replace 'image: bookstore-auth-service:latest', "image: $ECR_URL/bookstore-auth-service:latest" -replace 'imagePullPolicy: Never', 'imagePullPolicy: Always' | Set-Content k8s\auth-service.yaml

(Get-Content k8s\catalog-service.yaml) -replace 'image: bookstore-catalog-service:latest', "image: $ECR_URL/bookstore-catalog-service:latest" -replace 'imagePullPolicy: Never', 'imagePullPolicy: Always' | Set-Content k8s\catalog-service.yaml

(Get-Content k8s\orders-service.yaml) -replace 'image: bookstore-orders-service:latest', "image: $ECR_URL/bookstore-orders-service:latest" -replace 'imagePullPolicy: Never', 'imagePullPolicy: Always' | Set-Content k8s\orders-service.yaml
```

---

## 2.6 DESPLEGAR EN EKS (5 min)

```powershell
kubectl apply -f k8s/mysql.yaml
kubectl apply -f k8s/auth-service.yaml
kubectl apply -f k8s/catalog-service.yaml
kubectl apply -f k8s/orders-service.yaml

# Esperar
kubectl get pods --watch
```

### Exponer con LoadBalancer

```powershell
kubectl patch service auth-service -p '{"spec":{"type":"LoadBalancer"}}'
kubectl patch service catalog-service -p '{"spec":{"type":"LoadBalancer"}}'
kubectl patch service orders-service -p '{"spec":{"type":"LoadBalancer"}}'

# Ver URLs (espera 2-3 min)
kubectl get services
```

### Probar

```powershell
kubectl get services

# Anota EXTERNAL-IP del auth-service
$AUTH_LB = "a1b2c3-123456.us-east-1.elb.amazonaws.com"

curl http://$AUTH_LB/health
```

✅ **PARTE 2 COMPLETADA**

---

# 🎯 PARTE 3: DOMINIO Y CERTIFICADO SSL

**Tiempo: 30 minutos**

---

## 3.1 OBTENER DOMINIO (5 min)

**Opción A - Freenom (gratis):**
1. https://www.freenom.com
2. Buscar: `bookstore-eafit.tk`
3. Registrar (12 meses gratis)

**Opción B - Route53 ($12/año):**
```powershell
aws route53domains register-domain --domain-name proyecto2-tugrupo.com
```

---

## 3.2 CONFIGURAR ROUTE53 (10 min)

### Crear Hosted Zone

```powershell
aws route53 create-hosted-zone --name proyecto2-tugrupo.tk --caller-reference $(Get-Date -Format "yyyyMMddHHmmss")
```

### Actualizar nameservers

1. Copia los 4 NS de Route53
2. En Freenom → Nameservers → Custom
3. Pega los 4 NS
4. Guarda

### Crear registros

```powershell
$HOSTED_ZONE_ID = "Z1234567890ABC"  # TU ZONE ID
$DOMAIN = "proyecto2-tugrupo.tk"
$AUTH_LB = "a1b2c3-123456.us-east-1.elb.amazonaws.com"  # TU LOADBALANCER

# auth subdomain
aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "auth.'$DOMAIN'",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{"Value": "'$AUTH_LB'"}]
    }
  }]
}'
```

Repite para `catalog` y `orders`.

---

## 3.3 CERTIFICADO SSL (10 min)

### Solicitar certificado

```powershell
aws acm request-certificate `
  --domain-name "*.$DOMAIN" `
  --subject-alternative-names "$DOMAIN" `
  --validation-method DNS `
  --region us-east-1
```

### Validar

1. AWS Console → Certificate Manager
2. Copia el registro CNAME de validación
3. Agrégalo en Route53
4. Espera 5-10 min hasta "Issued" ✅

---

## 3.4 CONFIGURAR INGRESS (10 min)

### Instalar ALB Controller

```powershell
# Descargar policy
curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.7.0/docs/install/iam_policy.json

# Crear policy
aws iam create-policy `
  --policy-name AWSLoadBalancerControllerIAMPolicy `
  --policy-document file://iam-policy.json

# Service account
eksctl create iamserviceaccount `
  --cluster=bookstore-cluster `
  --namespace=kube-system `
  --name=aws-load-balancer-controller `
  --attach-policy-arn=arn:aws:iam::$ACCOUNT_ID:policy/AWSLoadBalancerControllerIAMPolicy `
  --approve

# Instalar controller (necesitas Helm)
choco install kubernetes-helm  # Windows
# O descarga de: https://helm.sh

helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller `
  -n kube-system `
  --set clusterName=bookstore-cluster `
  --set serviceAccount.create=false `
  --set serviceAccount.name=aws-load-balancer-controller
```

### Crear Ingress con SSL

Crea `k8s/ingress-ssl.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bookstore-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:ACCOUNT-ID:certificate/CERT-ID
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
spec:
  rules:
  - host: auth.proyecto2-tugrupo.tk
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 80
  - host: catalog.proyecto2-tugrupo.tk
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: catalog-service
            port:
              number: 80
  - host: orders.proyecto2-tugrupo.tk
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: orders-service
            port:
              number: 80
```

Aplicar:
```powershell
kubectl apply -f k8s/ingress-ssl.yaml
```

### Probar

```powershell
curl https://auth.proyecto2-tugrupo.tk/health
```

✅ **PARTE 3 COMPLETADA**

---

# 📸 CAPTURAS PARA EL PROYECTO

## Escalamiento VMs:
1. AWS Console → EC2 → Instancia Running
2. SSH con `docker-compose ps`
3. Navegador: `http://IP:30001/health`

## Escalamiento Kubernetes:
4. AWS Console → EKS → Cluster
5. Terminal: `kubectl get pods`
6. Terminal: `kubectl get services`
7. Navegador: `https://auth.proyecto2.tk/health` (candado verde)

## Pruebas:
8. Output: `python test_e2e.py aws IP` (7/7 ✅)

---

# 🧹 LIMPIEZA

```powershell
# Eliminar servicios (libera LoadBalancers)
kubectl delete service auth-service catalog-service orders-service

# Eliminar cluster
eksctl delete cluster --name bookstore-cluster

# Terminar EC2
# AWS Console → EC2 → Terminate

# Eliminar ECR repos
aws ecr delete-repository --repository-name bookstore-auth-service --force
aws ecr delete-repository --repository-name bookstore-catalog-service --force
aws ecr delete-repository --repository-name bookstore-orders-service --force
```

---

# 💰 COSTOS

- EC2 t2.medium: $0.05/hora
- EKS cluster: $0.10/hora
- 2x t3.medium: $0.08/hora
- 3x LoadBalancer: $0.075/hora
- **Total**: ~$0.30/hora

Con $100 créditos AWS Academy: ~300 horas

---

# 📚 RESUMEN

✅ **Implementado:**
- 3 microservicios (Auth, Catalog, Orders)
- 3 bases de datos MySQL independientes
- Escalamiento en VMs (EC2 + Docker Compose)
- Escalamiento en Kubernetes (EKS + 2 nodos)
- Dominio personalizado con SSL
- LoadBalancers AWS
- Ingress Controller con terminación SSL

✅ **Requisitos cumplidos:** 100%

¡Éxito! 🚀
