from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import bcrypt
import uuid
from datetime import datetime
from extensions import db
from api.task_routes import tasks_api
from config import Config
from domain.task import Task
from domain.user import User

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "specificgroupofpeople"

db.init_app(app)


def create_initial_tables():
    with app.app_context():
        try:
            db.create_all()
            print("--- INFO: Database tables verified ---")
        except Exception as e:
            print(f"--- FATAL ERROR: {e} ---")


@app.before_request
def setup_request_context():
    g.request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())


@app.after_request
def add_request_id_header(response):
    if hasattr(g, 'request_id'):
        response.headers["X-Request-Id"] = g.request_id
    return response


@app.errorhandler(Exception)
def handle_error(e):
    import traceback
    traceback.print_exc()
    code = getattr(e, 'code', 500)
    return jsonify({
        "error": "Internal Server Error",
        "code": f"HTTP_{code}",
        "requestId": getattr(g, 'request_id', "UNKNOWN")
    }), code


# --- АВТОРИЗАЦІЯ ---

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return "Заповніть всі поля", 400

        hashed_str = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            if User.query.filter_by(username=username).first():
                return "Помилка: Користувач вже існує", 400
            new_user = User(username=username, password=hashed_str)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}", 500
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        return "Невірний логін або пароль", 401
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --- ЗАВДАННЯ ---

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', username=session['username'], tasks=user_tasks)


@app.route('/tasks/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    title = request.form.get('title')
    if title:
        new_task = Task(user_id=session['user_id'], title=title)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/tasks/delete/<task_id>', methods=['POST'])
def delete_task_web(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Знаходимо завдання та перевіряємо, що воно належить поточному користувачу
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if task:
        db.session.delete(task)
        db.session.commit()

    return redirect(url_for('dashboard'))


@app.route("/")
def home():
    return redirect(url_for("dashboard")) if "user_id" in session else redirect(url_for("login"))


@app.route("/health")
def health_check():
    return jsonify({"status": "ok", "requestId": getattr(g, 'request_id', 'none')}), 200


app.register_blueprint(tasks_api, url_prefix='/api/v1')

if __name__ == "__main__":
    create_initial_tables()
    app.run(debug=True, port=5000)