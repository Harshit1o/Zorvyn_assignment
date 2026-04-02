# Zorvyn Assignment — Backend API

Django REST Framework backend with role-based access control, financial records management, and dashboard analytics.

---

## Tech Stack
- Python 3.12 / Django 6 / Django REST Framework
- PostgreSQL
- JWT Authentication (PyJWT)
- Docker + GitHub Actions CI/CD

---

## Roles

| Role | Permissions |
|---|---|
| `ADMIN` | Full access — manage users, create/update/delete records |
| `ANALYST` | View & filter records, dashboard |
| `VIEWER` | List records (no filters), dashboard |

---

## Apps

| App | Purpose |
|---|---|
| `accounts` | Register, login, JWT auth, role permissions |
| `user_management` | Admin manages VIEWER & ANALYST users |
| `financial_records` | CRUD for income/expense records |
| `dashboard` | Summary, trends, category totals |

---

## API Endpoints

### Auth
```
POST /api/auth/register/     # rate limited: 10/hour
POST /api/auth/login/        # rate limited: 5/minute
POST /api/auth/refresh/      # issue new access token using refresh token
```

Login returns:
- `access_token` (15 minutes)
- `refresh_token` (7 days)

Refresh request body:
```json
{
	"refresh_token": "<refresh_token>"
}
```

### User Management (ADMIN only)
```
GET    /api/manage/users/
POST   /api/manage/users/
GET    /api/manage/users/<id>/
PATCH  /api/manage/users/<id>/
DELETE /api/manage/users/<id>/
```

### Financial Records
```
GET    /api/finance/records/              # all roles (VIEWER: no filters)
POST   /api/finance/records/             # ADMIN only
GET    /api/finance/records/<id>/        # ANALYST, ADMIN
PATCH  /api/finance/records/<id>/        # ADMIN only
DELETE /api/finance/records/<id>/        # ADMIN only (soft delete)
```

**Filters** (ANALYST & ADMIN): `?type=INCOME&category=SALARY&date_from=2026-01-01&date_to=2026-04-01&search=<notes>`  
**Pagination**: `?page=1&page_size=10` (default 10, max 100)

### Dashboard (all roles)
```
GET /api/dashboard/summary/   # totals, category breakdown, trends, recent activity
```

### API Documentation
```
GET /api/schema/   # OpenAPI schema
GET /api/docs/     # Swagger UI
```

---

## Setup

```bash
# 1. Clone & create virtualenv
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@host/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DJANGO_LOG_LEVEL=WARNING
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# 4. Migrate & run
python manage.py migrate
gunicorn zorvyn_assignment.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## Run Tests
```bash
python manage.py test accounts financial_records --keepdb
```

## Docker
```bash
docker build -t zorvyn-assignment-be .
docker run -p 8000:8000 --env-file .env zorvyn-assignment-be
```

## Docker Compose (Recommended for Local Run)
```bash
docker compose up --build
```

This starts:
- API at `http://localhost:8000`
- Postgres at `localhost:5432`

Note: compose startup runs migrations and `collectstatic` automatically, so Django admin CSS/JS loads correctly in containerized mode.

---

## CI/CD

GitHub Actions (`.github/workflows/deploy.yml`) — on push to `main`:
1. Runs all tests
2. Builds Docker image
3. Pushes to Docker Hub as `zorvyn-assignment-be:latest`

**Required GitHub secrets:** `SECRET_KEY`, `DATABASE_URL`, `DOCKER_USERNAME`, `DOCKER_PASSWORD`
