from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import Order, OrderItem, Product
from app import db, cache, limiter

order_bp = Blueprint('order', __name__)

@order_bp.route('/orders', methods=['POST'])
@jwt_required()
@limiter.limit("100 per day")
def create_order():
    """
    Create a new order
    ---
    tags:
      - Orders
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                  quantity:
                    type: integer
    responses:
      201:
        description: Order created successfully
      400:
        description: Invalid request data
      404:
        description: Product not found
    """
    data = request.get_json()
    customer_id = get_jwt_identity()
    
    # Calculate total amount and validate products
    total_amount = 0
    order_items = []
    
    for item in data['items']:
        product = Product.query.get_or_404(item['product_id'])
        if product.stock < item['quantity']:
            return jsonify({'message': f'Insufficient stock for product {product.name}'}), 400
            
        total_amount += product.price * item['quantity']
        order_items.append({
            'product': product,
            'quantity': item['quantity'],
            'price': product.price
        })
    
    # Create order
    order = Order(
        customer_id=customer_id,
        total_amount=total_amount
    )
    db.session.add(order)
    
    # Create order items and update stock
    for item in order_items:
        order_item = OrderItem(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price=item['price']
        )
        item['product'].stock -= item['quantity']
        db.session.add(order_item)
    
    db.session.commit()
    
    return jsonify({'message': 'Order created successfully', 'id': order.id}), 201

@order_bp.route('/orders/<int:id>', methods=['GET'])
@jwt_required()
@limiter.limit("100 per day")
@cache.cached(timeout=300)
def get_order(id):
    """
    Get order details
    ---
    tags:
      - Orders
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Order details retrieved successfully
      404:
        description: Order not found
    """
    order = Order.query.get_or_404(id)
    customer_id = get_jwt_identity()
    
    # Only allow customers to view their own orders
    if order.customer_id != customer_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    return jsonify({
        'id': order.id,
        'customer_id': order.customer_id,
        'order_date': order.order_date.isoformat(),
        'total_amount': order.total_amount,
        'status': order.status,
        'items': [{
            'product_id': item.product_id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': item.price
        } for item in order.items]
    })
