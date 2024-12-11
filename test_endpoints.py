import requests
import json

BASE_URL = 'http://localhost:5000'

def test_endpoints():
    # 1. Create admin user
    admin_data = {
        'name': 'Admin User',
        'email': 'admin@example.com',
        'phone': '1234567890',
        'username': 'admin',
        'password': 'admin123'
    }
    
    print("1. Creating admin user...")
    response = requests.post(f'{BASE_URL}/customers', json=admin_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

    # 2. Login
    print("2. Logging in...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    if response.status_code == 200:
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 3. Create product
        print("3. Creating product...")
        product_data = {
            'name': 'Test Product',
            'description': 'A test product',
            'price': 99.99,
            'stock': 10
        }
        response = requests.post(f'{BASE_URL}/products', headers=headers, json=product_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
        
        if response.status_code == 201:
            product_id = response.json()['id']
            
            # 4. Get product
            print("4. Getting product...")
            response = requests.get(f'{BASE_URL}/products/{product_id}', headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}\n")
            
            # 5. Create order
            print("5. Creating order...")
            order_data = {
                'items': [
                    {
                        'product_id': product_id,
                        'quantity': 2
                    }
                ]
            }
            response = requests.post(f'{BASE_URL}/orders', headers=headers, json=order_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}\n")
            
            if response.status_code == 201:
                order_id = response.json()['id']
                
                # 6. Get order
                print("6. Getting order...")
                response = requests.get(f'{BASE_URL}/orders/{order_id}', headers=headers)
                print(f"Status: {response.status_code}")
                print(f"Response: {response.json()}\n")

if __name__ == '__main__':
    test_endpoints()
