from pymongo import MongoClient

class SavedResult:
    @staticmethod
    def insert(login, query_name, result_data):
        client = MongoClient()  # Підключення до MongoDB
        db = client["hotel_db"]  # Тут ім'я твоєї бази даних
        collection = db["SavedResults"]
        collection.insert_one({
            "login": login,
            "query_name": query_name,
            "result_data": result_data
        })

    @staticmethod
    def all_by_user(login):
        client = MongoClient()
        db = client["hotel_db"]
        collection = db["SavedResults"]
        return list(collection.find({"login": login}))
