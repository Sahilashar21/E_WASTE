"""
Seed script for E_WASTE project.

This script clears the main collections and inserts sample data (5 users, 5 pickup requests,
1 collection cluster, category prices and metal price snapshot) to help test the project.

Usage:
  python seed.py

It reads `MONGO_URI` from environment (default: mongodb://localhost:27017/) and uses
database name from the URI if present, otherwise `ewaste_db`.
"""

import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId


MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')

client = MongoClient(MONGO_URI)

# Determine database: if URI contains a DB, get_default_database(), else use ewaste_db
try:
    db = client.get_default_database()
    if db is None:
        db = client['ewaste_db']
except Exception:
    db = client['ewaste_db']


def reset_and_seed():
    print('Clearing existing collections...')
    for col in ['users', 'pickup_requests', 'collection_clusters', 'category_prices', 'metal_prices']:
        if col in db.list_collection_names():
            db[col].delete_many({})
            print(f'  - Cleared {col}')

    # Insert users (7+) - includes drivers for cluster assignments
    users = [
        { 'name': 'Main Warehouse Admin', 'email': 'warehouse@example.com', 'password': 'warehousepass', 'role': 'warehouse' },
        { 'name': 'Ramesh Engineer', 'email': 'engineer1@example.com', 'password': 'engineerpass', 'role': 'engineer', 'available_tomorrow': True },
        { 'name': 'Suresh Engineer', 'email': 'engineer2@example.com', 'password': 'engineerpass', 'role': 'engineer', 'available_tomorrow': True },
        { 'name': 'Driver One', 'email': 'driver1@example.com', 'password': 'driverpass', 'role': 'driver' },
        { 'name': 'Driver Two', 'email': 'driver2@example.com', 'password': 'driverpass', 'role': 'driver' },
        { 'name': 'Green Recycler', 'email': 'recycler@example.com', 'password': 'recyclerpass', 'role': 'recycler' },
        { 'name': 'Demo User', 'email': 'user@example.com', 'password': 'userpass', 'role': 'user' },
        { 'name': 'Local Doc', 'email': 'doctor1@example.com', 'password': 'doctorpass', 'role': 'doctor' }
    ]

    res = db.users.insert_many(users)
    user_ids = res.inserted_ids
    print(f'Inserted {len(user_ids)} users')

    # Create 10 pickup requests across several users (mix of demo user and others)
    pickups = []
    sample_types = ['Laptop', 'Desktop PC', 'Mobile Devices', 'Printer', 'UPS Batteries', 'Monitor', 'Router', 'Keyboard', 'Battery', 'TV']
    areas = ['Andheri', 'Borivali', 'Thane', 'Dadar', 'Vashi', 'Ghatkopar', 'Kurla', 'Chembur', 'Mulund', 'Kandivali']

    # create pickups for demo user and for the "doctor" and a couple others
    for i in range(10):
        pickup = {
            'user_id': user_ids[6],
            'user_name': 'Demo User',
            'area': areas[i],
            'address': f'{areas[i]} Sample Address',
            'latitude': 19.0 + 0.01 * i,
            'longitude': 72.8 + 0.01 * i,
            'ewaste_weight': 8 + i,
            'approx_weight': 8 + i,
            'ewaste_type': sample_types[i],
            'description': 'Seeded request',
            'items': [ { 'type': sample_types[i], 'weight': 8 + i, 'description': 'Sample item' } ],
            'status': 'pending',
            'engineer_price': None,
            'created_at': datetime.utcnow()
        }
        pickups.append(pickup)

    res_p = db.pickup_requests.insert_many(pickups)
    pickup_ids = res_p.inserted_ids
    print(f'Inserted {len(pickup_ids)} pickup requests')

    # Create multiple collection clusters and assign to engineers/drivers
    engineer1 = db.users.find_one({'email': 'engineer1@example.com'})
    engineer2 = db.users.find_one({'email': 'engineer2@example.com'})
    driver1 = db.users.find_one({'email': 'driver1@example.com'})
    driver2 = db.users.find_one({'email': 'driver2@example.com'})

    clusters = []
    # cluster 1: first 4 pickups assigned to engineer1/driver1
    c1_users = [ { 'user_id': pickup_ids[i], 'weight': pickups[i]['approx_weight'], 'distance_km': round(1.5 + i*0.5,1) } for i in range(4) ]
    cluster1 = {
        'engineer_id': str(engineer1['_id']) if engineer1 else None,
        'driver_id': str(driver1['_id']) if driver1 else None,
        'users': c1_users,
        'status': 'in_progress',
        'scheduled_for': datetime.utcnow(),
        'estimated_duration_minutes': 120,
        'route_distance_km': 12.5,
        'created_at': datetime.utcnow(),
        'total_weight': sum([u['weight'] for u in c1_users])
    }
    clusters.append(cluster1)

    # cluster 2: next 3 pickups assigned to engineer2/driver2
    c2_users = [ { 'user_id': pickup_ids[i], 'weight': pickups[i]['approx_weight'], 'distance_km': round(2.0 + i*0.6,1) } for i in range(4,7) ]
    cluster2 = {
        'engineer_id': str(engineer2['_id']) if engineer2 else None,
        'driver_id': str(driver2['_id']) if driver2 else None,
        'users': c2_users,
        'status': 'scheduled',
        'scheduled_for': datetime.utcnow(),
        'estimated_duration_minutes': 90,
        'route_distance_km': 9.2,
        'created_at': datetime.utcnow(),
        'total_weight': sum([u['weight'] for u in c2_users])
    }
    clusters.append(cluster2)

    # cluster 3: remaining pickups assigned to engineer1/driver2
    c3_users = [ { 'user_id': pickup_ids[i], 'weight': pickups[i]['approx_weight'], 'distance_km': round(1.0 + i*0.4,1) } for i in range(7,10) ]
    cluster3 = {
        'engineer_id': str(engineer1['_id']) if engineer1 else None,
        'driver_id': str(driver2['_id']) if driver2 else None,
        'users': c3_users,
        'status': 'scheduled',
        'scheduled_for': datetime.utcnow(),
        'estimated_duration_minutes': 75,
        'route_distance_km': 8.0,
        'created_at': datetime.utcnow(),
        'total_weight': sum([u['weight'] for u in c3_users])
    }
    clusters.append(cluster3)

    res_c = db.collection_clusters.insert_many(clusters)
    cluster_ids = res_c.inserted_ids
    print(f'Inserted {len(cluster_ids)} collection clusters')

    # Update pickup_requests to reference cluster_id for assigned pickups
    # Cluster 1 -> pickup_ids[0..3], Cluster2 -> [4..6], Cluster3 -> [7..9]
    for idx, cid in enumerate(cluster_ids):
        if idx == 0:
            ids = pickup_ids[0:4]
        elif idx == 1:
            ids = pickup_ids[4:7]
        else:
            ids = pickup_ids[7:10]
        db.pickup_requests.update_many({'_id': {'$in': ids}}, {'$set': {'cluster_id': str(cid), 'status': 'in_progress'}})

    # Category prices (simple fixtures)
    categories = [
        {'category': 'Laptop', 'base_price_per_kg': 300},
        {'category': 'Desktop PC', 'base_price_per_kg': 250},
        {'category': 'Mobile Devices', 'base_price_per_kg': 500}
    ]
    db.category_prices.insert_many(categories)
    print('Inserted category prices')

    # Metal prices snapshot
    db.metal_prices.insert_one({
        'gold_inr_per_gram': 5000.0,
        'silver_inr_per_gram': 70.0,
        'copper_inr_per_kg': 850.0,
        'aluminum_inr_per_kg': 150.0,
        'timestamp': datetime.utcnow()
    })
    print('Inserted metal prices snapshot')

    print('\nSeeding complete. Summary:')
    print('  users:', db.users.count_documents({}))
    print('  pickup_requests:', db.pickup_requests.count_documents({}))
    print('  collection_clusters:', db.collection_clusters.count_documents({}))
    print('  category_prices:', db.category_prices.count_documents({}))


if __name__ == '__main__':
    reset_and_seed()