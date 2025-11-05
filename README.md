# 📚 BookStore Microservices# ðŸ“š BookStore Microservices - Proyecto 2 (Objetivo 4)



**Universidad EAFIT - ST0263 Tópicos Especiales en Telemática 2025-2**  **Universidad EAFIT - ST0263 TÃ³picos Especiales en TelemÃ¡tica 2025-2**

**Proyecto 2 - Objetivo 4 Opción 1: Reingeniería Monolito a Microservicios**

Sistema de E-commerce para venta de libros, implementado con **arquitectura de microservicios**.

Sistema de e-commerce para venta de libros implementado con arquitectura de microservicios y desplegado en AWS EC2.

## ðŸŽ¯ DescripciÃ³n

---

Este repositorio contiene la implementaciÃ³n del **Objetivo 4** del Proyecto 2: ReingenierÃ­a de la aplicaciÃ³n BookStore desde una arquitectura monolÃ­tica a microservicios.

## 🎯 Descripción del Proyecto

### Microservicios Implementados

Migración de una aplicación monolítica BookStore a una arquitectura de microservicios con 3 servicios independientes:

- **AUTH Service**: AutenticaciÃ³n y gestiÃ³n de usuarios con JWT

- **auth-service** (puerto 30001): Autenticación con JWT, registro y login de usuarios- **CATALOG Service**: VisualizaciÃ³n del catÃ¡logo de libros

- **catalog-service** (puerto 30002): Consulta de catálogo de libros (público y autenticado)- **ORDERS Service**: GestiÃ³n de compras, pagos y entregas

- **orders-service** (puerto 30003): CRUD de libros, compras, pagos y entregas

## ðŸš€ Quick Start

---

### Desarrollo Local (Docker Compose)

## 🏗️ Arquitectura

```powershell

```docker-compose up --build

┌─────────────────────────────────────────────────┐```

│              AWS EC2 (t2.medium)                │

│                                                 │Servicios disponibles:

│  ┌─────────────────────────────────────────┐   │- Auth: http://localhost:5001

│  │        Docker Compose                   │   │- Catalog: http://localhost:5002

│  │                                         │   │- Orders: http://localhost:5003

│  │  ┌──────────┐  ┌──────────┐  ┌────────┐│   │

│  │  │  Auth    │  │ Catalog  │  │ Orders ││   │### ProducciÃ³n (Kubernetes)

│  │  │ Service  │  │ Service  │  │ Service││   │

│  │  │  :30001  │  │  :30002  │  │ :30003 ││   │```powershell

│  │  └────┬─────┘  └────┬─────┘  └───┬────┘│   │# Build y push a ECR

│  │       └─────────────┼────────────┘     │   │.\build-and-push.ps1

│  │                     │                  │   │

│  │              ┌──────▼──────┐           │   │# Desplegar en Kubernetes

│  │              │    MySQL    │           │   │cd k8s

│  │              │   3 schemas │           │   │kubectl apply -f .

│  │              └─────────────┘           │   │```

│  └─────────────────────────────────────────┘   │

└─────────────────────────────────────────────────┘## ðŸ“š DocumentaciÃ³n

```

- **[INDEX.md](INDEX.md)** - Ãndice de toda la documentaciÃ³n

### Bases de datos MySQL- **[QUICK-START.md](QUICK-START.md)** - GuÃ­a de inicio rÃ¡pido

- **[README-FULL.md](README-FULL.md)** - Arquitectura completa

- `bookstore_auth`: Usuarios- **[API-REFERENCE.md](API-REFERENCE.md)** - Referencia de APIs

- `bookstore_catalog`: Catálogo de libros- **[VIDEO-GUIDE.md](VIDEO-GUIDE.md)** - GuÃ­a para video sustentaciÃ³n

- `bookstore_orders`: Compras, pagos, entregas

## ðŸ—ï¸ Arquitectura

---

```

## 🚀 Despliegue en AWSNGINX Ingress â†’ Auth Service (5001)

              â†’ Catalog Service (5002)

### 📘 Guía Completa: [GUIA_AWS.md](GUIA_AWS.md)              â†’ Orders Service (5003)

```

**Resumen de pasos:**

Ver [ARCHITECTURE-COMPARISON.md](ARCHITECTURE-COMPARISON.md) para detalles completos.

1. **Preparar localmente** (5 min):

   ```powershell## ðŸ› ï¸ TecnologÃ­as

   .\deploy.ps1          # Construye imágenes

   .\prepare-aws.ps1     # Exporta imágenes- **Backend**: Python 3.11, Flask, SQLAlchemy, JWT

   ```- **Base de Datos**: MySQL 8.0

- **Infraestructura**: Docker, Kubernetes (EKS), AWS ECR, RDS

2. **Crear EC2 en AWS Academy** (10 min):

   - Tipo: t2.medium## ðŸ“Š Estructura del Proyecto

   - AMI: Amazon Linux 2023

   - Security Group: Puertos 22, 30001, 30002, 30003```

.

3. **Subir archivos** (10 min):â”œâ”€â”€ auth-service/          # Microservicio de autenticaciÃ³n

   ```powershellâ”œâ”€â”€ catalog-service/       # Microservicio de catÃ¡logo

   scp -i "key.pem" bookstore-images.tar.gz ec2-user@IP:~â”œâ”€â”€ orders-service/        # Microservicio de Ã³rdenes

   scp -i "key.pem" docker-compose.yml ec2-user@IP:~â”œâ”€â”€ k8s/                   # Manifiestos Kubernetes

   scp -i "key.pem" init-databases.sql ec2-user@IP:~â”œâ”€â”€ docs/                  # DocumentaciÃ³n completa

   ```â”œâ”€â”€ docker-compose.yml     # Desarrollo local

â””â”€â”€ test_microservices.py  # Tests de integraciÃ³n

4. **Desplegar en EC2** (5 min):```

   ```bash

   docker-compose up -d## ðŸ‘¥ Equipo

   ```

