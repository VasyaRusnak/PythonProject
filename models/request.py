from db import get_db

class Request:
    collection = get_db()["Requests"]

    @staticmethod
    def pending():
        return list(Request.collection.find({"status": "pending"}))

    @staticmethod
    def insert(login):
        if not Request.collection.find_one({"login": login, "status": "pending"}):
            Request.collection.insert_one({"login": login, "status": "pending"})

    @staticmethod
    def approve(login):
        # Оновлюємо роль користувача
        user_collection = get_db()["Keys"]
        user_collection.update_one({"login": login}, {"$set": {"role": "authorized"}})
        # Оновлюємо статус заявки
        Request.collection.update_one({"login": login, "status": "pending"}, {"$set": {"status": "approved"}})

    @staticmethod
    def reject(login):
        Request.collection.update_one({"login": login, "status": "pending"}, {"$set": {"status": "rejected"}})
