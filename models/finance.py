# models/finance.py
from db import get_db

class Finance:
    collection = get_db()["Finance"]

    @staticmethod
    def all():
        return list(Finance.collection.find())

    @staticmethod
    def find_by_id(finance_id):
        return Finance.collection.find_one({"_id": finance_id})

    @staticmethod
    def insert(data):
        return Finance.collection.insert_one(data)

    @staticmethod
    def update(finance_id, data):
        return Finance.collection.update_one({"_id": finance_id}, {"$set": data})

    @staticmethod
    def delete(finance_id):
        return Finance.collection.delete_one({"_id": finance_id})

    @staticmethod
    def total_income():
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$income"}}}]
        result = list(Finance.collection.aggregate(pipeline))
        return result[0]["total"] if result else 0