# ShoeShop Backend

This is the backend for the ShoeShop application built with FastAPI and SQL Server.

## Features
- JWT Authentication & RBAC
- Product, SKU, and Stock Management
- Shopping Cart & Order Flow
- File Upload for product images
- Audit Logging & Rate Limiting

## Tech Stack
- FastAPI
- SQLAlchemy (Async)
- SQL Server
- Alembic for migrations
- Pydantic v2
- SlowAPI for rate limiting

## Setup Instructions

### Local Environment
1. Ensure SQL Server is installed locally (e.g., `.\SQLEXPRESS`).
2. Install dependencies via Poetry:
   ```bash
   poetry install
   ```
3. Copy `.env.example` to `.env` and configure your settings.
4. Run migrations:
   ```bash
   poetry run alembic upgrade head
   ```
5. Start the server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Docker
To run via Docker:
```bash
docker-compose up -d --build
```
