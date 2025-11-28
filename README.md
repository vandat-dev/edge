# Edge Device Service for Hospital Integration

A FastAPI-based edge service deployed inside hospital infrastructure. The service ingests clinical data from hospital
systems, normalizes it, and securely pushes it to the central Platform. The codebase embraces clean architecture and
Domain-Driven Design (DDD) to keep the business rules clear and maintainable.

## System Context

```
Hospital Systems  ──►  Edge Device (this project)  ──►  Cloud Platform
```

- Collects patient and hospital device data through local adapters (future modules).
- Performs validation, caching and optional enrichment close to where data is generated.
- Publishes normalized events and exposes REST endpoints for remote management.
- Operates in environments with limited connectivity; uses lightweight SQLite storage.

## Technology Stack

- **Runtime**: Python 3.10+, FastAPI, Uvicorn
- **Database**: SQLite (Async I/O via `aiosqlite`)
- **ORM**: SQLAlchemy 2.x Async
- **Auth**: PyJWT, bcrypt
- **Storage**: MinIO client hooks (optional)
- **Testing**: Pytest suite

## Getting Started

### 1. Clone & Install

```bash
git clone <repository-url>
cd edge
pip install poetry
poetry install
```

### 2. Configure Environment

Create `.env` in the project root:

```env
# Database (SQLite file path is relative to project root)
SQLITE_DB_PATH=database.db

# Authentication
JWT_SECRET_KEY=super-secret-jwt-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_IN_MINUTES=60
REFRESH_TOKEN_EXPIRES_IN_DAYS=7

# API
API_PREFIX=/api
VERSION=0.1
ALLOW_ORIGINS=*
DEBUG=true

# MinIO (optional integration)
MINIO_ENDPOINT=localhost:9000
MINIO_PUBLIC_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=edge-storage
MINIO_SECURE=false
MINIO_PUBLIC_SECURE=false
```

> Legacy PostgreSQL variables can remain in `.env`; they are ignored.

### 3. Run the Service

```bash
uvicorn app.main:app --reload --port 8080
```

- SQLite file (default `database.db`) is created automatically and tables are generated on startup.
- Swagger UI available at `http://localhost:8080/docs`.

### 4. Create the First Admin (optional)

```bash
make create-admin
```

This script ensures tables exist and inserts an active admin user.

## Authentication Flow

1. `POST /api/user/login` with email/password → receives `access_token` & `refresh_token`.
2. Use Swagger's **Authorize** button or send `Authorization: Bearer <access_token>` header.
3. When the access token expires, call `POST /api/user/refresh` with the refresh token to obtain a new pair.
4. Protected endpoints require the bearer token (e.g. `/api/user/me`, user management APIs).

## Working with SQLite

- Default database file: `database.db` in project root.
- To inspect data, open the file with DataGrip/DB Browser using the full path (e.g. `path/database.db`).
- Removing the file resets the database; the app recreates tables on next start.


