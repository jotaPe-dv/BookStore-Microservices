# Guion para Video de Demostración - BookStore Microservices

## Introducción (30 segundos)
"Hola, en este video voy a demostrar el sistema BookStore implementado con arquitectura de microservices desplegado en AWS EC2."

## 1. Mostrar Arquitectura (1 minuto)

### Explicar la arquitectura:
- **3 Microservicios Backend**:
  - auth-service: Autenticación y gestión de usuarios
  - catalog-service: Gestión de catálogo de libros
  - orders-service: Gestión de pedidos, pagos y entregas
- **1 Frontend**: Interfaz web con Flask
- **Base de datos**: MySQL 8.0 con 3 esquemas separados
- **2 Patrones de despliegue**:
  - Patrón VM: Docker Compose en puerto 8080
  - Patrón K8s: k3s con NodePort 30000

Mostrar el diagrama de arquitectura en `README.md`

## 2. Mostrar Código Fuente (1 minuto)

### Estructura del proyecto:
```
BookStore-Microservices/
├── auth-service/          # Microservicio de autenticación
│   ├── app.py
│   ├── config.py
│   ├── Dockerfile
│   └── requirements.txt
├── catalog-service/       # Microservicio de catálogo
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── orders-service/        # Microservicio de pedidos
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend-service/      # Interfaz web
│   ├── app.py
│   ├── templates/         # 10 plantillas HTML
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/                   # Manifiestos Kubernetes
│   ├── auth-service.yaml
│   ├── catalog-service.yaml
│   ├── orders-service.yaml
│   └── secrets.yaml
├── docker-compose.yml     # Orquestación Docker Compose
└── init-databases.sql     # Script de inicialización BD
```

## 3. Conectarse a AWS EC2 (30 segundos)

Mostrar la conexión SSH:
```bash
ssh -i "bookstore-key.pem" ec2-user@98.93.165.242
```

## 4. Verificar Servicios Activos (1 minuto)

### Docker Compose (Puerto 8080):
```bash
docker ps
```
Mostrar los 5 contenedores corriendo:
- bookstore-frontend
- bookstore-auth-service
- bookstore-catalog-service
- bookstore-orders-service
- bookstore-mysql

### Kubernetes k3s (Puerto 30000):
```bash
sudo k3s kubectl get pods
sudo k3s kubectl get services
```
Mostrar pods y servicios desplegados

## 5. Demostración Funcional - Patrón VM (3 minutos)

Abrir navegador en: **http://98.93.165.242:8080**

### 5.1 Registro de Usuario
1. Ir a "Registrarse"
2. Completar formulario:
   - Nombre: Demo User
   - Email: demo@test.com
   - Password: demo123
3. Click en "Registrar"
4. Verificar mensaje de éxito

### 5.2 Login
1. Iniciar sesión con:
   - Email: demo@test.com
   - Password: demo123
2. Verificar mensaje de bienvenida
3. Mostrar que aparece el nombre del usuario en navbar

### 5.3 Explorar Catálogo
1. Ir a "Catálogo"
2. Mostrar los libros disponibles:
   - El Quijote
   - Cien Años de Soledad
   - 1984
   - Harry Potter
3. Verificar que se muestra precio y stock

### 5.4 Comprar Libro
1. Click en "Comprar" en cualquier libro
2. Verificar que se muestra:
   - Información del libro
   - Stock disponible
   - Campo para seleccionar cantidad
3. Ingresar cantidad (ejemplo: 2)
4. Click en "Comprar Ahora"
5. Verificar redirección a página de pago

### 5.5 Proceso de Pago
1. Seleccionar método de pago:
   - Tarjeta de Crédito
   - Tarjeta de Débito
   - PSE
2. Ingresar datos de tarjeta:
   - Número: 4111111111111111
   - Fecha: 12/25
   - CVV: 123
3. Click en "Procesar Pago"
4. Verificar mensaje de pago exitoso

### 5.6 Seleccionar Entrega
1. Elegir tipo de entrega:
   - Entrega Estándar
   - Entrega Express
   - Recogida en Tienda
2. Ingresar dirección de entrega
3. Click en "Confirmar Entrega"
4. Verificar mensaje de pedido completado

### 5.7 Ver Pedidos (si implementado)
1. Ir a "Mis Pedidos"
2. Verificar que aparece el pedido recién creado
3. Mostrar detalles del pedido

## 6. Demostración - Patrón K8s (2 minutos)

Abrir navegador en: **http://98.93.165.242:30000**

Repetir pruebas básicas:
1. Login con usuario existente
2. Ver catálogo
3. Intentar compra para verificar que funciona igual

## 7. Verificar Logs (1 minuto)

### Logs Docker Compose:
```bash
docker logs bookstore-frontend --tail=20
docker logs bookstore-auth-service --tail=20
docker logs bookstore-catalog-service --tail=20
```

### Logs Kubernetes:
```bash
sudo k3s kubectl logs -l app=frontend-service --tail=20
sudo k3s kubectl logs -l app=auth-service --tail=20
sudo k3s kubectl logs -l app=catalog-service --tail=20
```

Mostrar que los servicios están procesando requests correctamente

## 8. Verificar Base de Datos (1 minuto)

```bash
docker exec -it bookstore-mysql mysql -u root -prootpass
```

```sql
USE bookstore_catalog;
SELECT * FROM books;

USE bookstore_orders;
SELECT * FROM orders;

USE bookstore_auth;
SELECT * FROM users;
```

Mostrar los datos en las tablas

## 9. Conclusión (30 segundos)

Resumir:
- ✅ Arquitectura de microservices funcionando
- ✅ 2 patrones de despliegue operativos (VM y K8s)
- ✅ Funcionalidades completas: registro, login, catálogo, compra, pago, entrega
- ✅ Base de datos persistente
- ✅ Logs y monitoreo funcionando

"Esto concluye la demostración del proyecto BookStore Microservices. ¡Gracias por su atención!"

---

## Notas Técnicas para el Video

### Preparación antes de grabar:
1. Asegurar que todos los servicios están corriendo
2. Limpiar logs anteriores
3. Tener base de datos con datos de prueba
4. Probar flujos completos antes de grabar
5. Tener navegador limpio (sin pestañas innecesarias)

### Durante la grabación:
- Hablar claro y pausado
- Mostrar cada paso en pantalla completa
- Usar zoom en áreas importantes
- Pausar entre secciones para transiciones
- Verificar que se vea bien antes de continuar

### Herramientas recomendadas:
- OBS Studio para grabación de pantalla
- Zoom para acercar detalles importantes
- Editor de video para post-producción (opcional)

### Duración estimada: 10-12 minutos
