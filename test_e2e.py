#!/usr/bin/env python3
"""
Script de pruebas E2E para BookStore Microservices
Ejecuta un flujo completo: register -> login -> crear libro -> ver catálogo -> comprar -> pagar -> delivery

Uso:
  python test_e2e.py                    # Local (Docker Desktop/Minikube)
  python test_e2e.py aws 3.85.123.45    # AWS EC2 con IP pública
"""

import requests
import sys
import time

# Verificar si se proporcionó IP de AWS
if len(sys.argv) >= 3 and sys.argv[1] == "aws":
    AWS_IP = sys.argv[2]
    BASE_URL = f"http://{AWS_IP}"
    print(f"\n🌐 Modo AWS: usando IP {AWS_IP}\n")
# Detectar si estamos en Minikube o Docker Desktop
else:
    try:
        import subprocess
        result = subprocess.run(['kubectl', 'config', 'current-context'], 
                              capture_output=True, text=True, timeout=5)
        context = result.stdout.strip()
        
        if 'minikube' in context:
            # Obtener IP de Minikube
            result = subprocess.run(['minikube', 'ip'], 
                                  capture_output=True, text=True, timeout=5)
            MINIKUBE_IP = result.stdout.strip()
            BASE_URL = f"http://{MINIKUBE_IP}"
        else:
            BASE_URL = "http://localhost"
    except:
        BASE_URL = "http://localhost"

AUTH_URL = f"{BASE_URL}:30001"
CATALOG_URL = f"{BASE_URL}:30002"
ORDERS_URL = f"{BASE_URL}:30003"

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_step(step_num, total, description):
    print(f"\n{CYAN}[{step_num}/{total}] {description}{RESET}")
    print("-" * 60)

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")

def check_health():
    """Verificar que todos los servicios estén disponibles"""
    print_step(0, 7, "Verificando salud de los servicios")
    
    services = [
        ("Auth Service", f"{AUTH_URL}/health"),
        ("Catalog Service", f"{CATALOG_URL}/health"),
        ("Orders Service", f"{ORDERS_URL}/health")
    ]
    
    all_healthy = True
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success(f"{name} está saludable")
            else:
                print_error(f"{name} respondió con código {response.status_code}")
                all_healthy = False
        except Exception as e:
            print_error(f"{name} no está disponible: {e}")
            all_healthy = False
    
    if not all_healthy:
        print_error("Algunos servicios no están disponibles. Abortando pruebas.")
        sys.exit(1)
    
    return True

