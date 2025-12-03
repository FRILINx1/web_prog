from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"  # треба змінити на свій секретний ключ

def get_db_connection():
    conn = sqlite3.connect("test.db")
    conn.row_factory = sqlite3.Row
    return conn

# ------------------ РЕЄСТРАЦІЯ ------------------
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
        except Exception as e:
            conn.close()
            return f"Помилка: {e}"
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

# ------------------ ЛОГІН ------------------
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
            return "Неправильний логін або пароль"
    return render_template("login.html")

# ------------------ ЛОГАУТ ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ------------------ ЗАХИЩЕНА СТОРІНКА ------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return f"Привіт, {session['username']}! Це закрита сторінка."

# ------------------ ГОЛОВНА ------------------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
