# Use slim-bullseye which is more secure
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/moderation

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /moderation

# Install system dependencies and security updates
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /moderation

# Switch to non-root user
USER appuser
EXPOSE 8000

# Run the application
CMD ["uvicorn", "moderation.main:app", "--host", "0.0.0.0", "--port", "$PORT"]