# Customer Service RMH - Auth Service

Микросервис авторизации и управления пользователями, работающий по протоколу gRPC. Обеспечивает безопасность всей экосистемы RMH через механизмы JWT и ролевую модель доступа.

## 🏗 Архитектура сервиса

Проект построен на принципах Clean Architecture и DDD, что обеспечивает изоляцию логики безопасности от инфраструктуры.

*    gRPC API (src/api): Реализация сервера на основе Protobuf определений.

*    Application (src/application): Сервисы авторизации и управления пользователями (бизнес-логика).

*    Domain (src/domain): Ядро системы, содержащее сущности пользователя и интерфейсы репозиториев.

*    Infrastructure (src/infrastructure):

       *   Security: Хеширование паролей (Argon2/Bcrypt) и генерация JWT.

       *   DB: Асинхронное взаимодействие с PostgreSQL через SQLAlchemy 2.0.

       *   Config: Валидация настроек через Pydantic Settings.

## 🚀 Стек технологий

*    Language: Python 3.11

*    Communication: gRPC (grpcio, protobuf)

*    Database: PostgreSQL 15, SQLAlchemy 2.0 (Async), asyncpg

*    Security: PyJWT, Argon2, Passlib

*    Migrations: Alembic

*    DevOps: Docker, Docker Compose

## ⚙️ Переменные окружения (.env)

Создайте файл .env в корневой директории. Сервис использует гибкую настройку портов для предотвращения конфликтов с основной БД.
``` Ini, TOML

# Auth Database
AUTH_DB_HOST=auth-db
AUTH_DB_PORT=5433
AUTH_DB_USER=postgres
AUTH_DB_PASS=1111
AUTH_DB_NAME=auth_db

# gRPC Settings
AUTH_GRPC_PORT=50051

# Default Admin (Создается автоматически при старте)
ADMIN_LOGIN=admin
ADMIN_PASSWORD=your_secure_password

# Security
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## 🛠 Запуск проекта
Автономный запуск (Docker)

Сервис может работать независимо для тестирования gRPC методов:
```Bash
docker-compose up --build
```

При старте контейнер автоматически:

*    Ожидает готовности базы данных.

*    Применяет миграции Alembic.

*    Создает учетную запись администратора из .env.

*    Запускает gRPC сервер на порту 50051.

### Интеграция с основным проектом

Сервис автоматически подключается к общей сети microservices_network.

## 📡 gRPC Интерфейс (Proto)

Основные методы, определенные в auth.proto:

*    Login: Аутентификация и выдача JWT.

*    ValidateToken: Проверка токена и возврат payload (id, login, role).

*    CreateUser / UpdateUser / DeleteUser: CRUD операции над пользователями.

*    ListUsers: Получение списка всех зарегистрированных пользователей.

## 📝 Работа с миграциями

Миграции запускаются внутри контейнера:

*    Создать новую: docker compose exec auth-service alembic revision --autogenerate -m "description"

*    Обновить БД: docker compose exec auth-service alembic upgrade head

## 🔗 Связанные проекты

*    [Main Backend: Customer Service RMH - Backend](https://github.com/winamu6/customer_service_RMH) — основной потребитель сервиса (FastAPI).

*    [Frontend: Customer Service RMH - Client](https://github.com/winamu6/commerse-service-client) — интерфейс управления.