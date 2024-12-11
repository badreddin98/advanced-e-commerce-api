from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models.models import Customer, CustomerAccount
from app import db, bcrypt, cache, limiter

customer_bp = Blueprint('customer', __name__)

def admin_required():
    def wrapper(fn):
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if not claims.get('is_admin', False):
                return jsonify({'message': 'Admin access required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@customer_bp.route('/customers', methods=['POST'])
@admin_required()
@limiter.limit("100 per day")
def create_customer():
    """
    Create a new customer
    ---
    tags:
      - Customers
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
            phone:
              type: string
            username:
              type: string
            password:
              type: string
    responses:
      201:
        description: Customer created successfully
      400:
        description: Invalid request data
    """
    data = request.get_json()
    
    customer = Customer(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone', '')
    )
    
    account = CustomerAccount(
        username=data['username'],
        password=bcrypt.generate_password_hash(data['password']).decode('utf-8')
    )
    
    customer.account = account
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({'message': 'Customer created successfully', 'id': customer.id}), 201

@customer_bp.route('/customers/<int:id>', methods=['GET'])
@admin_required()
@limiter.limit("100 per day")
@cache.cached(timeout=300)
def get_customer(id):
    """
    Get customer details
    ---
    tags:
      - Customers
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Customer details retrieved successfully
      404:
        description: Customer not found
    """
    customer = Customer.query.get_or_404(id)
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'username': customer.account.username if customer.account else None
    })

@customer_bp.route('/customers/<int:id>', methods=['PUT'])
@admin_required()
@limiter.limit("100 per day")
def update_customer(id):
    """
    Update customer details
    ---
    tags:
      - Customers
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
            email:
              type: string
            phone:
              type: string
    responses:
      200:
        description: Customer updated successfully
      404:
        description: Customer not found
    """
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    
    customer.name = data.get('name', customer.name)
    customer.email = data.get('email', customer.email)
    customer.phone = data.get('phone', customer.phone)
    
    db.session.commit()
    cache.delete_memoized(get_customer, id)
    
    return jsonify({'message': 'Customer updated successfully'})

@customer_bp.route('/customers/<int:id>', methods=['DELETE'])
@admin_required()
@limiter.limit("100 per day")
def delete_customer(id):
    """
    Delete a customer
    ---
    tags:
      - Customers
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Customer deleted successfully
      404:
        description: Customer not found
    """
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    cache.delete_memoized(get_customer, id)
    
    return jsonify({'message': 'Customer deleted successfully'})
