from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["hotel_system"]

# Clients
db.Clients.insert_many([
    {
        "_id": "cl1",
        "name": "Іван Петренко",
        "registration_date": datetime(2024, 9, 1, 10, 0),
        "debts": 0
    },
    {
        "_id": "cl2",
        "name": "Олена Коваль",
        "registration_date": datetime(2024, 10, 1, 12, 0),
        "debts": 500
    }
])

# Firms
db.Firms.insert_one({
    "_id": "f1",
    "name": "ТОВ ТурСервіс",
    "contract_number": "TS-2024-01"
})

# Hotels
db.Hotels.insert_one({
    "_id": "h1",
    "name": "Готель Київ",
    "class": "4*",
    "city": "Київ",
    "address": "вул. Хрещатик, 1",
    "rooms_count": 2
})

# Rooms
db.Rooms.insert_many([
    {
        "_id": "r1",
        "hotel_id": "h1",
        "number": "101",
        "type": "Стандарт",
        "status": "free",
        "price": 1200
    },
    {
        "_id": "r2",
        "hotel_id": "h1",
        "number": "102",
        "type": "Люкс",
        "status": "occupied",
        "price": 2500
    }
])

# Bookings
db.Bookings.insert_many([
    {
        "_id": "b1",
        "client_id": "cl1",
        "firm_id": "f1",
        "room_id": "r2",
        "check_in": datetime(2024, 10, 1, 14, 0),
        "check_out": datetime(2024, 10, 5, 12, 0),
        "status": "active",
        "bill": 10000,
        "services": ["Сніданок", "Трансфер"]
    },
    {
        "_id": "b2",
        "client_id": "cl2",
        "room_id": "r1",
        "check_in": datetime(2024, 10, 10, 14, 0),
        "check_out": datetime(2024, 10, 12, 12, 0),
        "status": "planned",
        "bill": 2400,
        "services": []
    }
])

# Complaints
db.Complaints.insert_one({
    "_id": "cmp1",
    "client_id": "cl1",
    "text": "Не працював кондиціонер",
    "date": datetime(2024, 10, 2, 18, 0)
})

# Finance
db.Finance.insert_many([
    {
        "_id": "fin1",
        "income": 10000,
        "expense": 3000,
        "date": datetime(2024, 10, 5, 12, 0)
    },
    {
        "_id": "fin2",
        "income": 2400,
        "expense": 500,
        "date": datetime(2024, 10, 12, 12, 0)
    }
])

# Services
db.Services.insert_many([
    {
        "_id": "srv1",
        "type": "Сніданок",
        "price": 200
    },
    {
        "_id": "srv2",
        "type": "Трансфер",
        "price": 500
    }
])

# Keys (Users)
db.Keys.insert_many([
    {
        "_id": "admin1",
        "login": "admin",
        "password": "adminpass",
        "role": "admin"
    },
    {
        "_id": "op1",
        "login": "operator",
        "password": "operatorpass",
        "role": "operator"
    },
    {
        "_id": "guest1",
        "login": "guest",
        "password": "guestpass",
        "role": "guest"
    }
])

# Requests
db.Requests.insert_one({
    "_id": "req1",
    "login": "guest",
    "status": "pending"
})

print("Дані успішно імпортовано!")