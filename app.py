from flask import Flask, render_template, request, redirect, url_for, session, jsonify, has_request_context, g
import sqlite3
import bcrypt
import uuid
import time
import random
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from state import IDEMPOTENCY_STORE
from api.task_routes import tasks_api
from config import Config


#4
from api.task_routes import tasks_api


app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "specificgroupofpeople"





def create_initial_tables():
    with app.app_context():
        import domain.user
        import domain.task

        with app.app_context():
            print("--- INFO: Attempting database connection and table creation ---")
            try:
                db.create_all()
                print("--- INFO: Database tables created successfully (or already exist) ---")
            except Exception as e:
                import sys
                print(f"--- FATAL ERROR: Failed to create database tables: {e} ---", file=sys.stderr)
                sys.exit(1)


@app.before_request
def setup_request_context():
    time.sleep(0.0)

    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    g.request_id = request_id

    r = random.random()

    if r > 2:
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

    request_id = "UNKNOWN_REQUEST_ID"
    response_body = {
        "error": name,
        "code": f"HTTP_{code}",
        "requestId": request_id
    }
    return jsonify(response_body), code


@app.route("/register", methods=["GET", "POST"])
def register():
    from domain.user import User
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())


        try:
            new_user = User(username=username, password=hashed)
            db.session.add(new_user)
            db.session.commit()
        except sqlite3.IntegrityError:

            return "Помилка: Користувач з таким логіном вже існує", 400
        except Exception as e:
            db.session.rollback()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    from domain.user import User
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password, user.password):
            session["user_id"] = user.id
            session["username"] = user.username
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
    # Завдання: GET /health
    return jsonify({
        "status": "ok",
        "requestId": g.request_id
    }), 200


app.register_blueprint(tasks_api, url_prefix='/api/v1')

if __name__ == "__main__":
    db.init_app(app)
    create_initial_tables()
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=False)