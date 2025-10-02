# models/client.py
from db import get_db

class Client:
    collection = get_db()["Clients"]

    @staticmethod
    def all():
        return list(Client.collection.find())

    @staticmethod
    def find_by_id(client_id):
        return Client.collection.find_one({"_id": client_id})

    @staticmethod
    def insert(data):
        return Client.collection.insert_one(data)

    @staticmethod
    def update(client_id, data):
        return Client.collection.update_one({"_id": client_id}, {"$set": data})

    @staticmethod
    def delete(client_id):
        return Client.collection.delete_one({"_id": client_id})

    @staticmethod
    def search_by_name(name):
        return list(Client.collection.find({"name": {"$regex": name, "$options": "i"}}))

    @staticmethod
    def with_debt():
        return list(Client.collection.find({"debts": {"$gt": 0}}))