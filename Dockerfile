# First stage: build
FROM python:3.12-alpine AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Set work directory
WORKDIR "${APP_HOME}"

# Install system dependencies and clean up
RUN apk update && apk upgrade && apk add --no-cache \
    build-base \
    python3-dev \
    curl \
    gcc \
    musl-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*

# Install uv
RUN pip install --upgrade pip setuptools \
    && pip install --no-cache-dir uv

RUN pip cache purge

# Copy project files needed for building
COPY pyproject.toml uv.lock* README.md /app/
COPY src /app/src

# Install project dependencies
RUN uv sync --frozen --no-cache --group dev

# Remove unnecessary files and cache
RUN find . -type f -name "*.pyc" -print -delete && \
  find . -type d -name "__pycache__" -exec rm -rf {} + && \
  find . -type d -name "*.egg-info" -exec rm -rf {} + && \
  rm -rf /root/.cache/pip && \
  rm -rf /root/.cache/uv

# Second stage: runtime
FROM python:3.12-alpine

# Set environment variables
ENV APP_HOME=/app

# Upgrade pip, setuptools to the latest versions
RUN pip install --upgrade pip setuptools

# Install runtime dependencies
RUN apk update && apk upgrade && apk add --no-cache \
    libpq \
    && rm -rf /var/cache/apk/*

# Create the 1001 user
RUN addgroup -S app && adduser -S -u 1001 -G app app

# Set work directory
WORKDIR "${APP_HOME}"

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy project
COPY src "${APP_HOME}/src"
COPY pyproject.toml uv.lock* README.md "${APP_HOME}/"

# Chown all the files to the 1001 user
RUN chown -R 1001:1001 "${APP_HOME}"

# Change to the 1001 user
USER 1001

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

ARG COMMIT_ID
ARG BRANCH_NAME
ARG TAG
ARG BUILD_TIME

ENV COMMIT_ID=${COMMIT_ID}
ENV BRANCH_NAME=${BRANCH_NAME}
ENV TAG=${TAG}
ENV BUILD_TIME=${BUILD_TIME}

# Expose the port ASGI will listen on
EXPOSE 8000

# Run the application:
CMD ["python", "-m", "src.main", "--host", "0.0.0.0", "--port", "8000"]
