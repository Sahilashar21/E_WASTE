# seed.py: Seed MongoDB with demo users for E-Waste project
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
import os
from datetime import datetime

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ewaste_db')
client = MongoClient(mongo_uri)
db = client.get_default_database()
users = db['users']
pickup_requests = db['pickup_requests']

# Remove all existing users (optional, for a clean seed)
users.delete_many({})
pickup_requests.delete_many({})

# Demo users to insert
seed_users = [
    {
        'name': 'Demo User',
        'email': 'user@example.com',
        'mobile': '9999999991',
        'address': 'User Address',
        'age': 25,
        'password': generate_password_hash('userpass'),
        'role': 'user'
    },
    {
        'name': 'Demo Admin',
        'email': 'admin@example.com',
        'mobile': '9999999992',
        'address': 'Admin Address',
        'age': 30,
        'password': generate_password_hash('adminpass'),
        'role': 'admin'
    },
    {
        'name': 'Demo Engineer',
        'email': 'engineer@example.com',
        'mobile': '9999999993',
        'address': 'Engineer Address',
        'age': 28,
        'password': generate_password_hash('engineerpass'),
        'role': 'engineer'
    },
    {
        'name': 'Demo Warehouse',
        'email': 'warehouse@example.com',
        'mobile': '9999999994',
        'address': 'Warehouse Address',
        'age': 35,
        'password': generate_password_hash('warehousepass'),
        'role': 'warehouse'
    }
]

# Insert demo users
users.insert_many(seed_users)

# Seed pickup requests
seed_requests = [
    {
        'user_id': 'test_user_1',  # Static user_id matching app.py dev login
        'area': 'Colaba',
        'address': 'Near Gateway of India, Colaba, Mumbai',
        'ewaste_type': 'Old PC',
        'description': 'Full desktop setup, very old.\n[Details]: PC (10kg): Not booting',
        'approx_weight': 10,
        'items': [
            {'type': 'PC', 'weight': 10, 'description': 'Not booting'}
        ],
        'latitude': 18.9220,
        'longitude': 72.8347,
        'images': [],
        'status': 'pending',
        'engineer_price': None,
        'created_at': datetime.utcnow()
    },
    {
        'user_id': 'test_user_1',
        'area': 'Bandra West',
        'address': 'Linking Road, Bandra West, Mumbai',
        'ewaste_type': 'Washing Machine',
        'description': 'Rusted washing machine.\n[Details]: Washing Machine (30kg): Rusted drum',
        'approx_weight': 30,
        'items': [
            {'type': 'Washing Machine', 'weight': 30, 'description': 'Rusted drum'}
        ],
        'latitude': 19.0600,
        'longitude': 72.8330,
        'images': [],
        'status': 'priced',
        'engineer_price': 500,
        'created_at': datetime.utcnow()
    }
]

pickup_requests.insert_many(seed_requests)

print('Database seeded with demo users and pickup requests.')
