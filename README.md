# 🚀 Vektor API — Production стек бекенду

Високопродуктивний, масштабований REST API на базі **Django 6.x** та **Django REST Framework**, повністю контейнеризований за допомогою Docker. Архітектура спроєктована з урахуванням production-вимог: ізоляція компонентів, асинхронна черга задач, вебсервер Nginx і захищений тунель Cloudflare.

---

## 🛠 Архітектура та технологічний стек

### Core Backend
* **Framework:** Python 3.11+ / Django 6.0.x / Django REST Framework (DRF) 3.17+
* **Authentication:** JWT (JSON Web Tokens) через `djangorestframework-simplejwt`
* **API Documentation:** OpenAPI 3.0 / Swagger UI через `drf-spectacular`
* **Database:** PostgreSQL 16 (драйвер `psycopg2-binary`)
* **Environment:** `django-environ` для безпечного керування конфігурацією

### Asynchronous Stack (черга задач)
* **Task Queue:** Celery 5.6+
* **Message Broker & Backend:** Redis 8.0+

### Infrastructure & Security
* **Web Server:** Nginx 1.25 (Alpine) — виступає як Reverse Proxy, розвантажує Django та самостійно віддає статичні/медіа файли.
* **Tunneling:** Cloudflare Tunnel (`cloudflared`) — забезпечує безпечний доступ до API з інтернету без відкриття портів хост-машини назовні.
* **Code Quality:** Ruff & Flake8 для лінтингу та форматування коду.

---

## 📁 Структура Docker-сервісів (Docker Compose)

Проєкт розділений на ізольовані шари всередині внутрішньої мережі Docker:
1. `db` — СУБД PostgreSQL 16 з автоматичною перевіркою доступності (`healthcheck`).
2. `redis` — In-memory брокер для Celery-воркерів.
3. `web` — Додаток Django (Gunicorn). Порт `8000` прихований всередині мережі Docker.
4. `nginx` — Єдина точка входу. Проксіює запити до Django і віддає статику/медіа в режимі *Read-Only* (`:ro`). Локально доступний на порті `8000`.
5. `worker` — Контейнер Celery для виконання важких фонових задач.
6. `cloudflared` — Пробросує трафік з мережі Cloudflare прямо в контейнер `nginx`.

---

## ⚙️ Налаштування оточення (`.env`)

Для запуску проєкту створіть файл `.env` у кореневій директорії додатка. Приклад заповнення:

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

## 🚀 Швидкий запуск проєкту

### 1. Збірка і запуск контейнерів
Переконайтесь, що Docker запущений, і виконайте команду в корені проєкту:
```bash
docker compose up -d --build
```
*Команда автоматично збере образи бекенду і Nginx, застосує міграції бази даних, зібрає статичні файли додатка і запустить всі сервіси у фоновому режимі.*

### 2. Перевірка статусу
```bash
docker compose ps
```

### 3. Створення облікового запису адміністратора (Суперкористувач Django)
```bash
docker compose exec web python manage.py createsuperuser
```

---

## Можливості та їх реалізації

| Можливості | Де |
|-------------|-----|
| Каталог: фільтр, пошук, сортування, пагінація | `products/filters.py`, `products/views.py` |
| Сторінка товару, відгук, рейтинг | `products/views.py` (`ProductDetailView`) |
| Відгук тільки після покупки | `reviews/services.py`, `reviews/views.py` |
| Кошик на сесії з перевіркою залишків | `orders/cart.py` |
| Оформлення замовлення (транзакція, блокування складу, фіксація цін) | `orders/services.py` (`create_order`) |
| Email-push (async) | `orders/tasks.py` |
| Кабінет: реєстрація, вхід, історія, профіль, зміна паролю | `users/` |
| Адмінка: фільтри, інлайн, дія, аналітика (виручка/топ) | `*/admin.py` |
| REST API (товари, замовлення, відгуки) + JWT | `*/api.py`, `config/api_urls.py` |
| Картинки → WebP при load | `products/imaging.py` |
| Тести | `tests/` |

## 📖 Ендпоїнти API і документація

Завдяки інтеграції `drf-spectacular`, схема API генерується автоматично. Після запуску проєкту ви можете отримати доступ до інтерактивної документації за такими адресами:

* **Swagger UI:** `http://localhost:8000/api/docs/`
* **Raw OpenAPI Schema (YAML/JSON):** `http://localhost:8000/api/schema/`

---

## 🛠 Корисні команди для розробки і адміністрування

### Моніторинг логів
* **Логи всіх сервісів в реальному часі:**
  ```bash
docker compose logs -f
```
* **Логи конкретного сервісу (наприклад, Django веб-додатку або Celery):**
  ```bash
docker compose logs web -f
docker compose logs worker -f
```

### Робота з базою даних і міграціями
* **Створення нових міграцій (після зміни моделей):**
  ```bash
docker compose exec web python manage.py makemigrations
```
* **Застосування міграцій:**
  ```bash
docker compose exec web python manage.py migrate
```

### Зупинка і обслуговування
* **Зупинка контейнерів з збереженням даних у томах:**
  ```bash
docker compose down
```
* **Повне очищення контейнерів і локальних анонімних томів (очистить кеш шляхів):**
  ```bash
docker compose down -v
```
* **Перезавантаження веб-сервера Nginx (наприклад, після оновлення `default.conf`):**
  ```bash
docker compose restart nginx
```

---

## Структура

```
myshop/
├── config/            # settings/{base,dev,prod}, urls, api_urls, celery, wsgi/asgi
├── users/             # кастомний User, auth, кабінет, API реєстрація
├── products/          # каталог, фільтри, моделі, менеджер, WebP, seed-команда, API
├── orders/            # кошик, сервіс create_order, замовлення, async email, API
├── reviews/           # відгуки (web + API), перевірка покупки
├── templates/         # шаблони (+ admin override для аналітики)
├── static/ · media/
├── tests/             # pytest-suite
├── docker-compose.yml · docker-compose.prod.yml · Dockerfile
├── requirements.txt · setup.cfg
└── manage.py
```

**Індекси — під реальні запити**

| Індекс | Під який запит |
|--------|------------------|
| `Product(is_active, category)` | каталог: активні товари категорії |
| `Product(price)` | фільтр по range та сортування по ціні |
| `Product(-created_at)` | сортування спочатку нові |
| `Order(user, status)` | історія замовлення з фільтром по статусу |
| `Order(user, -created_at)` | історія замовлення користувача |
| `Order(status, created_at)` | аналітика по статусам/періодам |
| `Review(product, -created_at)` | список відгуків товару |
