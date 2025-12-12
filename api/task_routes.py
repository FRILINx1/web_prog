from flask import Blueprint, request, jsonify, g, session
import json
import uuid
from state import IDEMPOTENCY_STORE
from service.task_service import TaskService

tasks_api = Blueprint('tasks_api', __name__)
task_service = TaskService()




def authenticate_api():
    """Перевіряє авторизацію через сесію."""
    if 'user_id' not in session:
        return jsonify({
            "error": "Unauthorized",
            "code": "AUTH_REQUIRED",
            "requestId": g.request_id
        }), 401
    return None


def _task_error(message: str, code: str, status_code: int = 400, details=None):
    return jsonify({
        "error": message,
        "code": code,
        "details": details,
        "requestId": g.request_id
    }), status_code



@tasks_api.route("/tasks", methods=["POST"])
def create_task_idempotent():
    # 1. Перевірка авторизації
    auth_response = authenticate_api()
    if auth_response:
        return auth_response

    idem_key = request.headers.get("Idempotency-Key")
    if not idem_key:
        return _task_error("Idempotency key is required", "IDEMPOTENCY_KEY_REQUIRED", 400)

    if idem_key in IDEMPOTENCY_STORE:
        print(f"INFO: Reusing idempotent result for key {idem_key}")
        status, payload = IDEMPOTENCY_STORE[idem_key]
        payload["requestId"] = g.request_id
        return jsonify(payload), status

    # 4. Бізнес-логіка
    try:
        data = request.get_json()
        title = data.get("title", "")

        new_task = task_service.create_task(session['user_id'], title)

        response_data = new_task.to_dict()
        response_data["requestId"] = g.request_id

        IDEMPOTENCY_STORE[idem_key] = (201, response_data)

        return jsonify(response_data), 201

    except ValueError as ve:
        msg, code = str(ve).split(': ')
        return _task_error("Validation Error", code, 400, details=[{"field": "title", "message": msg}])

    except Exception as e:
        return _task_error("Unexpected Error", "TASK_CREATION_FAILED", 500)


@tasks_api.route("/tasks", methods=["GET"])
def list_tasks():
    auth_response = authenticate_api()
    if auth_response:
        return auth_response

    task_service.get_all_tasks(session['user_id'])

    # Симуляція:
    tasks = []

    response_list = [t.to_dict() for t in tasks]
    return jsonify(response_list), 200

#  GET /tasks/{id}, PATCH /tasks/{id}, DELETE /tasks/{id}