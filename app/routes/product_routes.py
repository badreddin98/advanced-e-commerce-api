from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.models import Product
from app import db, cache, limiter

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['POST'])
@jwt_required()
@limiter.limit("100 per day")
def create_product():
    """
    Create a new product
    ---
    tags:
      - Products
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            price:
              type: number
            stock:
              type: integer
    responses:
      201:
        description: Product created successfully
      400:
        description: Invalid request data
    """
    data = request.get_json()
    
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        stock=data.get('stock', 0)
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({'message': 'Product created successfully', 'id': product.id}), 201

@product_bp.route('/products/<int:id>', methods=['GET'])
@jwt_required()
@limiter.limit("100 per day")
@cache.cached(timeout=300)
def get_product(id):
    """
    Get product details
    ---
    tags:
      - Products
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Product details retrieved successfully
      404:
        description: Product not found
    """
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock
    })

@product_bp.route('/products', methods=['GET'])
@jwt_required()
@limiter.limit("100 per day")
@cache.cached(timeout=300)
def list_products():
    """
    List all products
    ---
    tags:
      - Products
    responses:
      200:
        description: List of products retrieved successfully
    """
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'stock': p.stock
    } for p in products])

@product_bp.route('/products/<int:id>', methods=['PUT'])
@jwt_required()
@limiter.limit("100 per day")
def update_product(id):
    """
    Update product details
    ---
    tags:
      - Products
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            price:
              type: number
            stock:
              type: integer
    responses:
      200:
        description: Product updated successfully
      404:
        description: Product not found
    """
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    
    db.session.commit()
    cache.delete_memoized(get_product, id)
    cache.delete_memoized(list_products)
    
    return jsonify({'message': 'Product updated successfully'})

@product_bp.route('/products/<int:id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("100 per day")
def delete_product(id):
    """
    Delete a product
    ---
    tags:
      - Products
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Product deleted successfully
      404:
        description: Product not found
    """
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    cache.delete_memoized(get_product, id)
    cache.delete_memoized(list_products)
    
    return jsonify({'message': 'Product deleted successfully'})
