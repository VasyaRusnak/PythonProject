# models/booking.py
from db import get_db

class Booking:
    collection = get_db()["Bookings"]

    @staticmethod
    def all():
        return list(Booking.collection.find())

    @staticmethod
    def find_by_id(booking_id):
        return Booking.collection.find_one({"_id": booking_id})

    @staticmethod
    def insert(data):
        return Booking.collection.insert_one(data)

    @staticmethod
    def update(booking_id, data):
        return Booking.collection.update_one({"_id": booking_id}, {"$set": data})

    @staticmethod
    def delete(booking_id):
        return Booking.collection.delete_one({"_id": booking_id})

    @staticmethod
    def search_by_status(status):
        return list(Booking.collection.find({"status": status}))

    @staticmethod
    def search_by_client(client_id):
        return list(Booking.collection.find({"client_id": client_id}))