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

# --- Допоміжна функція ---
def get_entity_data(entity):
    cls = entity_classes.get(entity)
    return cls.all() if cls else []

# --- Dashboard ---
@app.route("/")
def dashboard():
    if "login" not in session:
        return redirect(url_for("login"))
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

# --- CRUD ---
@app.route("/crud/<entity>")
def crud(entity):
    role = session.get("role", "guest")
    if role not in ["admin", "operator", "authorized"]:
        flash("Доступ заборонено")
        return redirect(url_for("dashboard"))

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

    return render_template("crud.html", entity=entity, data=data, role=role)

# --- Edit / Delete (admin/operator only) ---
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

# --- Reports ---
@app.route("/reports")
def reports():
    if "login" not in session:
        return redirect(url_for("login"))

    income = total_income()
    debtors = clients_with_debt()
    active_bookings = bookings_by_status("active")

    return render_template(
        "reports.html",
        income=income,
        debtors=debtors,
        active_bookings=active_bookings
    )

if __name__ == "__main__":
    app.run(debug=True)
