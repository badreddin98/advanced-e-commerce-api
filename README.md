# Advanced E-commerce API

This is a Flask-based e-commerce API that provides functionality for both customers and administrators to manage products, orders, and customer accounts.

## Features

- Customer and CustomerAccount Management (CRUD operations)
- Product Catalog Management
- Order Processing
- JWT Authentication
- Role-based Access Control
- Request Rate Limiting
- Response Caching
- Swagger Documentation

## Prerequisites

- Python 3.8+
- MySQL Server
- Virtual Environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Advanced-E-commerce-API
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export DATABASE_URL="mysql://username:password@localhost/ecommerce"
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret-key"
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Running the Application

1. Start the Flask development server:
```bash
flask run
```

2. Access the API documentation at:
```
http://localhost:5000/apidocs
```

## API Endpoints

### Authentication
- POST /login - User login

### Customers
- POST /customers - Create a new customer (Admin only)
- GET /customers/{id} - Get customer details (Admin only)
- PUT /customers/{id} - Update customer details (Admin only)
- DELETE /customers/{id} - Delete a customer (Admin only)

### Products
- POST /products - Create a new product
- GET /products - List all products
- GET /products/{id} - Get product details
- PUT /products/{id} - Update product details
- DELETE /products/{id} - Delete a product

### Orders
- POST /orders - Create a new order
- GET /orders/{id} - Get order details

## Testing

Run the unit tests:
```bash
python -m pytest
```

## Security Features

- JWT Authentication for API endpoints
- Password hashing using bcrypt
- Role-based access control for administrative endpoints
- Request rate limiting (100 requests per day)
- Response caching for improved performance

## API Documentation

The API documentation is automatically generated using Swagger and can be accessed at `/apidocs` when the application is running.

## Rate Limiting

All endpoints are rate-limited to 100 requests per day per IP address to prevent abuse.

## Caching

GET requests are cached for 5 minutes to improve performance. The cache is automatically invalidated when related resources are modified.
