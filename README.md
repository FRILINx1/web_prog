
[![CI Status](https://github.com/FRILINx1/web_prog/actions/workflows/main.yml/badge.svg)](https://github.com/FRILINx1/web_prog/actions/workflows/main.yml)

## 📦 Підхід до Continuous Delivery (CD)

Ми використовуємо **GitHub Actions** для автоматичної збірки та публікації контейнерного образу нашого API-сервісу.

* **Обраний метод (Варіант А):** **GitHub Container Registry (GHCR)**.
* **Workflow:** `.github/workflows/main.yml`.
* **Тригер:** При кожному `push` у гілки `main`/`master` (після успішного проходження юніт-тестів).
* **Адреса образу:** `ghcr.io/<owner>/<repo>-api:<SHA>`

## 🚀 Локальний запуск системи (Docker Compose)

Для запуску всіх компонентів (API та PostgreSQL) локально, переконайтеся, що встановлено Docker та Docker Compose.

1.  **Збірка та запуск:**
    ```bash
    docker compose up -d
    ```
2.  **Перевірка API:**
    Сервіс буде доступний на порту 8080.
    ```bash
    curl http://localhost:8080/health
    ```
3.  **Зупинка:**
    ```bash
    docker compose down
    ```