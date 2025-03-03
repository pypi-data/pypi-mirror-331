from pymongo.mongo_client import MongoClient
import os
import logging

MONGO_DB_USER = os.environ.get("MONGO_DB_USER")
MONGO_DB_PWD = os.environ.get("MONGO_DB_PWD")

connect_string = f"mongodb+srv://{MONGO_DB_USER}:{MONGO_DB_PWD}@fin4all.r3ihnkl.mongodb.net/?retryWrites=true&w=majority&appName=Fin4All"

client = MongoClient(connect_string)
db = client['Fin4All']

# assumes data is an object
def insert_into_collection(collection_name, data):
    try:
        create_collection_if_not_exists(collection_name)
        db[collection_name].insert_one(data)
    except Exception as e:
        logging.error(e)

def delete_from_collection_if_exists(collection_name, query):
    create_collection_if_not_exists(collection_name)
    db[collection_name].delete_many(query)

def update_collection(collection_name, new_data, filter):
    try:
        create_collection_if_not_exists(collection_name)
        db[collection_name].update_one(
            filter,
            {"$set": new_data}  # Use $set to update specific fields
        )
    except Exception as e:
        logging.error("Collection update failed: " + str(e))

# returns either None or a dict
def find_from_collection(collection_name, query):
    try:
        create_collection_if_not_exists(collection_name)
        document = db[collection_name].find_one(query)
        if document is None:
            return None
        document['_id'] = str(document['_id'])
        return document
    except Exception as e:
        logging.error(e)
        return None

def find_all_from_collection(collection_name, query):
    try:
        create_collection_if_not_exists(collection_name)
        documents = db[collection_name].find(query)
        result = []
        for document in documents:
            document['_id'] = str(document['_id'])
            result.append(document)
        return result
    except Exception as e:
        logging.error(e)
        return None

def create_collection_if_not_exists(collection_name):
    try:
        collection_names = db.list_collection_names()
        if collection_name not in collection_names:
            db.create_collection(collection_name)
            logging.info(f"Created the '{collection_name}' collection.")
    except Exception as e:
        logging.error(f"Error creating collection: {e}")

def clear_collection(collection_name):
    try:
        collection = db[collection_name]
        collection.delete_many({})
        logging.info(f"Deleted all documents from the '{collection_name}' collection.")
    except Exception as e:
        logging.error(f"Error clearing collection: {e}")