**ST0263 - Universidad EAFIT - 2025-2**

5. **Probar desde tu PC** (2 min):

   ```powershell[Agregar nombres de integrantes]

   python test_e2e.py aws TU-IP-EC2

   ```## ðŸ“ Licencia



---Proyecto acadÃ©mico - Universidad EAFIT



## 🧪 Pruebas---



### Ejecutar pruebas E2E**â­ Star este repo si te fue Ãºtil!**


```powershell
# Local (Kubernetes)
python test_e2e.py

# AWS (EC2)
python test_e2e.py aws 3.85.123.45
```

### Pruebas incluidas

1. ✅ Registro de usuario
2. ✅ Login y obtención de JWT
3. ✅ Crear libro (autenticado)
4. ✅ Ver catálogo (público)
5. ✅ Crear compra
6. ✅ Procesar pago
7. ✅ Crear entrega

---

## 🛠️ Tecnologías

- **Backend**: Python 3.11 + Flask
- **Autenticación**: JWT (Flask-JWT-Extended)
- **Base de datos**: MySQL 8.0
- **ORM**: SQLAlchemy
- **Contenedores**: Docker + Docker Compose
- **Cloud**: AWS EC2
- **Testing**: Python requests

---

## 📁 Estructura del Proyecto

```
BookStore-Microservices/
├── auth-service/           # Microservicio de autenticación
│   ├── app.py             # Endpoints: /register, /login, /validate
│   ├── config.py          # Configuración y secrets
│   ├── Dockerfile         # Imagen Docker
│   └── requirements.txt   # Dependencias
├── catalog-service/        # Microservicio de catálogo
│   ├── app.py             # Endpoints: /catalog, /search
│   ├── Dockerfile
│   └── requirements.txt
├── orders-service/         # Microservicio de órdenes
│   ├── app.py             # Endpoints: /books, /purchase, /payment, /delivery
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/                    # Manifests de Kubernetes (local)
│   ├── mysql.yaml
│   ├── auth-service.yaml
│   ├── catalog-service.yaml
│   └── orders-service.yaml
├── docker-compose.yml      # Orquestación para AWS
├── init-databases.sql      # Script SQL de inicialización
├── deploy.ps1              # Script de despliegue local
├── prepare-aws.ps1         # Script de preparación AWS
├── test-docker-compose.ps1 # Test local de docker-compose
├── test_e2e.py            # Suite de pruebas automatizadas
├── GUIA_AWS.md            # 📘 Guía completa de despliegue AWS
└── README.md              # Este archivo
```

---

## 🔌 API Endpoints

### Auth Service (puerto 30001)

- `POST /register` - Registrar usuario
- `POST /login` - Login y obtener JWT
- `GET /validate` - Validar token JWT
- `GET /health` - Health check

### Catalog Service (puerto 30002)

- `GET /catalog` - Listar libros (público)
- `GET /search?q=query` - Buscar libros
- `GET /my-books` - Libros del usuario (autenticado)
- `GET /health` - Health check

### Orders Service (puerto 30003)

- `POST /books` - Crear libro (autenticado)
- `PUT /books/:id` - Actualizar libro (autenticado)
- `DELETE /books/:id` - Eliminar libro (autenticado)
- `POST /purchase` - Crear compra (autenticado)
- `POST /payment` - Procesar pago (autenticado)
- `POST /delivery` - Crear entrega (autenticado)
- `GET /health` - Health check

---

## 💻 Desarrollo Local

### Opción 1: Kubernetes (Docker Desktop)

```powershell
# Habilitar Kubernetes en Docker Desktop
# Settings → Kubernetes → Enable Kubernetes

# Desplegar
.\deploy.ps1

# Acceder a servicios
# http://localhost:30001 (auth)
# http://localhost:30002 (catalog)
# http://localhost:30003 (orders)
```

### Opción 2: Docker Compose

```powershell
# Test completo (construye, despliega y prueba)
.\test-docker-compose.ps1

# O manualmente:
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

## 📸 Capturas para Entrega

Incluir screenshots de:

1. ✅ AWS Console mostrando EC2 corriendo
2. ✅ Terminal EC2 con `docker-compose ps`
3. ✅ Pruebas E2E exitosas (7/7)
4. ✅ Navegador accediendo a `/health` endpoints

---

## 🎥 Video del Proyecto

**Duración**: 8-10 minutos

**Contenido sugerido**:
1. Introducción y objetivos (1 min)
2. Demostración en AWS (3 min)
3. Explicación de código (3 min)
4. Pruebas E2E (2 min)
5. Conclusiones (1 min)

---

## 👥 Autores

- Juan Rua
- Universidad EAFIT
- ST0263 Tópicos Especiales en Telemática 2025-2

---

## 📚 Documentación

- **[GUIA_AWS.md](GUIA_AWS.md)** - 📘 Guía completa paso a paso para despliegue en AWS (incluye troubleshooting)

---

## ⚠️ Notas Importantes

- Las credenciales están hardcodeadas para simplificar la demo (solo para ambiente educativo)
- El Security Group debe tener los puertos 30001-30003 abiertos
- MySQL tarda ~30 segundos en inicializar las 3 bases de datos
- AWS Academy Learner Lab se cierra automáticamente después de 4 horas

---

## 📄 Licencia

Proyecto educativo - Universidad EAFIT 2025
