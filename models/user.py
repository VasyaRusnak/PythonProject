from db import get_db

class User:
    collection = get_db()["Keys"]

    @staticmethod
    def all():
        return list(User.collection.find())

    @staticmethod
    def find_by_login(login):
        return User.collection.find_one({"login": login})

    @staticmethod
    def find_by_login_and_password(login, password):
        return User.collection.find_one({"login": login, "password": password})

    @staticmethod
    def insert(data):
        # data: {"login": ..., "password": ..., "role": ...}
        return User.collection.insert_one(data)

    @staticmethod
    def update(login, data):
        return User.collection.update_one({"login": login}, {"$set": data})

    @staticmethod
    def delete(login):
        return User.collection.delete_one({"login": login})

    @staticmethod
    def search_by_role(role):
        return list(User.collection.find({"role": role}))

    @staticmethod
    def forgot_password(login):
        # Повертає пароль для введеного логіна (НЕБЕЗПЕЧНО, краще реалізувати скидання)
        user = User.find_by_login(login)
        return user["password"] if user else None
