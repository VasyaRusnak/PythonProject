# models/hotel.py
from db import get_db

class Hotel:
    collection = get_db()["Hotels"]

    @staticmethod
    def all():
        return list(Hotel.collection.find())

    @staticmethod
    def find_by_id(hotel_id):
        return Hotel.collection.find_one({"_id": hotel_id})

    @staticmethod
    def insert(data):
        return Hotel.collection.insert_one(data)

    @staticmethod
    def update(hotel_id, data):
        return Hotel.collection.update_one({"_id": hotel_id}, {"$set": data})

    @staticmethod
    def delete(hotel_id):
        return Hotel.collection.delete_one({"_id": hotel_id})

    @staticmethod
    def search_by_class(hotel_class):
        return list(Hotel.collection.find({"class": hotel_class}))