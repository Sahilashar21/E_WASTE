from pymongo import MongoClient
from datetime import datetime
import os

# ---------------- CONFIG ----------------
# Use the same URI as app.py
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "ewaste_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ---------------- CLEAN OLD DATA ----------------
print("Cleaning old data...")
db.pickup_requests.delete_many({})
db.collection_clusters.delete_many({})
db.users.delete_many({}) # Clear users to re-seed with new roles

print("Old data cleared.")

# ---------------- SEED USERS (Warehouse, Engineer, Driver, Recycler) ----------------
users = [
    {
        'name': 'Main Warehouse Admin',
        'email': 'warehouse@example.com',
        'password': 'warehousepass',
        'role': 'warehouse',
        'mobile': '9999999990'
    },
    {
        'name': 'Ramesh Engineer',
        'email': 'engineer1@example.com',
        'password': 'engineerpass',
        'role': 'engineer',
        'mobile': '9999999991'
    },
    {
        'name': 'Suresh Engineer',
        'email': 'engineer2@example.com',
        'password': 'engineerpass',
        'role': 'engineer',
        'mobile': '9999999992'
    },
    {
        'name': 'Mahesh Driver',
        'email': 'driver1@example.com',
        'password': 'driverpass',
        'role': 'driver',
        'mobile': '9999999993'
    },
    {
        'name': 'Ganesh Driver',
        'email': 'driver2@example.com',
        'password': 'driverpass',
        'role': 'driver',
        'mobile': '9999999994'
    },
    {
        'name': 'Green Earth Recyclers',
        'email': 'recycler@example.com',
        'password': 'recyclerpass',
        'role': 'recycler',
        'mobile': '9999999995',
        'address': 'MIDC Industrial Area, Navi Mumbai'
    }
]

db.users.insert_many(users)
print(f"{len(users)} users inserted (Warehouse, Engineers, Drivers, Recycler).")

# Fetch IDs for assignment logic if needed later
engineer1 = db.users.find_one({'email': 'engineer1@example.com'})
driver1 = db.users.find_one({'email': 'driver1@example.com'})

# ---------------- SEED PICKUP REQUESTS ----------------
# These represent requests submitted by users
requests = [
    {
        "user_id": "test_user_1", # Simulating the logged-in user's ID
        "user_name": "Rahul Sharma",
        "area": "Andheri East",
        "address": "Andheri East, Mumbai",
        "latitude": 19.1176,
        "longitude": 72.8631,
        "ewaste_weight": 60,       # Required by warehouse logic
        "approx_weight": 60,       # Required by user dashboard
        "ewaste_type": "Desktop PC",
        "description": "Old office desktop, monitor and CPU",
        "items": [
            {"type": "Desktop PC", "weight": 60, "description": "Full set"}
        ],
        "status": "pending",
        "cluster_id": None,
        "engineer_price": None,
        "created_at": datetime.utcnow()
    },
    {
        "user_id": "test_user_2",
        "user_name": "Amit Verma",
        "area": "Jogeshwari West",
        "address": "Jogeshwari West, Mumbai",
        "latitude": 19.1360,
        "longitude": 72.8486,
        "ewaste_weight": 30,
        "approx_weight": 30,
        "ewaste_type": "Laptop",
        "description": "Broken laptop and charger",
        "items": [
            {"type": "Laptop", "weight": 30, "description": "Broken screen"}
        ],
        "status": "pending",
        "cluster_id": None,
        "engineer_price": None,
        "created_at": datetime.utcnow()
    },
    {
        "user_id": "test_user_3",
        "user_name": "Suresh Patil",
        "area": "Borivali East",
        "address": "Borivali East, Mumbai",
        "latitude": 19.2290,
        "longitude": 72.8567,
        "ewaste_weight": 25,
        "approx_weight": 25,
        "ewaste_type": "Printer",
        "description": "Heavy duty printer",
        "items": [
            {"type": "Printer", "weight": 25, "description": "Not working"}
        ],
        "status": "pending",
        "cluster_id": None,
        "engineer_price": None,
        "created_at": datetime.utcnow()
    },
    {
        "user_id": "test_user_4",
        "user_name": "Neha Joshi",
        "area": "Thane West",
        "address": "Thane West",
        "latitude": 19.2183,
        "longitude": 72.9781,
        "ewaste_weight": 40,
        "approx_weight": 40,
        "ewaste_type": "Office PCs",
        "description": "2 old CPUs",
        "items": [
            {"type": "CPU", "weight": 20, "description": "Unit 1"},
            {"type": "CPU", "weight": 20, "description": "Unit 2"}
        ],
        "status": "pending",
        "cluster_id": None,
        "engineer_price": None,
        "created_at": datetime.utcnow()
    },
    {
        "user_id": "test_user_5",
        "user_name": "Karan Mehta",
        "area": "Kalyan",
        "address": "Kalyan",
        "latitude": 19.2403,
        "longitude": 73.1305,
        "ewaste_weight": 55,
        "approx_weight": 55,
        "ewaste_type": "Server Racks",
        "description": "Small server rack",
        "items": [
            {"type": "Server Rack", "weight": 55, "description": "Metal"}
        ],
        "status": "pending",
        "cluster_id": None,
        "engineer_price": None,
        "created_at": datetime.utcnow()
    },
    {
        "user_id": "test_user_6",
        "user_name": "Priya Nair",
        "area": "Navi Mumbai",
        "address": "Navi Mumbai",
        "latitude": 19.0330,
        "longitude": 73.0297,
        "ewaste_weight": 20,
        "approx_weight": 20,
        "ewaste_type": "Mobile Devices",
        "description": "Batch of old phones",
        "items": [
            {"type": "Mobiles", "weight": 20, "description": "Mixed lot"}
        ],
        "status": "pending",
        "cluster_id": None,
        "engineer_price": None,
        "created_at": datetime.utcnow()
    },
    {
        "user_id": "test_user_7",
        "user_name": "Vikas Singh",
        "area": "Panvel",
        "address": "Panvel",
        "latitude": 18.9894,
        "longitude": 73.1175,
        "ewaste_weight": 35,
        "approx_weight": 35,
        "ewaste_type": "UPS Batteries",
        "description": "Lead acid batteries",
        "items": [
            {"type": "Battery", "weight": 35, "description": "Heavy"}
        ],
        "status": "pending",
        "cluster_id": None,
        "engineer_price": None,
        "created_at": datetime.utcnow()
    }
]

# ---------------- INSERT DATA ----------------
db.pickup_requests.insert_many(requests)

print(f"{len(requests)} pickup requests inserted successfully.")

# ---------------- VERIFY ----------------
print("\nSeeded Requests:")
for u in db.pickup_requests.find():
    print(f"- {u.get('user_name', 'Unknown')} | {u.get('ewaste_weight')} kg | {u.get('area')}")

print("\n✅ Database seeded successfully.")
print("You can now:")
print("1. Login as Warehouse Admin (warehouse@example.com)")
print("2. Go to /warehouse/dashboard to assign Engineers AND Drivers.")