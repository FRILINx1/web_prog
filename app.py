from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import sqlite3
import bcrypt
import uuid
import time
import random
from datetime import datetime
from infrastructure.database import get_db_connection

#4
from api.task_routes import tasks_api


app = Flask(__name__)
app.secret_key = "specificgroupofpeople"




#5
@app.before_request
def setup_request_context():

    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    g.request_id = request_id

    r = random.random()

    if r < 0.15:
        # time.sleep(1.2 + random.random() * 0.8)
        pass


    if r > 0.90:
        err = "SERVER_UNAVAILABLE" if random.random() < 0.5 else "UNEXPECTED_ERROR"
        code = 503 if err == "SERVER_UNAVAILABLE" else 500

        return jsonify({
            "error": "Internal server error",
            "code": err,
            "requestId": g.request_id
        }), code


@app.after_request
def add_request_id_header(response):
    if hasattr(g, 'request_id'):
        response.headers["X-Request-Id"] = g.request_id
    return response



@app.errorhandler(Exception)
def handle_error(e):
    code = getattr(e, 'code', 500)
    name = getattr(e, 'name', 'Internal Server Error')

    response_body = {
        "error": name,
        "code": f"HTTP_{code}",
        "requestId": g.request_id
    }
    return jsonify(response_body), code


@app.route("/register", methods=["GET", "POST"])
def register():
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
        except Exception as e:
            conn.close()
            return f"Помилка: {e}", 500
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
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


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return f"Привіт, {session['username']}! Це закрита сторінка."


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/health", methods=["GET"])
def health_check():
    """Перевірка стану застосунку."""
    # Завдання: GET /health
    return jsonify({
        "status": "ok",
        "requestId": g.request_id
    }), 200


app.register_blueprint(tasks_api, url_prefix='/api/v1')

if __name__ == "__main__":
    app.run(debug=True)