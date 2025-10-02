from db import get_db

def get_pending_requests():
    # Беремо лише статус "pending"
    return list(get_db()["Requests"].find({"status": "pending"}))

def approve_request(login, new_role="authorized"):
    db = get_db()
    # Оновлюємо роль користувача
    db["Keys"].update_one({"login": login}, {"$set": {"role": new_role}})
    # Оновлюємо тільки pending заявки
    db["Requests"].update_many({"login": login, "status": "pending"}, {"$set": {"status": "approved"}})

def reject_request(login):
    db = get_db()
    # Оновлюємо тільки pending заявки
    db["Requests"].update_many({"login": login, "status": "pending"}, {"$set": {"status": "rejected"}})
