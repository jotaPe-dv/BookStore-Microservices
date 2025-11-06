from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secretkey-orders-service')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI',
    'mysql+pymysql://bookuser:bookpass@mysql-service:3306/bookstore_orders'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# URL del servicio de autenticación
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:5001')
# URL del servicio de catálogo
CATALOG_SERVICE_URL = os.getenv('CATALOG_SERVICE_URL', 'http://catalog-service:5002')

db = SQLAlchemy(app)

# Modelos
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    seller_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'seller_id': self.seller_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending Payment')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'purchase_id': self.purchase_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DeliveryProvider(db.Model):
    __tablename__ = 'delivery_providers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    coverage_area = db.Column(db.String(150), nullable=False)
    cost = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'coverage_area': self.coverage_area,
            'cost': self.cost
        }

class Delivery(db.Model):
    __tablename__ = 'deliveries'
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('delivery_providers.id'), nullable=False)
    address = db.Column(db.Text, nullable=False)
    delivery_status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'purchase_id': self.purchase_id,
            'provider_id': self.provider_id,
            'address': self.address,
            'delivery_status': self.delivery_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Helper: Validar token
def validate_token(token):
    try:
        response = requests.get(
            f'{AUTH_SERVICE_URL}/validate',
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error validating token: {e}")
        return None

def require_auth():
    """Decorator helper para validar autenticación"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, jsonify({'error': 'Missing or invalid token'}), 401
    
    token = auth_header.split(' ')[1]
    auth_data = validate_token(token)
    
    if not auth_data:
        return None, jsonify({'error': 'Invalid token'}), 401
    
    return auth_data['user'], None, None

# ============ ENDPOINTS ============

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'orders-service'}), 200

# ============ CRUD LIBROS (Admin) ============

@app.route('/books', methods=['POST'])
def create_book():
    """Crear un nuevo libro"""
    user, error, status = require_auth()
    if error:
        return error, status
    
    data = request.get_json()
    
    if not all(k in data for k in ['title', 'author', 'price', 'stock']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_book = Book(
        title=data['title'],
        author=data['author'],
        description=data.get('description', ''),
        price=float(data['price']),
        stock=int(data['stock']),
        seller_id=user['id']
    )
    
    db.session.add(new_book)
    db.session.commit()
    
    return jsonify({
        'message': 'Book created successfully',
        'book': new_book.to_dict()
    }), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Actualizar un libro existente"""
    user, error, status = require_auth()
    if error:
        return error, status
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # Verificar que el usuario sea el vendedor o admin
    if book.seller_id != user['id'] and not user.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'description' in data:
        book.description = data['description']
    if 'price' in data:
        book.price = float(data['price'])
    if 'stock' in data:
        book.stock = int(data['stock'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Book updated successfully',
        'book': book.to_dict()
    }), 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Eliminar un libro"""
    user, error, status = require_auth()
    if error:
        return error, status
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # Verificar que el usuario sea el vendedor o admin
    if book.seller_id != user['id'] and not user.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': 'Book deleted successfully'}), 200

# ============ COMPRAS ============

@app.route('/purchase', methods=['POST'])
def create_purchase():
    """Crear una compra"""
    user, error, status = require_auth()
    if error:
        return error, status
    
    data = request.get_json()
    
    if not all(k in data for k in ['book_id', 'quantity']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Consultar al catalog-service para obtener información del libro
    try:
        catalog_response = requests.get(
            f'{CATALOG_SERVICE_URL}/catalog/{data["book_id"]}',
            timeout=5
        )
        
        if catalog_response.status_code != 200:
            return jsonify({'error': 'Book not found'}), 404
        
        book_data = catalog_response.json().get('book')
        if not book_data:
            return jsonify({'error': 'Book not found'}), 404
            
    except Exception as e:
        print(f"Error fetching book from catalog: {e}")
        return jsonify({'error': 'Error fetching book information'}), 500
    
    quantity = int(data['quantity'])
    
    if book_data['stock'] < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    total_price = book_data['price'] * quantity
    
    # Crear la compra
    new_purchase = Purchase(
        user_id=user['id'],
        book_id=book_data['id'],
        quantity=quantity,
        total_price=total_price,
        status='Pending Payment'
    )
    
    db.session.add(new_purchase)
    db.session.commit()
    
    return jsonify({
        'message': 'Purchase created successfully',
        'purchase': new_purchase.to_dict(),
        'book': book_data
    }), 201

@app.route('/purchases', methods=['GET'])
def get_user_purchases():
    """Obtener compras del usuario autenticado"""
    user, error, status = require_auth()
    if error:
        return error, status
    
    purchases = Purchase.query.filter_by(user_id=user['id']).all()
    
    return jsonify({
        'purchases': [p.to_dict() for p in purchases],
        'total': len(purchases)
    }), 200

@app.route('/purchases/<int:purchase_id>', methods=['GET'])
def get_purchase(purchase_id):
    """Obtener detalles de una compra"""
    user, error, status = require_auth()
    if error:
        return error, status
    
    purchase = Purchase.query.get(purchase_id)
    if not purchase:
        return jsonify({'error': 'Purchase not found'}), 404
    
    if purchase.user_id != user['id'] and not user.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'purchase': purchase.to_dict()}), 200

# ============ PAGOS ============

@app.route('/payment', methods=['POST'])
def create_payment():
    """Procesar pago de una compra"""
    user, error, status = require_auth()
    if error:
        return error, status
    
    data = request.get_json()
    
    if not all(k in data for k in ['purchase_id', 'payment_method']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    purchase = Purchase.query.get(data['purchase_id'])
    if not purchase:
        return jsonify({'error': 'Purchase not found'}), 404
    
    if purchase.user_id != user['id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Crear el pago (simulado)
    new_payment = Payment(
        purchase_id=purchase.id,
        amount=purchase.total_price,
        payment_method=data['payment_method'],
        payment_status='Completed'  # Simulado como exitoso
    )
    
    # Actualizar estado de la compra
    purchase.status = 'Paid'
    
    db.session.add(new_payment)
    db.session.commit()
    
    return jsonify({
        'message': 'Payment processed successfully',
        'payment': new_payment.to_dict()
    }), 201

@app.route('/payments/<int:purchase_id>', methods=['GET'])
def get_payment(purchase_id):
    """Obtener pago de una compra"""
    user, error, status = require_auth()
    if error:
        return error, status
    
    payment = Payment.query.filter_by(purchase_id=purchase_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    # Verificar autorización
    purchase = Purchase.query.get(purchase_id)
    if purchase.user_id != user['id'] and not user.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'payment': payment.to_dict()}), 200

# ============ ENTREGAS ============

@app.route('/delivery-providers', methods=['GET'])
def get_delivery_providers():
    """Obtener proveedores de entrega disponibles"""
    providers = DeliveryProvider.query.all()
    return jsonify({
        'providers': [p.to_dict() for p in providers]
    }), 200

@app.route('/delivery', methods=['POST'])
def create_delivery():
    """Crear solicitud de entrega"""
    user, error, status = require_auth()
    if error:
        return error, status
    
    data = request.get_json()
    
    if not all(k in data for k in ['purchase_id', 'provider_id', 'address']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    purchase = Purchase.query.get(data['purchase_id'])
    if not purchase:
        return jsonify({'error': 'Purchase not found'}), 404
    
    if purchase.user_id != user['id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if purchase.status != 'Paid':
        return jsonify({'error': 'Purchase must be paid first'}), 400
    
    # Crear la entrega
    new_delivery = Delivery(
        purchase_id=purchase.id,
        provider_id=data['provider_id'],
        address=data['address'],
        delivery_status='In Transit'  # Simulado
    )
    
    # Actualizar estado de la compra
    purchase.status = 'Shipped'
    
    db.session.add(new_delivery)
    db.session.commit()
    
    return jsonify({
        'message': 'Delivery created successfully',
        'delivery': new_delivery.to_dict()
    }), 201

@app.route('/deliveries/<int:purchase_id>', methods=['GET'])
def get_delivery(purchase_id):
    """Obtener información de entrega"""
    user, error, status = require_auth()
    if error:
        return error, status
    
    delivery = Delivery.query.filter_by(purchase_id=purchase_id).first()
    if not delivery:
        return jsonify({'error': 'Delivery not found'}), 404
    
    # Verificar autorización
    purchase = Purchase.query.get(purchase_id)
    if purchase.user_id != user['id'] and not user.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'delivery': delivery.to_dict()}), 200

# Inicializar proveedores de entrega
def initialize_delivery_providers():
    if DeliveryProvider.query.count() == 0:
        providers = [
            DeliveryProvider(name="DHL", coverage_area="Internacional", cost=50.0),
            DeliveryProvider(name="FedEx", coverage_area="Internacional", cost=45.0),
            DeliveryProvider(name="Envía", coverage_area="Nacional", cost=20.0),
            DeliveryProvider(name="Servientrega", coverage_area="Nacional", cost=15.0),
        ]
        db.session.bulk_save_objects(providers)
        db.session.commit()
        print("✅ Delivery providers initialized")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_delivery_providers()
        print("✅ Database tables created")
    app.run(host='0.0.0.0', port=5003, debug=True)
