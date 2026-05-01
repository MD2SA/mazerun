from pymongo import MongoClient

def get_mongo_db(uri, db_name):
    client = MongoClient(uri)
    db = client[db_name]
    print(f"[DB] Connected to MongoDB: {db_name}")
    return db
