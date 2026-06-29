# 🚀 Vektor API — Backend Production Stack

Высокопроизводительный, масштабируемый REST API на базе **Django 6.x** и **Django REST Framework**, полностью контейнеризированный с помощью Docker. Архитектура спроектирована с учетом Production-требований: изоляция компонентов, асинхронная очередь задач, веб-сервер Nginx и защищенный туннель Cloudflare.

---

## 🛠 Архитектура и Технологический стек

### Core Backend
* **Framework:** Python 3.11+ / Django 6.0.x / Django REST Framework (DRF) 3.17+
* **Authentication:** JWT (JSON Web Tokens) через `djangorestframework-simplejwt`
* **API Documentation:** OpenAPI 3.0 / Swagger UI через `drf-spectacular`
* **Database:** PostgreSQL 16 (драйвер `psycopg2-binary`)
* **Environment:** `django-environ` для безопасного управления конфигурацией

### Asynchronous Stack (Очередь задач)
* **Task Queue:** Celery 5.6+
* **Message Broker & Backend:** Redis 8.0+

### Infrastructure & Security
* **Web Server:** Nginx 1.25 (Alpine) — выступает как Reverse Proxy, разгружает Django и самостоятельно раздает статические/медиа файлы.
* **Tunneling:** Cloudflare Tunnel (`cloudflared`) — обеспечивает безопасный доступ к API из интернета без открытия портов хост-машины наружу.
* **Code Quality:** Ruff & Flake8 для линтинга и форматирования кода.

---

## 📁 Структура Docker-сервисов (Docker Compose)

Проект разделен на изолированные слои внутри внутренней сети Docker:
1. `db` — СУБД PostgreSQL 16 с автоматической проверкой доступности (`healthcheck`).
2. `redis` — In-memory брокер для Celery-воркеров.
3. `web` — Приложение Django (Gunicorn). Порт `8000` скрыт внутри сети Docker.
4. `nginx` — Единственная точка входа. Проксирует запросы к Django и отдает статику/медиа в режиме *Read-Only* (`:ro`). Локально доступен на порту `8000`.
5. `worker` — Контейнер Celery для выполнения тяжелых фоновых задач.
6. `cloudflared` — Пробрасывает трафик из сети Cloudflare напрямую в контейнер `nginx`.

---

## ⚙️ Настройка окружения (`.env`)

Для запуска проекта создайте файл `.env` в корневой директории приложения. Пример заполнения:

```env
# Django settings
SECRET_KEY=your_super_secret_production_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# PostgreSQL database configuration
POSTGRES_DB=shop
POSTGRES_USER=shop
POSTGRES_PASSWORD=secure_postgres_password

# Database host connection (for Docker)
DB_HOST=db
DB_PORT=5432

# Cloudflare Tunnel Token
CLOUDFLARE_TUNNEL_TOKEN=your_cloudflare_tunnel_token_here
```

---

## 🚀 Быстрый запуск проекта

### 1. Сборка и запуск контейнеров
Убедитесь, что Docker запущен, и выполните команду в корне проекта:
```bash
docker compose up -d --build
```
*Команда автоматически соберет образы бэкенда и Nginx, применит миграции базы данных, соберет статические файлы приложения и запустит все сервисы в фоновом режиме.*

### 2. Проверка статуса работы
```bash
docker compose ps
```

### 3. Создание учетной записи администратора (Суперпользователь Django)
```bash
docker compose exec web python manage.py createsuperuser
```

---

## 📖 Эндпоинты API и Документация

Благодаря интеграции `drf-spectacular`, схема API генерируется автоматически. После запуска проекта вы можете получить доступ к интерактивной документации по следующим адресам:

* **Swagger UI:** `http://localhost:8000/api/docs/`
* **Raw OpenAPI Schema (YAML/JSON):** `http://localhost:8000/api/schema/`

---

## 🛠 Полезные команды для разработки и администрирования

### Мониторинг логов
* **Логи всех сервисов в реальном времени:**
  ```bash
  docker compose logs -f
  ```
* **Логи конкретного сервиса (например, Django веб-приложения или Celery):**
  ```bash
  docker compose logs web -f
  docker compose logs worker -f
  ```

### Работа с базой данных и миграциями
* **Создание новых миграций (после изменения моделей):**
  ```bash
  docker compose exec web python manage.py makemigrations
  ```
* **Применение миграций:**
  ```bash
  docker compose exec web python manage.py migrate
  ```

### Остановка и обслуживание
* **Остановка контейнеров с сохранением данных в Volumes:**
  ```bash
  docker compose down
  ```
* **Полная очистка контейнеров и локальных анонимных томов (очистит кэш путей):**
  ```bash
  docker compose down -v
  ```
* **Перезапуск веб-сервера Nginx (например, после обновления `default.conf`):**
  ```bash
  docker compose restart nginx
  ```

---

## 🛡 Качество кода (Linting)
Перед отправкой кода в репозиторий рекомендуется проверять проект встроенными линтерами:
```bash
# Проверка кода с помощью Ruff
docker compose exec web ruff check .

# Проверка кода с помощью Flake8
docker compose exec web flake8 .
```
