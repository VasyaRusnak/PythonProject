from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.user import User
from models.hotel import Hotel
from models.room import Room
from models.client import Client
from models.firm import Firm
from models.booking import Booking
from models.service import Service
from models.complaint import Complaint
from models.finance import Finance
from models.request import Request
from services.report_service import total_income, clients_with_debt, bookings_by_status
from services.queries_service import *
from datetime import datetime
import json
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Словник сутностей ---
entity_classes = {
    "Hotels": Hotel,
    "Rooms": Room,
    "Clients": Client,
    "Firms": Firm,
    "Bookings": Booking,
    "Services": Service,
    "Complaints": Complaint,
    "Finance": Finance,
    "Keys": User
}

# --- Людські назви запитів ---
query_names = {
    1: "Бронювання по фірмі та типу номерів",
    2: "Вільні номери за характеристиками",
    3: "Інформація про номер",
    4: "Нові клієнти за період",
    5: "Інформація про клієнта",
    6: "Інформація про гостя в номері",
    7: "Фірми з бронюваннями за період",
    8: "Клієнти за характеристиками номера",
    9: "Зайняті номери на дату",
    10: "Незадоволені клієнти"
}

# --- Клас для збережених результатів ---
class SavedResult:
    @staticmethod
    def insert(login, query_name, result_data):
        client = MongoClient()
        db = client["hotel_db"]
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

# --- Dashboard ---
@app.route("/")
def dashboard():
    role = session.get("role", "guest")
    return render_template("dashboard.html", role=role)

# --- Login ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_ = request.form["login"]
        password = request.form["password"]
        user = User.find_by_login_and_password(login_, password)
        if user:
            session["login"] = login_
            session["role"] = user.get("role", "guest")
            return redirect(url_for("dashboard"))
        else:
            flash("Невірний логін або пароль")
    return render_template("login.html")

# --- Logout ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- Register ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login_ = request.form["login"]
        password = request.form["password"]
        existing = User.find_by_login(login_)
        if existing:
            flash("Користувач з таким логіном вже існує")
        else:
            User.insert({"login": login_, "password": password, "role": "guest"})
            flash("Реєстрація успішна, чекайте на підтвердження прав")
            return redirect(url_for("login"))
    return render_template("register.html")


# --- Admin Panel ---
@app.route("/admin")
def admin_panel():
    role = session.get("role", "guest")
    if role not in ["admin", "operator"]:
        flash("Доступ заборонено")
        return redirect(url_for("dashboard"))
    requests_ = Request.pending() if role == "admin" else []
    return render_template("admin_panel.html", requests=requests_)

# --- Add Operator (Admin only) ---
@app.route("/add_operator", methods=["GET", "POST"])
def add_operator():
    if session.get("role") != "admin":
        flash("Доступ заборонено")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        login_ = request.form["login"]
        password = request.form["password"]
        existing = User.find_by_login(login_)
        if existing:
            flash("Користувач з таким логіном вже існує")
        else:
            User.insert({"login": login_, "password": password, "role": "operator"})
            flash("Оператор створений успішно")
            return redirect(url_for("admin_panel"))
    return render_template("add_operator.html")

# --- CRUD ---
@app.route("/crud/<entity>")
def crud(entity):
    role = session.get("role", "guest")
    can_edit = role in ["admin", "operator"]
    cls = entity_classes.get(entity)
    if not cls:
        flash("Невідома сутність")
        return redirect(url_for("dashboard"))

    data = cls.all()
    for row in data:
        if '_id' not in row:
            for key in ['id', f'{entity.lower()}_id']:
                if key in row:
                    row['_id'] = row[key]
                    break
            else:
                row['_id'] = None
    return render_template("crud.html", entity=entity, data=data, role=role, can_edit=can_edit)

@app.route("/edit/<entity>/<id>", methods=["GET", "POST"])
def edit_entity(entity, id):
    role = session.get("role", "guest")
    if role not in ["admin", "operator"]:
        flash("Доступ заборонено")
        return redirect(url_for("dashboard"))
    cls = entity_classes.get(entity)
    if not cls:
        flash("Невідома сутність")
        return redirect(url_for("dashboard"))

    record = cls.find_by_id(id)
    if request.method == "POST":
        data_ = {key: request.form[key] for key in request.form}
        cls.update(id, data_)
        flash(f"{entity} оновлено")
        return redirect(url_for("crud", entity=entity))
    return render_template("edit_entity.html", entity=entity, record=record)

@app.route("/delete/<entity>/<id>")
def delete_entity(entity, id):
    role = session.get("role", "guest")
    if role not in ["admin", "operator"]:
        flash("Доступ заборонено")
        return redirect(url_for("dashboard"))
    cls = entity_classes.get(entity)
    if not cls:
        flash("Невідома сутність")
        return redirect(url_for("dashboard"))

    cls.delete(id)
    flash(f"{entity} видалено")
    return redirect(url_for("crud", entity=entity))

