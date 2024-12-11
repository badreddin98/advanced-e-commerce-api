from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.models import CustomerAccount
from app import bcrypt, db, limiter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("100 per day")
def login():
    """
    User login endpoint
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    account = CustomerAccount.query.filter_by(username=username).first()
    if account and bcrypt.check_password_hash(account.password, password):
        access_token = create_access_token(
            identity=account.id,
            additional_claims={'is_admin': account.is_admin}
        )
        return jsonify({'access_token': access_token}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401
