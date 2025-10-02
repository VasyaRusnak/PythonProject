# check_mongo.py
from pymongo import MongoClient


def main():
    try:
        # Підключення до локальної MongoDB
        client = MongoClient("mongodb://localhost:27017/")  # або твій URI MongoDB
        print("Підключення успішне!")

        # Вибір бази даних
        db = client["hotel_system"]  # заміни на свою базу, якщо інша
        print("База даних:", db.name)

        # Виведення списку колекцій
        collections = db.list_collection_names()
        print("Колекції у базі даних:")
        for coll in collections:
            print("-", coll)

        # Перевірка наявності даних у колекціях
        for coll_name in collections:
            collection = db[coll_name]
            count = collection.count_documents({})
            print(f"У колекції '{coll_name}' {count} документів")

            # Виведемо перший документ, якщо є
            if count > 0:
                print("Приклад документа:", collection.find_one())
            print("-" * 40)

    except Exception as e:
        print("Помилка підключення або роботи з БД:", e)


if __name__ == "__main__":
    main()
