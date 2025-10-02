# models/complaint.py
from db import get_db

class Complaint:
    collection = get_db()["Complaints"]

    @staticmethod
    def all():
        return list(Complaint.collection.find())

    @staticmethod
    def find_by_id(complaint_id):
        return Complaint.collection.find_one({"_id": complaint_id})

    @staticmethod
    def insert(data):
        return Complaint.collection.insert_one(data)

    @staticmethod
    def update(complaint_id, data):
        return Complaint.collection.update_one({"_id": complaint_id}, {"$set": data})

    @staticmethod
    def delete(complaint_id):
        return Complaint.collection.delete_one({"_id": complaint_id})

    @staticmethod
    def search_by_client(client_id):
        return list(Complaint.collection.find({"client_id": client_id}))