# Zorvyn Assignment Backend

Django REST API for role-based user management, financial records, and dashboard analytics.

## Stack
- Python 3.12
- Django 6
- Django REST Framework
- PostgreSQL
- JWT (access + refresh)
- Docker + GitHub Actions

## Roles
- ADMIN: full access
- ANALYST: view records with filters and dashboard
- VIEWER: list records and dashboard

## Authentication
- Access token lifetime: 15 minutes
- Refresh token lifetime: 7 days
- Authorization header:

```http
Authorization: Bearer <access_token>
```

## API

### Auth
```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
```

### User Management (ADMIN)
```text
GET    /api/manage/users/
POST   /api/manage/users/
GET    /api/manage/users/<id>/
PATCH  /api/manage/users/<id>/
DELETE /api/manage/users/<id>/
```

### Financial Records
```text
GET    /api/finance/records/
POST   /api/finance/records/
GET    /api/finance/records/<id>/
PATCH  /api/finance/records/<id>/
DELETE /api/finance/records/<id>/
```

Filters for ANALYST and ADMIN:
- `type`
- `category`
- `date`
- `date_from`
- `date_to`
- `search`
- `page`
- `page_size`

### Dashboard
```text
GET /api/dashboard/summary/
```

### API Docs
```text
GET /api/schema/
GET /api/docs/
```

## Run With Docker Compose

```bash
docker compose up -d --build
```

Services:
- API: http://localhost:8000
- Postgres: localhost:5432

Compose startup runs:
- `python manage.py migrate`
- `python manage.py collectstatic --noinput`
- Gunicorn

## Admin

Create superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Admin URL:
- http://localhost:8000/admin/

## Local Development (without Docker)

```bash
python -m venv .venv
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Required environment variables:
- `SECRET_KEY`
- `DATABASE_URL`
- `DEBUG`

Optional:
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `DJANGO_LOG_LEVEL`
- `JWT_ACCESS_TOKEN_LIFETIME_MINUTES`
- `JWT_REFRESH_TOKEN_LIFETIME_DAYS`

## Tests

```bash
docker compose exec web python manage.py test accounts financial_records user_management dashboard
```

## CI/CD

Workflow file: `.github/workflows/deploy.yml`

Triggers:
- push to `master`
- pull request to `master`

Behavior:
- runs tests on push and pull request
- builds and pushes Docker image on push only

Required GitHub secrets for Docker publish:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
