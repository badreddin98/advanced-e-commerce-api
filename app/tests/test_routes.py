import unittest
from unittest.mock import patch
from app import create_app, db
from app.models.models import Customer, CustomerAccount, Product, Order
from flask_jwt_extended import create_access_token

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test admin account
            customer = Customer(name='Admin', email='admin@test.com', phone='1234567890')
            account = CustomerAccount(
                username='admin',
                password='password',
                is_admin=True
            )
            customer.account = account
            db.session.add(customer)
            db.session.commit()
            
            self.admin_token = create_access_token(
                identity=account.id,
                additional_claims={'is_admin': True}
            )
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_create_customer(self):
        """Test customer creation endpoint"""
        data = {
            'name': 'Test User',
            'email': 'test@test.com',
            'phone': '1234567890',
            'username': 'testuser',
            'password': 'password123'
        }
        
        response = self.client.post(
            '/customers',
            json=data,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('Customer created successfully', response.get_json()['message'])
    
    def test_create_product(self):
        """Test product creation endpoint"""
        data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': 99.99,
            'stock': 10
        }
        
        response = self.client.post(
            '/products',
            json=data,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('Product created successfully', response.get_json()['message'])
    
    def test_create_order(self):
        """Test order creation endpoint"""
        # Create a test product first
        product_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': 99.99,
            'stock': 10
        }
        
        product_response = self.client.post(
            '/products',
            json=product_data,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        product_id = product_response.get_json()['id']
        
        # Create an order
        order_data = {
            'items': [
                {
                    'product_id': product_id,
                    'quantity': 2
                }
            ]
        }
        
        response = self.client.post(
            '/orders',
            json=order_data,
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('Order created successfully', response.get_json()['message'])

if __name__ == '__main__':
    unittest.main()
