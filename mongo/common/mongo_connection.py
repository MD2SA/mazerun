import os
from pymongo import MongoClient

def get_mongo_db(uri, db_name):
    # Overwrite URI if environment variable is present (Docker support)
    docker_uri = os.environ.get("MONGO_URI")
    if docker_uri:
        uri = docker_uri
        
    client = MongoClient(uri)
    db = client[db_name]
    print(f"[DB] Connected to MongoDB: {db_name} (via {uri})")
    return db
