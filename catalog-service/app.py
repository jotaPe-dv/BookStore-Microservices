from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secretkey-catalog-service')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI',
    'mysql+pymysql://bookuser:bookpass@mysql-service:3306/bookstore_catalog'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# URL del servicio de autenticación
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:5001')

db = SQLAlchemy(app)

# Modelo Book (solo lectura y escritura limitada)
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

# Helper: Validar token con AUTH service
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

# Endpoints
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'catalog-service'}), 200

@app.route('/catalog', methods=['GET'])
def get_catalog():
    """Obtener catálogo completo de libros (público)"""
    books = Book.query.all()
    return jsonify({
        'books': [book.to_dict() for book in books],
        'total': len(books)
    }), 200

@app.route('/catalog/search', methods=['GET'])
def search_books():
    """Buscar libros por título o autor"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    books = Book.query.filter(
        db.or_(
            Book.title.ilike(f'%{query}%'),
            Book.author.ilike(f'%{query}%')
        )
    ).all()
    
    return jsonify({
        'books': [book.to_dict() for book in books],
        'total': len(books)
    }), 200

@app.route('/catalog/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Obtener detalles de un libro específico"""
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify({'book': book.to_dict()}), 200

@app.route('/my-books', methods=['GET'])
def my_books():
    """Obtener libros del usuario autenticado"""
    # Obtener token del header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid token'}), 401
    
    token = auth_header.split(' ')[1]
    
    # Validar token
    auth_data = validate_token(token)
    if not auth_data:
        return jsonify({'error': 'Invalid token'}), 401
    
    user_id = auth_data['user']['id']
    
    # Obtener libros del usuario
    books = Book.query.filter_by(seller_id=user_id).all()
    
    return jsonify({
        'books': [book.to_dict() for book in books],
        'total': len(books)
    }), 200

@app.route('/catalog/seller/<int:seller_id>', methods=['GET'])
def get_books_by_seller(seller_id):
    """Obtener todos los libros de un vendedor específico"""
    books = Book.query.filter_by(seller_id=seller_id).all()
    
    return jsonify({
        'books': [book.to_dict() for book in books],
        'seller_id': seller_id,
        'total': len(books)
    }), 200

@app.route('/catalog/available', methods=['GET'])
def get_available_books():
    """Obtener solo libros con stock disponible"""
    books = Book.query.filter(Book.stock > 0).all()
    
    return jsonify({
        'books': [book.to_dict() for book in books],
        'total': len(books)
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
    app.run(host='0.0.0.0', port=5002, debug=True)
