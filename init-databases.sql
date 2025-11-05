-- Crear bases de datos para los microservicios
CREATE DATABASE IF NOT EXISTS bookstore_auth;
CREATE DATABASE IF NOT EXISTS bookstore_catalog;
CREATE DATABASE IF NOT EXISTS bookstore_orders;

-- Crear usuario (opcional, si no usas root)
CREATE USER IF NOT EXISTS 'bookuser'@'%' IDENTIFIED BY 'bookpass';

-- Dar permisos
GRANT ALL PRIVILEGES ON bookstore_auth.* TO 'bookuser'@'%';
GRANT ALL PRIVILEGES ON bookstore_catalog.* TO 'bookuser'@'%';
GRANT ALL PRIVILEGES ON bookstore_orders.* TO 'bookuser'@'%';

FLUSH PRIVILEGES;
