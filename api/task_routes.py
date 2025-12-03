from flask import Blueprint, request, jsonify, g, session
import uuid
from datetime import datetime
import json
# ВАЖЛИВО: Імпортуємо сховище та функції з app.py
from app import IDEMPOTENCY_STORE, get_db_connection

tasks_api = Blueprint('tasks_api', __name__)


# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def authenticate_api():
    """Перевіряє авторизацію через сесію."""
    if 'user_id' not in session:
        # Повертаємо 401 Unauthorized для API
        return jsonify({
            "error": "Unauthorized",
            "code": "AUTH_REQUIRED",
            "requestId": g.request_id
        }), 401
    return None  # Успішна авторизація


def serialize_task(task_data, request_id):
    """Форматує дані завдання відповідно до TaskResponse DTO."""
    return {
        "id": task_data['id'],
        "user_id": task_data['user_id'],
        "title": task_data['title'],
        "is_completed": task_data.get('is_completed', False),
        "created_at": task_data.get('created_at'),
        "updated_at": task_data.get('updated_at', None),
        "requestId": request_id
    }


# --- ENDPOINT: Ідемпотентний POST /tasks ---

@tasks_api.route("/tasks", methods=["POST"])
def create_task_idempotent():
    # 1. Перевірка авторизації
    auth_response = authenticate_api()
    if auth_response:
        return auth_response

    # 2. Перевірка Idempotency-Key
    idem_key = request.headers.get("Idempotency-Key")
    if not idem_key:
        return jsonify({
            "error": "Idempotency key is required",
            "code": "IDEMPOTENCY_KEY_REQUIRED",
            "requestId": g.request_id
        }), 400

    # 3. Перевірка сховища для ідемпотентності
    if idem_key in IDEMPOTENCY_STORE:
        # Повторний запит: повертаємо збережений результат
        status, payload = IDEMPOTENCY_STORE[idem_key]
        payload["requestId"] = g.request_id
        return jsonify(payload), status

    # 4. Бізнес-логіка (якщо ключ новий)
    try:
        data = request.get_json()
        title = data.get("title")

        # Валідація DTO
        if not title or len(title.strip()) == 0:
            return jsonify({
                "error": "Validation Error",
                "code": "TITLE_REQUIRED",
                "details": [{"field": "title", "message": "Title is required and cannot be empty"}],
                "requestId": g.request_id
            }), 400

        # Симуляція Service/DB-логіки (заміна на реальну логіку у service/task_service.py)
        task_id = str(uuid.uuid4())
        new_task_data = {
            "id": task_id,
            "user_id": session['user_id'],
            "title": title.strip(),
            "is_completed": False,
            "created_at": datetime.now().isoformat() + "Z"
        }

        # ⚠️ Тут має бути виклик service/task_service.py для збереження у БД
        # task_service.create_task(session['user_id'], title)

        # 5. Збереження результату та повернення
        response_data = serialize_task(new_task_data, g.request_id)

        # Зберігаємо статус 201 та тіло відповіді у сховищі
        IDEMPOTENCY_STORE[idem_key] = (201, response_data)

        return jsonify(response_data), 201

    except Exception as e:
        # Непередбачувана помилка під час обробки
        return jsonify({
            "error": "Unexpected Error",
            "code": "TASK_CREATION_FAILED",
            "requestId": g.request_id
        }), 500


# --- ENDPOINT: GET /tasks (Базовий Read) ---

@tasks_api.route("/tasks", methods=["GET"])
def list_tasks():
    auth_response = authenticate_api()
    if auth_response:
        return auth_response

    # ⚠️ Тут має бути виклик service/task_service.py для отримання завдань з БД
    # current_tasks = task_service.get_all_tasks(session['user_id'])

    # Симуляція порожнього списку
    tasks = []

    response_list = [serialize_task(t, g.request_id) for t in tasks]
    return jsonify(response_list), 200

# ⚠️ Додайте роути для GET /tasks/{id}, PATCH /tasks/{id}, DELETE /tasks/{id}
