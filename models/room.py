# models/room.py
from db import get_db

class Room:
    collection = get_db()["Rooms"]

    @staticmethod
    def all():
        return list(Room.collection.find())

    @staticmethod
    def find_by_id(room_id):
        return Room.collection.find_one({"_id": room_id})

    @staticmethod
    def insert(data):
        return Room.collection.insert_one(data)

    @staticmethod
    def update(room_id, data):
        return Room.collection.update_one({"_id": room_id}, {"$set": data})

    @staticmethod
    def delete(room_id):
        return Room.collection.delete_one({"_id": room_id})

    @staticmethod
    def search_by_status(status):
        return list(Room.collection.find({"status": status}))