from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import sqlite3
import bcrypt
import uuid
from datetime import datetime
import time
import random

# --- Ініціалізація та конфігурація ---
app = Flask(__name__)
# ЗВЕРНІТЬ УВАГУ: Використовуйте безпечний ключ для production!
app.secret_key = "supersecretkey"

# Сховище для ідемпотентності (Пам'ять: тільки для демонстрації!)
IDEMPOTENCY_STORE = {}


def get_db_connection():
    """Створює з'єднання з БД."""
    conn = sqlite3.connect("test.db")
    conn.row_factory = sqlite3.Row
    return conn


# --- MIDDLEWARE: Стійкість та Кореляція ---

@app.before_request
def setup_request_context():
    """Встановлює X-Request-Id та імітує мережеві збої."""

    # 1. X-Request-Id (Кореляція)
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    g.request_id = request_id

    # 2. Імітація затримок/збоїв (Injection)
    r = random.random()

    # Імітація затримки (> 1с) - 15% запитів
    if r < 0.15:
        time.sleep(1.2 + random.random() * 0.8)

    # Імітація помилок сервера (500/503) - 20% запитів
    if r > 2.80:
        err = "SERVER_UNAVAILABLE" if random.random() < 0.5 else "UNEXPECTED_ERROR"
        code = 503 if err == "SERVER_UNAVAILABLE" else 500
        return jsonify({
            "error": "Internal server error",
            "code": err,
            "requestId": g.request_id
        }), code

    # 3. Імітація Rate Limit (429) - (Тільки для демонстрації, логіка спрощена)
    # Якщо потрібно: перевіряти IP та ліміти тут.
    # if should_rate_limit(request.remote_addr):
    #     response = jsonify({"error": "TOO_MANY_REQUESTS", "code": "RATE_LIMIT", "requestId": g.request_id})
    #     response.headers['Retry-After'] = '2'
    #     return response, 429


@app.after_request
def add_request_id_header(response):
    """Додає заголовок X-Request-Id до всіх відповідей."""
    if hasattr(g, 'request_id'):
        response.headers["X-Request-Id"] = g.request_id
    return response


# --- Єдиний обробник помилок (для внутрішніх помилок) ---
@app.errorhandler(Exception)
def handle_error(e):
    # Обробка 4xx і 5xx помилок, які не були спіймані раніше
    code = getattr(e, 'code', 500)
    name = getattr(e, 'name', 'Internal Server Error')

    # Форматуємо помилку відповідно до ErrorResponse
    response_body = {
        "error": name,
        "code": f"HTTP_{code}",
        "requestId": g.request_id
    }
    return jsonify(response_body), code


# --- Загальні та Auth-роути (можна винести в окремий api/auth_routes.py) ---

# ------------------ РЕЄСТРАЦІЯ ------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    # ... (Ваша оригінальна логіка реєстрації)
    # Для стислості, тут припускаємо, що вона залишилася у app.py
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Помилка: Користувач з таким логіном вже існує", 400
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")


# ------------------ ЛОГІН ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    # ... (Ваша оригінальна логіка логіну)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password, user["password"]):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            return "Неправильний логін або пароль", 401
    return render_template("login.html")


# ------------------ ЛОГАУТ та DASHBOARD ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    # У реальності тут буде рендер HTML з таблицею завдань
    return f"Привіт, {session['username']}! Це закрита сторінка."


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ------------------ HEALTH CHECK (Обов'язкова вимога) ------------------
@app.route("/health", methods=["GET"])
def health_check():
    """Перевірка стану застосунку."""
    # Зверніть увагу: X-Request-Id додається через @app.after_request
    return jsonify({
        "status": "ok",
        "requestId": g.request_id
    }), 200


# --- Реєстрація API роутів ---
# ⚠️ ПІСЛЯ ТОГО, ЯК ВИ СТВОРИТЕ api/task_routes.py, ДОДАЙТЕ ЦЕЙ ІМПОРТ:
# from api.task_routes import tasks_api
# app.register_blueprint(tasks_api, url_prefix='/api/v1')

if __name__ == "__main__":
    app.run(debug=True)