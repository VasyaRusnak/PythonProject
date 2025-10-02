# models/service.py
from db import get_db

class Service:
    collection = get_db()["Services"]

    @staticmethod
    def all():
        return list(Service.collection.find())

    @staticmethod
    def find_by_id(service_id):
        return Service.collection.find_one({"_id": service_id})

    @staticmethod
    def insert(data):
        return Service.collection.insert_one(data)

    @staticmethod
    def update(service_id, data):
        return Service.collection.update_one({"_id": service_id}, {"$set": data})

    @staticmethod
    def delete(service_id):
        return Service.collection.delete_one({"_id": service_id})

    @staticmethod
    def search_by_type(service_type):
        return list(Service.collection.find({"type": {"$regex": service_type, "$options": "i"}}))