# --- Request Upgrade ---
@app.route("/request_upgrade")
def request_upgrade_route():
    if "login" not in session:
        flash("Вхід потрібен")
        return redirect(url_for("login"))
    login_ = session["login"]
    Request.insert(login_)
    flash("Запит на підвищення прав відправлено адміністратору")
    return redirect(url_for("dashboard"))

# --- Queries Dashboard ---
@app.route("/queries")
def queries_dashboard():
    role = session.get("role", "guest")
    if role not in ["authorized","admin","operator"]:
        flash("Доступ до запитів дозволено лише авторизованим користувачам!")
        return redirect(url_for("dashboard"))
    return render_template("queries.html", role=role)

# --- Queries ---
def parse_user_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except Exception:
        return date_str

@app.route("/queries/<int:query_id>", methods=["GET", "POST"])
def run_query(query_id):
    role = session.get("role", "guest")
    if role not in ["authorized","admin","operator"]:
        flash("Доступ до запитів дозволено лише авторизованим користувачам!")
        return redirect(url_for("dashboard"))

    data = []
    if request.method == "POST":
        params = request.form.to_dict()
        for key in ["start_date", "end_date", "date"]:
            if key in params and params[key]:
                params[key] = parse_user_date(params[key])

        characteristics = None
        if "characteristics" in params:
            raw = params["characteristics"]
            if raw and raw.strip():
                try:
                    characteristics = json.loads(raw)
                except Exception:
                    characteristics = None

        # --- Виконання запитів ---
        if query_id == 1:
            data = bookings_by_firm_and_room_type(params["firm_id"], params["start_date"], params["end_date"])
        elif query_id == 2:
            data = free_rooms(characteristics)
        elif query_id == 3:
            data = free_room_info(params["room_id"])
        elif query_id == 4:
            data = new_clients(params["start_date"], params["end_date"])
        elif query_id == 5:
            data = client_info(params["client_id"])
        elif query_id == 6:
            data = guest_room_info(params["room_id"])
        elif query_id == 7:
            data = firms_with_bookings(params["start_date"], params["end_date"])
        elif query_id == 8:
            data = clients_by_room_characteristics(characteristics, params["start_date"], params["end_date"])
        elif query_id == 9:
            data = occupied_rooms_until(params["date"])
        elif query_id == 10:
            data = unsatisfied_clients()

        # --- Зберігаємо результат ---
        query_name = query_names.get(query_id, f"Запит {query_id}")
        SavedResult.insert(session["login"], query_name, data)

    return render_template("query_result.html", data=data, query_id=query_id, role=role)

# --- Saved Results ---
@app.route("/saved_results")
def saved_results():
    if "login" not in session:
        flash("Вхід потрібен")
        return redirect(url_for("login"))
    login_ = session["login"]
    results = SavedResult.all_by_user(login_)
    return render_template("saved_results.html", results=results)

# --- Approve / Reject Requests ---
@app.route("/approve/<login_>")
def approve(login_):
    if session.get("role") != "admin":
        flash("Доступ заборонено")
        return redirect(url_for("dashboard"))
    Request.approve(login_)
    flash(f"Користувачу {login_} надано права авторизованого користувача")
    return redirect(url_for("admin_panel"))

@app.route("/reject/<login_>")
def reject(login_):
    if session.get("role") != "admin":
        flash("Доступ заборонено")
        return redirect(url_for("dashboard"))
    Request.reject(login_)
    flash(f"Заявку користувача {login_} відхилено")
    return redirect(url_for("admin_panel"))

# --- Reports ---
@app.route("/reports")
def reports():
    role = session.get("role", "guest")
    income = total_income()
    debtors = clients_with_debt()
    active_bookings = bookings_by_status("active")

    return render_template(
        "reports.html",
        income=income,
        debtors=debtors,
        active_bookings=active_bookings,
        role=role
    )
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password_route():
    if request.method == "POST":
        login_ = request.form.get("login")
        phone = request.form.get("phone")

        user = User.find_by_login(login_)
        if not user:
            flash("Користувача не знайдено", "danger")
            return render_template("forgot_password.html")

        # якщо користувач є, але ще не ввели номер — просимо номер
        if not phone:
            flash("Введіть номер телефону, прив'язаний до акаунта", "info")
            return render_template("forgot_password.html", login=login_, step=2)

        # перевірка номера телефону
        if user.get("phone") == phone:
            flash(f"Ваш пароль: {user['password']}", "success")
        else:
            flash("Номер телефону не співпадає", "danger")

    return render_template("forgot_password.html")

if __name__ == "__main__":
    app.run(debug=True)