def test_register():
    """Prueba 1: Registrar un usuario"""
    print_step(1, 7, "Registrar usuario")
    
    payload = {
        "name": "Test User",
        "email": f"testuser_{int(time.time())}@bookstore.com",
        "password": "testpass123",
        "is_admin": False
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/register", json=payload, timeout=10)
        if response.status_code == 201:
            data = response.json()
            print_success(f"Usuario registrado: {data['user']['email']}")
            return payload['email'], payload['password']
        else:
            print_error(f"Error en registro: {response.text}")
            sys.exit(1)
    except Exception as e:
        print_error(f"Excepción en registro: {e}")
        sys.exit(1)

def test_login(email, password):
    """Prueba 2: Login"""
    print_step(2, 7, "Login de usuario")
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/login", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            print_success(f"Login exitoso. Token obtenido (primeros 20 chars): {token[:20]}...")
            return token
        else:
            print_error(f"Error en login: {response.text}")
            sys.exit(1)
    except Exception as e:
        print_error(f"Excepción en login: {e}")
        sys.exit(1)

def test_create_book(token):
    """Prueba 3: Crear un libro"""
    print_step(3, 7, "Crear libro en Orders Service")
    
    payload = {
        "title": "El Señor de los Anillos",
        "author": "J.R.R. Tolkien",
        "description": "Épica fantasía de la Tierra Media",
        "price": 45.99,
        "stock": 10
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{ORDERS_URL}/books", json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            data = response.json()
            book_id = data['book']['id']
            print_success(f"Libro creado con ID: {book_id}")
            return book_id
        else:
            print_error(f"Error creando libro: {response.text}")
            sys.exit(1)
    except Exception as e:
        print_error(f"Excepción creando libro: {e}")
        sys.exit(1)

def test_view_catalog():
    """Prueba 4: Ver catálogo"""
    print_step(4, 7, "Ver catálogo (público)")
    
    try:
        response = requests.get(f"{CATALOG_URL}/catalog", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data['total']
            print_success(f"Catálogo obtenido: {total} libro(s) disponible(s)")
            if total > 0:
                print(f"   Ejemplo: {data['books'][0]['title']} por {data['books'][0]['author']}")
            return data['books']
        else:
            print_error(f"Error obteniendo catálogo: {response.text}")
            sys.exit(1)
    except Exception as e:
        print_error(f"Excepción obteniendo catálogo: {e}")
        sys.exit(1)

def test_purchase(token, book_id):
    """Prueba 5: Crear una compra"""
    print_step(5, 7, "Crear compra")
    
    payload = {
        "book_id": book_id,
        "quantity": 2
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{ORDERS_URL}/purchase", json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            data = response.json()
            purchase_id = data['purchase']['id']
            total_price = data['purchase']['total_price']
            print_success(f"Compra creada con ID: {purchase_id}, Total: ${total_price}")
            return purchase_id
        else:
            print_error(f"Error creando compra: {response.text}")
            sys.exit(1)
    except Exception as e:
        print_error(f"Excepción creando compra: {e}")
        sys.exit(1)

def test_payment(token, purchase_id):
    """Prueba 6: Procesar pago"""
    print_step(6, 7, "Procesar pago")
    
    payload = {
        "purchase_id": purchase_id,
        "payment_method": "credit_card"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{ORDERS_URL}/payment", json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            data = response.json()
            payment_id = data['payment']['id']
            status = data['payment']['payment_status']
            print_success(f"Pago procesado con ID: {payment_id}, Estado: {status}")
            return payment_id
        else:
            print_error(f"Error procesando pago: {response.text}")
            sys.exit(1)
    except Exception as e:
        print_error(f"Excepción procesando pago: {e}")
        sys.exit(1)

def test_delivery(token, purchase_id):
    """Prueba 7: Crear delivery"""
    print_step(7, 7, "Crear entrega")
    
    # Primero obtener proveedores
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{ORDERS_URL}/delivery-providers", timeout=10)
        if response.status_code != 200:
            print_warning("No se pudieron obtener proveedores, usando provider_id=1")
            provider_id = 1
        else:
            providers = response.json()['providers']
            provider_id = providers[0]['id'] if providers else 1
            print(f"   Usando proveedor: ID {provider_id}")
        
        # Crear delivery
        payload = {
            "purchase_id": purchase_id,
            "provider_id": provider_id,
            "address": "Calle Falsa 123, Springfield"
        }
        
        response = requests.post(f"{ORDERS_URL}/delivery", json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            data = response.json()
            delivery_id = data['delivery']['id']
            status = data['delivery']['delivery_status']
            print_success(f"Entrega creada con ID: {delivery_id}, Estado: {status}")
            return delivery_id
        else:
            print_error(f"Error creando entrega: {response.text}")
            sys.exit(1)
    except Exception as e:
        print_error(f"Excepción creando entrega: {e}")
        sys.exit(1)

def main():
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}BookStore Microservices - Pruebas E2E{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"\n{YELLOW}URLs:{RESET}")
    print(f"  Auth:    {AUTH_URL}")
    print(f"  Catalog: {CATALOG_URL}")
    print(f"  Orders:  {ORDERS_URL}")
    
    # Health check
    check_health()
    
    # Flujo completo
    email, password = test_register()
    token = test_login(email, password)
    book_id = test_create_book(token)
    test_view_catalog()
    purchase_id = test_purchase(token, book_id)
    test_payment(token, purchase_id)
    test_delivery(token, purchase_id)
    
    # Resumen final
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"\n{CYAN}Resumen del flujo:{RESET}")
    print(f"  1. Usuario registrado: {email}")
    print(f"  2. Login exitoso (token obtenido)")
    print(f"  3. Libro creado (ID: {book_id})")
    print(f"  4. Catálogo consultado")
    print(f"  5. Compra creada (ID: {purchase_id})")
    print(f"  6. Pago procesado")
    print(f"  7. Entrega creada")
    print(f"\n{GREEN}🎉 Sistema funcionando correctamente!{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Pruebas interrumpidas por el usuario{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Error inesperado: {e}{RESET}")
        sys.exit(1)
