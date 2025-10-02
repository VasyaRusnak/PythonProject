# services/auth_service.py
from models.user import User

def login_user(login, password):
    return User.find_by_login_and_password(login, password)

def register_user(login, password, role="guest"):
    if User.find_by_login(login):
        return False
    User.insert({"login": login, "password": password, "role": role})
    return True

def forgot_password(login):
    user = User.find_by_login(login)
    return user["password"] if user else None

def request_role_upgrade(login):
    from db import get_db
    get_db()["Requests"].insert_one({"login": login, "status": "pending"})