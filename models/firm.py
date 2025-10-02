# models/firm.py
from db import get_db

class Firm:
    collection = get_db()["Firms"]

    @staticmethod
    def all():
        return list(Firm.collection.find())

    @staticmethod
    def find_by_id(firm_id):
        return Firm.collection.find_one({"_id": firm_id})

    @staticmethod
    def insert(data):
        return Firm.collection.insert_one(data)

    @staticmethod
    def update(firm_id, data):
        return Firm.collection.update_one({"_id": firm_id}, {"$set": data})

    @staticmethod
    def delete(firm_id):
        return Firm.collection.delete_one({"_id": firm_id})

    @staticmethod
    def search_by_name(name):
        return list(Firm.collection.find({"name": {"$regex": name, "$options": "i"}}))