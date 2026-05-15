# Storage Inventory API (Lab 8)
Реализация событийно-ориентированной архитектуры (Event-Driven Architecture) для выполнения фоновых задач (отправка Email-уведомлений) с использованием RabbitMQ в качестве брокера сообщений.
----
# 🛠 Стек технологий
Framework: FastAPI (Python 3.12+) — асинхронная обработка запросов.

Database: MongoDB + Beanie ODM — документоориентированная БД с асинхронным маппингом моделей.

Object Storage: MinIO (S3-compatible) — надежное хранение бинарных данных (файлов).

Caching: Redis — ускорение доступа к метаданным и спискам файлов с механизмом инвалидации.

Auth: JWT (Access & Refresh tokens) — безопасная авторизация с поддержкой OAuth-провайдеров.

Containerization: Docker & Docker Compose — развертывание всей инфраструктуры одной командой.

Брокер: RabbitMQ.

Библиотека RabbitMQ: aio-pika (асинхронный клиент).

Почтовый клиент: aiosmtplib (асинхронный SMTP).

----
# 🌟 Основные возможности
1. Отказоустойчивость (Dead Letter Exchange)
Для обработки сценариев, когда письмо не может быть отправлено (например, неверный Email), реализован механизм DLX:

Если воркер не может обработать сообщение, оно перемещается в очередь wp.auth.user.registered.dlq.

Это гарантирует, что данные о событиях не будут потеряны при сбоях внешней системы.

2. Совместимость с OAuth (Sparse Indexes)
В модели User реализованы разреженные индексы (sparse=True) для полей yandex_id:

Это позволяет хранить нескольких пользователей с null значением в полях провайдеров, предотвращая ошибку DuplicateKeyError при обычной регистрации [cite: 2026-05-13].

3. Гарантия доставки (Acknowledgements)
Воркер использует контекстный менеджер message.process(requeue=True), который отправляет подтверждение (ACK) в RabbitMQ только после успешного выполнения функции send_welcome_email.
----

# 🚀 Быстрый запуск
Настройте окружение:
Создайте файл .env на основе примера и укажите доступы к MongoDB, MinIO и Redis.
Запустите проект:
```
docker-compose up --build

docker exec -it storage_mongo mongosh -u <user> -p <pass> --authenticationDatabase admin storage_db --eval "db.users.drop()"

docker logs -f storage_api
```

----
🐰 Очереди сообщений (RabbitMQ)
После запуска контейнеров вы можете отслеживать работу очередей через Management UI:

Адрес: http://localhost:15672
~~~~
Логин: student   
Пароль: secure_pass   
~~~~
### Важно: Соединение от воркера появится в панели сразу после запуска, а соединение от API — только в момент первой публикации события (регистрации пользователя) [cite: 2026-05-15].
----

# Документация API:
После запуска Swagger UI будет доступен по адресу: http://localhost:8000/docs
После запуска RabbitMQ будет доступен по адресу: http://localhost:15672/#/
----

# 🏗 Архитектура проекта
app/models/ — модели данных Beanie (MongoDB).

app/schemas/ — схемы валидации Pydantic v2.

app/services/ — бизнес-логика (Auth, Storage, Cache).

app/api/ — эндпоинты FastAPI, разделенные по версиям.

app/core/ — конфигурация клиентов MinIO, Redis и настройки проекта.
