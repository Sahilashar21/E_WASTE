"""
Seed additional demo data: 3 engineers, 5 recyclers, many pickup_requests (weights in grams), and several clusters
Run with: python seed_more_demo.py
"""
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import os

# Connect to MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ewaste_db')
client = MongoClient(MONGO_URI)
db = client['ewaste_db']

users = db.users
pickups = db.pickup_requests
clusters = db.collection_clusters

WAREHOUSES = [
    "North Warehouse (Borivali)",
    "West Warehouse (Andheri)",
    "East Warehouse (Thane)",
    "South Warehouse (Colaba)",
    "CENTRAL HUB (Ghatkopar)"
]

def create_user_if_missing(name, email, mobile, address, role):
    if not users.find_one({'email': email}):
        users.insert_one({
            'name': name,
            'email': email,
            'mobile': mobile,
            'address': address,
            'password': generate_password_hash('password123'),
            'role': role
        })

# Add 3 engineers
for i in range(1, 4):
    create_user_if_missing(f'Engineer {i+1}', f'engineer{i+1}@example.com', f'90000000{i+1}', f'Engineer Addr {i+1}', 'engineer')

# Add 5 recyclers
for i in range(1, 6):
    create_user_if_missing(f'Recycler {i}', f'recycler{i}@example.com', f'80000000{i}', f'Recycler Addr {i}', 'recycler')

# Create many pickup requests (weights in grams)
ewaste_types = ['Mobile', 'Laptop', 'TV', 'Battery', 'Cables', 'Fridge']
areas = ['Borivali', 'Andheri', 'Thane', 'Colaba', 'Ghatkopar', 'Dadar']

inserted_pickups = []
for i in range(1, 31):
    wt = random.randint(200, 5000)  # grams
    created_at = datetime.utcnow() - timedelta(days=random.randint(0, 13), hours=random.randint(0,23))
    doc = {
        'user_name': f'Demo User {i}',
        'email': f'user{i}@example.com',
        'mobile': f'70000000{i:02d}',
        'address': f'Address {i}',
        'area': random.choice(areas),
        'status': random.choice(['pending', 'collected', 'delivered', 'recycled', 'scheduled']),
        'approx_weight': wt,
        'ewaste_weight': wt,
        'final_weight': wt if random.random() < 0.6 else None,
        'ewaste_type': random.choice(ewaste_types),
        'created_at': created_at,
        'updated_at': created_at,
        'items': [{'name': 'sample', 'qty': 1}],
    }
    res = pickups.insert_one(doc)
    inserted_pickups.append(res.inserted_id)

# Create some clusters referencing the above pickups and assign destinations
for idx, hub in enumerate(WAREHOUSES[:4]):
    # group a few pickups
    group = inserted_pickups[idx*5:(idx+1)*5]
    if not group:
        continue
    users_arr = []
    total_wt = 0
    for pid in group:
        p = pickups.find_one({'_id': pid})
        w = p.get('final_weight') or p.get('approx_weight') or p.get('ewaste_weight') or 0
        users_arr.append({'user_id': pid, 'weight': w, 'distance_km': 0})
        total_wt += w

    cluster_doc = {
        'anchor_user_id': str(group[0]),
        'anchor_location': {'lat': 19.0 + random.random()/10, 'lng': 72.8 + random.random()/10},
        'destination': hub,
        'dist_to_hub': round(random.uniform(1.0, 10.0), 2),
        'radius_used_km': round(random.uniform(1.0, 5.0), 2),
        'total_weight': total_wt,
        'user_count': len(users_arr),
        'users': users_arr,
        'efficiency_score': round(total_wt / (random.uniform(1.0, 5.0) or 1), 2),
        'status': random.choice(['delivered', 'assigned', 'completed']),
        'admin_override': False,
        'created_at': datetime.utcnow() - timedelta(days=random.randint(0,7))
    }
    cid = clusters.insert_one(cluster_doc).inserted_id
    # update pickups to reference cluster_id
    pickups.update_many({'_id': {'$in': group}}, {'$set': {'cluster_id': str(cid)}})

print('Seeding complete: added engineers, recyclers, pickups, clusters.')
print('Added pickups:', len(inserted_pickups))
print('Run the app and check the dashboard/advanced analytics, and hub inventory endpoints.')
