# Customer Service RMH - Auth Service

Микросервис авторизации и управления пользователями, работающий по протоколу gRPC. Обеспечивает безопасность всей системы RMH через механизмы JWT и ролевую модель доступа.

## 🏗 Архитектура и структура

Проект построен на принципах Clean Architecture и DDD, что обеспечивает изоляцию логики безопасности от технической реализации.
``` Plaintext

.
├── proto/               # Исходные .proto определения
├── alembic/             # Миграции базы данных
├── src/
│   ├── api/             # gRPC сервер (точка входа)
│   ├── application/     # Сервисы бизнес-логики (Auth/User)
│   ├── domain/          # Ядро: сущности и интерфейсы репозиториев
│   └── infrastructure/  # Техническая реализация
│       ├── config/      # Настройки и конфигурация логгера
│       ├── db/          # Модели SQLAlchemy и скрипты инициализации
│       ├── grpc/        # Сгенерированные из proto классы
│       ├── repository.py # Реализация доступа к БД
│       └── security.py   # Логика JWT и хеширования паролей
└── tests/               # Unit и интеграционные тесты
```

## 🚀 Стек технологий

*    Language: Python 3.13

*    Communication: gRPC (grpcio, protobuf)

*    Database: PostgreSQL 15, SQLAlchemy 2.0 (Async), asyncpg

*    Security: PyJWT, Argon2, Passlib

*    Migrations: Alembic

*    DevOps: Docker, Docker Compose

## ⚙️ Переменные окружения (.env)

Создайте файл .env в корневой директории. Сервис использует гибкую настройку портов для предотвращения конфликтов.

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
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 🛠 Запуск проекта
**Автономный запуск (Docker)**

Сервис может работать независимо для тестирования gRPC методов:
``` Bash

docker compose up --build
```
При старте контейнер автоматически:

1.   Ожидает готовности базы данных PostgreSQL.

2.   Применяет миграции Alembic (alembic upgrade head).

3.   Инициализирует учетную запись администратора из .env.

4.   Запускает gRPC сервер на порту 50051.

## 📡 gRPC Интерфейс (Proto)

Описание методов находится в proto/auth.proto. Основные операции:

*    Login: Аутентификация и выдача JWT.

*    ValidateToken: Проверка токена и возврат данных пользователя.

*    User Management: Полный цикл CRUD операций (Create, List, Update, Delete).

## 🧪 Тестирование и логи

Запуск тестов:
``` Bash

docker compose exec auth-service pytest
```
Логи приложения сохраняются в директорию logs/app.log внутри контейнера и дублируются в консоль.

## 📝 Работа с миграциями

Если вы изменили модели в src/infrastructure/db/model/:

*    Создать миграцию: docker compose exec auth-service alembic revision --autogenerate -m "description"

*    Применить: docker compose exec auth-service alembic upgrade head

🔗 Связанные проекты
## 🔗 Связанные проекты

*    [Main Backend: Customer Service RMH - Backend](https://github.com/winamu6/customer_servic) — основной потребитель сервиса (FastAPI).

*    [Frontend: Customer Service RMH - Client](https://github.com/winamu6/commerse-service-client) — интерфейс управления.