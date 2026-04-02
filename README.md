# Zorvyn Assignment

## Executive Summary

Reference documentation: https://harshit1o.github.io/Zorvyn_assignment/

This project is more than a basic CRUD implementation. It includes custom JWT authentication, role-aware permissions, filtered and paginated record access, soft deletion for safer data lifecycle management, analytics endpoints, containerized deployment, API documentation, and CI-backed validation.

## Project Scope

The system is divided into four primary domains:

- Authentication and identity management
- Role-based user management
- Financial record operations
- Dashboard analytics and reporting

### Core Functional Capabilities

- Register users and authenticate them through JWT-based login and refresh flows
- Manage users with explicit ADMIN, ANALYST, and VIEWER roles
- Create, update, retrieve, filter, paginate, and soft-delete financial records
- Expose summary-level dashboard analytics for business visibility
- Publish OpenAPI schema and Swagger documentation for integration and review

## Technology Stack

### Backend

- Python 3.12
- Django 6
- Django REST Framework

### Database and Persistence

- PostgreSQL 16
- Django ORM

### Authentication and Security

- Custom JWT authentication built with `PyJWT`
- Django password validation
- Role-based permission classes
- DRF request throttling for anonymous, authenticated, login, and registration flows

### Documentation and API Tooling

- `drf-spectacular` for OpenAPI schema generation
- Swagger UI endpoint at `/api/docs/`

### Deployment and Runtime

- Docker
- Docker Compose
- Gunicorn
- WhiteNoise for static asset handling
- `django-cors-headers` for controlled cross-origin access

### Delivery and Validation

- GitHub Actions
- Automated test execution
- Docker image build and push workflow

## Architecture Overview

### `accounts`

Handles custom user identity, registration, login, token refresh, and permission classes.

### `user_management`

Exposes administrator-only endpoints for managing analyst and viewer accounts.

### `financial_records`

Provides the financial record model, filtering, pagination, soft deletion, and CRUD operations.

### `dashboard`

Aggregates financial data into totals, category breakdowns, recent activity, and trend views.

## Roles and Access Model

The access model is intentionally explicit:

- `ADMIN`
  Full access to user management and financial record mutation
- `ANALYST`
  Access to filtered financial record views, record detail retrieval, and dashboard analytics
- `VIEWER`
  Read-oriented access to record listings and dashboard analytics

This is one of the project's main strengths. Business permissions are enforced in the API layer rather than left to client-side assumptions.

## Authentication Model

The API uses Bearer token authentication.

```http
Authorization: Bearer <access_token>
```

### Token Policy

- Access token lifetime defaults to 15 minutes
- Refresh token lifetime defaults to 7 days
- Token durations are configurable through environment variables

### Security Notes

- Tokens are signed using the Django `SECRET_KEY`
- Refresh tokens are validated separately from access tokens
- Invalid, expired, malformed, or wrong-token-type credentials are rejected

## API Endpoints

### Authentication

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
```

### User Management

Administrator-only endpoints:

```text
GET    /api/manage/users/
POST   /api/manage/users/
GET    /api/manage/users/<uuid>/
PATCH  /api/manage/users/<uuid>/
DELETE /api/manage/users/<uuid>/
```

### Financial Records

```text
GET    /api/finance/records/
POST   /api/finance/records/
GET    /api/finance/records/<uuid>/
PATCH  /api/finance/records/<uuid>/
DELETE /api/finance/records/<uuid>/
```

Available filters for ANALYST and ADMIN users:

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

The dashboard endpoint includes:

- Total income
- Total expense
- Net balance
- Category-wise aggregates
- Recent financial activity
- Monthly trends
- Weekly trends

### Platform Health and Documentation

```text
GET /health/
GET /api/schema/
GET /api/docs/
```

## What Differentiates This Project

### 1. Role-aware domain design

Many comparable backend assignments expose endpoints without meaningful operational boundaries. Zorvyn uses an explicit role model and enforces authorization in the API layer, which makes the service closer to a real internal business platform.

### 2. Analytics built into the product surface

The system does not stop at data entry. It also produces actionable reporting through dashboard summaries, category-level totals, and time-based trends. This makes the service useful for decision support, not just record storage.

### 3. Safer record lifecycle through soft deletion

Financial records are soft-deleted instead of being immediately removed from persistence. This is important because financial systems benefit from recoverability, auditability, and reduced accidental data loss.

### 4. Deployment discipline

Containerization, runtime server configuration, migration execution, static collection, and CI automation are already included. That is a substantial difference from projects that remain tied to local-only execution.

## Why It Is Production Ready

The project includes several characteristics associated with production-capable backend systems:

- Containerized deployment with Docker and Docker Compose
- Dedicated PostgreSQL service
- Gunicorn-based application serving
- Environment-driven configuration
- `ALLOWED_HOSTS` and CORS configuration
- Request throttling for abuse mitigation
- OpenAPI schema generation and Swagger docs
- Automated tests in CI
- Docker image build and publish workflow
- WhiteNoise static asset management
- Structured logging configuration

Production ready here means the system already reflects the operational concerns needed for controlled deployment, maintainability, and extension. It does not imply that no further hardening or monitoring would ever be needed.

## Local Development

### Prerequisites

- Python 3.12+
- PostgreSQL
- Docker and Docker Compose, if running containerized

### Run Locally Without Docker

```bash
python -m venv .venv
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Required Environment Variables

- `SECRET_KEY`
- `DATABASE_URL`
- `DEBUG`

### Optional Environment Variables

- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `DJANGO_LOG_LEVEL`
- `JWT_ACCESS_TOKEN_LIFETIME_MINUTES`
- `JWT_REFRESH_TOKEN_LIFETIME_DAYS`

## Docker Execution

Start the full stack:

```bash
docker compose up -d --build
```

Available services:

- API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

Container startup performs:

- `python manage.py migrate`
- `python manage.py collectstatic --noinput`
- Gunicorn application startup

### Django Admin

Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Admin console:

- `http://localhost:8000/admin/`

## Testing

Run tests with Docker:

```bash
docker compose exec web python manage.py test accounts financial_records user_management dashboard
```

The repository currently includes active test coverage for authentication and financial-record behavior in CI. Those tests validate core API paths and permission-sensitive logic.

## CI/CD

Workflow file:

- `.github/workflows/deploy.yml`

### Current workflow behavior

- Runs on push to `master`
- Runs on pull requests targeting `master`
- Installs dependencies
- Executes Django tests
- Builds a Docker image on push events
- Pushes the image to Docker Hub on push events

### Required GitHub Secrets

- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

## Project Positioning

Zorvyn should be presented as a secure financial operations backend rather than a generic API assignment. Its primary value lies in combining access governance, financial data handling, analytics, and deployment discipline into one coherent service. That combination is the project's strongest differentiator and the main reason it reads as production-capable rather than academic.
