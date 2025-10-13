from models.booking import Booking
from models.room import Room
from models.client import Client
from models.firm import Firm
from models.complaint import Complaint
from bson import ObjectId
from datetime import datetime

def parse_user_date(date_str):
    """Парсить дату з формату дд-мм-рррр у datetime"""
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except Exception:
        # fallback: спроба стандартного формату
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return None

# 1) Обсяг бронювання по фірмі і категорії номерів
def bookings_by_firm_and_room_type(firm_id, start_date, end_date):
    start = parse_user_date(start_date)
    end = parse_user_date(end_date)
    bookings = Booking.collection.find({
        "firm_id": firm_id,
        "check_in": {"$gte": start},
        "check_out": {"$lte": end}
    })
    counts = {}
    for b in bookings:
        room = Room.find_by_id(b["room_id"])
        room_type = room.get("type", "unknown") if room else "unknown"
        counts[room_type] = counts.get(room_type, 0) + 1

    result = [{"room_type": k, "count": v} for k, v in counts.items()]
    return result or []

# 2) Вільні номери
def free_rooms(characteristics=None):
    query = {"status": "free"}
    if characteristics:
        query.update(characteristics)
    rooms = Room.collection.find(query)
    result = [r for r in rooms]
    return result or []

# 3) Інформація про конкретний вільний номер
def free_room_info(room_id):
    room = Room.find_by_id(room_id)
    if not room:
        return []
    bookings = Booking.collection.find({"room_id": room_id})
    occupied_dates = [(b["check_in"], b["check_out"]) for b in bookings]
    return [{"room": room, "occupied_dates": occupied_dates}]

# 4) Нові клієнти за період
def new_clients(start_date, end_date):
    start = parse_user_date(start_date)
    end = parse_user_date(end_date)
    clients = Client.collection.find({
        "registration_date": {"$gte": start, "$lte": end}
    })
    return [c for c in clients] or []

# 5) Інформація про конкретного клієнта
def client_info(client_id):
    client = Client.find_by_id(client_id)
    if not client:
        return []
    bookings_cursor = Booking.collection.find({"client_id": client_id})
    bookings = list(bookings_cursor)
    bills = [b.get("bill", 0) for b in bookings]
    room_ids = [b["room_id"] for b in bookings]
    rooms = [Room.find_by_id(rid) for rid in room_ids]
    return [{
        "client": client,
        "bookings_count": len(bookings),
        "rooms": rooms,
        "total_paid": sum(bills)
    }]

# 6) Постоялець з конкретного номера
def guest_room_info(room_id):
    bookings_cursor = Booking.collection.find({"room_id": room_id, "status": "active"})
    bookings = list(bookings_cursor)
    result = []
    for b in bookings:
        client = Client.find_by_id(b["client_id"])
        complaints = list(Complaint.collection.find({"client_id": b["client_id"]}))
        result.append({
            "client": client,
            "additional_services": b.get("services", []),
            "complaints": complaints
        })
    return result or []

# 7) Фірми з договорами на період
def firms_with_bookings(start_date, end_date):
    start = parse_user_date(start_date)
    end = parse_user_date(end_date)
    bookings = Booking.collection.find({
        "check_in": {"$gte": start},
        "check_out": {"$lte": end},
        "firm_id": {"$exists": True}
    })
    firm_ids = set([b["firm_id"] for b in bookings])
    result = [Firm.find_by_id(fid) for fid in firm_ids if Firm.find_by_id(fid)]
    return result or []

# 8) Клієнти за характеристиками кімнат і період
def clients_by_room_characteristics(characteristics, start_date, end_date):
    start = parse_user_date(start_date)
    end = parse_user_date(end_date)
    rooms_cursor = Room.collection.find(characteristics)
    room_ids = [r["_id"] for r in rooms_cursor]
    if not room_ids:
        return []
    bookings_cursor = Booking.collection.find({
        "room_id": {"$in": room_ids},
        "check_in": {"$gte": start},
        "check_out": {"$lte": end}
    })
    client_ids = set([b["client_id"] for b in bookings_cursor])
    result = [Client.find_by_id(cid) for cid in client_ids if Client.find_by_id(cid)]
    return result or []

# 9) Заселені номери, що звільняються до дати
def occupied_rooms_until(date):
    target = parse_user_date(date)
    bookings_cursor = Booking.collection.find({
        "check_out": {"$lte": target},
        "status": "active"
    })
    room_ids = [b["room_id"] for b in bookings_cursor]
    result = [Room.find_by_id(rid) for rid in room_ids if Room.find_by_id(rid)]
    return result or []

# 10) Незадоволені клієнти та їх скарги
def unsatisfied_clients():
    complaints_cursor = Complaint.collection.find()
    result = []
    for c in complaints_cursor:
        client = Client.find_by_id(c["client_id"])
        if client:
            result.append({
                "client": client,
                "complaint": c
            })
    return result or []