from pymongo import MongoClient

# HARDCODED MongoDB URI
MONGO_URI = "mongodb+srv://darpanmeher1346_db_user:E8kreTF6Z8G5mFbn@cluster0.mhkyevr.mongodb.net/?retryWrites=true&w=majority"

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # ⬅ IMPORTANT

    return _client["ewaste_db"]
