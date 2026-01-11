# MongoDB connection helper for other modules
from pymongo import MongoClient
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv

load_dotenv()

mongo = PyMongo()

def get_db():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ewaste_db')
    client = MongoClient(mongo_uri)
    db = client['ewaste_db']
    return db
