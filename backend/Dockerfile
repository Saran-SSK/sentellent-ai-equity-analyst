# Use official Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevent Python from writing .pyc files
# PYTHONUNBUFFERED: Ensure Python output is sent straight to stdout/stderr
# PYTHONPATH: Add /app to Python path for module imports
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
# gcc and g++ are required for building some Python packages
# curl is required for healthcheck
# postgresql-client is required for psql in entrypoint script
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements file first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies
# --mount=type=cache: Use Docker BuildKit cache for pip downloads to avoid re-downloading unchanged packages
# --upgrade pip: Ensure pip is up to date
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Create a non-root user for security
# Running as root is a security risk in production
RUN useradd --create-home --shell /bin/bash appuser

# Copy application source code with ownership
COPY --chown=appuser:appuser . .

# Copy and make entrypoint script executable
COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose FastAPI port (default 8000)
EXPOSE 8000

# Healthcheck to verify FastAPI server is responding
# Checks root endpoint (/) every 30s with 10s timeout, 3 retries before marking unhealthy
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=5s \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application with entrypoint script
# Entrypoint waits for PostgreSQL, runs migrations, then starts FastAPI
CMD ["/app/entrypoint.sh"]
