# BookStore Microservices - Proyecto 2 (Objetivo 4)

## Universidad EAFIT - ST0263 Tópicos Especiales en Telemática 2025-2
---

## Proyecto 2 - Objetivo 4, Opción 1: Reingeniería del Monolito hacia una Arquitectura de Microservicios

Sistema de comercio electrónico para venta de libros, implementado bajo una arquitectura de microservicios y desplegado en AWS EC2.

**Descripción General:**

Este repositorio contiene la implementación correspondiente al Objetivo 4 del Proyecto 2, enfocado en la reingeniería de la aplicación BookStore desde una arquitectura monolítica hacia un modelo distribuido basado en microservicios.

## Descripción del Proyecto

**Microservicios Implementados**
---

Migración de la aplicación monolítica BookStore hacia una arquitectura modular con tres servicios independientes:

- Auth Service (puerto 30001): Autenticación y gestión de usuarios mediante JWT.

- Catalog Service (puerto 30002): Consulta del catálogo de libros, tanto pública como autenticada.

- Orders Service (puerto 30003): Gestión de compras, pagos y entregas, con operaciones CRUD.

## Ejecución Rápida (Quick Start)

Desarrollo Local con Docker Compose:

```bash
docker-compose up --build
```

## Servicios disponibles localmente:

Auth Service → http://localhost:5001

Catalog Service → http://localhost:5002

Orders Service → http://localhost:5003


## Arquitectura General

Los servicios fueron diseñados bajo una arquitectura basada en contenedores y orquestados con Docker Compose y Kubernetes (EKS) para entornos de producción.

### Despliegue Local (Docker Compose)

Cada microservicio se ejecuta como un contenedor independiente que se comunica con una base de datos MySQL compartida, la cual contiene tres esquemas correspondientes a los servicios Auth, Catalog y Orders.

Despliegue en Producción (Kubernetes)

Para el despliegue en AWS, se utilizaron manifiestos YAML que definen los objetos Deployment, Service y PersistentVolumeClaim.
El proceso de compilación y despliegue se automatizó con los scripts build-and-push.ps1 y deploy.ps1, que publican las imágenes en Amazon ECR y aplican los manifiestos en EKS.


## Despliegue en AWS

El balanceo de tráfico se gestiona mediante NGINX Ingress, el cual enruta las peticiones hacia:

- Auth Service (puerto 5001)

- Catalog Service (puerto 5002)

- Orders Service (puerto 5003)



## Tecnologías Utilizadas

- Backend: Python 3.11, Flask, SQLAlchemy, JWT.

- Base de datos: MySQL 8.0.

- Infraestructura: Docker, Kubernetes (EKS), AWS ECR, RDS.

- Testing: Python (requests library).

## Estructura del Proyecto

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

## Endpoints de las APIs

- Auth Service (30001)

- POST /register – Registro de usuario.

- POST /login – Inicio de sesión y obtención de JWT.

- GET /validate – Validación de token JWT.

- GET /health – Verificación del servicio.

- Catalog Service (30002)

- GET /catalog – Listar libros (público).
 
- GET /search?q= – Búsqueda de libros.

- GET /my-books – Libros asociados al usuario autenticado.

- GET /health – Estado del servicio.

- Orders Service (30003)

- POST /books – Crear libro.

- PUT /books/:id – Actualizar libro.

- DELETE /books/:id – Eliminar libro.

- POST /purchase – Registrar compra.

- POST /payment – Procesar pago.

- POST /delivery – Registrar entrega.
