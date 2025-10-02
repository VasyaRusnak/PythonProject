# services/report_service.py
from db import get_db

def total_income():
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$income"}}}]
    result = list(get_db()["Finance"].aggregate(pipeline))
    return result[0]["total"] if result else 0

def clients_with_debt():
    return list(get_db()["Clients"].find({"debts": {"$gt": 0}}))

def bookings_by_status(status):
    return list(get_db()["Bookings"].find({"status": status}))
