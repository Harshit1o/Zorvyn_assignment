# ---------- Stage 1: Build Layer ----------
    FROM python:3.12-slim-bookworm AS builder

    WORKDIR /app
    
    # Install build dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    # Install Python dependencies
    COPY requirements.txt .
    RUN pip install --upgrade pip \
     && pip install --no-cache-dir --prefix=/install -r requirements.txt
    
    # ---------- Stage 2: Minimal Runtime ----------
    FROM python:3.12-slim-bookworm
    
    WORKDIR /app
    
    # Install libpq only for psycopg2 (no compilers needed here)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy installed dependencies from builder
    COPY --from=builder /install /usr/local
    
    # Copy your app code
    COPY . .
    
    EXPOSE 8000
    
    # Run the application
    CMD ["gunicorn", "zorvyn_assignment.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
    